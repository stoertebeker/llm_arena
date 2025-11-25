from __future__ import annotations
import asyncio, json, os
import typer
from rich import print as rprint
from pathlib import Path

from llm_arena.config import load_config
from llm_arena.generation import generate_triplet
from llm_arena.judging import run_judging
from llm_arena.aggregation import aggregate_results
from llm_arena.elo import update_elo, triplet_pairs
from llm_arena.logging_ext import log_jsonl
from llm_arena.utils import new_run_id

app = typer.Typer(add_completion=False)

@app.command()
def main(
    prompt: str = typer.Option(..., "--prompt", "-p", help="User prompt to evaluate"),
    config_path: str = typer.Option("config.toml", "--config", "-c"),
    reveal_provenance: bool = typer.Option(None, "--reveal-provenance/--no-reveal-provenance", help="Override config setting"),
):
    cfg = load_config(config_path)
    settings = cfg.settings
    if reveal_provenance is not None:
        settings.reveal_provenance = reveal_provenance

    params = dict(
        temperature=settings.temperature,
        top_p=settings.top_p,
        max_tokens=settings.max_tokens,
        timeout=settings.request_timeout_seconds,
    )

    run_id = new_run_id()

    async def _run():
        triplet, gen_clients = await generate_triplet(
            user_prompt=prompt,
            candidates=cfg.candidates,
            base_url=cfg.providers.base_url,
            default_api_key=cfg.providers.api_key,
            params=params
        )
        for c in gen_clients.values():
            await c.aclose()

        judge_tpl = Path("llm_arena/prompts/judge_prompt.txt").read_text(encoding="utf-8")
        judgements = await run_judging(
            user_prompt=prompt,
            triplet=triplet,
            judges=cfg.judges,
            base_url=cfg.providers.base_url,
            default_api_key=cfg.providers.api_key,
            judge_template_text=judge_tpl,
            reveal_provenance=cfg.settings.reveal_provenance,
            params=params,
            retries=cfg.settings.retries,
            run_id=run_id,
        )

        agg = aggregate_results(judgements, triplet)

        elo_updates = None
        if cfg.settings.elo_enabled and agg["winner_provider"]:
            ratings = {c.name: cfg.settings.elo_initial for c in cfg.candidates}
            pairs = triplet_pairs(agg["winner_provider"], [c.name for c in cfg.candidates])
            for w,l in pairs:
                update_elo(ratings, winner=w, loser=l, k=cfg.settings.elo_k)
            elo_updates = ratings

        result = {
            "run_id": run_id,
            "prompt": prompt,
            "settings": {
                "reveal_provenance": cfg.settings.reveal_provenance,
                "elo_enabled": cfg.settings.elo_enabled,
                "k": cfg.settings.elo_k,
            },
            "judgements": {k: v.model_dump() for k,v in judgements.items()},
            "aggregation": agg,
            "elo": elo_updates,
        }

        os.makedirs("runs", exist_ok=True)
        with open(f"runs/{run_id}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        log_jsonl("logs/events.jsonl", result)

        out = {
            "run_id": run_id,
            "winner_provider": agg["winner_provider"],
            "votes": agg["votes"],
            "mean_scores": agg["mean_scores"],
            "winner_answer": {
                "id": agg["winner_answer_id"],
                "text": agg["winner_answer_text"]
            }
        }
        rprint(json.dumps(out, ensure_ascii=False, indent=2))

    asyncio.run(_run())

if __name__ == "__main__":
    app()

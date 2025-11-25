from __future__ import annotations
import asyncio, json, re
from typing import List, Dict
from jinja2 import Template
from .types import ChatMessage, JudgeOutput, Candidate, Triplet
from .logging_ext import log_jsonl
from .providers.openai_compat import OpenAICompatClient

def _render_prompt(tpl_text: str, *, user_prompt: str, triplet: Triplet, reveal_provenance: bool) -> str:
    tpl = Template(tpl_text)
    prov = triplet.provenance_map
    return tpl.render(
        user_prompt=user_prompt,
        answer_A=triplet.answers["A"],
        answer_B=triplet.answers["B"],
        answer_C=triplet.answers["C"],
        reveal_provenance=reveal_provenance,
        prov_A=prov["A"], prov_B=prov["B"], prov_C=prov["C"],
    )

def _extract_json(text: str) -> str | None:
    # Find JSON block within ```json ... ```
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Find JSON block within ``` ... ```
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # If no markdown, assume the whole text might be JSON
    return text

async def _judge_one(client: OpenAICompatClient, rendered_prompt: str, params: dict, retries: int = 1, run_id: str | None = None) -> JudgeOutput | None:
    sys = ChatMessage(role="system", content="You are a strict evaluator that outputs ONLY valid JSON per the given schema.")
    usr = ChatMessage(role="user", content=rendered_prompt)
    for attempt in range(retries + 1):
        raw_response = ""
        try:
            raw_response = await client.chat(messages=[sys, usr], params=params)
            clean_json_str = _extract_json(raw_response)
            if not clean_json_str:
                raise ValueError("Extracted JSON string is empty")
            data = json.loads(clean_json_str)
            return JudgeOutput.model_validate(data)
        except Exception as e:
            log_jsonl(
                "logs/events.jsonl",
                {
                    "event": "judge_failure",
                    "run_id": run_id,
                    "judge": client.name,
                    "error": str(e),
                    "raw_response": raw_response,
                    "attempt": attempt,
                    "is_repair": False,
                },
            )
            if attempt < retries:
                repair = ChatMessage(role="user", content="Your last output was not valid JSON per schema. Respond again with ONLY the valid JSON object.")
                try:
                    raw_response_repair = await client.chat(messages=[sys, usr, repair], params=params)
                    clean_json_str_repair = _extract_json(raw_response_repair)
                    if not clean_json_str_repair:
                        raise ValueError("Extracted JSON string from repair is empty")
                    data2 = json.loads(clean_json_str_repair)
                    return JudgeOutput.model_validate(data2)
                except Exception as e2:
                    log_jsonl(
                        "logs/events.jsonl",
                        {
                            "event": "judge_failure",
                            "run_id": run_id,
                            "judge": client.name,
                            "error": str(e2),
                            "raw_response": raw_response_repair,
                            "attempt": attempt,
                            "is_repair": True,
                        },
                    )
                    continue
            return None

async def run_judging(*, user_prompt: str, triplet: Triplet, judges: List[Candidate], base_url: str, default_api_key: str, judge_template_text: str, reveal_provenance: bool, params: dict, retries: int, run_id: str) -> Dict[str, JudgeOutput]:
    rendered = _render_prompt(judge_template_text, user_prompt=user_prompt, triplet=triplet, reveal_provenance=reveal_provenance)
    clients: Dict[str, OpenAICompatClient] = {}
    for j in judges:
        clients[j.name] = OpenAICompatClient(
            name=j.name,
            model=j.model,
            base_url=(j.base_url or base_url),
            api_key=(j.api_key or default_api_key),
            timeout=params.get("timeout", 120)
        )
    tasks = [
        _judge_one(clients[name], rendered, params, retries=retries, run_id=run_id)
        for name in clients
    ]
    results = await asyncio.gather(*tasks)
    out: Dict[str, JudgeOutput] = {}
    for name, res in zip(clients.keys(), results):
        if res is not None:
            out[name] = res
    await asyncio.gather(*[c.aclose() for c in clients.values()])
    return out

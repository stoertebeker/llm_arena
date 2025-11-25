from __future__ import annotations
import asyncio, json
from typing import List, Dict
from jinja2 import Template
from .types import ChatMessage, JudgeOutput, Candidate, Triplet
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

async def _judge_one(client: OpenAICompatClient, rendered_prompt: str, params: dict, retries: int = 1) -> JudgeOutput | None:
    sys = ChatMessage(role="system", content="You are a strict evaluator that outputs ONLY valid JSON per the given schema.")
    usr = ChatMessage(role="user", content=rendered_prompt)
    for attempt in range(retries + 1):
        try:
            raw = await client.chat(messages=[sys, usr], params=params)
            data = json.loads(raw)
            return JudgeOutput.model_validate(data)
        except Exception:
            if attempt < retries:
                repair = ChatMessage(role="user", content="Your last output was not valid JSON per schema. Respond again with ONLY the valid JSON object.")
                try:
                    raw2 = await client.chat(messages=[sys, usr, repair], params=params)
                    data2 = json.loads(raw2)
                    return JudgeOutput.model_validate(data2)
                except Exception:
                    continue
            return None

async def run_judging(*, user_prompt: str, triplet: Triplet, judges: List[Candidate], base_url: str, default_api_key: str, judge_template_text: str, reveal_provenance: bool, params: dict, retries: int) -> Dict[str, JudgeOutput]:
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
    results = await asyncio.gather(*[
        _judge_one(clients[name], rendered, params, retries=retries) for name in clients
    ])
    out: Dict[str, JudgeOutput] = {}
    for name, res in zip(clients.keys(), results):
        if res is not None:
            out[name] = res
    await asyncio.gather(*[c.aclose() for c in clients.values()])
    return out

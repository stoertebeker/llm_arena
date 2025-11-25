from __future__ import annotations
import asyncio, random
from typing import Dict, Tuple, List
from .types import ChatMessage, Triplet, Candidate
from .providers.openai_compat import OpenAICompatClient
from .normalization import normalize_text

async def _generate_one(client: OpenAICompatClient, user_prompt: str, params: dict) -> str:
    msgs = [
        ChatMessage(role="system", content="You are a helpful, concise assistant."),
        ChatMessage(role="user", content=user_prompt),
    ]
    return await client.chat(messages=msgs, params=params)

async def generate_triplet(*, user_prompt: str, candidates: List[Candidate], base_url: str, default_api_key: str, params: dict) -> Tuple[Triplet, Dict[str, OpenAICompatClient]]:
    clients: Dict[str, OpenAICompatClient] = {}
    for c in candidates:
        clients[c.name] = OpenAICompatClient(
            name=c.name,
            model=c.model,
            base_url=(c.base_url or base_url),
            api_key=(c.api_key or default_api_key),
            timeout=params.get("timeout", 120)
        )
    results = await asyncio.gather(*[
        _generate_one(clients[name], user_prompt, params) for name in clients
    ])
    texts = {name: normalize_text(text) for name, text in zip(clients.keys(), results)}
    provider_names = list(texts.keys())
    random.shuffle(provider_names)
    id_map = {"A": provider_names[0], "B": provider_names[1], "C": provider_names[2]}
    answers = {"A": texts[id_map["A"]], "B": texts[id_map["B"]], "C": texts[id_map["C"]]}
    triplet = Triplet(answers=answers, provenance_map=id_map)
    return triplet, clients

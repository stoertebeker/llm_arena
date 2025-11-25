from __future__ import annotations
import httpx
from typing import Sequence, Mapping, Any, Optional
from ..types import ChatMessage
from .base import ModelClient

class OpenAICompatClient(ModelClient):
    def __init__(self, *, name: str, model: str, base_url: str, api_key: Optional[str] = None, timeout: int = 120):
        self.name = name
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
    
    async def chat(self, *, messages: Sequence[ChatMessage], params: Mapping[str, Any]) -> str:
        payload = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "temperature": params.get("temperature", 0.2),
            "top_p": params.get("top_p", 1.0),
            "max_tokens": params.get("max_tokens", 1024),
        }
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        r = await self._client.post("/v1/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        try:
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"{self.name} invalid response format: {data}") from e
    
    async def aclose(self):
        await self._client.aclose()

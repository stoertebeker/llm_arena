from __future__ import annotations
from typing import Sequence, Mapping, Any
from ..types import ChatMessage

class ModelClient:
    name: str
    async def chat(self, *, messages: Sequence[ChatMessage], params: Mapping[str, Any]) -> str: ...

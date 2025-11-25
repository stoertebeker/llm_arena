from __future__ import annotations
from typing import Literal, Dict, List, Optional
from pydantic import BaseModel, Field

Role = Literal["system","user","assistant"]

class ChatMessage(BaseModel):
    role: Role
    content: str

CriteriaKey = Literal["correctness","completeness","clarity","safety","evidence","relevance"]

class ScoreVector(BaseModel):
    correctness: int = Field(ge=0, le=10)
    completeness: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    safety: int = Field(ge=0, le=10)
    evidence: int = Field(ge=0, le=10)
    relevance: int = Field(ge=0, le=10)

AnswerID = Literal["A","B","C"]

class JudgeOutput(BaseModel):
    winner: AnswerID
    scores: Dict[AnswerID, ScoreVector]
    rationale: str

class Candidate(BaseModel):
    name: str          # provider logical name
    model: str         # route/model ID
    base_url: Optional[str] = None
    api_key: Optional[str] = None

class Settings(BaseModel):
    reveal_provenance: bool = False
    elo_enabled: bool = True
    elo_initial: int = 1500
    elo_k: int = 16
    temperature: float = 0.2
    top_p: float = 1.0
    max_tokens: int = 1024
    request_timeout_seconds: int = 120
    retries: int = 1

class Providers(BaseModel):
    base_url: str
    api_key: str

class Config(BaseModel):
    providers: Providers
    candidates: List[Candidate]
    judges: List[Candidate]
    settings: Settings

class Triplet(BaseModel):
    # After shuffle/anon
    answers: Dict[AnswerID, str]
    provenance_map: Dict[AnswerID, str]  # A->provider name

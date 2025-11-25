from __future__ import annotations
from typing import Dict, List, Tuple

def expected_score(r_self: float, r_opp: float) -> float:
    return 1.0 / (1.0 + 10 ** ((r_opp - r_self) / 400.0))

def update_elo(ratings: Dict[str, float], *, winner: str, loser: str, k: int = 16) -> None:
    rw, rl = ratings.get(winner, 1500), ratings.get(loser, 1500)
    ew = expected_score(rw, rl)
    el = expected_score(rl, rw)
    ratings[winner] = rw + k * (1 - ew)
    ratings[loser]  = rl + k * (0 - el)

def triplet_pairs(overall_winner_provider: str, all_providers: List[str]) -> List[Tuple[str,str]]:
    losers = [p for p in all_providers if p != overall_winner_provider]
    return [(overall_winner_provider, l) for l in losers]

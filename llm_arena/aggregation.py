from __future__ import annotations
from typing import Dict
from .types import JudgeOutput, Triplet

def aggregate_results(judgements: Dict[str, JudgeOutput], triplet: Triplet) -> dict:
    vote_counts: Dict[str, int] = {}
    score_sums: Dict[str, list] = {}
    prov = triplet.provenance_map
    for j in judgements.values():
        winner_id = j.winner
        prov_name = prov[winner_id]
        vote_counts[prov_name] = vote_counts.get(prov_name, 0) + 1
        for ans_id, scores in j.scores.items():
            pname = prov[ans_id]
            score_sums.setdefault(pname, []).append(scores.model_dump())
    winner_provider = max(vote_counts.items(), key=lambda kv: kv[1])[0] if vote_counts else None
    winner_answer_id = None
    winner_answer_text = None
    if winner_provider:
        for aid, pname in prov.items():
            if pname == winner_provider:
                winner_answer_id = aid
                winner_answer_text = triplet.answers[aid]
                break
    mean_scores: Dict[str, dict] = {}
    for pname, vecs in score_sums.items():
        if not vecs: 
            continue
        keys = vecs[0].keys()
        mean_scores[pname] = {k: round(sum(v[k] for v in vecs)/len(vecs), 2) for k in keys}
    return {
        "winner_provider": winner_provider,
        "winner_answer_id": winner_answer_id,
        "winner_answer_text": winner_answer_text,
        "votes": vote_counts,
        "mean_scores": mean_scores,
        "provenance_map": prov
    }

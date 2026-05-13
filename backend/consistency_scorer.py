"""
Consistency Scorer.

For a set of retrieved judgments, finds pairs with similar facts
(cosine similarity > threshold) but different outcomes.

This is the research contribution:
- Similarity threshold: 0.75 cosine similarity on fact embeddings
- Divergence score: 1.0 if outcomes differ, 0.0 if same
- Weighted by similarity (highly similar cases with different outcomes = high divergence)

Use case: a legal researcher or journalist can use this to flag
potential judicial inconsistency or regional bias across similar cases.
"""

import numpy as np
from backend.models import RetrievalResult, ConsistencyFlag
from backend.embeddings import embed

SIMILARITY_THRESHOLD = 0.72

OUTCOME_GROUPS = {
    "convicted": "against_accused",
    "acquitted": "for_accused",
    "dismissed": "for_accused",
    "settled": "neutral",
}

def _outcome_group(outcome: str) -> str:
    return OUTCOME_GROUPS.get(outcome.lower(), "unknown")

def score(results: list[RetrievalResult]) -> list[ConsistencyFlag]:
    """
    Compare all pairs of results for factual similarity + outcome divergence.
    Returns flags for pairs that are highly similar but reached different outcomes.
    """
    if len(results) < 2:
        return []

    # Embed all fact summaries
    texts = [r.facts_summary for r in results]
    vecs = np.array(embed(texts), dtype=np.float32)
    # Already normalised from embed(), but normalise again to be safe
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    vecs = vecs / np.where(norms == 0, 1e-9, norms)

    # Compute pairwise cosine similarity matrix
    sim_matrix = vecs @ vecs.T

    flags: list[ConsistencyFlag] = []
    seen = set()

    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            sim = float(sim_matrix[i, j])
            if sim < SIMILARITY_THRESHOLD:
                continue

            outcome_i = _outcome_group(results[i].outcome)
            outcome_j = _outcome_group(results[j].outcome)

            if outcome_i == "neutral" or outcome_j == "neutral":
                continue

            pair_key = tuple(sorted([results[i].case_id, results[j].case_id]))
            if pair_key in seen:
                continue
            seen.add(pair_key)

            diverged = outcome_i != outcome_j
            divergence_score = sim if diverged else 0.0

            if diverged:
                explanation = (
                    f"Cases {results[i].case_id} ({results[i].outcome}) and "
                    f"{results[j].case_id} ({results[j].outcome}) have "
                    f"{sim:.0%} factual similarity but reached opposite outcomes. "
                    f"Both involve {results[i].section_cited}. "
                    f"Possible causes: different evidence quality, judicial discretion, "
                    f"regional variation, or procedural differences."
                )
                flags.append(ConsistencyFlag(
                    case_id_a=results[i].case_id,
                    case_id_b=results[j].case_id,
                    similarity_score=round(sim, 4),
                    outcome_a=results[i].outcome,
                    outcome_b=results[j].outcome,
                    divergence_score=round(divergence_score, 4),
                    explanation=explanation,
                ))

    # Sort by divergence score descending
    flags.sort(key=lambda f: f.divergence_score, reverse=True)
    return flags

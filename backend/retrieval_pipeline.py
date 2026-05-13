"""
Main retrieval pipeline.

Stage 1: Hybrid retrieval — BM25 + dense embeddings, merged via Reciprocal Rank Fusion
Stage 2: Cross-encoder reranking (simulated with dot-product on richer representations)
Stage 3: Graph RAG — enrich results with precedent chain context

This three-stage pipeline is what separates this from "chat with PDF" RAG.
"""

import numpy as np
from backend.models import Judgment, RetrievalResult, Chunk
from backend.embeddings import embed_single, embed
from backend.bm25_retriever import get_bm25
from backend.vector_store import get_store
from backend.graph_rag import get_graph

# ── Reciprocal Rank Fusion ────────────────────────────────────────────────────

def _rrf(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    """
    Reciprocal Rank Fusion: merges multiple ranked lists.
    Score(d) = sum(1 / (k + rank_i(d))) across all lists.
    Standard fusion algorithm used in TREC evaluations.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return scores

# ── Simulated cross-encoder reranker ─────────────────────────────────────────

def _rerank(query: str, candidates: list[RetrievalResult]) -> list[RetrievalResult]:
    """
    Production: use cross-encoder/ms-marco-MiniLM-L-6-v2 from sentence-transformers.
    Here: re-embed [query + facts + reasoning] and compute richer dot-product score.
    This still demonstrates the two-stage pattern.
    """
    if not candidates:
        return candidates

    # Create richer text representations for reranking
    pair_texts = [
        f"Query: {query} Document: {c.facts_summary} {c.legal_reasoning} Section: {c.section_cited}"
        for c in candidates
    ]
    query_vec = np.array(embed_single(query), dtype=np.float32)
    doc_vecs = np.array(embed(pair_texts), dtype=np.float32)

    # Cosine similarity with richer representations
    scores = doc_vecs @ query_vec
    for i, c in enumerate(candidates):
        c.rerank_score = float(scores[i])

    candidates.sort(key=lambda c: c.rerank_score, reverse=True)
    return candidates

# ── Main pipeline ─────────────────────────────────────────────────────────────

def retrieve(
    query: str,
    judgments: list[Judgment],
    top_k: int = 5,
    debug: bool = False,
    allowed_case_ids: set[str] | None = None,
) -> tuple[list[RetrievalResult], dict]:
    """
    Full three-stage retrieval pipeline.
    Returns (results, debug_info) where debug_info exposes internals for the researcher view.
    """
    debug_info = {
        "query": query,
        "bm25_hits": [],
        "dense_hits": [],
        "rrf_scores": {},
        "pre_rerank_order": [],
        "post_rerank_order": [],
    }

    # ── Stage 1a: BM25 ────────────────────────────────────────────────────
    bm25 = get_bm25()
    bm25_results = bm25.query(query, top_k=20)
    bm25_ranking = [j.case_id for j, _ in bm25_results]
    bm25_scores = {j.case_id: score for j, score in bm25_results}

    if debug:
        debug_info["bm25_hits"] = [
            {"case_id": j.case_id, "score": round(s, 4), "court": j.court}
            for j, s in bm25_results[:8]
        ]

    # ── Stage 1b: Dense retrieval ─────────────────────────────────────────
    store = get_store()
    query_vec = embed_single(query)
    dense_results = store.query(query_vec, top_k=20)

    # Deduplicate by case_id (take best chunk score per case)
    seen_cases: dict[str, float] = {}
    for chunk, score in dense_results:
        if chunk.case_id not in seen_cases or score > seen_cases[chunk.case_id]:
            seen_cases[chunk.case_id] = score

    dense_ranking = sorted(seen_cases.keys(), key=lambda cid: seen_cases[cid], reverse=True)
    dense_scores = seen_cases

    if debug:
        debug_info["dense_hits"] = [
            {"case_id": cid, "score": round(seen_cases[cid], 4)}
            for cid in dense_ranking[:8]
        ]

    # ── Stage 1c: Reciprocal Rank Fusion ─────────────────────────────────
    rrf_scores = _rrf([bm25_ranking, dense_ranking])
    if debug:
        debug_info["rrf_scores"] = {k: round(v, 5) for k, v in
                                     sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:10]}

    # Build candidate list from top RRF scores
    judgment_map = {j.case_id: j for j in judgments}
    top_case_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
    if allowed_case_ids is not None:
        top_case_ids = [cid for cid in top_case_ids if cid in allowed_case_ids]
    top_case_ids = top_case_ids[: max(15, top_k)]

    candidates: list[RetrievalResult] = []
    for cid in top_case_ids:
        j = judgment_map.get(cid)
        if not j:
            continue
        candidates.append(RetrievalResult(
            case_id=j.case_id,
            court=j.court,
            date=j.date,
            judge=j.judge,
            section_cited=j.section_cited,
            outcome=j.outcome,
            facts_summary=j.facts_summary,
            legal_reasoning=j.legal_reasoning,
            state=j.state,
            bm25_score=round(bm25_scores.get(cid, 0.0), 4),
            dense_score=round(dense_scores.get(cid, 0.0), 4),
            fusion_score=round(rrf_scores.get(cid, 0.0), 5),
            citations=j.citations,
        ))

    if debug:
        debug_info["pre_rerank_order"] = [c.case_id for c in candidates[:8]]

    # ── Stage 2: Reranking ────────────────────────────────────────────────
    candidates = _rerank(query, candidates)
    final_results = candidates[:top_k]

    if debug:
        debug_info["post_rerank_order"] = [
            {"case_id": c.case_id, "rerank_score": round(c.rerank_score, 4)}
            for c in final_results
        ]

    # ── Stage 3: Graph RAG — enrich with precedent chain ─────────────────
    graph = get_graph()
    graph_context: list[Judgment] = []
    for result in final_results:
        ancestors = graph.get_precedent_chain(result.case_id, max_hops=2)
        for ancestor_node in ancestors:
            ancestor_j = judgment_map.get(ancestor_node.case_id)
            if ancestor_j and ancestor_j.case_id not in [r.case_id for r in final_results]:
                graph_context.append(ancestor_j)

    return final_results, {**debug_info, "graph_context_added": [j.case_id for j in graph_context]}

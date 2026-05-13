"""
FastAPI application - Nyay
"""

from pathlib import Path
import sys
import time
from collections import Counter
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from consistency_scorer import score as consistency_score
from graph_rag import get_graph
from indexing import build_indexes
from llm_synthesis import synthesise_citizen, synthesise_researcher
from models import Judgment
from retrieval_pipeline import retrieve

app = FastAPI(
    title="Nyay",
    description=(
        "Graph-RAG pipeline over Indian district court judgments with "
        "precedent-chain traversal and consistency scoring."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_judgments: list[Judgment] = []
_ready = False


@app.on_event("startup")
async def startup():
    global _judgments, _ready
    _judgments = build_indexes()
    _ready = True
    print("API ready.")


class QueryRequest(BaseModel):
    query: str
    mode: str = "citizen"
    top_k: int = 5
    use_llm: bool = True
    section: Optional[str] = None
    state: Optional[str] = None
    outcome: Optional[str] = None


class JudgmentResult(BaseModel):
    case_id: str
    court: str
    date: str
    judge: str
    section_cited: str
    outcome: str
    state: str
    facts_summary: str
    legal_reasoning: str
    bm25_score: float
    dense_score: float
    fusion_score: float
    rerank_score: float
    citations: list[str]
    precedent_chain: list[dict]


class ConsistencyResult(BaseModel):
    case_id_a: str
    case_id_b: str
    similarity_score: float
    outcome_a: str
    outcome_b: str
    divergence_score: float
    explanation: str


class QueryResponse(BaseModel):
    query: str
    results: list[JudgmentResult]
    consistency_flags: list[ConsistencyResult]
    synthesis: Optional[str]
    graph_data: dict
    debug_info: dict
    metadata: dict
    latency_ms: float


def _normalise_filter(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    if not value or value.lower() == "all":
        return None
    return value


def _matches_filters(
    judgment: Judgment,
    section: Optional[str],
    state: Optional[str],
    outcome: Optional[str],
) -> bool:
    if section and section.lower() not in judgment.section_cited.lower():
        return False
    if state and state.lower() != judgment.state.lower():
        return False
    if outcome and outcome.lower() != judgment.outcome.lower():
        return False
    return True


def _analytics(judgments: list[Judgment]) -> dict:
    by_section = Counter(j.section_cited for j in judgments)
    by_state = Counter(j.state for j in judgments)
    by_outcome = Counter(j.outcome for j in judgments)
    graph = get_graph()
    return {
        "total_judgments": len(judgments),
        "sections": dict(by_section.most_common()),
        "states": dict(by_state.most_common()),
        "outcomes": dict(by_outcome.most_common()),
        "graph": {
            "nodes": graph.G.number_of_nodes(),
            "edges": graph.G.number_of_edges(),
        },
    }


@app.get("/health")
def health():
    graph = get_graph()
    return {
        "status": "ready" if _ready else "indexing",
        "judgments": len(_judgments),
        "graph_nodes": graph.G.number_of_nodes(),
        "graph_edges": graph.G.number_of_edges(),
    }


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    if not _ready:
        raise HTTPException(status_code=503, detail="Still indexing, please wait.")

    t0 = time.time()
    section = _normalise_filter(req.section)
    state = _normalise_filter(req.state)
    outcome = _normalise_filter(req.outcome)
    top_k = max(1, min(req.top_k, 10))
    filtered_judgments = [
        j for j in _judgments if _matches_filters(j, section, state, outcome)
    ]
    allowed_case_ids = {j.case_id for j in filtered_judgments}

    if not filtered_judgments:
        return QueryResponse(
            query=req.query,
            results=[],
            consistency_flags=[],
            synthesis="No indexed judgments match the selected filters.",
            graph_data={"nodes": [], "edges": []},
            debug_info={"query": req.query, "filtered_out": True},
            metadata={
                "applied_filters": {"section": section, "state": state, "outcome": outcome},
                "corpus": _analytics(_judgments),
                "filtered_count": 0,
                "retrieval_quality": {},
            },
            latency_ms=round((time.time() - t0) * 1000, 1),
        )

    results, debug_info = retrieve(
        query=req.query,
        judgments=_judgments,
        top_k=top_k,
        debug=True,
        allowed_case_ids=allowed_case_ids,
    )

    flags = consistency_score(results)

    judgment_map = {j.case_id: j for j in _judgments}
    graph = get_graph()
    precedent_judgments = []
    seen_precedents = {r.case_id for r in results}
    for r in results:
        chain = graph.get_precedent_chain(r.case_id, max_hops=2)
        for node in chain:
            if node.case_id not in seen_precedents:
                j = judgment_map.get(node.case_id)
                if j:
                    precedent_judgments.append(j)
                    seen_precedents.add(node.case_id)

    synthesis = None
    if req.use_llm and results:
        try:
            if req.mode == "researcher":
                synthesis = synthesise_researcher(
                    req.query,
                    results,
                    precedent_judgments,
                    flags,
                )
            else:
                synthesis = synthesise_citizen(
                    req.query,
                    results,
                    precedent_judgments,
                    flags,
                )
        except Exception as e:
            synthesis = f"LLM synthesis unavailable: {e}"

    result_case_ids = [r.case_id for r in results]
    graph_data = graph.get_subgraph(result_case_ids)

    result_objs = []
    for r in results:
        chain = graph.get_precedent_chain(r.case_id, max_hops=2)
        result_objs.append(
            JudgmentResult(
                case_id=r.case_id,
                court=r.court,
                date=r.date,
                judge=r.judge,
                section_cited=r.section_cited,
                outcome=r.outcome,
                state=r.state,
                facts_summary=r.facts_summary,
                legal_reasoning=r.legal_reasoning,
                bm25_score=r.bm25_score,
                dense_score=r.dense_score,
                fusion_score=r.fusion_score,
                rerank_score=r.rerank_score,
                citations=r.citations,
                precedent_chain=[
                    {"case_id": n.case_id, "court": n.court, "depth": n.depth}
                    for n in chain
                ],
            )
        )

    latency = (time.time() - t0) * 1000

    return QueryResponse(
        query=req.query,
        results=result_objs,
        consistency_flags=[ConsistencyResult(**f.__dict__) for f in flags],
        synthesis=synthesis,
        graph_data=graph_data,
        debug_info=debug_info,
        metadata={
            "applied_filters": {"section": section, "state": state, "outcome": outcome},
            "corpus": _analytics(_judgments),
            "filtered_count": len(filtered_judgments),
            "retrieval_quality": {
                "top_rerank_score": round(max((r.rerank_score for r in results), default=0.0), 4),
                "avg_fusion_score": round(
                    sum(r.fusion_score for r in results) / max(len(results), 1), 5
                ),
                "pipeline": ["BM25", "Dense", "RRF", "Rerank", "Graph RAG", "Consistency"],
            },
        },
        latency_ms=round(latency, 1),
    )


@app.get("/graph")
def full_graph():
    """Return the full citation graph for the D3 visualisation."""
    return get_graph().get_graph_data()


@app.get("/analytics")
def analytics():
    """Return corpus and graph statistics for the portfolio dashboard."""
    if not _ready:
        raise HTTPException(status_code=503, detail="Still indexing, please wait.")
    return _analytics(_judgments)


@app.get("/case/{case_id}")
def case_detail(case_id: str):
    """Return a full judgment record by ID."""
    for j in _judgments:
        if j.case_id == case_id:
            return {
                "case_id": j.case_id,
                "court": j.court,
                "date": j.date,
                "judge": j.judge,
                "section_cited": j.section_cited,
                "outcome": j.outcome,
                "state": j.state,
                "facts_summary": j.facts_summary,
                "legal_reasoning": j.legal_reasoning,
                "raw_text": j.raw_text,
                "citations": j.citations,
                "citing_cases": get_graph().get_citing_cases(j.case_id),
                "precedent_chain": [
                    node.__dict__ for node in get_graph().get_precedent_chain(j.case_id)
                ],
            }
    raise HTTPException(status_code=404, detail="Case not found")


@app.get("/judgments")
def list_judgments():
    return [
        {
            "case_id": j.case_id,
            "court": j.court,
            "section": j.section_cited,
            "outcome": j.outcome,
            "state": j.state,
            "date": j.date,
        }
        for j in _judgments
    ]

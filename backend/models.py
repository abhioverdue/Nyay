from dataclasses import dataclass, field
from typing import Optional
from datetime import date

@dataclass
class Judgment:
    case_id: str
    court: str
    date: str
    judge: str
    section_cited: str
    outcome: str          # "convicted" | "acquitted" | "settled" | "dismissed"
    facts_summary: str
    legal_reasoning: str
    raw_text: str
    state: str
    citations: list[str] = field(default_factory=list)   # case_ids this judgment cites

@dataclass
class Chunk:
    chunk_id: str
    case_id: str
    text: str
    embedding: Optional[list[float]] = None

@dataclass
class RetrievalResult:
    case_id: str
    court: str
    date: str
    judge: str
    section_cited: str
    outcome: str
    facts_summary: str
    legal_reasoning: str
    state: str
    bm25_score: float = 0.0
    dense_score: float = 0.0
    fusion_score: float = 0.0
    rerank_score: float = 0.0
    citations: list[str] = field(default_factory=list)

@dataclass
class ConsistencyFlag:
    case_id_a: str
    case_id_b: str
    similarity_score: float
    outcome_a: str
    outcome_b: str
    divergence_score: float
    explanation: str

@dataclass
class GraphNode:
    case_id: str
    court: str
    date: str
    outcome: str
    depth: int = 0

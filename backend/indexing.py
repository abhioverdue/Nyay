"""
Indexing script.
Runs once at startup to build BM25 index, embed all chunks into vector store,
and build the precedent graph.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models import Judgment, Chunk
from seed_data import JUDGMENTS as RAW_JUDGMENTS, CITATION_GRAPH
from real_data_loader import load_real_judgments
from bm25_retriever import get_bm25
from vector_store import get_store
from graph_rag import get_graph
from embeddings import embed
import hashlib

def chunk_judgment(j: Judgment) -> list[Chunk]:
    """
    Split a judgment into overlapping chunks.
    We create 3 chunks per judgment:
    - Facts chunk: section + facts summary
    - Reasoning chunk: legal reasoning
    - Full text chunk: complete raw text (truncated)
    This preserves semantic boundaries rather than splitting mid-sentence.
    """
    chunks = []
    base = f"{j.section_cited} {j.court} {j.state}"

    segments = [
        ("facts", f"{base} FACTS: {j.facts_summary}"),
        ("reasoning", f"{base} REASONING: {j.legal_reasoning}"),
        ("full", f"{base} {j.facts_summary} {j.legal_reasoning}"),
    ]

    for seg_type, text in segments:
        chunk_id = hashlib.md5(f"{j.case_id}_{seg_type}".encode()).hexdigest()[:12]
        chunks.append(Chunk(
            chunk_id=chunk_id,
            case_id=j.case_id,
            text=text,
        ))
    return chunks


def build_indexes() -> list[Judgment]:
    """Build all indexes. Returns list of Judgment objects."""
    print("Building indexes...")

    use_real = os.getenv("NYAY_USE_REAL_DATA", "auto").lower()
    real_judgments: list[Judgment] = []
    if use_real in {"1", "true", "yes", "auto"}:
        try:
            real_judgments = load_real_judgments()
        except Exception as exc:
            if use_real in {"1", "true", "yes"}:
                raise
            print(f"  Real data unavailable, using seed corpus: {exc}")

    if real_judgments:
        judgments = real_judgments
        citation_graph = {j.case_id: j.citations for j in judgments}
        print(f"  Loaded {len(judgments)} real Supreme Court judgments")
    else:
        judgments = [Judgment(**j) for j in RAW_JUDGMENTS]
        citation_graph = CITATION_GRAPH
        print(f"  Loaded {len(judgments)} synthetic seed judgments")

    # ── BM25 ────────────────────────────────────────────────────────────────
    print(f"  Indexing {len(judgments)} judgments in BM25...")
    get_bm25().index(judgments)

    # ── Embeddings + Vector Store ───────────────────────────────────────────
    store = get_store()
    all_chunks: list[Chunk] = []
    for j in judgments:
        all_chunks.extend(chunk_judgment(j))

    print(f"  Embedding {len(all_chunks)} chunks...")
    texts = [c.text for c in all_chunks]
    embeddings = embed(texts)
    for chunk, emb in zip(all_chunks, embeddings):
        chunk.embedding = emb
        store.add_chunk(chunk)

    # Force matrix rebuild
    store._rebuild_matrix()
    print(f"  Vector store ready: {len(store.chunks)} chunks")

    # ── Citation Graph ──────────────────────────────────────────────────────
    print("  Building precedent citation graph...")
    get_graph().build(judgments, citation_graph)
    graph = get_graph()
    n_nodes = graph.G.number_of_nodes()
    n_edges = graph.G.number_of_edges()
    print(f"  Graph: {n_nodes} nodes, {n_edges} edges")

    print("Indexes built successfully.")
    return judgments

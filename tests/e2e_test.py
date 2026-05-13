r"""
End-to-end smoke tests for the Nyay portfolio demo.

These tests exercise the API the same way a reviewer would:
- startup indexing
- health and analytics
- hybrid query pipeline
- structured filters
- graph metadata
- case detail lookup
- frontend/backend wiring contract

Run from the repository root:
    .\myenv\Scripts\python.exe tests\e2e_test.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend.html"
sys.path.insert(0, str(ROOT))

from backend.main import app


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def post_query(client: TestClient, payload: dict) -> dict:
    response = client.post("/query", json=payload)
    assert_true(response.status_code == 200, f"/query returned {response.status_code}: {response.text}")
    return response.json()


def test_health_and_analytics(client: TestClient) -> None:
    health = client.get("/health").json()
    assert_true(health["status"] == "ready", "API did not report ready status")
    assert_true(health["judgments"] >= 18, "Expected seeded judgment corpus")
    assert_true(health["graph_nodes"] == health["judgments"], "Graph node count should match corpus")
    assert_true(health["graph_edges"] >= 5, "Expected seeded citation edges")

    analytics = client.get("/analytics").json()
    assert_true(analytics["total_judgments"] == health["judgments"], "Analytics corpus mismatch")
    assert_true("Section 138 NI Act" in analytics["sections"], "Missing Section 138 analytics")
    assert_true("convicted" in analytics["outcomes"], "Missing outcome analytics")


def test_query_pipeline_with_real_filters(client: TestClient) -> None:
    data = post_query(
        client,
        {
            "query": "cheque bounce hand loan insufficient funds",
            "mode": "researcher",
            "top_k": 5,
            "use_llm": False,
            "section": "Section 138 NI Act",
            "state": "Maharashtra",
            "outcome": "all",
        },
    )

    assert_true(len(data["results"]) == 3, "Expected 3 Maharashtra Section 138 results")
    assert_true(data["metadata"]["filtered_count"] == 3, "Filtered pool count should be exact")
    assert_true(data["metadata"]["applied_filters"]["section"] == "Section 138 NI Act", "Section filter not applied")
    assert_true(data["metadata"]["applied_filters"]["state"] == "Maharashtra", "State filter not applied")

    for result in data["results"]:
        assert_true(result["section_cited"] == "Section 138 NI Act", "Returned result violates section filter")
        assert_true(result["state"] == "Maharashtra", "Returned result violates state filter")
        assert_true(result["fusion_score"] >= 0, "Fusion score missing")
        assert_true("facts_summary" in result and result["facts_summary"], "Result missing facts summary")

    quality = data["metadata"]["retrieval_quality"]
    assert_true("BM25" in quality["pipeline"], "Pipeline metadata missing BM25")
    assert_true("Graph RAG" in quality["pipeline"], "Pipeline metadata missing Graph RAG")
    assert_true(quality["top_rerank_score"] > 0, "Reranker did not score top result")


def test_consistency_and_graph_context(client: TestClient) -> None:
    data = post_query(
        client,
        {
            "query": "cheque bounce notice within 30 days hand loan dishonoured",
            "mode": "citizen",
            "top_k": 5,
            "use_llm": True,
            "section": "Section 138 NI Act",
            "state": "all",
            "outcome": "all",
        },
    )

    assert_true(len(data["results"]) >= 3, "Expected multiple Section 138 results")
    assert_true(data["graph_data"]["nodes"], "Query should return graph nodes")
    assert_true(data["debug_info"]["bm25_hits"], "Debug info missing BM25 hits")
    assert_true(data["debug_info"]["dense_hits"], "Debug info missing dense hits")
    assert_true(data["synthesis"], "Synthesis should be present")
    assert_true("LLM synthesis unavailable" not in data["synthesis"], "Raw LLM failure leaked into UX")


def test_outcome_filter_and_empty_filter(client: TestClient) -> None:
    convicted = post_query(
        client,
        {
            "query": "fraud investment dishonest intention",
            "mode": "researcher",
            "top_k": 5,
            "use_llm": False,
            "section": "Section 420 IPC",
            "state": "all",
            "outcome": "convicted",
        },
    )
    assert_true(convicted["results"], "Expected convicted Section 420 results")
    assert_true(all(r["outcome"] == "convicted" for r in convicted["results"]), "Outcome filter leaked")

    empty = post_query(
        client,
        {
            "query": "anything",
            "mode": "citizen",
            "top_k": 5,
            "use_llm": False,
            "section": "Section 304B IPC",
            "state": "Delhi",
            "outcome": "settled",
        },
    )
    assert_true(empty["results"] == [], "Impossible filter should return no results")
    assert_true(empty["metadata"]["filtered_count"] == 0, "Empty filter count should be 0")


def test_case_detail_and_full_graph(client: TestClient) -> None:
    case = client.get("/case/CC_138_2018_TN_003")
    assert_true(case.status_code == 200, "Case detail lookup failed")
    detail = case.json()
    assert_true(detail["case_id"] == "CC_138_2018_TN_003", "Wrong case detail returned")
    assert_true(detail["precedent_chain"], "Expected precedent chain for cited case")

    graph = client.get("/graph").json()
    assert_true(len(graph["nodes"]) >= 18, "Full graph missing nodes")
    assert_true(len(graph["edges"]) >= 5, "Full graph missing edges")


def test_frontend_contract() -> None:
    html = FRONTEND.read_text(encoding="utf-8")
    assert_true("const API = 'http://localhost:8765'" in html, "Frontend API base URL changed")
    assert_true("fetch(`${API}/health`)" in html, "Frontend should check backend health")
    assert_true("fetch(`${API}/query`" in html, "Frontend should call /query")
    assert_true("section:filters.section" in html, "Frontend should send section filter")
    assert_true("state:filters.state" in html, "Frontend should send state filter")
    assert_true("outcome:filters.outcome" in html, "Frontend should send outcome filter")
    assert_true("System signal" in html, "Frontend should render backend metadata")

    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    assert_true(scripts, "Expected inline frontend script")
    assert_true("function render(data)" in scripts[-1], "Frontend render function missing")


def main() -> None:
    tests = [
        ("health and analytics", test_health_and_analytics),
        ("query pipeline with real filters", test_query_pipeline_with_real_filters),
        ("consistency and graph context", test_consistency_and_graph_context),
        ("outcome and empty filters", test_outcome_filter_and_empty_filter),
        ("case detail and full graph", test_case_detail_and_full_graph),
    ]

    results: list[dict] = []
    with TestClient(app) as client:
        for name, test in tests:
            test(client)
            results.append({"test": name, "status": "passed"})
            print(f"PASS {name}")

    test_frontend_contract()
    results.append({"test": "frontend contract", "status": "passed"})
    print("PASS frontend contract")

    print("\nE2E summary")
    print(json.dumps({"passed": len(results), "failed": 0, "results": results}, indent=2))


if __name__ == "__main__":
    main()

"""
Evaluation script for Nyay system.
Generates metrics for:
- Consistency scorer validation
- Retrieval pipeline comparison (BM25 vs Dense vs Fusion vs Rerank)
- End-to-end latency
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.indexing import build_indexes
from backend.retrieval_pipeline import retrieve
from backend.consistency_scorer import score as consistency_score
from backend.seed_data import JUDGMENTS as SEED_JUDGMENTS
from backend.bm25_retriever import get_bm25
from backend.vector_store import get_store
from backend.embeddings import embed


def evaluate_consistency_scorer():
    """Test consistency scorer on seed data."""
    print("\n=== CONSISTENCY SCORER EVALUATION ===")
    
    judgments = build_indexes()
    
    # Test queries designed to retrieve similar cases with different outcomes
    test_queries = [
        "cheque dishonour hand loan Section 138",
        "assault conviction justified",
        "theft conviction evidence",
    ]
    
    all_flags = []
    for query in test_queries:
        results, _ = retrieve(query, judgments, top_k=10, debug=False)
        flags = consistency_score(results)
        all_flags.extend(flags)
    
    total_flags = len(all_flags)
    high_confidence = len([f for f in all_flags if f.divergence_score > 0.8])
    
    print(f"Total inconsistencies flagged: {total_flags}")
    print(f"High confidence (>0.80): {high_confidence}")
    print(f"Coverage: {total_flags}/{len(SEED_JUDGMENTS)} cases checked")
    
    if all_flags:
        print(f"\nTop 3 divergences:")
        for i, flag in enumerate(all_flags[:3], 1):
            print(f"  {i}. {flag.case_id_a} vs {flag.case_id_b}")
            print(f"     Similarity: {flag.similarity_score:.0%}, Divergence: {flag.divergence_score:.2f}")
    
    return {
        "total_flags": total_flags,
        "high_confidence": high_confidence,
        "seed_data_size": len(SEED_JUDGMENTS)
    }


def evaluate_retrieval_pipeline():
    """Compare BM25 vs Dense vs Fusion vs Rerank."""
    print("\n=== RETRIEVAL PIPELINE COMPARISON ===")
    
    judgments = build_indexes()
    
    test_queries = [
        "cheque bounce dishonour Maharashtra",
        "criminal conviction appeal",
        "theft stolen property",
        "section 138 negotiable instruments",
    ]
    
    results_by_method = {
        "bm25": [],
        "dense": [],
        "fusion": [],
        "rerank": []
    }
    
    timings_by_method = {
        "bm25": [],
        "dense": [],
        "fusion": [],
        "rerank": []
    }
    
    for query in test_queries:
        t0 = time.time()
        results, debug_info = retrieve(query, judgments, top_k=5, debug=True)
        total_time = (time.time() - t0) * 1000
        
        # Extract scores from debug_info
        if debug_info.get("bm25_hits"):
            bm25_score = max([r["bm25_score"] for r in debug_info["bm25_hits"]], default=0)
            results_by_method["bm25"].append(bm25_score)
            timings_by_method["bm25"].append(debug_info.get("bm25_latency_ms", 0))
        
        if debug_info.get("dense_hits"):
            dense_score = max([r["dense_score"] for r in debug_info["dense_hits"]], default=0)
            results_by_method["dense"].append(dense_score)
            timings_by_method["dense"].append(debug_info.get("dense_latency_ms", 0))
        
        if debug_info.get("rrf_scores"):
            rrf_score = max(debug_info["rrf_scores"].values(), default=0)
            results_by_method["fusion"].append(rrf_score)
            timings_by_method["fusion"].append(debug_info.get("fusion_latency_ms", 0))
        
        if results:
            rerank_score = max([r.rerank_score for r in results], default=0)
            results_by_method["rerank"].append(rerank_score)
            timings_by_method["rerank"].append(debug_info.get("rerank_latency_ms", 0))
    
    # Print summary
    print(f"\nAverage top-1 scores across {len(test_queries)} queries:")
    for method, scores in results_by_method.items():
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  {method.upper()}: {avg:.3f}")
    
    print(f"\nLatency (ms):")
    for method, times in timings_by_method.items():
        if times:
            avg = sum(times) / len(times)
            print(f"  {method.upper()}: {avg:.1f}ms")
    
    return {
        "top1_scores": results_by_method,
        "latencies_ms": timings_by_method
    }


def evaluate_end_to_end():
    """Full end-to-end latency."""
    print("\n=== END-TO-END LATENCY ===")
    
    t0 = time.time()
    judgments = build_indexes()
    build_time = (time.time() - t0) * 1000
    
    test_queries = [
        "cheque dishonour",
        "criminal conviction",
        "theft evidence",
    ]
    
    query_times = []
    for query in test_queries:
        t0 = time.time()
        results, _ = retrieve(query, judgments, top_k=5, debug=True)
        flags = consistency_score(results)
        query_time = (time.time() - t0) * 1000
        query_times.append(query_time)
    
    avg_query_time = sum(query_times) / len(query_times)
    
    print(f"Startup (build indexes): {build_time:.0f}ms")
    print(f"Average query latency: {avg_query_time:.0f}ms (retrieval + rerank + consistency)")
    print(f"P99 query latency: {max(query_times):.0f}ms")
    print(f"P50 query latency: {sorted(query_times)[len(query_times)//2]:.0f}ms")
    
    return {
        "startup_ms": round(build_time, 1),
        "avg_query_ms": round(avg_query_time, 1),
        "p99_query_ms": round(max(query_times), 1),
        "p50_query_ms": round(sorted(query_times)[len(query_times)//2], 1)
    }


if __name__ == "__main__":
    print("Starting Nyay evaluation...")
    
    consistency = evaluate_consistency_scorer()
    retrieval = evaluate_retrieval_pipeline()
    latency = evaluate_end_to_end()
    
    # Summary
    print("\n=== EVALUATION SUMMARY ===")
    print(json.dumps({
        "consistency_scorer": consistency,
        "retrieval_pipeline": retrieval,
        "latency": latency
    }, indent=2))

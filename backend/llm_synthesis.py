"""
LLM synthesis layer.
Takes retrieved judgment chunks + precedent chain context
and synthesises a plain-language answer for the citizen view,
and a structured legal analysis for the researcher view.
"""

from functools import lru_cache
import os
from pathlib import Path

import anthropic
import httpx
from dotenv import load_dotenv

from backend.models import RetrievalResult, Judgment, ConsistencyFlag

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent

# Support both common launch styles:
#   uvicorn backend.main:app  -> project root is cwd
#   cd backend && uvicorn main:app -> backend is cwd
load_dotenv(ROOT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env", override=True)


@lru_cache(maxsize=1)
def _get_client() -> anthropic.Anthropic:
    try:
        return anthropic.Anthropic()
    except TypeError as exc:
        if "proxies" not in str(exc):
            raise

        # anthropic==0.28.0 passes a removed "proxies" kwarg to httpx>=0.28.
        # Providing the httpx client ourselves avoids that incompatible path.
        return anthropic.Anthropic(http_client=httpx.Client())

def _build_context(
    results: list[RetrievalResult],
    precedent_judgments: list[Judgment],
    consistency_flags: list[ConsistencyFlag],
) -> str:
    ctx_parts = []

    ctx_parts.append("=== RETRIEVED JUDGMENTS ===")
    for i, r in enumerate(results, 1):
        ctx_parts.append(
            f"\n[{i}] {r.case_id}\n"
            f"Court: {r.court} | State: {r.state} | Date: {r.date}\n"
            f"Section: {r.section_cited} | Outcome: {r.outcome.upper()}\n"
            f"Facts: {r.facts_summary}\n"
            f"Reasoning: {r.legal_reasoning}\n"
        )

    if precedent_judgments:
        ctx_parts.append("\n=== PRECEDENT CHAIN (via citation graph) ===")
        for j in precedent_judgments:
            ctx_parts.append(
                f"\n[PRECEDENT] {j.case_id}\n"
                f"Court: {j.court} | Date: {j.date} | Outcome: {j.outcome.upper()}\n"
                f"Reasoning: {j.legal_reasoning}\n"
            )

    if consistency_flags:
        ctx_parts.append("\n=== CONSISTENCY FLAGS ===")
        for f in consistency_flags[:3]:
            ctx_parts.append(
                f"\nFLAG: {f.explanation} (similarity: {f.similarity_score:.0%}, divergence score: {f.divergence_score:.2f})"
            )

    return "\n".join(ctx_parts)


def has_llm_config() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN"))


def _local_citizen_summary(
    results: list[RetrievalResult],
    precedent_judgments: list[Judgment],
    consistency_flags: list[ConsistencyFlag],
) -> str:
    if not results:
        return "No matching judgments were retrieved for this query."

    outcomes: dict[str, int] = {}
    sections = sorted({r.section_cited for r in results})
    for r in results:
        outcomes[r.outcome] = outcomes.get(r.outcome, 0) + 1

    top = results[0]
    lines = [
        f"From the retrieved judgments, courts most often turn on evidence quality and procedural compliance. The closest match is {top.case_id} from {top.court}, where the outcome was {top.outcome}.",
        "",
        "What mattered in these cases:",
    ]
    for outcome, count in sorted(outcomes.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"- {count} retrieved case(s) ended as {outcome}.")
    lines.extend([
        f"- Covered section(s): {', '.join(sections)}.",
        f"- Precedent context added: {len(precedent_judgments)} related cited judgment(s).",
    ])
    if consistency_flags:
        lines.append(
            f"- {len(consistency_flags)} potential inconsistency flag(s) were found where similar facts led to different outcomes."
        )
    lines.append("")
    lines.append("This is legal information based only on the indexed judgments, not personal legal advice.")
    return "\n".join(lines)


def _local_researcher_summary(
    results: list[RetrievalResult],
    precedent_judgments: list[Judgment],
    consistency_flags: list[ConsistencyFlag],
) -> str:
    if not results:
        return "No matching judgments were retrieved for this query."

    ranked = ", ".join(r.case_id for r in results[:5])
    top = results[0]
    lines = [
        "Local legal research synthesis:",
        f"1. Retrieval set: {ranked}. Top-ranked judgment is {top.case_id} with rerank score {top.rerank_score:.4f}.",
        f"2. Outcome pattern: {', '.join(f'{r.case_id}={r.outcome}' for r in results[:5])}.",
        f"3. Precedent chain: {len(precedent_judgments)} cited ancestor judgment(s) were added through graph traversal.",
    ]
    if consistency_flags:
        lines.append(
            f"4. Consistency analysis: {len(consistency_flags)} divergent similar-fact pair(s) flagged; highest divergence is {consistency_flags[0].divergence_score:.4f}."
        )
    else:
        lines.append("4. Consistency analysis: no divergent similar-fact pairs crossed the configured threshold.")
    lines.append("5. Evidence caveat: analysis is bounded to the indexed corpus and returned metadata.")
    return "\n".join(lines)


def synthesise_citizen(
    query: str,
    results: list[RetrievalResult],
    precedent_judgments: list[Judgment],
    consistency_flags: list[ConsistencyFlag],
) -> str:
    if not has_llm_config():
        return _local_citizen_summary(results, precedent_judgments, consistency_flags)

    context = _build_context(results, precedent_judgments, consistency_flags)

    prompt = f"""You are a plain-language legal information assistant for Indian citizens.
A citizen has asked: "{query}"

Based on the following Indian court judgments, provide:
1. A clear, simple summary of how courts have typically decided cases like this (2-3 sentences)
2. Key factors that led to conviction vs acquittal in similar cases (bullet points)
3. What the citizen should be aware of (practical takeaways)
4. If there are consistency flags, mention that similar cases have had different outcomes

Use simple English. No legal jargon without explanation. Be honest about uncertainty.
Do not give specific legal advice — recommend consulting a lawyer for personal situations.

{context}

IMPORTANT: Base your answer strictly on the provided judgments. Do not invent cases."""

    try:
        message = _get_client().messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception:
        return _local_citizen_summary(results, precedent_judgments, consistency_flags)


def synthesise_researcher(
    query: str,
    results: list[RetrievalResult],
    precedent_judgments: list[Judgment],
    consistency_flags: list[ConsistencyFlag],
) -> str:
    if not has_llm_config():
        return _local_researcher_summary(results, precedent_judgments, consistency_flags)

    context = _build_context(results, precedent_judgments, consistency_flags)

    prompt = f"""You are a legal research assistant for lawyers, researchers, and journalists.
Query: "{query}"

Provide a structured legal analysis including:
1. Pattern of outcomes across retrieved cases
2. Key legal principles established by these cases
3. Precedent chain analysis — how earlier cases influenced later ones
4. Consistency analysis — are there unexplained outcome divergences?
5. Potential research angles or areas of legal uncertainty

Use precise legal language. Cite case IDs when referencing specific judgments.

{context}"""

    try:
        message = _get_client().messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception:
        return _local_researcher_summary(results, precedent_judgments, consistency_flags)

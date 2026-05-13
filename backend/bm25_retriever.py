"""
BM25 retrieval over judgment texts.
Catches exact legal references: section numbers, case names, terms like
'mens rea', 'locus standi', 'Section 139 NI Act' that dense retrieval misses.
"""

from rank_bm25 import BM25Okapi
import re
from models import Judgment

class BM25Retriever:
    def __init__(self):
        self.judgments: list[Judgment] = []
        self._bm25: BM25Okapi | None = None

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        # Keep legal terms intact: "section_138", "ni_act" etc
        text = re.sub(r'section\s+(\d+)', r'section_\1', text)
        text = re.sub(r'\bni\s+act\b', 'ni_act', text)
        text = re.sub(r'\bipc\b', 'ipc', text)
        tokens = re.findall(r'[a-z0-9_]+', text)
        return tokens

    def index(self, judgments: list[Judgment]):
        self.judgments = judgments
        corpus = [
            self._tokenize(
                f"{j.section_cited} {j.facts_summary} {j.legal_reasoning} {j.raw_text} {j.court} {j.state}"
            )
            for j in judgments
        ]
        self._bm25 = BM25Okapi(corpus)

    def query(self, query_text: str, top_k: int = 20) -> list[tuple[Judgment, float]]:
        if not self._bm25:
            return []
        tokens = self._tokenize(query_text)
        scores = self._bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = [(self.judgments[i], float(scores[i])) for i in top_indices if scores[i] > 0]
        return results


_retriever = BM25Retriever()

def get_bm25() -> BM25Retriever:
    return _retriever

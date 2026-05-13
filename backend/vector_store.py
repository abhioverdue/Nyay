"""
In-memory vector store using numpy cosine similarity.
Architecture is identical to pgvector — swap the query method
for a pg_vector ANN query and everything else stays the same.
"""

import numpy as np
from typing import Optional
from backend.models import Judgment, Chunk
import json, hashlib

class VectorStore:
    def __init__(self):
        self.chunks: list[Chunk] = []
        self.embeddings: Optional[np.ndarray] = None  # shape (N, D)
        self._dirty = True

    def add_chunk(self, chunk: Chunk):
        self.chunks.append(chunk)
        self._dirty = True

    def _rebuild_matrix(self):
        if not self.chunks:
            return
        vecs = [c.embedding for c in self.chunks if c.embedding]
        if vecs:
            self.embeddings = np.array(vecs, dtype=np.float32)
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1e-9, norms)
            self.embeddings = self.embeddings / norms  # L2 normalise
        self._dirty = False

    def query(self, query_embedding: list[float], top_k: int = 20) -> list[tuple[Chunk, float]]:
        if self._dirty:
            self._rebuild_matrix()
        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        q = np.array(query_embedding, dtype=np.float32)
        q = q / (np.linalg.norm(q) + 1e-9)
        scores = self.embeddings @ q          # cosine similarity (already normalised)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in top_indices]

    def get_all_case_ids(self) -> list[str]:
        return list({c.case_id for c in self.chunks})


# Global singleton
_store = VectorStore()

def get_store() -> VectorStore:
    return _store

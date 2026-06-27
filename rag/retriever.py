"""
Hybrid retriever — dense (FAISS) + sparse (BM25) candidates fused via
Reciprocal Rank Fusion.

Loads the index, BM25, metadata, and the e5 embedder once at construction so a
single instance can serve many queries (CLI run or long-lived API process).
Logic is lifted from scripts/search_test.py and made reusable; that script
stays as the retrieval-only debug tool.
"""

import pickle

import numpy as np
from loguru import logger

from ingestion.embedders import E5Embedder
from ingestion.indexers import BM25Builder, FaissBuilder
from rag.config import METADATA_FILE, RETRIEVE_K, RRF_K
from rag.models import RetrievedChunk


class HybridRetriever:
    """FAISS + BM25 retrieval fused with RRF. Domain metadata is NOT used to
    filter (the keyword enricher is unreliable) — only for display/citation."""

    def __init__(self):
        logger.info("Loading FAISS index...")
        self._faiss = FaissBuilder.load()

        logger.info("Loading BM25 index...")
        self._bm25 = BM25Builder.load()

        logger.info("Loading chunk metadata...")
        with open(METADATA_FILE, "rb") as f:
            self._metadata: list[dict] = pickle.load(f)

        # E5Embedder loads the sentence-transformers model (handles "query: " prefix)
        self._embedder = E5Embedder()

        logger.info(f"HybridRetriever ready: {len(self._metadata)} chunks.")

    def _faiss_search(self, query: str, k: int) -> list[int]:
        """Dense semantic search → ranked chunk indices."""
        vec = self._embedder.embed_query(query)  # (1, dim), normalized
        _, indices = self._faiss.search(vec, k)
        return [int(i) for i in indices[0] if 0 <= i < len(self._metadata)]

    def _bm25_search(self, query: str, k: int) -> list[int]:
        """Sparse keyword search → ranked chunk indices (positive scores only)."""
        tokens = query.lower().split()
        scores = self._bm25.get_scores(tokens)
        top = np.argsort(scores)[::-1][:k]
        return [int(i) for i in top if scores[i] > 0]

    def retrieve(self, query: str, k: int = RETRIEVE_K) -> list[RetrievedChunk]:
        """
        Return up to ~k fused candidates, highest RRF score first.

        RRF score = sum over systems of 1 / (RRF_K + rank). A chunk appearing in
        both lists accumulates from both, so consensus rises to the top.
        """
        faiss_ids = self._faiss_search(query, k)
        bm25_ids = self._bm25_search(query, k)

        rrf: dict[int, float] = {}
        for rank, idx in enumerate(faiss_ids):
            rrf[idx] = rrf.get(idx, 0.0) + 1.0 / (RRF_K + rank + 1)
        for rank, idx in enumerate(bm25_ids):
            rrf[idx] = rrf.get(idx, 0.0) + 1.0 / (RRF_K + rank + 1)

        ranked = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)

        results = []
        for idx, score in ranked:
            meta = self._metadata[idx]
            results.append(
                RetrievedChunk(
                    chunk_id=meta.get("chunk_id", str(idx)),
                    text=meta["text"],
                    metadata=meta,
                    retrieval_score=score,
                )
            )
        logger.debug(f"Retrieved {len(results)} fused candidates for: {query!r}")
        return results

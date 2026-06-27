"""
Cross-encoder reranker — re-scores (query, chunk) pairs jointly and keeps the
top-N. This is the precision fix for hybrid-RRF noise: in testing, raw RRF leaked
off-topic Supreme Court judgments into the top results; a cross-encoder pushes
genuinely relevant chunks back to the top.
"""

from loguru import logger
from sentence_transformers import CrossEncoder

from rag.config import RERANK_TOP_N, RERANKER_MODEL
from rag.models import RetrievedChunk


class CrossEncoderReranker:
    """Wraps a sentence-transformers CrossEncoder (ms-marco-MiniLM)."""

    def __init__(self):
        logger.info(f"Loading reranker: {RERANKER_MODEL}")
        self._model = CrossEncoder(RERANKER_MODEL)
        logger.info("Reranker ready.")

    def rerank(
        self, query: str, candidates: list[RetrievedChunk], top_n: int = RERANK_TOP_N
    ) -> list[RetrievedChunk]:
        """Score each candidate against the query, sort desc, return top_n.

        Sets `rerank_score` on each returned chunk (used for confidence scoring).
        """
        if not candidates:
            return []

        pairs = [(query, c.text) for c in candidates]
        scores = self._model.predict(pairs)

        for chunk, score in zip(candidates, scores):
            chunk.rerank_score = float(score)

        ranked = sorted(candidates, key=lambda c: c.rerank_score, reverse=True)
        top = ranked[:top_n]
        logger.debug(
            f"Reranked {len(candidates)} → top {len(top)} "
            f"(best score {top[0].rerank_score:.3f})" if top else "Reranked 0"
        )
        return top

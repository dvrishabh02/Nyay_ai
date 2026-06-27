"""
RAG pipeline — orchestrates retrieve → rerank → generate → post-process.

Construct ONCE (loads e5, cross-encoder, FAISS/BM25, Groq client) and reuse for
every query. `ask()` returns a structured RAGResponse.
"""

import re
import time

from loguru import logger

from rag.config import (
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    NO_CONTEXT_FALLBACK,
    RERANK_TOP_N,
)
from rag.generator import GroqGenerator
from rag.models import Citation, RAGResponse, RetrievedChunk
from rag.prompt import build_messages
from rag.reranker import CrossEncoderReranker
from rag.retriever import HybridRetriever

_CITATION_RE = re.compile(r"\[(\d+)\]")


class RAGPipeline:
    """End-to-end question → grounded, cited answer."""

    def __init__(self):
        logger.info("Initializing RAG pipeline (this loads several models)...")
        self.retriever = HybridRetriever()
        self.reranker = CrossEncoderReranker()
        self.generator = GroqGenerator()
        logger.info("RAG pipeline ready.")

    def ask(self, question: str, top_n: int = RERANK_TOP_N) -> RAGResponse:
        start = time.time()

        # 1. Retrieve + 2. Rerank
        candidates = self.retriever.retrieve(question)
        reranked = self.reranker.rerank(question, candidates, top_n=top_n)

        if not reranked:
            return RAGResponse(
                question=question,
                answer=f"{NO_CONTEXT_FALLBACK} in my sources to answer this reliably.",
                confidence="LOW",
                latency_ms=int((time.time() - start) * 1000),
            )

        # 3. Generate
        messages = build_messages(question, reranked)
        answer = self.generator.generate(messages)

        # 4. Post-process
        citations = self._extract_citations(answer, reranked)
        confidence = self._score_confidence(answer, reranked)

        return RAGResponse(
            question=question,
            answer=answer,
            confidence=confidence,
            citations=citations,
            sources=reranked,
            latency_ms=int((time.time() - start) * 1000),
        )

    @staticmethod
    def _extract_citations(answer: str, chunks: list[RetrievedChunk]) -> list[Citation]:
        """Map each distinct [n] marker in the answer back to its source chunk."""
        seen: dict[int, Citation] = {}
        for match in _CITATION_RE.findall(answer):
            n = int(match)
            if n in seen or not (1 <= n <= len(chunks)):
                continue
            c = chunks[n - 1]
            seen[n] = Citation(n=n, title=c.title, source=c.source, doc_type=c.doc_type)
        return [seen[n] for n in sorted(seen)]

    @staticmethod
    def _score_confidence(answer: str, chunks: list[RetrievedChunk]) -> str:
        """Heuristic from the top reranker score; forced LOW on the grounding fallback."""
        if NO_CONTEXT_FALLBACK.lower() in answer.lower():
            return "LOW"
        top = chunks[0].rerank_score if chunks and chunks[0].rerank_score is not None else 0.0
        if top >= CONFIDENCE_HIGH:
            return "HIGH"
        if top >= CONFIDENCE_MEDIUM:
            return "MEDIUM"
        return "LOW"

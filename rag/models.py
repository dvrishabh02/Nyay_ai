"""
Data models for the RAG chain — what flows between retriever, reranker,
generator, and the API/CLI surface.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RetrievedChunk:
    """A candidate chunk plus its scores at each retrieval stage."""

    chunk_id: str
    text: str
    metadata: dict                         # flat dict from Chunk.to_dict() (title, source, ...)
    retrieval_score: float = 0.0           # RRF fusion score
    rerank_score: Optional[float] = None   # cross-encoder score (set after rerank)

    @property
    def title(self) -> str:
        return self.metadata.get("title") or self.metadata.get("source", "Unknown source")

    @property
    def source(self) -> str:
        return self.metadata.get("source", "unknown")

    @property
    def doc_type(self) -> str:
        return self.metadata.get("doc_type", "unknown")


@dataclass
class Citation:
    """A source the answer referenced, by its [n] marker."""

    n: int
    title: str
    source: str
    doc_type: str

    def to_dict(self) -> dict:
        return {"n": self.n, "title": self.title, "source": self.source, "doc_type": self.doc_type}


@dataclass
class RAGResponse:
    """Final result of the chain."""

    question: str
    answer: str
    confidence: str                                # "HIGH" | "MEDIUM" | "LOW"
    citations: list[Citation] = field(default_factory=list)
    sources: list[RetrievedChunk] = field(default_factory=list)  # reranked chunks used
    latency_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "answer": self.answer,
            "confidence": self.confidence,
            "citations": [c.to_dict() for c in self.citations],
            "latency_ms": self.latency_ms,
        }

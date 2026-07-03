"""Request/response models for the API."""

from typing import Optional

from pydantic import BaseModel, Field

from rag.config import RERANK_TOP_N


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The legal question to answer")
    top_k: Optional[int] = Field(
        default=RERANK_TOP_N, ge=1, le=20, description="Chunks fed to the LLM after rerank"
    )


class SourceModel(BaseModel):
    title: str
    source: str
    doc_type: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    confidence: str
    sources: list[SourceModel]
    latency_ms: int

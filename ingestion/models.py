"""
Shared data models for the ingestion pipeline.
Every module passes Chunk objects — single data structure, no duplication.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChunkMetadata:
    """Metadata attached to every chunk for filtering and citation."""
    doc_type: str                          # "act" | "judgment"
    court: Optional[str] = None            # "supreme_court" | None
    jurisdiction: str = "central"          # "central" | state name
    domain: str = "general"               # "property" | "consumer" | "criminal" | etc.
    year: Optional[int] = None
    title: Optional[str] = None            # Act name or case title
    source: str = ""                       # Dataset key from config
    source_file: str = ""                  # Original file path
    chunk_index: int = 0                   # Position within parent document
    total_chunks: int = 1                  # Total chunks from parent document


@dataclass
class Chunk:
    """
    Single unit of text ready for embedding.
    This is the universal data structure passed between all pipeline stages.
    """
    chunk_id: str                          # Unique ID: "{source}_{doc_idx}_{chunk_idx}"
    text: str                              # The actual text content
    metadata: ChunkMetadata = field(default_factory=ChunkMetadata)
    token_count: int = 0                   # Set during quality check

    def to_dict(self) -> dict:
        """Serialize for storage in metadata.pkl."""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "token_count": self.token_count,
            **vars(self.metadata),
        }

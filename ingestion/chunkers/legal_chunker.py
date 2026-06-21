"""
Legal Chunker — splits legal documents respecting section boundaries.

Uses a recursive splitting strategy: tries the most meaningful separator
first (headings, sections), then falls back to paragraphs and sentences.
Converts token limits to character estimates for splitting.
"""

import tiktoken
from loguru import logger

from ingestion.config import (
    CHUNK_OVERLAP_TOKENS,
    CHUNK_SEPARATORS,
    CHUNK_SIZE_TOKENS,
    MIN_CHUNK_TOKENS,
)
from ingestion.models import Chunk, ChunkMetadata


class LegalChunker:
    """Splits long legal text into overlapping, section-aware chunks."""

    # Approx chars per token for English legal text
    CHARS_PER_TOKEN = 4

    def __init__(self):
        self._tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_document(
        self,
        text: str,
        source: str,
        doc_idx: int,
        metadata: ChunkMetadata,
    ) -> list[Chunk]:
        """
        Split a single document into chunks.

        Args:
            text: Full document text.
            source: Dataset key (e.g., "central_acts").
            doc_idx: Document index within the dataset.
            metadata: Base metadata to copy into each chunk.

        Returns:
            List of Chunk objects with chunk_index set.
        """
        if not text or not text.strip():
            return []

        raw_chunks = self._recursive_split(
            text,
            chunk_size=CHUNK_SIZE_TOKENS * self.CHARS_PER_TOKEN,
            overlap=CHUNK_OVERLAP_TOKENS * self.CHARS_PER_TOKEN,
            separators=list(CHUNK_SEPARATORS),
        )

        # Filter by minimum token count
        chunks = []
        for i, chunk_text in enumerate(raw_chunks):
            token_count = len(self._tokenizer.encode(chunk_text))
            if token_count < MIN_CHUNK_TOKENS:
                continue

            chunk_meta = ChunkMetadata(
                doc_type=metadata.doc_type,
                court=metadata.court,
                jurisdiction=metadata.jurisdiction,
                domain=metadata.domain,
                year=metadata.year,
                title=metadata.title,
                source=source,
                source_file=metadata.source_file,
                chunk_index=i,
                total_chunks=len(raw_chunks),  # Updated below
            )

            chunks.append(Chunk(
                chunk_id=f"{source}_{doc_idx:05d}_chunk_{i:03d}",
                text=chunk_text.strip(),
                metadata=chunk_meta,
                token_count=token_count,
            ))

        # Update total_chunks to reflect filtered count
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)

        return chunks

    def wrap_pre_chunked(
        self,
        text: str,
        source: str,
        doc_idx: int,
        metadata: ChunkMetadata,
    ) -> Chunk:
        """Wrap an already-chunked passage as a Chunk (no splitting)."""
        return Chunk(
            chunk_id=f"{source}_{doc_idx:05d}",
            text=text.strip(),
            metadata=metadata,
            token_count=len(self._tokenizer.encode(text)),
        )

    def _recursive_split(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
        separators: list[str],
    ) -> list[str]:
        """
        Recursively split text using a priority list of separators.
        Tries the first separator; if a segment is still too long,
        falls back to the next separator.
        """
        if len(text) <= chunk_size:
            return [text]

        # Pick the best separator that exists in the text
        separator = ""
        for sep in separators:
            if sep in text:
                separator = sep
                break

        # Split on the chosen separator
        if separator:
            parts = text.split(separator)
        else:
            # Last resort: hard split by character
            return self._hard_split(text, chunk_size, overlap)

        # Merge small parts into chunks respecting size limit
        chunks = []
        current = ""

        for part in parts:
            candidate = current + separator + part if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # If single part exceeds limit, recurse with next separator
                if len(part) > chunk_size:
                    remaining_seps = separators[separators.index(separator) + 1:]
                    sub_chunks = self._recursive_split(part, chunk_size, overlap, remaining_seps)
                    chunks.extend(sub_chunks)
                    current = ""
                else:
                    current = part

        if current:
            chunks.append(current)

        # Add overlap between consecutive chunks
        return self._add_overlap(chunks, overlap)

    def _hard_split(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Character-level split as last resort."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    def _add_overlap(self, chunks: list[str], overlap: int) -> list[str]:
        """Add trailing overlap from previous chunk to each chunk."""
        if len(chunks) <= 1 or overlap <= 0:
            return chunks

        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(prev_tail + chunks[i])
        return overlapped

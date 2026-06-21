"""
E5 Embedder — generates dense vectors using e5-base-v2.

The e5 model family requires a prefix on all inputs:
  - "passage: " for documents being indexed
  - "query: " for search queries at runtime

This wrapper handles prefixing, batching, and normalization.
"""

import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer

from ingestion.config import (
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    EMBEDDING_PREFIX,
    QUERY_PREFIX,
)
from ingestion.models import Chunk


class E5Embedder:
    """Wraps sentence-transformers for e5-base-v2 embedding."""

    def __init__(self):
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        self._model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"Model loaded. Dimension: {EMBEDDING_DIM}")

    def embed_chunks(self, chunks: list[Chunk]) -> np.ndarray:
        """
        Embed a list of chunks for indexing.

        Args:
            chunks: List of Chunk objects to embed.

        Returns:
            numpy array of shape (len(chunks), EMBEDDING_DIM), float32, L2-normalized.
        """
        texts = [EMBEDDING_PREFIX + chunk.text for chunk in chunks]
        logger.info(f"Embedding {len(texts)} chunks (batch_size={EMBEDDING_BATCH_SIZE})...")

        embeddings = self._model.encode(
            texts,
            batch_size=EMBEDDING_BATCH_SIZE,
            show_progress_bar=True,
            normalize_embeddings=True,  # Unit vectors for cosine sim via dot product
        )

        result = np.array(embeddings, dtype=np.float32)
        logger.info(f"Embeddings shape: {result.shape}")
        return result

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query for search (uses "query: " prefix).

        Args:
            query: User's search query string.

        Returns:
            numpy array of shape (1, EMBEDDING_DIM), float32, L2-normalized.
        """
        embedding = self._model.encode(
            [QUERY_PREFIX + query],
            normalize_embeddings=True,
        )
        return np.array(embedding, dtype=np.float32)

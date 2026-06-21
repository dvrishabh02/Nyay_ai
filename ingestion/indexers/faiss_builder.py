"""
FAISS Builder — creates and persists a dense vector index.

Uses IndexFlatIP (inner product) since embeddings are L2-normalized,
making dot product equivalent to cosine similarity.
"""

from pathlib import Path

import faiss
import numpy as np
from loguru import logger

from ingestion.config import EMBEDDING_DIM, FAISS_INDEX_FILE


class FaissBuilder:
    """Builds, saves, and loads a FAISS flat index."""

    def __init__(self, dim: int = EMBEDDING_DIM):
        self._dim = dim

    def build(self, embeddings: np.ndarray) -> faiss.IndexFlatIP:
        """
        Build a FAISS index from embeddings.

        Args:
            embeddings: numpy array of shape (n, dim), float32.

        Returns:
            FAISS IndexFlatIP with all vectors added.
        """
        if embeddings.shape[1] != self._dim:
            raise ValueError(f"Expected dim={self._dim}, got {embeddings.shape[1]}")

        index = faiss.IndexFlatIP(self._dim)
        index.add(embeddings)
        logger.info(f"FAISS index built: {index.ntotal} vectors, dim={self._dim}")
        return index

    def save(self, index: faiss.IndexFlatIP, path: Path = FAISS_INDEX_FILE):
        """Save FAISS index to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(path))
        size_mb = path.stat().st_size / (1024 * 1024)
        logger.info(f"FAISS index saved: {path} ({size_mb:.1f} MB)")

    @staticmethod
    def load(path: Path = FAISS_INDEX_FILE) -> faiss.IndexFlatIP:
        """Load a FAISS index from disk."""
        if not path.exists():
            raise FileNotFoundError(f"FAISS index not found: {path}")
        index = faiss.read_index(str(path))
        logger.info(f"FAISS index loaded: {index.ntotal} vectors")
        return index

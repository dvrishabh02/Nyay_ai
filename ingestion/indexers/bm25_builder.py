"""
BM25 Builder — creates and persists a sparse keyword index.

BM25 complements FAISS by catching keyword matches that dense
vectors might miss (e.g., exact section numbers, case names).
Combined with FAISS via Reciprocal Rank Fusion at query time.
"""

import pickle
from pathlib import Path

from loguru import logger
from rank_bm25 import BM25Okapi

from ingestion.config import BM25_INDEX_FILE
from ingestion.models import Chunk


class BM25Builder:
    """Builds, saves, and loads a BM25 keyword index."""

    def build(self, chunks: list[Chunk]) -> BM25Okapi:
        """
        Build a BM25 index from chunk text.

        Args:
            chunks: List of Chunk objects to index.

        Returns:
            BM25Okapi instance ready for queries.
        """
        tokenized = [self._tokenize(chunk.text) for chunk in chunks]
        bm25 = BM25Okapi(tokenized)
        logger.info(f"BM25 index built: {len(tokenized)} documents")
        return bm25

    def save(self, bm25: BM25Okapi, path: Path = BM25_INDEX_FILE):
        """Save BM25 index to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(bm25, f)
        size_mb = path.stat().st_size / (1024 * 1024)
        logger.info(f"BM25 index saved: {path} ({size_mb:.1f} MB)")

    @staticmethod
    def load(path: Path = BM25_INDEX_FILE) -> BM25Okapi:
        """Load a BM25 index from disk."""
        if not path.exists():
            raise FileNotFoundError(f"BM25 index not found: {path}")
        with open(path, "rb") as f:
            bm25 = pickle.load(f)
        logger.info(f"BM25 index loaded: {bm25.corpus_size} documents")
        return bm25

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Simple whitespace + lowercase tokenization for BM25."""
        return text.lower().split()

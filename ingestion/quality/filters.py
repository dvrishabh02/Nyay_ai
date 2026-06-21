"""
Quality Filters — removes junk, duplicates, and non-legal content.

Each filter is a separate method returning (passed: bool, reason: str).
Filters are applied in sequence; first failure skips the chunk.
"""

import hashlib
from loguru import logger

from ingestion.config import MIN_CHUNK_TOKENS
from ingestion.models import Chunk


class QualityFilter:
    """Applies quality checks to chunks. Tracks stats and seen hashes."""

    # Keywords that indicate legal content
    LEGAL_KEYWORDS = {
        "section", "act", "court", "judgment", "article", "order",
        "petition", "plaintiff", "defendant", "hereby", "whereas",
        "tribunal", "appeal", "bail", "constitution", "provision",
        "statute", "accused", "prosecution", "advocate", "bench",
        "writ", "decree", "arbitration", "complainant", "respondent",
    }

    def __init__(self):
        self._seen_hashes: set[str] = set()
        self.stats = {"total": 0, "passed": 0, "dropped": {}}

    def filter_chunks(self, chunks: list[Chunk]) -> list[Chunk]:
        """Apply all filters to a list of chunks. Returns passing chunks."""
        passed = []
        for chunk in chunks:
            self.stats["total"] += 1
            is_valid, reason = self._check(chunk)
            if is_valid:
                self.stats["passed"] += 1
                passed.append(chunk)
            else:
                self.stats["dropped"][reason] = self.stats["dropped"].get(reason, 0) + 1
        return passed

    def log_stats(self):
        """Print filtering summary."""
        dropped = self.stats["total"] - self.stats["passed"]
        logger.info(
            f"Quality filter: {self.stats['passed']}/{self.stats['total']} passed "
            f"({dropped} dropped)"
        )
        for reason, count in sorted(self.stats["dropped"].items(), key=lambda x: -x[1]):
            logger.info(f"  Dropped [{reason}]: {count}")

    def _check(self, chunk: Chunk) -> tuple[bool, str]:
        """Run all filters on a single chunk. Returns (passed, reason)."""
        # Order matters: cheapest checks first
        if not chunk.text or not chunk.text.strip():
            return False, "empty"

        if chunk.token_count < MIN_CHUNK_TOKENS:
            return False, "too_short"

        text_hash = self._hash(chunk.text)
        if text_hash in self._seen_hashes:
            return False, "duplicate"
        self._seen_hashes.add(text_hash)

        return True, ""

    @staticmethod
    def _hash(text: str) -> str:
        """SHA-256 hash of normalized text for dedup."""
        normalized = text.strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

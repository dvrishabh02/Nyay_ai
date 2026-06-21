"""
Metadata Enricher — tags chunks with domain, jurisdiction, and year.

Uses keyword-based classification (no ML model needed).
Domains map to the top 10 citizen legal problem categories.
"""

import re
from ingestion.models import Chunk


class MetadataEnricher:
    """Tags each chunk with a legal domain based on keyword matching."""

    # Domain → keywords mapping (top citizen legal categories)
    DOMAIN_KEYWORDS: dict[str, list[str]] = {
        "property": [
            "rent", "tenant", "landlord", "eviction", "lease", "property",
            "mutation", "registration", "land", "possession", "trespass",
        ],
        "consumer": [
            "consumer", "defective", "refund", "insurance", "complaint",
            "service deficiency", "unfair trade", "product liability",
        ],
        "criminal": [
            "fir", "bail", "accused", "prosecution", "ipc", "bns", "bnss",
            "cognizable", "arrest", "chargesheet", "investigation",
        ],
        "labour": [
            "salary", "wage", "termination", "employer", "employee",
            "provident fund", "esic", "gratuity", "retrenchment",
        ],
        "family": [
            "maintenance", "divorce", "custody", "domestic violence",
            "marriage", "alimony", "guardianship", "adoption",
        ],
        "constitutional": [
            "fundamental right", "article 14", "article 19", "article 21",
            "writ petition", "constitution", "directive principles",
        ],
        "cheque_bounce": [
            "section 138", "negotiable instruments", "cheque bounce",
            "dishonour", "cheque", "drawer", "drawee",
        ],
        "rti": [
            "right to information", "rti", "public authority",
            "information officer", "cic", "transparency",
        ],
        "motor_accident": [
            "motor accident", "mact", "motor vehicle", "insurance claim",
            "road accident", "compensation", "third party",
        ],
        "tax": [
            "income tax", "gst", "assessment", "tax tribunal",
            "capital gains", "deduction", "tax evasion",
        ],
    }

    # Jurisdiction hints from source names
    JURISDICTION_MAP = {
        "central": "central",
        "andhra_pradesh": "andhra_pradesh",
        "arunachal_pradesh": "arunachal_pradesh",
        "andaman": "andaman_and_nicobar",
    }

    def enrich(self, chunks: list[Chunk]) -> list[Chunk]:
        """Add domain and jurisdiction to each chunk in place."""
        for chunk in chunks:
            if chunk.metadata.domain == "general":
                chunk.metadata.domain = self._classify_domain(chunk.text)
            if not chunk.metadata.jurisdiction or chunk.metadata.jurisdiction == "central":
                chunk.metadata.jurisdiction = self._infer_jurisdiction(chunk.metadata.source)
        return chunks

    def _classify_domain(self, text: str) -> str:
        """Classify chunk into a legal domain by keyword frequency."""
        text_lower = text.lower()
        scores: dict[str, int] = {}

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[domain] = score

        if not scores:
            return "general"
        return max(scores, key=scores.get)

    def _infer_jurisdiction(self, source: str) -> str:
        """Infer jurisdiction from the source dataset key."""
        for key, jurisdiction in self.JURISDICTION_MAP.items():
            if key in source:
                return jurisdiction
        return "central"

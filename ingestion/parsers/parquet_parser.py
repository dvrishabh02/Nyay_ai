"""
Parquet Parser — loads HuggingFace parquet files into raw documents.

Handles varying column schemas across datasets by auto-detecting
the primary text column. Returns a list of (text, metadata_dict) tuples.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger


class ParquetParser:
    """Loads parquet files and extracts text + metadata."""

    # Columns likely to contain the main text (ordered by priority)
    TEXT_COLUMN_CANDIDATES = [
        "text", "content", "passage", "chunk", "body",
        "markdown", "act_text", "document", "judgement",
    ]

    def parse(
        self,
        path: Path,
        text_column: Optional[str] = None,
        title_column: Optional[str] = None,
    ) -> list[dict]:
        """
        Load a parquet file and return list of raw documents.

        Args:
            path: Path to .parquet file.
            text_column: Override auto-detection of text column.
            title_column: Column containing document title (if any).

        Returns:
            List of dicts: [{"text": "...", "title": "...", "row_idx": 0}, ...]
        """
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return []

        df = pd.read_parquet(path)
        logger.info(f"Loaded {len(df)} rows from {path.name} | Columns: {list(df.columns)}")

        # Find the text column
        text_col = text_column or self._detect_text_column(df)
        if text_col is None:
            logger.error(f"No text column found in {path.name}. Columns: {list(df.columns)}")
            return []

        # Find title column if not specified
        title_col = title_column or self._detect_title_column(df)

        documents = []
        for idx, row in df.iterrows():
            text = str(row[text_col]).strip()
            if not text:
                continue

            doc = {
                "text": text,
                "title": str(row[title_col]).strip() if title_col else None,
                "row_idx": idx,
            }
            documents.append(doc)

        logger.info(f"Parsed {len(documents)} documents from {path.name} (text_col='{text_col}')")
        return documents

    def _detect_text_column(self, df: pd.DataFrame) -> Optional[str]:
        """Auto-detect the column containing main text content."""
        # Check known candidates first
        for col in self.TEXT_COLUMN_CANDIDATES:
            if col in df.columns:
                return col

        # Fallback: pick the string column with longest average length
        str_cols = df.select_dtypes(include=["object"]).columns
        if len(str_cols) == 0:
            return None

        avg_lengths = {col: df[col].astype(str).str.len().mean() for col in str_cols}
        return max(avg_lengths, key=avg_lengths.get)

    def _detect_title_column(self, df: pd.DataFrame) -> Optional[str]:
        """Auto-detect a title/name column if present (case/space-insensitive)."""
        title_candidates = [
            "short title", "title", "short_title", "name",
            "act_name", "case_name", "heading",
        ]
        # Normalize actual columns: lowercased, underscores/spaces unified
        normalized = {col.lower().replace("_", " ").strip(): col for col in df.columns}
        for cand in title_candidates:
            key = cand.replace("_", " ").strip()
            if key in normalized:
                return normalized[key]
        return None

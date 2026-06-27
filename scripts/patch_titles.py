#!/usr/bin/env python3
"""
Nyay.AI — Backfill chunk titles in metadata.pkl (no re-embedding).

The first index build dropped the act `Short Title` column, so citations show the
source key ("central_acts") instead of the real act name. This patches titles in
place, keyed by chunk_id, which preserves the exact ordering that aligns with the
FAISS index — so it's safe to run without rebuilding embeddings.

  - Act sources (central/ap/arunachal/andaman): title <- parquet "Short Title".
  - Judgment sources (sc_chunked/legal_chunks): no title column exists, so a
    readable fallback label is set instead of the raw source key.

Run:
    python scripts/patch_titles.py
A backup is written to metadata.pkl.bak before saving.

The parser is already fixed for future full rebuilds; this is for the existing index.
"""

import pickle
import shutil
import sys
from pathlib import Path

import pandas as pd
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.config import METADATA_FILE, PARQUET_SOURCES

# Readable fallback labels for pre-chunked judgment sources (no title column)
JUDGMENT_FALLBACK_TITLES = {
    "sc_chunked": "Supreme Court of India (judgment)",
    "legal_chunks": "Legal reference guide",
}
TITLE_COLUMN = "Short Title"


def build_title_maps() -> dict[str, dict[int, str]]:
    """For each act source, map parquet row index -> Short Title."""
    maps: dict[str, dict[int, str]] = {}
    for key, src in PARQUET_SOURCES.items():
        if src["pre_chunked"] or not src["path"].exists():
            continue
        df = pd.read_parquet(src["path"])
        if TITLE_COLUMN not in df.columns:
            logger.warning(f"{key}: no '{TITLE_COLUMN}' column, skipping")
            continue
        maps[key] = {
            idx: str(title).strip()
            for idx, title in df[TITLE_COLUMN].items()
            if str(title).strip() and str(title).strip().lower() != "nan"
        }
        logger.info(f"{key}: {len(maps[key])} act titles loaded")
    return maps


def row_index_from_chunk_id(chunk_id: str, source: str) -> int | None:
    """chunk_id = '{source}_{rowidx:05d}_chunk_{chunkidx:03d}' -> rowidx."""
    prefix = f"{source}_"
    if not chunk_id.startswith(prefix):
        return None
    rest = chunk_id[len(prefix):]              # '00000_chunk_000'
    try:
        return int(rest.split("_chunk_")[0])
    except (ValueError, IndexError):
        return None


def main():
    if not METADATA_FILE.exists():
        logger.error(f"metadata not found: {METADATA_FILE}")
        return

    with open(METADATA_FILE, "rb") as f:
        metadata: list[dict] = pickle.load(f)
    logger.info(f"Loaded {len(metadata)} chunks")

    title_maps = build_title_maps()

    patched_acts = 0
    patched_judgments = 0
    missed = 0
    for m in metadata:
        source = m.get("source", "")
        if source in title_maps:
            idx = row_index_from_chunk_id(m["chunk_id"], source)
            title = title_maps[source].get(idx) if idx is not None else None
            if title:
                m["title"] = title
                patched_acts += 1
            else:
                missed += 1
        elif source in JUDGMENT_FALLBACK_TITLES:
            m["title"] = JUDGMENT_FALLBACK_TITLES[source]
            patched_judgments += 1

    # Back up, then save
    backup = METADATA_FILE.with_suffix(".pkl.bak")
    shutil.copy2(METADATA_FILE, backup)
    logger.info(f"Backup written: {backup}")

    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)

    logger.info(
        f"Done. Act titles set: {patched_acts} | "
        f"Judgment labels set: {patched_judgments} | Unmatched acts: {missed}"
    )
    # Show a few examples
    for m in metadata[:1] + [x for x in metadata if x.get("source") == "ap_acts"][:1]:
        logger.info(f"  e.g. {m['chunk_id']} -> {m['title']!r}")


if __name__ == "__main__":
    main()

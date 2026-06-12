"""
Nyay.AI — Dataset Downloader
Downloads pre-built legal datasets from HuggingFace and Kaggle.
These are the fastest path to a working RAG corpus.
"""

import os
import sys
import argparse
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ──────────────────────────────────────────────
# HuggingFace Datasets
# ──────────────────────────────────────────────
HUGGINGFACE_DATASETS = [
    {
        "name": "Indian Supreme Court Judgements (Chunked)",
        "repo": "vihaannnn/Indian-Supreme-Court-Judgements-Chunked",
        "save_dir": DATA_DIR / "judgments" / "supreme_court" / "hf_chunked",
        "description": "Pre-chunked SC judgments — ready for RAG embedding",
    },
    {
        "name": "Indian Legal Acts",
        "repo": "geekyrakshit/indian-legal-acts",
        "save_dir": DATA_DIR / "legislation" / "hf_acts",
        "description": "Indian central legal acts — structured dataset",
    },
    {
        "name": "MyScheme Government Schemes",
        "repo": "shrijayan/gov_myscheme",
        "save_dir": DATA_DIR / "schemes" / "hf_myscheme",
        "description": "723 government scheme PDFs from myscheme.gov.in",
    },
    {
        "name": "Legal Dataset for India (RAG-ready chunks)",
        "repo": "ShreyasP123/Legal-Dataset-for-india",
        "save_dir": DATA_DIR / "judgments" / "hf_legal_chunks",
        "description": "Semantic chunks from Indian judicial system — ready for RAG",
    },
    {
        "name": "Indian Judgements Dataset (Categorized)",
        "repo": "opennyaiorg/InJudgements_dataset",
        "save_dir": DATA_DIR / "judgments" / "hf_injudgements",
        "description": "Categorized Indian judgments by case type (tax, criminal, etc.)",
    },
    {
        "name": "Constitution of India (Full Text)",
        "repo": "nisaar/Constitution_of_India",
        "save_dir": DATA_DIR / "legislation" / "hf_constitution",
        "description": "Full text of the Indian Constitution — articles, schedules, amendments",
    },
    {
        "name": "Constitution QA Instruction Set (3300 pairs)",
        "repo": "nisaar/Articles_Constitution_3300_Instruction_Set",
        "save_dir": DATA_DIR / "legislation" / "hf_constitution_qa",
        "description": "3,300 question-answer pairs on Indian Constitution articles",
    },
    {
        "name": "Indian Law Dataset (Comprehensive)",
        "repo": "viber1/indian-law-dataset",
        "save_dir": DATA_DIR / "legislation" / "hf_indian_law",
        "description": "Comprehensive Indian law dataset — acts, sections, explanations",
    },
    {
        "name": "IL-TUR (Indian Legal Text Understanding & Reasoning)",
        "repo": "Exploration-Lab/IL-TUR",
        "save_dir": DATA_DIR / "judgments" / "hf_iltur",
        "description": "Multi-task Indian legal NLP benchmark — bail prediction, judgment, summarization",
    },
    {
        "name": "Indian Constitution + IPC Instruct Dataset",
        "repo": "RaagulQB/Indian-Constitution-And-IPC-Instruct",
        "save_dir": DATA_DIR / "legislation" / "hf_constitution_ipc_instruct",
        "description": "Instruction-tuned QA pairs on Constitution + IPC sections",
    },
]

# ──────────────────────────────────────────────
# Kaggle Datasets
# ──────────────────────────────────────────────
KAGGLE_DATASETS = [
    {
        "name": "Indian Supreme Court Judgments (Full PDFs)",
        "dataset": "vangap/indian-supreme-court-judgments",
        "save_dir": DATA_DIR / "judgments" / "supreme_court" / "kaggle_full",
        "description": "SC judgments metadata CSV + PDF links (85K+ judgments)",
    },
    {
        "name": "Legal Dataset: SC Judgments 1950-2024",
        "dataset": "adarshsingh0903/legal-dataset-sc-judgments-india-19502024",
        "save_dir": DATA_DIR / "judgments" / "supreme_court" / "kaggle_1950_2024",
        "description": "Comprehensive SC judgments from 1950 to 2024",
    },
    {
        "name": "High Court Cases in India",
        "dataset": "saurabhshahane/high-court-cases-in-india",
        "save_dir": DATA_DIR / "judgments" / "high_courts" / "kaggle_hc_cases",
        "description": "High Court cases across India with case details and outcomes",
    },
]


def download_huggingface_datasets(selected=None):
    """Download datasets from HuggingFace Hub."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("ERROR: 'datasets' package not installed. Run: pip install datasets")
        return False

    hf_token = os.getenv("HF_TOKEN")

    for i, ds_info in enumerate(HUGGINGFACE_DATASETS):
        if selected is not None and i not in selected:
            continue

        save_dir = ds_info["save_dir"]
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(HUGGINGFACE_DATASETS)}] {ds_info['name']}")
        print(f"  Repo: {ds_info['repo']}")
        print(f"  Desc: {ds_info['description']}")
        print(f"  Save: {save_dir}")
        print(f"{'='*60}")

        if save_dir.exists() and any(save_dir.iterdir()):
            print(f"  ⏭ Already downloaded. Skipping.")
            continue

        try:
            save_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ⬇ Downloading from HuggingFace...")
            dataset = load_dataset(ds_info["repo"], token=hf_token)

            # Save each split
            for split_name, split_data in dataset.items():
                out_path = save_dir / f"{split_name}.parquet"
                split_data.to_parquet(str(out_path))
                print(f"  ✅ Saved {split_name}: {len(split_data)} rows → {out_path.name}")

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            continue

    return True


def download_kaggle_datasets(selected=None):
    """Download datasets from Kaggle."""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("ERROR: 'kaggle' package not installed. Run: pip install kaggle")
        print("Also ensure ~/.kaggle/kaggle.json exists with your credentials.")
        return False

    try:
        api = KaggleApi()
        api.authenticate()
    except Exception as e:
        print(f"ERROR: Kaggle authentication failed: {e}")
        print("Ensure ~/.kaggle/kaggle.json exists or set KAGGLE_USERNAME + KAGGLE_KEY env vars.")
        return False

    for i, ds_info in enumerate(KAGGLE_DATASETS):
        if selected is not None and i not in selected:
            continue

        save_dir = ds_info["save_dir"]
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(KAGGLE_DATASETS)}] {ds_info['name']}")
        print(f"  Dataset: {ds_info['dataset']}")
        print(f"  Desc: {ds_info['description']}")
        print(f"  Save: {save_dir}")
        print(f"{'='*60}")

        if save_dir.exists() and any(save_dir.iterdir()):
            print(f"  ⏭ Already downloaded. Skipping.")
            continue

        try:
            save_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ⬇ Downloading from Kaggle...")
            api.dataset_download_files(
                ds_info["dataset"],
                path=str(save_dir),
                unzip=True,
            )
            print(f"  ✅ Downloaded to {save_dir}")

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            continue

    return True


def list_datasets():
    """Print all available datasets."""
    print("\n📚 HuggingFace Datasets:")
    print("-" * 60)
    for i, ds in enumerate(HUGGINGFACE_DATASETS):
        status = "✅ Downloaded" if ds["save_dir"].exists() and any(ds["save_dir"].iterdir()) else "⬜ Not downloaded"
        print(f"  [{i}] {ds['name']}")
        print(f"      {ds['repo']}")
        print(f"      {status}")
        print()

    print("\n📚 Kaggle Datasets:")
    print("-" * 60)
    for i, ds in enumerate(KAGGLE_DATASETS):
        status = "✅ Downloaded" if ds["save_dir"].exists() and any(ds["save_dir"].iterdir()) else "⬜ Not downloaded"
        print(f"  [{i}] {ds['name']}")
        print(f"      {ds['dataset']}")
        print(f"      {status}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Nyay.AI Dataset Downloader")
    parser.add_argument("--source", choices=["hf", "kaggle", "all"], default="all",
                        help="Which source to download from (default: all)")
    parser.add_argument("--list", action="store_true",
                        help="List all available datasets and their status")
    args = parser.parse_args()

    if args.list:
        list_datasets()
        return

    print("🏛️  Nyay.AI — Dataset Downloader")
    print("=" * 60)
    print(f"Data directory: {DATA_DIR}")
    print()

    if args.source in ("hf", "all"):
        print("\n📥 Downloading HuggingFace datasets...")
        download_huggingface_datasets()

    if args.source in ("kaggle", "all"):
        print("\n📥 Downloading Kaggle datasets...")
        download_kaggle_datasets()

    print("\n✅ Done! Run with --list to see download status.")


if __name__ == "__main__":
    main()

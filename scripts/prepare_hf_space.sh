#!/usr/bin/env bash
# Assembles a minimal, self-contained export of the backend for pushing to a
# Hugging Face Space (Docker SDK). Deliberately does NOT reuse the main repo's
# git history — that history carries the multi-GB raw legal corpus (tracked
# via Git LFS), which would make the Space repo huge and slow to build.
#
# Usage:
#   ./scripts/prepare_hf_space.sh [output_dir]   # default: dist/hf-space
#
# Then, one-time per Space:
#   cd dist/hf-space
#   git init && git lfs install
#   git lfs track "*.faiss" "*.pkl"
#   git add . && git commit -m "Deploy backend"
#   git remote add space https://huggingface.co/spaces/<user>/<space-name>
#   git push --force space main
#
# On later updates, just re-run this script and `git add -A && git commit && git push`.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${1:-$ROOT/dist/hf-space}"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/data/index"

cp -r "$ROOT/api" "$OUT_DIR/api"
cp -r "$ROOT/rag" "$OUT_DIR/rag"
cp -r "$ROOT/ingestion" "$OUT_DIR/ingestion"
cp "$ROOT"/data/index/*.faiss "$ROOT"/data/index/*.pkl "$ROOT"/data/index/manifest.json "$OUT_DIR/data/index/"
cp "$ROOT/requirements.txt" "$OUT_DIR/requirements.txt"
cp "$ROOT/deploy/Dockerfile" "$OUT_DIR/Dockerfile"
cp "$ROOT/deploy/.dockerignore" "$OUT_DIR/.dockerignore"
cp "$ROOT/deploy/hf_space_README.md" "$OUT_DIR/README.md"

find "$OUT_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +

echo "Prepared Hugging Face Space export at: $OUT_DIR"
du -sh "$OUT_DIR"

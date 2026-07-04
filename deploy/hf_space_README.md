---
title: Nyay Backend
emoji: ⚖️
colorFrom: gray
colorTo: yellow
sdk: docker
app_port: 7860
---

# Nyay.AI — Backend (RAG API)

FastAPI backend for Nyay.AI, serving `/health` and `/query` over the RAG
pipeline (hybrid FAISS+BM25 retrieval → cross-encoder rerank → Groq
generation). Deployed from a curated export of the main repo — see
`scripts/prepare_hf_space.sh` there.

Requires a `GROQ_API_KEY` Repository Secret (Space Settings → Variables and
secrets) to start.

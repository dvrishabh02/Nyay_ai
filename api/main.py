"""
FastAPI app for Nyay.AI.

The RAG pipeline (e5 embedder, cross-encoder, FAISS/BM25 indices, Groq client) is
heavy to construct, so it's built ONCE at startup and stored on app.state, then
reused for every request.

Run:
    uvicorn api.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.routes import router
from rag.pipeline import RAGPipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: loading RAG pipeline...")
    app.state.pipeline = RAGPipeline()
    logger.info("Startup complete: pipeline ready.")
    yield
    app.state.pipeline = None


app = FastAPI(title="Nyay.AI API", version="0.1.0", lifespan=lifespan)

# Open CORS for the Next.js dev frontend; tighten before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

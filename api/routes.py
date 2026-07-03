"""API routes — query endpoint + health check."""

from fastapi import APIRouter, HTTPException, Request

from api.schemas import QueryRequest, QueryResponse, SourceModel

router = APIRouter()


@router.get("/health")
def health(request: Request):
    """Ready once the pipeline (models + indices) has loaded at startup."""
    ready = getattr(request.app.state, "pipeline", None) is not None
    return {"status": "ok" if ready else "loading", "ready": ready}


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline still loading, try again shortly.")

    resp = pipeline.ask(req.question, top_n=req.top_k)

    # Deduplicate the reranked sources by name for a clean, number-free list.
    seen: set[tuple[str, str, str]] = set()
    sources: list[SourceModel] = []
    for c in resp.sources:
        key = (c.title, c.source, c.doc_type)
        if key in seen:
            continue
        seen.add(key)
        sources.append(SourceModel(title=c.title, source=c.source, doc_type=c.doc_type))

    return QueryResponse(
        question=resp.question,
        answer=resp.answer,
        confidence=resp.confidence,
        sources=sources,
        latency_ms=resp.latency_ms,
    )

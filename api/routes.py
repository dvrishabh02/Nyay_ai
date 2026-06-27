"""API routes — query endpoint + health check."""

from fastapi import APIRouter, HTTPException, Request

from api.schemas import QueryRequest, QueryResponse

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
    return QueryResponse(
        question=resp.question,
        answer=resp.answer,
        confidence=resp.confidence,
        citations=[c.to_dict() for c in resp.citations],
        latency_ms=resp.latency_ms,
    )

"""FastAPI REST router for Mutual Fund FAQ Assistant (v1)."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.chat_service import ChatPipelineService
from backend.app.schemas.chat import (
    ChatQueryRequest,
    ChatQueryResponse,
    ErrorResponse,
    HealthResponse,
    SchemeListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Mutual Fund FAQ Assistant"])

# Global service instance dependency
_service_instance: ChatPipelineService | None = None


def get_chat_service() -> ChatPipelineService:
    """Dependency provider returning singleton ChatPipelineService."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ChatPipelineService()
    return _service_instance


@router.post(
    "/chat/query",
    response_model=ChatQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute facts-only query against HDFC Mutual Fund corpus",
    description=(
        "Processes natural language queries through PII scrubbing, intent routing, "
        "two-stage entity-filtered retrieval, and zero-temperature grounded generation "
        "enforcing ≤ 3 sentences, canonical Groww citations, and compliance disclaimers."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query payload"},
        422: {"description": "Unprocessable Entity / Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def query_chat(
    request: ChatQueryRequest,
    service: ChatPipelineService = Depends(get_chat_service),
) -> ChatQueryResponse:
    """Execute end-to-end RAG query."""
    try:
        response = await service.execute_query(user_query=request.query)
        return response
    except Exception as e:
        logger.exception("Unexpected error processing chat query: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}",
        )


@router.get(
    "/schemes",
    response_model=SchemeListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all 5 supported HDFC Mutual Fund schemes",
    description="Returns metadata, categories, benchmarks, and Groww source links for supported schemes.",
)
async def list_schemes(
    service: ChatPipelineService = Depends(get_chat_service),
) -> SchemeListResponse:
    """Get all 5 curated HDFC Mutual Fund schemes."""
    schemes = service.get_supported_schemes()
    return SchemeListResponse(total=len(schemes), schemes=schemes)


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System health, vector store readiness, and Groq rate limit metrics",
    description="Returns diagnostic status of vector index, embeddings, and real-time quota telemetry.",
)
async def health_check(
    service: ChatPipelineService = Depends(get_chat_service),
) -> HealthResponse:
    """Get system health and telemetry metrics."""
    metrics = service.get_health_metrics()
    return HealthResponse(
        status=metrics["status"],
        app=metrics["app"],
        version=metrics["version"],
        environment=metrics["environment"],
        vector_store_initialized=metrics["vector_store_initialized"],
        total_indexed_chunks=metrics["total_indexed_chunks"],
        rate_limiter=metrics["rate_limiter"],
    )


@router.get(
    "/rate-limit",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Groq API Rate & Token Quota Telemetry",
    description="Real-time sliding window usage for 30 RPM, 8K TPM, 1K RPD, 200K TPD.",
)
async def get_rate_limit_status(
    service: ChatPipelineService = Depends(get_chat_service),
) -> Dict[str, Any]:
    """Get live Groq rate limiter metrics."""
    return service.generator.rate_limiter.get_metrics()

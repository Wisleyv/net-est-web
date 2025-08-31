"""API endpoints for semantic alignment functionality"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status, Body

from ..models.semantic_alignment import (
    AlignmentConfiguration,
    AlignmentMethod,
    AlignmentRequest,
    AlignmentResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)
from ..services.semantic_alignment_service import SemanticAlignmentService


logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/semantic-alignment", tags=["Semantic Alignment"])

# Initialize service
alignment_service = SemanticAlignmentService()


@router.post("/align", response_model=AlignmentResponse)
async def align_paragraphs(request: AlignmentRequest) -> AlignmentResponse:
    """Perform semantic alignment of paragraphs between source and target texts"""
    try:
        logger.info(
            f"Alignment request: {len(request.source_paragraphs)} source, {len(request.target_paragraphs)} target"
        )

        # Validate input
        if len(request.source_paragraphs) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Source paragraphs cannot be empty"
            )

        if len(request.target_paragraphs) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Target paragraphs cannot be empty"
            )

        # Perform alignment
        result = await alignment_service.align_paragraphs(request)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Alignment failed: {'; '.join(result.errors or [])}",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in paragraph alignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/", response_model=AlignmentResponse)
async def align_paragraphs_root(request_body: dict = Body(...)) -> AlignmentResponse:
    """Compatibility root POST endpoint -> accepts legacy payloads (source_text/target_text)
    and forwards to /align by coercing into AlignmentRequest when necessary."""
    # If already matching new model shape, let pydantic handle it by creating AlignmentRequest
    if isinstance(request_body, dict) and (
        "source_paragraphs" in request_body or "target_paragraphs" in request_body
    ):
        request = AlignmentRequest(**request_body)
    elif isinstance(request_body, dict) and ("source_text" in request_body and "target_text" in request_body):
        # Legacy simple payload: single strings -> wrap into single-paragraph lists
        request = AlignmentRequest(
            source_paragraphs=[request_body.get("source_text", "")],
            target_paragraphs=[request_body.get("target_text", "")],
        )
    else:
        # Fallback: attempt to coerce generically
        request = AlignmentRequest(**request_body)

    return await align_paragraphs(request)


@router.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest) -> EmbeddingResponse:
    """Generate embeddings for a list of texts"""
    try:
        logger.info(f"Embedding request: {len(request.texts)} texts")

        if len(request.texts) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Texts list cannot be empty"
            )

        if len(request.texts) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many texts. Maximum 100 texts per request",
            )

        # Generate embeddings
        result = await alignment_service.generate_embeddings(request)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/health")
async def get_health_status() -> dict[str, Any]:
    """Get health status of the semantic alignment service"""
    try:
        return await alignment_service.get_health_status()
    except Exception as e:
        logger.error(f"Error getting health status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}",
        )


@router.get("/methods")
async def get_alignment_methods() -> dict[str, Any]:
    """Get available alignment methods and their descriptions"""
    return {
        "methods": {
            "COSINE_SIMILARITY": {
                "name": "Cosine Similarity",
                "description": "Measures cosine of angle between vectors. Range: [-1, 1], higher is more similar.",
                "recommended_threshold": 0.7,
            },
            "EUCLIDEAN_DISTANCE": {
                "name": "Euclidean Distance",
                "description": "Measures straight-line distance between vectors. Converted to similarity (0-1).",
                "recommended_threshold": 0.8,
            },
            "DOT_PRODUCT": {
                "name": "Dot Product",
                "description": "Measures dot product between normalized vectors. Similar to cosine similarity.",
                "recommended_threshold": 0.7,
            },
        },
        "default_method": "COSINE_SIMILARITY",
        "recommended_thresholds": {"high_precision": 0.85, "balanced": 0.7, "high_recall": 0.5},
    }


@router.get("/config")
async def get_current_config() -> dict[str, Any]:
    """Get current alignment service configuration"""
    config = alignment_service.config
    return {
        "model": config.bertimbau_model,
        "similarity_threshold": config.similarity_threshold,
        "max_sequence_length": config.max_sequence_length,
        "batch_size": config.batch_size,
        "device": config.device,
        "cache_embeddings": config.cache_embeddings,
        "confidence_thresholds": config.confidence_thresholds,
    }


@router.post("/config")
async def update_config(new_config: AlignmentConfiguration) -> dict[str, Any]:
    """Update alignment service configuration (creates new service instance)"""
    try:
        global alignment_service
        # Create new service with updated config
        alignment_service = SemanticAlignmentService(new_config)

        return {
            "success": True,
            "message": "Configuration updated successfully",
            "new_config": {
                "model": new_config.bertimbau_model,
                "similarity_threshold": new_config.similarity_threshold,
                "max_sequence_length": new_config.max_sequence_length,
                "batch_size": new_config.batch_size,
                "device": new_config.device,
                "cache_embeddings": new_config.cache_embeddings,
                "confidence_thresholds": new_config.confidence_thresholds,
            },
        }
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration update failed: {str(e)}",
        )


@router.post("/align-simple")
async def align_paragraphs_simple(
    source_paragraphs: list[str],
    target_paragraphs: list[str],
    similarity_threshold: float = 0.7,
    method: AlignmentMethod = AlignmentMethod.COSINE_SIMILARITY,
) -> AlignmentResponse:
    """Simplified endpoint for paragraph alignment with basic parameters"""
    request = AlignmentRequest(
        source_paragraphs=source_paragraphs,
        target_paragraphs=target_paragraphs,
        similarity_threshold=similarity_threshold,
        alignment_method=method,
        max_alignments_per_source=3,
    )

    return await align_paragraphs(request)


@router.delete("/cache")
async def clear_embedding_cache() -> dict[str, Any]:
    """Clear the embedding cache"""
    try:
        cache_size_before = len(alignment_service.embedding_cache.cache)
        alignment_service.embedding_cache.cache.clear()
        alignment_service.embedding_cache.access_order.clear()

        return {
            "success": True,
            "message": f"Cache cleared successfully. Removed {cache_size_before} entries.",
            "cache_size_before": cache_size_before,
            "cache_size_after": 0,
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache clear failed: {str(e)}",
        )

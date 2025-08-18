"""Manual Tags API Endpoints
API endpoints for managing user-created manual tags on sentences
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
import structlog

from ..models.manual_tags import (
    ManualTag,
    CreateTagRequest,
    UpdateTagRequest,
    TagResponse,
    TagListResponse,
    DeleteTagResponse
)
from ..services.manual_tags_service import manual_tags_service, ManualTagsService


logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/manual-tags", tags=["manual-tags"])


def get_manual_tags_service() -> ManualTagsService:
    """Dependency to get manual tags service"""
    return manual_tags_service


@router.post("/", response_model=TagResponse)
async def create_manual_tag(
    request: CreateTagRequest,
    service: ManualTagsService = Depends(get_manual_tags_service)
):
    """Create a new manual tag for a sentence"""
    try:
        logger.info("Creating manual tag", 
                   tag_type=request.tag_type.value,
                   sentence_index=request.sentence_index,
                   analysis_id=request.analysis_id)
        
        # Check if tag already exists for this sentence and tag type
        existing_tags = service.get_tags_for_sentence(
            request.analysis_id, 
            request.sentence_index
        )
        
        # Check if same tag type already exists for this sentence
        for existing_tag in existing_tags:
            if existing_tag.tag_type == request.tag_type:
                return TagResponse(
                    success=False,
                    message=f"Tag {request.tag_type.value} already exists for sentence {request.sentence_index}",
                    tag=existing_tag
                )
        
        tag = service.create_tag(request)
        
        logger.info("Manual tag created successfully", 
                   tag_id=tag.id,
                   tag_type=tag.tag_type.value)
        
        return TagResponse(
            success=True,
            tag=tag,
            message="Tag created successfully"
        )
        
    except Exception as e:
        logger.error("Failed to create manual tag", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tag: {str(e)}"
        )


@router.get("/{analysis_id}", response_model=TagListResponse)
async def get_tags_for_analysis(
    analysis_id: str,
    service: ManualTagsService = Depends(get_manual_tags_service)
):
    """Get all manual tags for a specific analysis session"""
    try:
        logger.info("Getting tags for analysis", analysis_id=analysis_id)
        
        tags = service.get_tags_for_analysis(analysis_id)
        
        logger.info("Retrieved tags for analysis", 
                   analysis_id=analysis_id,
                   tag_count=len(tags))
        
        return TagListResponse(
            success=True,
            tags=tags,
            total_count=len(tags),
            analysis_id=analysis_id
        )
        
    except Exception as e:
        logger.error("Failed to get tags for analysis", 
                    analysis_id=analysis_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tags: {str(e)}"
        )


@router.get("/sentence/{analysis_id}/{sentence_index}", response_model=TagListResponse)
async def get_tags_for_sentence(
    analysis_id: str,
    sentence_index: int,
    service: ManualTagsService = Depends(get_manual_tags_service)
):
    """Get all manual tags for a specific sentence in an analysis"""
    try:
        logger.info("Getting tags for sentence", 
                   analysis_id=analysis_id,
                   sentence_index=sentence_index)
        
        tags = service.get_tags_for_sentence(analysis_id, sentence_index)
        
        return TagListResponse(
            success=True,
            tags=tags,
            total_count=len(tags),
            analysis_id=analysis_id
        )
        
    except Exception as e:
        logger.error("Failed to get tags for sentence", 
                    analysis_id=analysis_id,
                    sentence_index=sentence_index,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tags for sentence: {str(e)}"
        )


@router.put("/{tag_id}", response_model=TagResponse)
async def update_manual_tag(
    tag_id: str,
    request: UpdateTagRequest,
    service: ManualTagsService = Depends(get_manual_tags_service)
):
    """Update an existing manual tag"""
    try:
        logger.info("Updating manual tag", tag_id=tag_id)
        
        updated_tag = service.update_tag(tag_id, request)
        
        if not updated_tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag with ID {tag_id} not found"
            )
        
        logger.info("Manual tag updated successfully", tag_id=tag_id)
        
        return TagResponse(
            success=True,
            tag=updated_tag,
            message="Tag updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update manual tag", tag_id=tag_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tag: {str(e)}"
        )


@router.delete("/{tag_id}", response_model=DeleteTagResponse)
async def delete_manual_tag(
    tag_id: str,
    service: ManualTagsService = Depends(get_manual_tags_service)
):
    """Delete a manual tag"""
    try:
        logger.info("Deleting manual tag", tag_id=tag_id)
        
        success = service.delete_tag(tag_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag with ID {tag_id} not found"
            )
        
        logger.info("Manual tag deleted successfully", tag_id=tag_id)
        
        return DeleteTagResponse(
            success=True,
            message="Tag deleted successfully",
            deleted_tag_id=tag_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete manual tag", tag_id=tag_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tag: {str(e)}"
        )


@router.get("/tag-types/available", response_model=Dict[str, str])
async def get_available_tag_types(
    service: ManualTagsService = Depends(get_manual_tags_service)
):
    """Get available manual tag types with descriptions"""
    try:
        tag_types = service.get_available_tag_types()
        return tag_types
        
    except Exception as e:
        logger.error("Failed to get available tag types", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tag types: {str(e)}"
        )


@router.get("/stats/{analysis_id}")
async def get_tag_stats(
    analysis_id: str,
    service: ManualTagsService = Depends(get_manual_tags_service)
):
    """Get statistics about manual tags for an analysis"""
    try:
        logger.info("Getting tag stats", analysis_id=analysis_id)
        
        stats = service.get_stats(analysis_id)
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "stats": stats
        }
        
    except Exception as e:
        logger.error("Failed to get tag stats", 
                    analysis_id=analysis_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.delete("/analysis/{analysis_id}")
async def delete_all_tags_for_analysis(
    analysis_id: str,
    service: ManualTagsService = Depends(get_manual_tags_service)
):
    """Delete all manual tags for an analysis session"""
    try:
        logger.info("Deleting all tags for analysis", analysis_id=analysis_id)
        
        deleted_count = service.delete_tags_for_analysis(analysis_id)
        
        logger.info("Deleted tags for analysis", 
                   analysis_id=analysis_id,
                   deleted_count=deleted_count)
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} tags for analysis {analysis_id}",
            "deleted_count": deleted_count,
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        logger.error("Failed to delete tags for analysis", 
                    analysis_id=analysis_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tags: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for manual tags service"""
    return {
        "status": "healthy",
        "service": "manual-tags",
        "version": "1.0.0"
    }
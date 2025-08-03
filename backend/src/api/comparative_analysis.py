"""
Comparative Analysis API - Phase 2.B.5 Implementation
Handles dual-input comparative analysis for simplification strategy identification
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import structlog

from ..models.comparative_analysis import (
    ComparativeAnalysisRequest,
    ComparativeAnalysisResponse,
    AnalysisHistoryItem,
    AnalysisExportRequest,
    AnalysisOptions
)
from ..services.comparative_analysis_service import ComparativeAnalysisService

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/comparative-analysis", tags=["comparative-analysis"])

# Service dependency
def get_comparative_analysis_service() -> ComparativeAnalysisService:
    return ComparativeAnalysisService()

@router.post("/", response_model=ComparativeAnalysisResponse)
async def perform_comparative_analysis(
    request: ComparativeAnalysisRequest,
    service: ComparativeAnalysisService = Depends(get_comparative_analysis_service)
):
    """
    Perform comparative analysis between source and target texts
    """
    try:
        logger.info("Starting comparative analysis", 
                   source_length=len(request.source_text),
                   target_length=len(request.target_text))
        
        result = await service.perform_comparative_analysis(request)
        
        logger.info("Comparative analysis completed", 
                   analysis_id=result.analysis_id,
                   overall_score=result.overall_score)
        
        return result
        
    except Exception as e:
        logger.error("Comparative analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/history", response_model=List[AnalysisHistoryItem])
async def get_analysis_history(
    limit: int = 10,
    service: ComparativeAnalysisService = Depends(get_comparative_analysis_service)
):
    """
    Get analysis history with pagination
    """
    try:
        # Return the last 'limit' items from history
        history = service.analysis_history[-limit:]
        return history
    except Exception as e:
        logger.error("Failed to retrieve analysis history", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

@router.post("/upload-text")
async def upload_text_file(file: bytes):
    """
    Upload and extract text from file
    """
    try:
        # For now, assume it's a text file and decode
        # In production, you'd want proper file type detection
        content = file.decode('utf-8')
        
        return {
            "content": content,
            "filename": "uploaded_file.txt",
            "size": len(content),
            "file_type": "text/plain",
            "encoding": "utf-8",
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error("Failed to upload text file", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process file")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for comparative analysis service
    """
    return {
        "status": "healthy",
        "service": "comparative-analysis",
        "version": "2.B.5"
    }
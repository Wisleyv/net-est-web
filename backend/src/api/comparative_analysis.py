"""
Comparative Analysis API - Phase 2.B.5 Implementation
Handles dual-input comparative analysis for simplification strategy identification
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
import structlog
import base64

from ..models.comparative_analysis import (
    ComparativeAnalysisRequest,
    ComparativeAnalysisResponse,
    AnalysisHistoryItem,
    AnalysisExportRequest,
    AnalysisOptions
)
from ..models.text_input import FileType, TextInputRequest, InputType
from ..services.comparative_analysis_service import ComparativeAnalysisService
from ..services.text_input_service import TextInputService

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/comparative-analysis", tags=["comparative-analysis"])

# Service dependencies
_comparative_analysis_service_instance = None

def get_comparative_analysis_service() -> ComparativeAnalysisService:
    global _comparative_analysis_service_instance
    if _comparative_analysis_service_instance is None:
        _comparative_analysis_service_instance = ComparativeAnalysisService()
    return _comparative_analysis_service_instance

def get_text_input_service() -> TextInputService:
    return TextInputService()

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
        
        # Debug log
        logger.info("Strategy count",
                   count=len(result.simplification_strategies),
                   strategies=str(result.simplification_strategies))
        
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

@router.get("/{analysis_id}/export")
async def export_analysis(
    analysis_id: str,
    format: str = "pdf",
    service: ComparativeAnalysisService = Depends(get_comparative_analysis_service)
):
    """
    Export analysis results in specified format
    """
    try:
        if format not in ["pdf", "csv", "json"]:
            raise HTTPException(status_code=400, detail="Supported formats: pdf, csv, json")
        
        export_result = await service.export_analysis(analysis_id, format)
        
        return export_result
        
    except ValueError as e:
        logger.error("Analysis not found for export", analysis_id=analysis_id, error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Export failed", analysis_id=analysis_id, format=format, error=str(e))
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/upload-text")
async def upload_text_file(
    file: UploadFile = File(...),
    text_service: TextInputService = Depends(get_text_input_service)
):
    """Upload and extract text from file for comparative analysis"""
    try:
        # Read file content first to get size
        content = await file.read()
        file_size = len(content)
        
        # Get file info with proper parameters
        file_info = text_service.get_file_info(file.filename or "unknown.txt", file_size)
        
        if not file_info.supported:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_info.file_type}"
            )
        
        # Process file content
        file_content_b64 = base64.b64encode(content).decode('utf-8')
        
        # Create text input request
        request = TextInputRequest(
            input_type=InputType.FILE,
            file_content=file_content_b64,
            file_name=file.filename,
            file_type=file_info.file_type,
            user_config={}
        )
        
        # Process the file to extract text
        result = await text_service.process_text_input(request)
        
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process file: {'; '.join(result.errors)}"
            )
        
        # Return processed text content
        extracted_text = ""
        if result.processed_text:
            if result.processed_text.source_text:
                extracted_text = result.processed_text.source_text
            elif result.processed_text.target_text:
                extracted_text = result.processed_text.target_text
        
        return {
            "success": True,
            "content": extracted_text,
            "file_name": file.filename,
            "file_size": file_info.file_size,
            "extracted_words": len(extracted_text.split()) if extracted_text else 0,
            "character_count": len(extracted_text),
            "validation": {
                "warnings": result.warnings,
                "errors": result.errors
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("File upload failed", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/validate-texts")
async def validate_comparative_texts(
    source_text: str = Form(...),
    target_text: str = Form(...),
    text_service: TextInputService = Depends(get_text_input_service)
):
    """Validate both source and target texts for comparative analysis"""
    try:
        # Validate source text
        source_validation = text_service.validate_text_input(source_text)
        
        # Validate target text  
        target_validation = text_service.validate_text_input(target_text)
        
        # Combined validation result
        combined_warnings = source_validation.warnings + target_validation.warnings
        combined_errors = source_validation.errors + target_validation.errors
        
        is_valid = source_validation.is_valid and target_validation.is_valid
        
        return {
            "success": is_valid,
            "source_validation": source_validation,
            "target_validation": target_validation,
            "combined_warnings": combined_warnings,
            "combined_errors": combined_errors,
            "ready_for_analysis": is_valid and len(combined_errors) == 0
        }
        
    except Exception as e:
        logger.error("Text validation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
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
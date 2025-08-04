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
def get_comparative_analysis_service() -> ComparativeAnalysisService:
    return ComparativeAnalysisService()

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
async def upload_text_file(
    file: UploadFile = File(...),
    text_service: TextInputService = Depends(get_text_input_service)
):
    """
    Upload and extract text from file for comparative analysis
    Supports TXT, MD, DOCX, ODT, PDF formats
    """
    try:
        logger.info("Processing file upload for comparative analysis", 
                   filename=file.filename,
                   content_type=file.content_type)
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        file_ext = file.filename.split(".")[-1].lower()
        
        # Validate file type using Module 1's validation
        try:
            file_type = FileType(file_ext)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_ext}. Supported: {list(text_service.supported_formats.keys())}"
            )

        # Check if file format is actually supported (libraries available)
        if not text_service.supported_formats.get(file_ext, False):
            raise HTTPException(
                status_code=400,
                detail=f"File format {file_ext} is not currently supported on this server"
            )

        # Check file size limits
        if file_size > text_service.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {text_service.MAX_FILE_SIZE:,} bytes ({text_service.MAX_FILE_SIZE//1024//1024}MB)"
            )

        # Extract text using Module 1's comprehensive text extraction
        try:
            # Encode file content to base64 string as expected by text service
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
            
            extracted_text, extraction_warnings = text_service.extract_text_from_file(
                file_content_b64, file_type, file.filename
            )
            
            # Clean and validate the extracted text
            cleaned_text = text_service.clean_text(extracted_text)
            validation_result = text_service.validate_text_input(cleaned_text)
            
            # Combine extraction warnings with validation warnings
            all_warnings = extraction_warnings + validation_result.warnings
            
            logger.info("File text extraction completed",
                       filename=file.filename,
                       original_size=file_size,
                       extracted_chars=len(cleaned_text),
                       is_valid=validation_result.is_valid,
                       warnings_count=len(all_warnings))
            
            return {
                "success": True,
                "content": cleaned_text,
                "filename": file.filename,
                "file_type": file_ext,
                "file_size": file_size,
                "extracted_chars": len(cleaned_text),
                "extracted_words": validation_result.word_count,
                "extracted_paragraphs": validation_result.paragraph_count,
                "validation": {
                    "is_valid": validation_result.is_valid,
                    "warnings": all_warnings,
                    "errors": validation_result.errors,
                    "recommendations": validation_result.processing_recommendations
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as extraction_error:
            logger.error("Text extraction failed", 
                        filename=file.filename,
                        error=str(extraction_error))
            raise HTTPException(
                status_code=422,
                detail=f"Failed to extract text from {file.filename}: {str(extraction_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("File upload processing failed", 
                    filename=getattr(file, 'filename', 'unknown'),
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.post("/validate-texts")
async def validate_comparative_texts(
    source_text: str = Form(...),
    target_text: str = Form(...),
    text_service: TextInputService = Depends(get_text_input_service)
):
    """
    Validate both source and target texts for comparative analysis
    Provides comprehensive validation including text statistics and recommendations
    """
    try:
        logger.info("Validating texts for comparative analysis",
                   source_length=len(source_text),
                   target_length=len(target_text))
        
        # Validate both texts
        source_validation = text_service.validate_text_input(source_text)
        target_validation = text_service.validate_text_input(target_text)
        
        # Additional comparative validation rules
        comparative_warnings = []
        comparative_errors = []
        
        # Check text length ratios
        source_words = source_validation.word_count
        target_words = target_validation.word_count
        
        if source_words > 0 and target_words > 0:
            ratio = target_words / source_words
            if ratio > 1.5:
                comparative_warnings.append(
                    f"Target text is significantly longer than source ({ratio:.1f}x). "
                    "Simplification typically reduces text length."
                )
            elif ratio < 0.3:
                comparative_warnings.append(
                    f"Target text is much shorter than source ({ratio:.1f}x). "
                    "Very short simplifications may lose important information."
                )
        
        # Check paragraph structure alignment
        if (source_validation.paragraph_count > 1 and 
            target_validation.paragraph_count == 1):
            comparative_warnings.append(
                "Source has multiple paragraphs but target has only one. "
                "Consider maintaining paragraph structure in simplification."
            )
        
        # Overall validation status
        is_ready_for_analysis = (
            source_validation.is_valid and 
            target_validation.is_valid and
            len(comparative_errors) == 0
        )
        
        return {
            "ready_for_analysis": is_ready_for_analysis,
            "source_validation": {
                "is_valid": source_validation.is_valid,
                "character_count": source_validation.character_count,
                "word_count": source_validation.word_count,
                "paragraph_count": source_validation.paragraph_count,
                "warnings": source_validation.warnings,
                "errors": source_validation.errors,
                "recommendations": source_validation.processing_recommendations
            },
            "target_validation": {
                "is_valid": target_validation.is_valid,
                "character_count": target_validation.character_count,
                "word_count": target_validation.word_count,
                "paragraph_count": target_validation.paragraph_count,
                "warnings": target_validation.warnings,
                "errors": target_validation.errors,
                "recommendations": target_validation.processing_recommendations
            },
            "comparative_analysis": {
                "word_count_ratio": target_words / source_words if source_words > 0 else 0,
                "warnings": comparative_warnings,
                "errors": comparative_errors,
                "recommendations": [
                    "Both texts are ready for comparative analysis",
                    "Review paragraph alignment if needed",
                    "Consider text length ratios in analysis interpretation"
                ] if is_ready_for_analysis else [
                    "Fix validation errors before proceeding with analysis"
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Validation failed", error=str(e))
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
"""Text Input API endpoints for NET-EST System
Handles text input processing and file uploads
"""

import base64
import logging
import time

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
try:
    from backend.src.models.text_input import (
        FileType,
        FileUploadInfo,
        InputType,
        TextInputRequest,
        TextInputResponse,
        TextValidationResult,
    )
    from backend.src.services.text_input_service import TextInputService
except Exception:
    from ..models.text_input import (
        FileType,
        FileUploadInfo,
        InputType,
        TextInputRequest,
        TextInputResponse,
        TextValidationResult,
    )
    from ..services.text_input_service import TextInputService
from ..services.text_input_service import TextInputService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/text-input", tags=["Text Input"])

# Initialize text input service
text_input_service = TextInputService()


@router.post("/validate", response_model=TextValidationResult)
async def validate_text(text: str) -> TextValidationResult:
    """Validate text input and provide recommendations"""
    try:
        return text_input_service.validate_text_input(text)
    except Exception as e:
        logger.error(f"Error validating text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.post("/file-info", response_model=FileUploadInfo)
async def get_file_info(file: UploadFile = File(...)) -> FileUploadInfo:
    """Get information about uploaded file without processing"""
    try:
        # Read file size
        file_content = await file.read()
        file_size = len(file_content)

        # Reset file position
        await file.seek(0)

        return text_input_service.get_file_info(file.filename or "unknown", file_size)
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File info error: {str(e)}")


@router.post("/process-typed", response_model=TextInputResponse)
async def process_typed_text(
    source_text: str = Form(...), target_text: str | None = Form(None)
) -> TextInputResponse:
    """Process typed text input"""
    try:
        start_time = time.time()

        request = TextInputRequest(
            input_type=InputType.TYPED, source_text=source_text, target_text=target_text
        )

        response = await text_input_service.process_text_input(request)

        # Add processing time to metadata
        processing_time = time.time() - start_time
        if response.metadata:
            response.metadata["processing_time"] = f"{processing_time:.2f}s"

        return response

    except Exception as e:
        logger.error(f"Error processing typed text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.post("/process-file", response_model=TextInputResponse)
async def process_file_upload(
    file: UploadFile = File(...), target_text: str | None = Form(None)
) -> TextInputResponse:
    """Process uploaded file"""
    try:
        start_time = time.time()

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Get file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="File name is required")

        file_ext = file.filename.split(".")[-1].lower()

        # Validate file type
        try:
            file_type = FileType(file_ext)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")

        # Check file size
        if file_size > text_input_service.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {text_input_service.MAX_FILE_SIZE:,} bytes",
            )

        # Encode file content to base64
        file_content_b64 = base64.b64encode(file_content).decode("utf-8")

        request = TextInputRequest(
            input_type=InputType.FILE,
            file_content=file_content_b64,
            file_name=file.filename,
            file_type=file_type,
            target_text=target_text,
        )

        response = await text_input_service.process_text_input(request)

        # Add processing time to metadata
        processing_time = time.time() - start_time
        if response.metadata:
            response.metadata["processing_time"] = f"{processing_time:.2f}s"
            response.metadata["file_size"] = file_size

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")


@router.get("/supported-formats")
async def get_supported_formats() -> JSONResponse:
    """Get list of supported file formats"""
    try:
        return JSONResponse(
            {
                "supported_formats": text_input_service.supported_formats,
                "limits": {
                    "max_file_size": text_input_service.MAX_FILE_SIZE,
                    "max_characters": text_input_service.MAX_CHARS,
                    "max_paragraphs": text_input_service.MAX_PARAGRAPHS,
                    "warning_file_size": text_input_service.WARNING_FILE_SIZE,
                    "warning_characters": text_input_service.WARNING_CHARS,
                    "warning_paragraphs": text_input_service.WARNING_PARAGRAPHS,
                },
            }
        )
    except Exception as e:
        logger.error(f"Error getting supported formats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/bulk-validate")
async def bulk_validate_texts(texts: list[str]) -> list[TextValidationResult]:
    """Validate multiple texts in bulk"""
    try:
        if len(texts) > 10:  # Limit bulk operations
            raise HTTPException(status_code=400, detail="Maximum 10 texts per bulk request")

        results = []
        for text in texts:
            validation = text_input_service.validate_text_input(text)
            results.append(validation)

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk validation error: {str(e)}")


@router.get("/health")
async def text_input_health() -> JSONResponse:
    """Health check for text input module"""
    try:
        # Test basic functionality
        test_text = "This is a test text for validation."
        validation = text_input_service.validate_text_input(test_text)

        return JSONResponse(
            {
                "status": "healthy",
                "module": "text_input",
                "supported_formats": text_input_service.supported_formats,
                "test_validation": {
                    "success": validation.is_valid,
                    "character_count": validation.character_count,
                },
            }
        )
    except Exception as e:
        logger.error(f"Text input health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "module": "text_input", "error": str(e)},
        )

"""Text Input API endpoints for NET-EST System
Handles text input processing and file uploads
"""

import base64
import logging
import time

from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from fastapi.responses import JSONResponse

from ..models.text_input import (
    FileType,
    FileUploadInfo,
    InputType,
    TextInputRequest,
    TextInputResponse,
    TextValidationResult,
)
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
        # Read file to get size
        content = await file.read()
        file_size = len(content)
        
        return text_input_service.get_file_info(file.filename or "unknown.txt", file_size)
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File info error: {str(e)}")


@router.post("/process-typed", response_model=TextInputResponse)
async def process_typed_text(
    source_text: str = Form(...),
    target_text: str = Form(...),
    user_config: str = Form("{}"),  # JSON string of user configuration
) -> TextInputResponse:
    """Process typed text input"""
    try:
        import json
        config = json.loads(user_config) if user_config else {}
        
        request = TextInputRequest(
            input_type=InputType.TYPED,
            source_text=source_text,
            target_text=target_text,
            user_config=config
        )
        
        return await text_input_service.process_text_input(request)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid user_config JSON")
    except Exception as e:
        logger.error(f"Error processing typed text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.post("/process-file", response_model=TextInputResponse)
async def process_file_upload(
    file: UploadFile = File(...),
    user_config: str = Form("{}"),  # JSON string of user configuration
) -> TextInputResponse:
    """Process uploaded file"""
    try:
        import json
        config = json.loads(user_config) if user_config else {}
        
        # Read file content
        content = await file.read()
        file_content_b64 = base64.b64encode(content).decode('utf-8')
        
        # Determine file type from extension
        file_ext = file.filename.split('.')[-1].lower() if file.filename else 'txt'
        try:
            file_type = FileType(file_ext)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        request = TextInputRequest(
            input_type=InputType.FILE,
            file_content=file_content_b64,
            file_name=file.filename,
            file_type=file_type,
            user_config=config
        )
        
        return await text_input_service.process_text_input(request)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid user_config JSON")
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

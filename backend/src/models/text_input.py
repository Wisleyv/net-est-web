"""Text Input Models for NET-EST System
Handles input validation and processing for text analysis
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class InputType(str, Enum):
    """Types of text input supported by the system"""

    TYPED = "typed"
    FILE = "file"


class FileType(str, Enum):
    """Supported file formats for text input"""

    TXT = "txt"
    MD = "md"
    DOCX = "docx"
    ODT = "odt"
    PDF = "pdf"


class TextInputRequest(BaseModel):
    """Request model for text input processing"""

    input_type: InputType
    source_text: str | None = Field(None, description="Source text content")
    target_text: str | None = Field(None, description="Target text content")
    file_content: str | None = Field(None, description="Base64 encoded file content")
    file_name: str | None = Field(None, description="Original file name")
    file_type: FileType | None = Field(None, description="File format type")
    user_config: dict[str, Any] = Field(default_factory=dict, description="User configuration")

    @field_validator("source_text", "target_text")
    @classmethod
    def validate_text_length(cls, v: str | None) -> str | None:
        """Validate text length and provide warnings for long texts"""
        if v and len(v) > 50000:  # 50k characters threshold
            raise ValueError("Text is too long. Maximum allowed: 50,000 characters")
        return v

    @field_validator("file_name")
    @classmethod
    def validate_file_extension(cls, v: str | None, info) -> str | None:
        """Validate file extension matches file_type"""
        if v and info.data.get("file_type"):
            expected_ext = f".{info.data['file_type'].value}"
            if not v.lower().endswith(expected_ext):
                raise ValueError(f"File extension must be {expected_ext}")
        return v


class ProcessedText(BaseModel):
    """Processed text output model"""

    source_text: str = Field(..., description="Cleaned source text")
    target_text: str = Field(..., description="Cleaned target text")
    source_paragraphs: list[str] = Field(..., description="Source text segmented by paragraphs")
    target_paragraphs: list[str] = Field(..., description="Target text segmented by paragraphs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Processing metadata")


class TextInputResponse(BaseModel):
    """Response model for text input processing"""

    success: bool
    processed_text: ProcessedText | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FileUploadInfo(BaseModel):
    """File upload information model"""

    file_name: str
    file_size: int
    file_type: FileType
    supported: bool
    estimated_processing_time: float | None = None
    warnings: list[str] = Field(default_factory=list)


class TextValidationResult(BaseModel):
    """Text validation result model"""

    is_valid: bool
    character_count: int
    word_count: int
    paragraph_count: int
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    processing_recommendations: list[str] = Field(default_factory=list)

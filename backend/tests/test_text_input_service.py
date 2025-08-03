"""
Comprehensive test suite for Text Input Service
Tests validation, file processing, and text cleaning functionality
"""

import pytest
import base64
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.models.text_input import (
    InputType,
    FileType,
    TextInputRequest,
    ProcessedText,
    TextValidationResult,
    FileUploadInfo,
)
from src.services.text_input_service import TextInputService


class TestTextInputService:
    """Test suite for TextInputService functionality."""

    @pytest.fixture
    def service(self):
        """Create TextInputService instance for testing."""
        return TextInputService()

    @pytest.fixture
    def sample_text(self):
        """Sample text for testing."""
        return "This is a sample text for testing.\n\nIt has multiple paragraphs.\n\nAnd proper formatting."

    @pytest.fixture
    def long_text(self):
        """Long text that exceeds warning thresholds."""
        return "Lorem ipsum dolor sit amet. " * 2000  # Over 25k chars

    @pytest.fixture
    def sample_file_content(self):
        """Sample file content encoded in base64."""
        content = "Sample file content\n\nWith multiple paragraphs."
        return base64.b64encode(content.encode('utf-8')).decode('ascii')

    def test_text_validation_valid(self, service, sample_text):
        """Test validation of valid text."""
        result = service.validate_text_input(sample_text)
        
        assert isinstance(result, TextValidationResult)
        assert result.is_valid
        assert result.character_count > 0
        assert result.word_count > 0
        assert result.paragraph_count > 0
        assert len(result.errors) == 0

    def test_text_validation_empty(self, service):
        """Test validation of empty text."""
        result = service.validate_text_input("")
        
        assert isinstance(result, TextValidationResult)
        assert result.is_valid
        assert result.character_count == 0
        assert result.word_count == 0
        assert result.paragraph_count == 0

    def test_text_validation_long_text(self, service, long_text):
        """Test validation of text that exceeds warning limits."""
        result = service.validate_text_input(long_text)
        
        assert isinstance(result, TextValidationResult)
        # Text that exceeds MAX_CHARS should be invalid, not just warning
        assert not result.is_valid  # Should be invalid due to exceeding MAX_CHARS
        assert len(result.errors) > 0
        assert "exceeds maximum limit" in result.errors[0]

    def test_text_validation_too_long(self, service):
        """Test validation of text that exceeds maximum limits."""
        too_long_text = "a" * (service.MAX_CHARS + 1)
        result = service.validate_text_input(too_long_text)
        
        assert isinstance(result, TextValidationResult)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "exceeds maximum limit" in result.errors[0]

    def test_clean_text_normalization(self, service):
        """Test text cleaning and normalization."""
        messy_text = "  This   has    excessive    whitespace  \r\n\r\n  And   weird   line breaks  \r\r\n  "
        cleaned = service.clean_text(messy_text)
        
        assert "   " not in cleaned  # No excessive whitespace
        assert cleaned.startswith("This")  # Trimmed
        assert cleaned.endswith("breaks")  # Trimmed
        assert "\r" not in cleaned  # Normalized line breaks

    def test_segment_paragraphs(self, service, sample_text):
        """Test paragraph segmentation."""
        paragraphs = service.segment_paragraphs(sample_text)
        
        assert isinstance(paragraphs, list)
        assert len(paragraphs) == 3  # Based on sample_text structure
        assert all(p.strip() for p in paragraphs)  # No empty paragraphs

    def test_segment_paragraphs_empty(self, service):
        """Test paragraph segmentation with empty text."""
        paragraphs = service.segment_paragraphs("")
        
        assert isinstance(paragraphs, list)
        assert len(paragraphs) == 0

    def test_get_file_info_txt(self, service):
        """Test file info for TXT file."""
        info = service.get_file_info("test.txt", 1024)
        
        assert isinstance(info, FileUploadInfo)
        assert info.file_name == "test.txt"
        assert info.file_size == 1024
        assert info.file_type == FileType.TXT
        assert info.supported
        assert info.estimated_processing_time is not None

    def test_get_file_info_unsupported(self, service):
        """Test file info for unsupported file type."""
        info = service.get_file_info("test.xyz", 1024)
        
        assert isinstance(info, FileUploadInfo)
        assert not info.supported
        assert len(info.warnings) > 0

    def test_get_file_info_large_file(self, service):
        """Test file info for large file."""
        large_size = service.WARNING_FILE_SIZE + 1000
        info = service.get_file_info("test.txt", large_size)
        
        assert isinstance(info, FileUploadInfo)
        assert len(info.warnings) > 0
        assert "Large file detected" in info.warnings[0]

    def test_extract_text_from_txt_file(self, service, sample_file_content):
        """Test text extraction from TXT file."""
        text, warnings = service.extract_text_from_file(
            sample_file_content, FileType.TXT, "test.txt"
        )
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Sample file content" in text
        assert isinstance(warnings, list)

    def test_extract_text_from_md_file(self, service):
        """Test text extraction from Markdown file."""
        content = "# Header\n\nThis is **markdown** content."
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
        
        text, warnings = service.extract_text_from_file(
            content_b64, FileType.MD, "test.md"
        )
        
        assert isinstance(text, str)
        assert "Header" in text
        assert "markdown" in text

    @pytest.mark.asyncio
    async def test_process_typed_text_input(self, service, sample_text):
        """Test processing typed text input."""
        request = TextInputRequest(
            input_type=InputType.TYPED,
            source_text=sample_text,
            target_text="Target text for testing."
        )
        
        response = await service.process_text_input(request)
        
        assert response.success
        assert response.processed_text is not None
        assert isinstance(response.processed_text, ProcessedText)
        assert len(response.processed_text.source_paragraphs) > 0
        assert len(response.processed_text.target_paragraphs) > 0
        assert response.processed_text.metadata is not None

    @pytest.mark.asyncio
    async def test_process_typed_text_missing_source(self, service):
        """Test processing typed text input without source text."""
        request = TextInputRequest(
            input_type=InputType.TYPED,
            source_text=None
        )
        
        response = await service.process_text_input(request)
        
        assert not response.success
        assert len(response.errors) > 0
        assert "requires source_text" in response.errors[0]

    @pytest.mark.asyncio
    async def test_process_file_input(self, service, sample_file_content):
        """Test processing file input."""
        request = TextInputRequest(
            input_type=InputType.FILE,
            file_content=sample_file_content,
            file_name="test.txt",
            file_type=FileType.TXT
        )
        
        response = await service.process_text_input(request)
        
        assert response.success
        assert response.processed_text is not None
        assert len(response.processed_text.source_paragraphs) > 0

    @pytest.mark.asyncio
    async def test_process_file_input_missing_params(self, service):
        """Test processing file input with missing parameters."""
        request = TextInputRequest(
            input_type=InputType.FILE,
            file_content=None
        )
        
        response = await service.process_text_input(request)
        
        assert not response.success
        assert len(response.errors) > 0
        assert "File input requires" in response.errors[0]

    @pytest.mark.asyncio
    async def test_process_unsupported_file_type(self, service, sample_file_content):
        """Test processing unsupported file type."""
        # Mock unsupported format
        with patch.object(service, 'supported_formats', {'txt': False}):
            request = TextInputRequest(
                input_type=InputType.FILE,
                file_content=sample_file_content,
                file_name="test.txt",
                file_type=FileType.TXT
            )
            
            response = await service.process_text_input(request)
            
            assert not response.success
            assert "not supported" in response.errors[0]

    @pytest.mark.asyncio
    async def test_process_invalid_text(self, service):
        """Test processing text that fails validation."""
        too_long_text = "a" * (service.MAX_CHARS + 1)
        
        # Since Pydantic will reject this at the model level, we test the service validation directly
        result = service.validate_text_input(too_long_text)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "exceeds maximum limit" in result.errors[0]

    def test_supported_formats_check(self, service):
        """Test supported formats detection."""
        formats = service._check_supported_formats()
        
        assert isinstance(formats, dict)
        assert 'txt' in formats
        assert 'md' in formats
        assert formats['txt'] is True  # Should always be supported
        assert formats['md'] is True  # Should always be supported

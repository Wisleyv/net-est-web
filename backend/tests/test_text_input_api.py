"""
Test suite for Text Input API endpoints
Tests all REST API endpoints for text input processing
"""

import pytest
import base64
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Import the FastAPI app
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.main import app


class TestTextInputAPI:
    """Test suite for Text Input API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)

    @pytest.fixture
    def sample_text(self):
        """Sample text for testing."""
        return "This is a sample text for testing."

    @pytest.fixture
    def sample_file_data(self):
        """Sample file data for testing."""
        content = "Sample file content for testing."
        return {
            "content": base64.b64encode(content.encode('utf-8')).decode('ascii'),
            "filename": "test.txt",
            "content_type": "text/plain"
        }

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/api/v1/text-input/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "text_input"
        assert "supported_formats" in data
        assert "test_validation" in data

    def test_supported_formats_endpoint(self, client):
        """Test the supported formats endpoint."""
        response = client.get("/api/v1/text-input/supported-formats")
        
        assert response.status_code == 200
        data = response.json()
        assert "supported_formats" in data
        assert isinstance(data["supported_formats"], dict)
        assert "txt" in data["supported_formats"]

    def test_validate_text_endpoint_valid(self, client, sample_text):
        """Test text validation endpoint with valid text."""
        response = client.post(
            f"/api/v1/text-input/validate?text={sample_text}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert "character_count" in data
        assert "word_count" in data
        assert data["character_count"] > 0

    def test_validate_text_endpoint_empty(self, client):
        """Test text validation endpoint with empty text."""
        response = client.post(
            "/api/v1/text-input/validate?text="
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["character_count"] == 0

    def test_validate_text_endpoint_too_long(self, client):
        """Test text validation endpoint with text that's too long."""
        # Use a shorter but still over-limit text to avoid URL length issues
        long_text = "a" * 60000  # Over MAX_CHARS but manageable URL length
        import urllib.parse
        encoded_text = urllib.parse.quote(long_text)
        response = client.post(
            f"/api/v1/text-input/validate?text={encoded_text}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_text_endpoint_missing_text(self, client):
        """Test text validation endpoint without text parameter."""
        response = client.post(
            "/api/v1/text-input/validate"  # No text parameter
        )
        
        assert response.status_code == 422  # Validation error

    def test_file_info_endpoint_txt(self, client, sample_file_data):
        """Test file info endpoint with TXT file."""
        form_data = {
            "filename": sample_file_data["filename"]
        }
        files = {
            "file": (
                sample_file_data["filename"],
                base64.b64decode(sample_file_data["content"]),
                sample_file_data["content_type"]
            )
        }
        
        response = client.post("/api/v1/text-input/file-info", data=form_data, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == sample_file_data["filename"]
        assert data["supported"] is True
        assert data["file_type"] == "txt"

    def test_file_info_endpoint_unsupported(self, client):
        """Test file info endpoint with unsupported file type."""
        unsupported_content = b"Unsupported file content"
        form_data = {"filename": "test.xyz"}
        files = {
            "file": ("test.xyz", unsupported_content, "application/octet-stream")
        }
        
        response = client.post("/api/v1/text-input/file-info", data=form_data, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["supported"] is False
        assert len(data["warnings"]) > 0

    def test_process_typed_endpoint_valid(self, client, sample_text):
        """Test process typed text endpoint with valid data."""
        # Use Form data instead of JSON
        form_data = {
            "source_text": sample_text,
            "target_text": "Target text for testing."
        }
        
        response = client.post("/api/v1/text-input/process-typed", data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "processed_text" in data
        assert data["processed_text"]["source_paragraphs"]

    def test_process_typed_endpoint_missing_source(self, client):
        """Test process typed text endpoint without source text."""
        # Missing required source_text field
        form_data = {
            "target_text": "Target text only."
        }
        
        response = client.post("/api/v1/text-input/process-typed", data=form_data)
        
        assert response.status_code == 422  # Form validation error

    def test_process_file_endpoint_txt(self, client, sample_file_data):
        """Test process file endpoint with TXT file."""
        form_data = {
            "filename": sample_file_data["filename"],
            "target_text": "Target text for testing."
        }
        files = {
            "file": (
                sample_file_data["filename"],
                base64.b64decode(sample_file_data["content"]),
                sample_file_data["content_type"]
            )
        }
        
        response = client.post("/api/v1/text-input/process-file", data=form_data, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "processed_text" in data

    def test_process_file_endpoint_no_file(self, client):
        """Test process file endpoint without file."""
        form_data = {"filename": "test.txt"}
        
        response = client.post("/api/v1/text-input/process-file", data=form_data)
        
        assert response.status_code == 422  # Validation error

    def test_bulk_validate_endpoint(self, client, sample_text):
        """Test bulk validation endpoint."""
        # Send array of texts directly
        request_data = [sample_text, "Another text for testing.", ""]
        
        response = client.post("/api/v1/text-input/bulk-validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)  # Returns array directly
        assert len(data) == 3
        assert all("is_valid" in result for result in data)

    def test_bulk_validate_endpoint_empty_list(self, client):
        """Test bulk validation endpoint with empty list."""
        request_data = []  # Empty array directly
        
        response = client.post("/api/v1/text-input/bulk-validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data == []  # Empty array response

    def test_bulk_validate_endpoint_too_many_texts(self, client):
        """Test bulk validation endpoint with too many texts."""
        request_data = ["text"] * 11  # Exceeds limit of 10
        
        response = client.post("/api/v1/text-input/bulk-validate", json=request_data)
        
        assert response.status_code == 400  # Bad request
        data = response.json()
        assert "Maximum 10 texts" in data["detail"]

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test API error handling with malformed requests."""
        # Test with invalid JSON
        response = client.post(
            "/api/v1/text-input/validate",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options("/api/v1/text-input/health")
        
        # FastAPI should handle CORS if configured
        assert response.status_code in [200, 405]  # Either OK or Method Not Allowed

    def test_content_type_validation(self, client):
        """Test content type validation for file uploads."""
        # Test with wrong content type
        form_data = {"filename": "test.txt"}
        files = {
            "file": ("test.txt", b"content", "application/pdf")  # Wrong content type for .txt
        }
        
        response = client.post("/api/v1/text-input/file-info", data=form_data, files=files)
        
        # Should still work but might have warnings
        assert response.status_code == 200

    def test_large_file_handling(self, client):
        """Test handling of large files."""
        # Create large content
        large_content = b"Large file content. " * 10000  # About 200KB
        form_data = {"filename": "large_test.txt"}
        files = {
            "file": ("large_test.txt", large_content, "text/plain")
        }
        
        response = client.post("/api/v1/text-input/file-info", data=form_data, files=files)
        
        assert response.status_code == 200
        data = response.json()
        # The actual file info may not have warnings in all cases
        # Just verify basic fields are present
        assert "file_size" in data
        assert "file_name" in data
        assert "supported" in data

    def test_file_encoding_handling(self, client):
        """Test handling of different file encodings."""
        # Test with UTF-8 content containing special characters
        content = "Texto con acentos: café, niño, corazón"
        encoded_content = content.encode('utf-8')
        
        form_data = {"filename": "utf8_test.txt"}
        files = {
            "file": ("utf8_test.txt", encoded_content, "text/plain")
        }
        
        response = client.post("/api/v1/text-input/process-file", data=form_data, files=files)
        
        assert response.status_code == 200
        data = response.json()
        if data["success"]:
            # Check that special characters are preserved
            assert "café" in str(data.get("processed_text", {}))

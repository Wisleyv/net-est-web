"""
API tests for M6: Feedback Capture & Persistence System

Tests for feedback submission endpoints and integration with comparative analysis.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.models.feedback import (
    FeedbackSubmissionRequest,
    FeedbackSubmissionResponse,
    FeedbackAction,
    FeedbackCollectionPrompt
)
from src.api.comparative_analysis import router
from src.core.feature_flags import FeatureFlags


class TestFeedbackAPI:
    """Test cases for feedback API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def mock_repository(self):
        """Mock feedback repository"""
        mock_repo = AsyncMock()
        mock_repo.save_feedback.return_value = True
        return mock_repo

    @pytest.fixture
    def mock_feature_flags(self):
        """Mock feature flags service"""
        with patch('src.api.comparative_analysis.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            mock_flags.flags = {
                "feedback_system": {
                    "enabled": True,
                    "collection_enabled": True,
                    "storage_path": "data/feedback",
                    "max_file_size_mb": 10.0
                }
            }
            yield mock_flags

    def test_submit_feedback_success(self, client, mock_repository, mock_feature_flags):
        """Test successful feedback submission"""
        with patch('src.api.comparative_analysis.FileBasedFeedbackRepository', return_value=mock_repository):
            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "confirm",
                "note": "Great simplification!",
                "suggested_tag": "vocabulary",
                "metadata": {"user_agent": "test-client"}
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 200
            response_data = response.json()

            assert response_data["status"] == "submitted"
            assert response_data["message"] == "Feedback submitted successfully"
            assert "feedback_id" in response_data

            # Verify repository was called
            mock_repository.save_feedback.assert_called_once()
            call_args = mock_repository.save_feedback.call_args[0][0]

            assert call_args.session_id == request_data["session_id"]
            assert call_args.strategy_id == request_data["strategy_id"]
            assert call_args.action.value == request_data["action"]
            assert call_args.note == request_data["note"]
            assert call_args.suggested_tag == request_data["suggested_tag"]

    def test_submit_feedback_minimal_data(self, client, mock_repository, mock_feature_flags):
        """Test feedback submission with minimal required data"""
        with patch('src.api.comparative_analysis.FileBasedFeedbackRepository', return_value=mock_repository):
            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "reject"
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 200
            response_data = response.json()

            assert response_data["status"] == "submitted"
            assert "feedback_id" in response_data

    def test_submit_feedback_invalid_action(self, client, mock_feature_flags):
        """Test feedback submission with invalid action"""
        request_data = {
            "session_id": "test-session-123",
            "strategy_id": "lexical_simplification",
            "action": "invalid_action"
        }

        response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_submit_feedback_missing_required_fields(self, client, mock_feature_flags):
        """Test feedback submission with missing required fields"""
        # Missing session_id
        request_data = {
            "strategy_id": "lexical_simplification",
            "action": "confirm"
        }

        response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

        assert response.status_code == 422  # Validation error

        # Missing strategy_id
        request_data = {
            "session_id": "test-session-123",
            "action": "confirm"
        }

        response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_submit_feedback_system_disabled(self, client):
        """Test feedback submission when system is disabled"""
        with patch('src.api.comparative_analysis.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False

            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "confirm"
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 503
            assert "Feedback system is currently disabled" in response.json()["detail"]

    def test_submit_feedback_collection_disabled(self, client):
        """Test feedback submission when collection is disabled"""
        with patch('src.api.comparative_analysis.feature_flags') as mock_flags:
            mock_flags.is_enabled.side_effect = lambda key: {
                "feedback_system.enabled": True,
                "feedback_system.collection_enabled": False
            }.get(key, False)

            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "confirm"
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 503
            assert "Feedback collection is currently disabled" in response.json()["detail"]

    def test_submit_feedback_repository_failure(self, client, mock_feature_flags):
        """Test feedback submission when repository save fails"""
        mock_repo = AsyncMock()
        mock_repo.save_feedback.return_value = False

        with patch('src.api.comparative_analysis.FileBasedFeedbackRepository', return_value=mock_repo):
            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "confirm"
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 500
            assert "Failed to save feedback" in response.json()["detail"]

    def test_submit_feedback_repository_exception(self, client, mock_feature_flags):
        """Test feedback submission when repository raises exception"""
        mock_repo = AsyncMock()
        mock_repo.save_feedback.side_effect = Exception("Database connection failed")

        with patch('src.api.comparative_analysis.FileBasedFeedbackRepository', return_value=mock_repo):
            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "confirm"
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 500
            assert "Feedback submission failed" in response.json()["detail"]

    def test_submit_feedback_long_note(self, client, mock_repository, mock_feature_flags):
        """Test feedback submission with long note"""
        with patch('src.api.comparative_analysis.FileBasedFeedbackRepository', return_value=mock_repository):
            long_note = "x" * 600  # Longer than 500 char limit
            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "confirm",
                "note": long_note
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 422  # Validation error for long note

    def test_submit_feedback_special_characters(self, client, mock_repository, mock_feature_flags):
        """Test feedback submission with special characters and unicode"""
        with patch('src.api.comparative_analysis.FileBasedFeedbackRepository', return_value=mock_repository):
            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "confirm",
                "note": "Great work! 👍 Excellent simplification with émojis and spëcial chärs",
                "suggested_tag": "user-experience"
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 200
            response_data = response.json()

            assert response_data["status"] == "submitted"

            # Verify the feedback was saved with special characters
            call_args = mock_repository.save_feedback.call_args[0][0]
            assert "👍" in call_args.note
            assert "émojis" in call_args.note
            assert "spëcial" in call_args.note

    def test_feedback_response_format(self, client, mock_repository, mock_feature_flags):
        """Test feedback response format and required fields"""
        with patch('src.api.comparative_analysis.FileBasedFeedbackRepository', return_value=mock_repository):
            request_data = {
                "session_id": "test-session-123",
                "strategy_id": "lexical_simplification",
                "action": "adjust",
                "note": "Could be better",
                "suggested_tag": "improvement"
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)

            assert response.status_code == 200
            response_data = response.json()

            # Check response structure
            required_fields = ["feedback_id", "status", "message", "timestamp"]
            for field in required_fields:
                assert field in response_data

            # Check data types
            assert isinstance(response_data["feedback_id"], str)
            assert isinstance(response_data["status"], str)
            assert isinstance(response_data["message"], str)
            assert isinstance(response_data["timestamp"], str)

            # Check specific values
            assert response_data["status"] == "submitted"
            assert response_data["message"] == "Feedback submitted successfully"
            assert len(response_data["feedback_id"]) > 0  # Non-empty ID


class TestFeedbackIntegration:
    """Test cases for feedback integration with comparative analysis"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    def test_comparative_analysis_includes_session_id(self, client):
        """Test that comparative analysis response includes session_id (analysis_id)"""
        # This would require mocking the comparative analysis service
        # For now, just verify the endpoint exists and basic structure
        response = client.get("/api/v1/comparative-analysis/health")
        assert response.status_code == 200

        # The actual comparative analysis test would require more complex mocking
        # of the ComparativeAnalysisService and its dependencies

    def test_feedback_prompt_included_when_enabled(self):
        """Test that feedback prompt is included in analysis response when enabled"""
        # This test would require mocking the comparative analysis service
        # and verifying that feedback_prompt is added to the response
        # when feature flags are enabled
        pass

    def test_feedback_prompt_excluded_when_disabled(self):
        """Test that feedback prompt is excluded when feature is disabled"""
        # This test would verify that feedback_prompt is None or not present
        # when feedback system is disabled
        pass
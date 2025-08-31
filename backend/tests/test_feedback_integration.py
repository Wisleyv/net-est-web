"""
Integration tests for M6: Feedback Capture & Persistence System

Tests for end-to-end feedback workflow integrated with comparative analysis.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from src.models.feedback import FeedbackAction, FeedbackItem
from src.models.comparative_analysis import (
    ComparativeAnalysisRequest,
    ComparativeAnalysisResponse,
    SimplificationStrategy,
    SimplificationStrategyType
)
from src.repositories.feedback_repository import FileBasedFeedbackRepository
from src.api.comparative_analysis import router


class TestFeedbackIntegration:
    """Integration tests for feedback system with comparative analysis"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def client(self, temp_dir):
        """Create test client with temporary storage"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)

        # Override feature flags for testing
        with patch('src.api.comparative_analysis.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            mock_flags.flags = {
                "feedback_system": {
                    "enabled": True,
                    "collection_enabled": True,
                    "prompt_enabled": True,
                    "storage_path": str(temp_dir / "feedback"),
                    "max_file_size_mb": 10.0
                }
            }
            yield TestClient(app)

    @pytest.fixture
    def mock_analysis_service(self):
        """Mock comparative analysis service"""
        mock_service = AsyncMock()

        # Create mock response with strategies
        strategies = [
            SimplificationStrategy(
                name="lexical_simplification",
                type=SimplificationStrategyType.LEXICAL,
                description="Simplified vocabulary",
                impact="medium",
                confidence=0.85,
                examples=[{"original": "complex", "simplified": "simple"}]
            ),
            SimplificationStrategy(
                name="syntactic_simplification",
                type=SimplificationStrategyType.SYNTACTIC,
                description="Simplified sentence structure",
                impact="high",
                confidence=0.92,
                examples=[{"original": "long sentence", "simplified": "short sentence"}]
            )
        ]

        mock_response = ComparativeAnalysisResponse(
            analysis_id="test-analysis-123",
            timestamp="2025-01-01T12:00:00Z",
            source_text="Complex source text",
            target_text="Simple target text",
            source_length=100,
            target_length=80,
            compression_ratio=0.8,
            overall_score=85,
            overall_assessment="Good simplification",
            simplification_strategies=strategies,
            strategies_count=2,
            semantic_preservation=88.5,
            readability_improvement=15.2,
            processing_time=1.5,
            model_version="1.0.0"
        )

        mock_service.perform_comparative_analysis.return_value = mock_response
        return mock_service

    def test_complete_feedback_workflow(self, client, mock_analysis_service, temp_dir):
        """Test complete feedback workflow from analysis to feedback submission"""
        with patch('src.api.comparative_analysis.ComparativeAnalysisService', return_value=mock_analysis_service):
            # Step 1: Perform comparative analysis
            analysis_request = {
                "source_text": "This is a complex sentence with difficult vocabulary and intricate structure.",
                "target_text": "This is a simple sentence with easy words and clear structure."
            }

            analysis_response = client.post("/api/v1/comparative-analysis/", json=analysis_request)

            assert analysis_response.status_code == 200
            analysis_data = analysis_response.json()

            # Verify analysis response includes session_id
            assert "analysis_id" in analysis_data
            session_id = analysis_data["analysis_id"]

            # Verify feedback prompt is included when enabled
            assert "feedback_prompt" in analysis_data
            feedback_prompt = analysis_data["feedback_prompt"]
            assert feedback_prompt["enabled"] is True
            assert feedback_prompt["session_id"] == session_id
            assert len(feedback_prompt["strategies"]) > 0

            # Step 2: Submit feedback for the analysis
            feedback_request = {
                "session_id": session_id,
                "strategy_id": "lexical_simplification",
                "action": "confirm",
                "note": "Great lexical simplification!",
                "suggested_tag": "vocabulary"
            }

            feedback_response = client.post("/api/v1/comparative-analysis/feedback", json=feedback_request)

            assert feedback_response.status_code == 200
            feedback_data = feedback_response.json()

            assert feedback_data["status"] == "submitted"
            assert "feedback_id" in feedback_data
            feedback_id = feedback_data["feedback_id"]

            # Step 3: Verify feedback was persisted
            repository = FileBasedFeedbackRepository(storage_path=str(temp_dir / "feedback"))

            # Retrieve feedback by session
            session_feedback = repository.get_feedback_by_session(session_id)
            assert len(session_feedback) == 1

            feedback_item = session_feedback[0]
            assert feedback_item.feedback_id == feedback_id
            assert feedback_item.session_id == session_id
            assert feedback_item.strategy_id == "lexical_simplification"
            assert feedback_item.action.value == "confirm"
            assert feedback_item.note == "Great lexical simplification!"
            assert feedback_item.suggested_tag == "vocabulary"

    def test_multiple_feedback_submissions(self, client, mock_analysis_service, temp_dir):
        """Test submitting multiple feedback items for same analysis"""
        with patch('src.api.comparative_analysis.ComparativeAnalysisService', return_value=mock_analysis_service):
            # Perform analysis
            analysis_request = {
                "source_text": "Complex text for analysis",
                "target_text": "Simple text result"
            }

            analysis_response = client.post("/api/v1/comparative-analysis/", json=analysis_request)
            session_id = analysis_response.json()["analysis_id"]

            # Submit feedback for multiple strategies
            feedback_requests = [
                {
                    "session_id": session_id,
                    "strategy_id": "lexical_simplification",
                    "action": "confirm",
                    "note": "Good vocabulary choices"
                },
                {
                    "session_id": session_id,
                    "strategy_id": "syntactic_simplification",
                    "action": "adjust",
                    "note": "Could be clearer",
                    "suggested_tag": "structure"
                }
            ]

            feedback_ids = []
            for request_data in feedback_requests:
                response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)
                assert response.status_code == 200
                feedback_ids.append(response.json()["feedback_id"])

            # Verify all feedback was saved
            repository = FileBasedFeedbackRepository(storage_path=str(temp_dir / "feedback"))
            session_feedback = repository.get_feedback_by_session(session_id)

            assert len(session_feedback) == 2

            # Verify feedback details
            lexical_feedback = next(f for f in session_feedback if f.strategy_id == "lexical_simplification")
            syntactic_feedback = next(f for f in session_feedback if f.strategy_id == "syntactic_simplification")

            assert lexical_feedback.action.value == "confirm"
            assert lexical_feedback.note == "Good vocabulary choices"

            assert syntactic_feedback.action.value == "adjust"
            assert syntactic_feedback.note == "Could be clearer"
            assert syntactic_feedback.suggested_tag == "structure"

    def test_feedback_with_disabled_prompt(self, client, mock_analysis_service):
        """Test analysis response when feedback prompt is disabled"""
        with patch('src.api.comparative_analysis.feature_flags') as mock_flags:
            mock_flags.is_enabled.side_effect = lambda key: {
                "feedback_system.enabled": True,
                "feedback_system.collection_enabled": True,
                "feedback_system.prompt_enabled": False  # Disabled
            }.get(key, False)

            with patch('src.api.comparative_analysis.ComparativeAnalysisService', return_value=mock_analysis_service):
                analysis_request = {
                    "source_text": "Complex text",
                    "target_text": "Simple text"
                }

                response = client.post("/api/v1/comparative-analysis/", json=analysis_request)

                assert response.status_code == 200
                data = response.json()

                # Feedback prompt should not be included or should be disabled
                if "feedback_prompt" in data:
                    assert data["feedback_prompt"]["enabled"] is False

    def test_feedback_persistence_across_restarts(self, temp_dir):
        """Test that feedback persists across application restarts"""
        # First "application run"
        repository1 = FileBasedFeedbackRepository(storage_path=str(temp_dir / "feedback"))

        feedback1 = FeedbackItem(
            session_id="persistent-session",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM,
            note="Persistent feedback"
        )

        # Save feedback
        success1 = repository1.save_feedback(feedback1)
        assert success1 is True

        # Simulate application restart - create new repository instance
        repository2 = FileBasedFeedbackRepository(storage_path=str(temp_dir / "feedback"))

        # Retrieve feedback with new instance
        feedback_list = repository2.get_feedback_by_session("persistent-session")

        assert len(feedback_list) == 1
        assert feedback_list[0].session_id == "persistent-session"
        assert feedback_list[0].note == "Persistent feedback"

    def test_feedback_data_integrity(self, client, mock_analysis_service, temp_dir):
        """Test data integrity of feedback storage and retrieval"""
        with patch('src.api.comparative_analysis.ComparativeAnalysisService', return_value=mock_analysis_service):
            # Perform analysis
            analysis_response = client.post("/api/v1/comparative-analysis/", json={
                "source_text": "Complex source",
                "target_text": "Simple target"
            })
            session_id = analysis_response.json()["analysis_id"]

            # Submit feedback with special characters and metadata
            special_feedback = {
                "session_id": session_id,
                "strategy_id": "special_chars_test",
                "action": "confirm",
                "note": "Feedback with spëcial chärs, émojis 👍, and unicode: αβγδε",
                "suggested_tag": "test-tag-123",
                "metadata": {
                    "user_id": "user-456",
                    "browser": "test-browser",
                    "timestamp": "2025-01-01T12:00:00Z",
                    "nested": {"key": "value", "number": 42}
                }
            }

            response = client.post("/api/v1/comparative-analysis/feedback", json=special_feedback)
            assert response.status_code == 200

            # Verify data integrity
            repository = FileBasedFeedbackRepository(storage_path=str(temp_dir / "feedback"))
            feedback_list = repository.get_feedback_by_session(session_id)

            assert len(feedback_list) == 1
            feedback = feedback_list[0]

            assert feedback.note == special_feedback["note"]
            assert feedback.suggested_tag == special_feedback["suggested_tag"]
            assert feedback.metadata == special_feedback["metadata"]

            # Verify unicode characters are preserved
            assert "spëcial" in feedback.note
            assert "émojis" in feedback.note
            assert "👍" in feedback.note
            assert "αβγδε" in feedback.note

    def test_concurrent_feedback_submissions(self, client, mock_analysis_service, temp_dir):
        """Test concurrent feedback submissions from multiple users"""
        import asyncio
        import aiohttp
        from concurrent.futures import ThreadPoolExecutor

        with patch('src.api.comparative_analysis.ComparativeAnalysisService', return_value=mock_analysis_service):
            # Perform analysis to get session_id
            analysis_response = client.post("/api/v1/comparative-analysis/", json={
                "source_text": "Concurrent test source",
                "target_text": "Concurrent test target"
            })
            session_id = analysis_response.json()["analysis_id"]

            # Submit multiple feedback items concurrently
            feedback_requests = []
            for i in range(10):
                request_data = {
                    "session_id": session_id,
                    "strategy_id": f"concurrent-strategy-{i}",
                    "action": "confirm" if i % 2 == 0 else "reject",
                    "note": f"Concurrent feedback #{i}",
                    "metadata": {"sequence": i}
                }
                feedback_requests.append(request_data)

            # Submit concurrently using threads
            results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for request_data in feedback_requests:
                    future = executor.submit(
                        lambda data: client.post("/api/v1/comparative-analysis/feedback", json=data),
                        request_data
                    )
                    futures.append(future)

                for future in futures:
                    results.append(future.result())

            # Verify all submissions succeeded
            assert len(results) == 10
            for response in results:
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "submitted"
                assert "feedback_id" in data

            # Verify all feedback was persisted
            repository = FileBasedFeedbackRepository(storage_path=str(temp_dir / "feedback"))
            session_feedback = repository.get_feedback_by_session(session_id)

            assert len(session_feedback) == 10

            # Verify no data corruption occurred
            notes = [f.note for f in session_feedback]
            expected_notes = [f"Concurrent feedback #{i}" for i in range(10)]
            assert set(notes) == set(expected_notes)

    def test_feedback_performance_under_load(self, client, mock_analysis_service, temp_dir):
        """Test feedback system performance with high volume"""
        import time

        with patch('src.api.comparative_analysis.ComparativeAnalysisService', return_value=mock_analysis_service):
            # Perform analysis
            analysis_response = client.post("/api/v1/comparative-analysis/", json={
                "source_text": "Performance test source",
                "target_text": "Performance test target"
            })
            session_id = analysis_response.json()["analysis_id"]

            # Submit high volume of feedback
            start_time = time.time()
            feedback_count = 100

            for i in range(feedback_count):
                request_data = {
                    "session_id": session_id,
                    "strategy_id": f"perf-strategy-{i % 5}",  # 5 different strategies
                    "action": ["confirm", "reject", "adjust"][i % 3],
                    "note": f"Performance test feedback #{i}",
                    "metadata": {"batch": i // 10, "index": i}
                }

                response = client.post("/api/v1/comparative-analysis/feedback", json=request_data)
                assert response.status_code == 200

            end_time = time.time()
            total_time = end_time - start_time

            # Verify reasonable performance (should complete within reasonable time)
            # Note: This is a basic performance check - adjust threshold based on environment
            assert total_time < 30  # Should complete in less than 30 seconds

            # Verify all feedback was saved
            repository = FileBasedFeedbackRepository(storage_path=str(temp_dir / "feedback"))
            session_feedback = repository.get_feedback_by_session(session_id)

            assert len(session_feedback) == feedback_count

            # Verify data integrity
            feedback_ids = set(f.feedback_id for f in session_feedback)
            assert len(feedback_ids) == feedback_count  # All IDs should be unique
"""
Persistence tests for M6: Feedback Capture & Persistence System

Tests for data persistence, retrieval, and integrity validation.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

from src.models.feedback import FeedbackItem, FeedbackAction
from src.repositories.feedback_repository import FileBasedFeedbackRepository


class TestFeedbackPersistence:
    """Test cases for feedback data persistence and retrieval"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def repository(self, temp_dir):
        """Create repository instance with temporary directory"""
        return FileBasedFeedbackRepository(
            storage_path=str(temp_dir),
            max_file_size_mb=1.0  # Small for testing rotation
        )

    def test_feedback_file_creation(self, repository, temp_dir):
        """Test that feedback files are created correctly"""
        feedback = FeedbackItem(
            session_id="test-session",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM
        )

        success = repository.save_feedback(feedback)
        assert success is True

        # Check file was created
        files = list(temp_dir.glob("*.json"))
        assert len(files) == 1

        # Check file naming convention
        file_path = files[0]
        assert "feedback_" in file_path.name
        assert file_path.name.endswith(".json")

    def test_feedback_json_structure(self, repository, temp_dir):
        """Test that feedback is stored in correct JSON structure"""
        feedback = FeedbackItem(
            session_id="test-session-123",
            strategy_id="lexical_simplification",
            action=FeedbackAction.CONFIRM,
            note="Great work!",
            suggested_tag="vocabulary",
            metadata={"user_id": "user-456"}
        )

        success = repository.save_feedback(feedback)
        assert success is True

        # Read and verify JSON structure
        files = list(temp_dir.glob("*.json"))
        assert len(files) == 1

        with open(files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 1

        stored_feedback = data[0]
        assert stored_feedback["feedback_id"] == feedback.feedback_id
        assert stored_feedback["session_id"] == "test-session-123"
        assert stored_feedback["strategy_id"] == "lexical_simplification"
        assert stored_feedback["action"] == "confirm"
        assert stored_feedback["note"] == "Great work!"
        assert stored_feedback["suggested_tag"] == "vocabulary"
        assert stored_feedback["metadata"] == {"user_id": "user-456"}
        assert "timestamp" in stored_feedback

    def test_multiple_feedback_in_same_file(self, repository, temp_dir):
        """Test storing multiple feedback items in the same file"""
        feedback_items = []
        for i in range(3):
            feedback = FeedbackItem(
                session_id=f"session-{i}",
                strategy_id=f"strategy-{i}",
                action=FeedbackAction.CONFIRM,
                note=f"Note {i}"
            )
            feedback_items.append(feedback)
            success = repository.save_feedback(feedback)
            assert success is True

        # Check single file contains all feedback
        files = list(temp_dir.glob("*.json"))
        assert len(files) == 1

        with open(files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data) == 3

        # Verify all feedback items are present
        stored_ids = {item["feedback_id"] for item in data}
        expected_ids = {f.feedback_id for f in feedback_items}
        assert stored_ids == expected_ids

    def test_feedback_file_rotation(self, repository, temp_dir):
        """Test automatic file rotation when size limit is exceeded"""
        # Create feedback items that exceed file size limit
        large_note = "x" * 200000  # ~200KB per item

        feedback_items = []
        for i in range(6):  # Should exceed 1MB total
            feedback = FeedbackItem(
                session_id=f"session-{i}",
                strategy_id="large-test",
                action=FeedbackAction.CONFIRM,
                note=large_note
            )
            feedback_items.append(feedback)
            success = repository.save_feedback(feedback)
            assert success is True

        # Check that multiple files were created
        files = list(temp_dir.glob("*.json"))
        assert len(files) > 1

        # Verify all feedback can still be retrieved
        all_feedback = repository.get_all_feedback()
        assert len(all_feedback) == 6

        # Verify feedback IDs match
        stored_ids = {f.feedback_id for f in all_feedback}
        expected_ids = {f.feedback_id for f in feedback_items}
        assert stored_ids == expected_ids

    def test_feedback_timestamp_preservation(self, repository, temp_dir):
        """Test that feedback timestamps are preserved correctly"""
        fixed_timestamp = datetime(2025, 1, 15, 10, 30, 45)

        feedback = FeedbackItem(
            session_id="timestamp-test",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM
        )
        feedback.timestamp = fixed_timestamp

        success = repository.save_feedback(feedback)
        assert success is True

        # Retrieve and verify timestamp
        retrieved_feedback = repository.get_feedback_by_session("timestamp-test")
        assert len(retrieved_feedback) == 1

        stored_feedback = retrieved_feedback[0]
        assert stored_feedback.timestamp == fixed_timestamp

        # Also verify in raw JSON
        files = list(temp_dir.glob("*.json"))
        with open(files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data[0]["timestamp"] == fixed_timestamp.isoformat()

    def test_feedback_data_types_preservation(self, repository, temp_dir):
        """Test that all data types are preserved correctly"""
        complex_metadata = {
            "string": "text",
            "integer": 42,
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "list": [1, 2, "three"],
            "dict": {"nested": "value", "number": 123}
        }

        feedback = FeedbackItem(
            session_id="types-test",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM,
            note="Testing data types: émoji 👍 unicode αβγ",
            suggested_tag="test-tag-123",
            metadata=complex_metadata
        )

        success = repository.save_feedback(feedback)
        assert success is True

        # Retrieve and verify all data types
        retrieved_feedback = repository.get_feedback_by_session("types-test")
        assert len(retrieved_feedback) == 1

        stored_feedback = retrieved_feedback[0]
        assert stored_feedback.session_id == "types-test"
        assert stored_feedback.strategy_id == "test-strategy"
        assert stored_feedback.action == FeedbackAction.CONFIRM
        assert "émoji" in stored_feedback.note
        assert "👍" in stored_feedback.note
        assert "αβγ" in stored_feedback.note
        assert stored_feedback.suggested_tag == "test-tag-123"
        assert stored_feedback.metadata == complex_metadata

    def test_corrupted_file_handling(self, repository, temp_dir):
        """Test handling of corrupted JSON files"""
        # Create a corrupted JSON file
        bad_file = temp_dir / "feedback_2025-01-01.json"
        bad_file.write_text("{ invalid json content")

        # Try to retrieve feedback (should handle gracefully)
        feedback_list = repository.get_feedback_by_session("any-session")
        assert feedback_list == []  # Should return empty list, not crash

        # Should still be able to save new feedback
        feedback = FeedbackItem(
            session_id="recovery-test",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM
        )

        success = repository.save_feedback(feedback)
        assert success is True

        # Verify new feedback was saved despite corrupted file
        retrieved_feedback = repository.get_feedback_by_session("recovery-test")
        assert len(retrieved_feedback) == 1
        assert retrieved_feedback[0].session_id == "recovery-test"

    def test_empty_file_handling(self, repository, temp_dir):
        """Test handling of empty files"""
        # Create an empty file
        empty_file = temp_dir / "feedback_2025-01-01.json"
        empty_file.write_text("")

        # Should handle gracefully
        feedback_list = repository.get_feedback_by_session("any-session")
        assert feedback_list == []

        # Should still be able to save feedback
        feedback = FeedbackItem(
            session_id="empty-file-test",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM
        )

        success = repository.save_feedback(feedback)
        assert success is True

    def test_file_permissions_and_access(self, repository, temp_dir):
        """Test file access permissions and error handling"""
        # Create feedback
        feedback = FeedbackItem(
            session_id="permissions-test",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM
        )

        success = repository.save_feedback(feedback)
        assert success is True

        # Verify file permissions allow reading
        files = list(temp_dir.glob("*.json"))
        assert len(files) == 1

        file_path = files[0]
        assert file_path.exists()
        assert file_path.is_file()

        # Should be able to read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data) == 1

    def test_concurrent_file_access_simulation(self, repository, temp_dir):
        """Test handling of concurrent file access scenarios"""
        import threading
        import time

        results = []
        errors = []

        def save_feedback_worker(session_id: str):
            """Worker function to save feedback"""
            try:
                feedback = FeedbackItem(
                    session_id=session_id,
                    strategy_id="concurrent-test",
                    action=FeedbackAction.CONFIRM,
                    note=f"Feedback from {session_id}"
                )
                success = repository.save_feedback(feedback)
                results.append((session_id, success))
            except Exception as e:
                errors.append((session_id, str(e)))

        # Start multiple threads saving feedback concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=save_feedback_worker, args=[f"session-{i}"])
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations succeeded
        assert len(results) == 5
        assert len(errors) == 0
        assert all(success for _, success in results)

        # Verify all feedback was saved
        all_feedback = repository.get_all_feedback()
        assert len(all_feedback) == 5

        # Verify no data corruption
        session_ids = {f.session_id for f in all_feedback}
        expected_sessions = {f"session-{i}" for i in range(5)}
        assert session_ids == expected_sessions

    def test_large_dataset_performance(self, repository, temp_dir):
        """Test performance with large feedback datasets"""
        import time

        # Create a large number of feedback items
        start_time = time.time()
        feedback_count = 1000

        for i in range(feedback_count):
            feedback = FeedbackItem(
                session_id=f"perf-session-{i % 10}",  # 10 different sessions
                strategy_id=f"perf-strategy-{i % 5}",  # 5 different strategies
                action=FeedbackAction.CONFIRM if i % 2 == 0 else FeedbackAction.REJECT,
                note=f"Performance test feedback #{i}",
                metadata={"index": i, "batch": i // 100}
            )
            success = repository.save_feedback(feedback)
            assert success is True

        save_time = time.time() - start_time

        # Verify reasonable save performance
        assert save_time < 60  # Should complete in less than 60 seconds

        # Test retrieval performance
        start_time = time.time()
        all_feedback = repository.get_all_feedback()
        retrieve_time = time.time() - start_time

        assert len(all_feedback) == feedback_count
        assert retrieve_time < 10  # Retrieval should be fast

        # Test summary generation performance
        start_time = time.time()
        summary = repository.get_feedback_summary()
        summary_time = time.time() - start_time

        assert summary.total_feedback == feedback_count
        assert summary_time < 5  # Summary generation should be reasonably fast

    def test_data_integrity_across_file_operations(self, repository, temp_dir):
        """Test data integrity across various file operations"""
        # Create initial feedback
        original_feedback = FeedbackItem(
            session_id="integrity-test",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM,
            note="Original feedback with special chars: émoji 👍 αβγδε",
            suggested_tag="integrity",
            metadata={"test": "value", "number": 42}
        )

        success = repository.save_feedback(original_feedback)
        assert success is True

        # Retrieve and verify
        feedback_list = repository.get_feedback_by_session("integrity-test")
        assert len(feedback_list) == 1
        retrieved = feedback_list[0]

        # Verify all fields match exactly
        assert retrieved.feedback_id == original_feedback.feedback_id
        assert retrieved.session_id == original_feedback.session_id
        assert retrieved.strategy_id == original_feedback.strategy_id
        assert retrieved.action == original_feedback.action
        assert retrieved.note == original_feedback.note
        assert retrieved.suggested_tag == original_feedback.suggested_tag
        assert retrieved.metadata == original_feedback.metadata
        assert retrieved.timestamp == original_feedback.timestamp

        # Verify special characters are preserved
        assert "émoji" in retrieved.note
        assert "👍" in retrieved.note
        assert "αβγδε" in retrieved.note

        # Add more feedback and verify again
        additional_feedback = FeedbackItem(
            session_id="integrity-test",
            strategy_id="another-strategy",
            action=FeedbackAction.REJECT,
            note="Additional feedback"
        )

        success = repository.save_feedback(additional_feedback)
        assert success is True

        # Verify both feedback items exist
        feedback_list = repository.get_feedback_by_session("integrity-test")
        assert len(feedback_list) == 2

        # Verify original feedback is still intact
        original_retrieved = next(f for f in feedback_list if f.feedback_id == original_feedback.feedback_id)
        assert original_retrieved.note == original_feedback.note
        assert original_retrieved.metadata == original_feedback.metadata
"""
Unit tests for M6: Feedback Repository

Tests for feedback data persistence, retrieval, and management operations.
"""

import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from src.models.feedback import FeedbackItem, FeedbackAction
from src.repositories.feedback_repository import FileBasedFeedbackRepository


class TestFileBasedFeedbackRepository:
    """Test cases for FileBasedFeedbackRepository"""

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

    @pytest.fixture
    def sample_feedback(self):
        """Create sample feedback item"""
        return FeedbackItem(
            session_id="test-session-123",
            strategy_id="lexical_simplification",
            action=FeedbackAction.CONFIRM,
            note="Great simplification!",
            suggested_tag="vocabulary",
            metadata={"user_agent": "test-client"}
        )

    @pytest.mark.asyncio
    async def test_save_feedback_success(self, repository, sample_feedback):
        """Test successful feedback saving"""
        success = await repository.save_feedback(sample_feedback)

        assert success is True
        assert sample_feedback.feedback_id is not None

        # Verify file was created
        files = list(repository.storage_path.glob("*.json"))
        assert len(files) == 1

    @pytest.mark.asyncio
    async def test_save_feedback_creates_directory(self, temp_dir):
        """Test that repository creates storage directory if it doesn't exist"""
        storage_path = temp_dir / "nested" / "feedback"
        repository = FileBasedFeedbackRepository(storage_path=str(storage_path))

        feedback = FeedbackItem(
            session_id="test-session",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM
        )

        success = await repository.save_feedback(feedback)
        assert success is True
        assert storage_path.exists()

    @pytest.mark.asyncio
    async def test_get_feedback_by_session(self, repository, sample_feedback):
        """Test retrieving feedback by session ID"""
        # Save feedback
        await repository.save_feedback(sample_feedback)

        # Add another feedback item for different session
        other_feedback = FeedbackItem(
            session_id="other-session",
            strategy_id="syntactic_simplification",
            action=FeedbackAction.REJECT,
            note="Not helpful"
        )
        await repository.save_feedback(other_feedback)

        # Retrieve feedback for specific session
        feedback_list = await repository.get_feedback_by_session(sample_feedback.session_id)

        assert len(feedback_list) == 1
        assert feedback_list[0].session_id == sample_feedback.session_id
        assert feedback_list[0].strategy_id == sample_feedback.strategy_id
        assert feedback_list[0].action == sample_feedback.action

    @pytest.mark.asyncio
    async def test_get_feedback_by_session_empty(self, repository):
        """Test retrieving feedback for non-existent session"""
        feedback_list = await repository.get_feedback_by_session("non-existent-session")
        assert feedback_list == []

    @pytest.mark.asyncio
    async def test_get_all_feedback(self, repository):
        """Test retrieving all feedback with limit"""
        # Create multiple feedback items
        feedback_items = []
        for i in range(5):
            feedback = FeedbackItem(
                session_id=f"session-{i}",
                strategy_id=f"strategy-{i}",
                action=FeedbackAction.CONFIRM if i % 2 == 0 else FeedbackAction.REJECT
            )
            await repository.save_feedback(feedback)
            feedback_items.append(feedback)

        # Retrieve all feedback
        all_feedback = await repository.get_all_feedback()

        assert len(all_feedback) == 5
        # Should be sorted by timestamp (newest first)
        assert all_feedback[0].timestamp >= all_feedback[-1].timestamp

    @pytest.mark.asyncio
    async def test_get_all_feedback_with_limit(self, repository):
        """Test retrieving feedback with limit"""
        # Create multiple feedback items
        for i in range(10):
            feedback = FeedbackItem(
                session_id=f"session-{i}",
                strategy_id=f"strategy-{i}",
                action=FeedbackAction.CONFIRM
            )
            await repository.save_feedback(feedback)

        # Retrieve with limit
        limited_feedback = await repository.get_all_feedback(limit=3)
        assert len(limited_feedback) == 3

    @pytest.mark.asyncio
    async def test_get_feedback_summary(self, repository):
        """Test generating feedback summary"""
        # Create feedback items with different actions
        actions = [FeedbackAction.CONFIRM, FeedbackAction.REJECT, FeedbackAction.ADJUST]
        for i, action in enumerate(actions * 3):  # 9 total items
            feedback = FeedbackItem(
                session_id=f"session-{i % 3}",  # 3 sessions
                strategy_id=f"strategy-{i % 2}",  # 2 strategies
                action=action
            )
            await repository.save_feedback(feedback)

        # Get summary
        summary = await repository.get_feedback_summary(days_back=30)

        assert summary.total_feedback == 9
        assert summary.confirm_count == 3
        assert summary.reject_count == 3
        assert summary.adjust_count == 3
        assert summary.average_feedback_per_session == 3.0  # 9 items / 3 sessions
        assert len(summary.strategy_feedback_counts) == 2
        assert summary.most_feedback_strategy in ["strategy-0", "strategy-1"]

    @pytest.mark.asyncio
    async def test_get_feedback_summary_empty(self, repository):
        """Test feedback summary with no data"""
        summary = await repository.get_feedback_summary()

        assert summary.total_feedback == 0
        assert summary.confirm_count == 0
        assert summary.reject_count == 0
        assert summary.adjust_count == 0
        assert summary.average_feedback_per_session == 0.0

    @pytest.mark.asyncio
    async def test_file_rotation(self, repository):
        """Test automatic file rotation when size limit is reached"""
        # Create large feedback items to trigger rotation
        large_note = "x" * 100000  # 100KB note

        feedback_items = []
        for i in range(15):  # Should exceed 1MB limit
            feedback = FeedbackItem(
                session_id=f"session-{i}",
                strategy_id="large-strategy",
                action=FeedbackAction.CONFIRM,
                note=large_note
            )
            feedback_items.append(feedback)
            success = await repository.save_feedback(feedback)
            assert success is True

        # Check that multiple files were created
        files = list(repository.storage_path.glob("*.json"))
        assert len(files) > 1

        # Debug: Print file information
        print(f"Found {len(files)} files:")
        for file_path in files:
            print(f"  {file_path.name}")

        # Verify all feedback can still be retrieved
        all_feedback = await repository.get_all_feedback()

        # Debug: Print feedback count
        print(f"Retrieved {len(all_feedback)} feedback items")

        # Check that we have all expected feedback items
        expected_session_ids = {f"session-{i}" for i in range(15)}
        actual_session_ids = {f.session_id for f in all_feedback}

        print(f"Expected sessions: {expected_session_ids}")
        print(f"Actual sessions: {actual_session_ids}")

        assert expected_session_ids == actual_session_ids
        assert len(all_feedback) == 15

    @pytest.mark.asyncio
    async def test_cleanup_old_feedback(self, repository):
        """Test cleanup of old feedback"""
        # Create feedback with different timestamps
        now = datetime.now()

        # Recent feedback (should be kept)
        recent_feedback = FeedbackItem(
            session_id="recent-session",
            strategy_id="recent-strategy",
            action=FeedbackAction.CONFIRM
        )
        await repository.save_feedback(recent_feedback)

        # Old feedback (should be deleted) - mock timestamp
        old_feedback = FeedbackItem(
            session_id="old-session",
            strategy_id="old-strategy",
            action=FeedbackAction.REJECT
        )
        # Manually set old timestamp
        old_feedback.timestamp = now - timedelta(days=100)
        await repository.save_feedback(old_feedback)

        # Cleanup old feedback (90 days retention)
        deleted_count = await repository.cleanup_old_feedback(days_to_keep=90)

        assert deleted_count == 1

        # Verify only recent feedback remains
        all_feedback = await repository.get_all_feedback()
        assert len(all_feedback) == 1
        assert all_feedback[0].session_id == "recent-session"

    @pytest.mark.asyncio
    async def test_thread_safety(self, repository):
        """Test thread-safe operations"""
        import asyncio
        import threading

        results = []
        errors = []

        async def save_feedback_async(session_id: str):
            """Async function to save feedback"""
            try:
                feedback = FeedbackItem(
                    session_id=session_id,
                    strategy_id="thread-test",
                    action=FeedbackAction.CONFIRM
                )
                success = await repository.save_feedback(feedback)
                results.append(success)
            except Exception as e:
                errors.append(e)

        # Run multiple concurrent saves
        tasks = []
        for i in range(10):
            task = save_feedback_async(f"concurrent-session-{i}")
            tasks.append(task)

        await asyncio.gather(*tasks)

        # Verify all saves succeeded
        assert len(results) == 10
        assert all(results)
        assert len(errors) == 0

        # Verify all feedback was saved
        all_feedback = await repository.get_all_feedback()
        assert len(all_feedback) == 10

    @pytest.mark.asyncio
    async def test_atomic_write_rollback(self, repository, sample_feedback):
        """Test that failed writes don't corrupt data"""
        # First, save valid feedback
        await repository.save_feedback(sample_feedback)

        # Mock a write failure
        with patch.object(repository, '_atomic_write', side_effect=Exception("Write failed")):
            failed_feedback = FeedbackItem(
                session_id="fail-session",
                strategy_id="fail-strategy",
                action=FeedbackAction.REJECT
            )

            success = await repository.save_feedback(failed_feedback)
            assert success is False

        # Verify original feedback is still intact
        all_feedback = await repository.get_all_feedback()
        assert len(all_feedback) == 1
        assert all_feedback[0].session_id == sample_feedback.session_id

    @pytest.mark.asyncio
    async def test_malformed_json_handling(self, repository, temp_dir):
        """Test handling of malformed JSON files"""
        # Create a malformed JSON file
        bad_file = temp_dir / "feedback_2025-01-01.json"
        bad_file.write_text("{ invalid json content")

        # Try to retrieve feedback (should handle gracefully)
        feedback_list = await repository.get_feedback_by_session("any-session")

        # Should return empty list instead of crashing
        assert feedback_list == []

        # Should still be able to save new feedback
        feedback = FeedbackItem(
            session_id="test-session",
            strategy_id="test-strategy",
            action=FeedbackAction.CONFIRM
        )
        success = await repository.save_feedback(feedback)
        assert success is True
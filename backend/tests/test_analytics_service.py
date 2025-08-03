"""
Tests for Analytics Service
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.models.analytics import (
    AnalysisRecord,
    AnalysisType,
    FeedbackItem,
    SessionAnalytics,
    SystemMetrics,
    UserSession,
)
from src.services.analytics_service import AnalyticsService


class TestAnalyticsService:
    """Test analytics service functionality"""

    @pytest.fixture
    def analytics_service(self):
        """Create a fresh analytics service for each test"""
        return AnalyticsService()

    @pytest.fixture  
    def sample_session_id(self, analytics_service):
        """Create a sample session"""
        return analytics_service.create_session(
            user_agent="Mozilla/5.0 Test Browser",
            referrer="https://test.com"
        )

    def test_create_session(self, analytics_service):
        """Test session creation"""
        session_id = analytics_service.create_session(
            user_agent="Test Browser",
            referrer="https://example.com"
        )
        
        assert session_id is not None
        assert session_id in analytics_service.sessions
        assert session_id in analytics_service.user_sessions
        
        # Check session data
        session = analytics_service.sessions[session_id]
        assert session.session_id == session_id
        assert session.total_analyses == 0
        
        user_session = analytics_service.user_sessions[session_id]
        assert user_session.session_id == session_id
        assert user_session.user_agent == "Test Browser"
        assert user_session.referrer == "https://example.com"

    def test_record_analysis(self, analytics_service, sample_session_id):
        """Test recording analysis operations"""
        analysis_record = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            analysis_type=AnalysisType.SEMANTIC_ALIGNMENT,
            source_text_length=100,
            target_text_length=95,
            processing_time_seconds=1.5,
            similarity_score=0.85,
            alignment_count=12
        )
        
        analytics_service.record_analysis(analysis_record)
        
        # Check session analytics updated
        session = analytics_service.sessions[sample_session_id]
        assert session.total_analyses == 1
        assert session.semantic_analyses == 1
        assert session.total_processing_time == 1.5
        assert session.average_processing_time == 1.5
        assert session.total_characters_processed == 195
        assert session.average_text_length == 195.0
        assert session.average_similarity_score == 0.85
        assert session.total_alignments_found == 12
        assert session.success_rate == 1.0
        assert session.error_count == 0
        
        # Check analysis stored
        analyses = analytics_service.analysis_records[sample_session_id]
        assert len(analyses) == 1
        assert analyses[0].analysis_id == analysis_record.analysis_id

    def test_record_multiple_analyses(self, analytics_service, sample_session_id):
        """Test recording multiple analyses updates averages correctly"""
        # First analysis
        analysis1 = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            analysis_type=AnalysisType.SEMANTIC_ALIGNMENT,
            source_text_length=100,
            target_text_length=90,
            processing_time_seconds=1.0,
            similarity_score=0.8,
            alignment_count=10
        )
        
        # Second analysis  
        analysis2 = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            analysis_type=AnalysisType.TEXT_INPUT,
            source_text_length=200,
            target_text_length=180,
            processing_time_seconds=2.0,
            error_occurred=True,
            error_message="Test error"
        )
        
        analytics_service.record_analysis(analysis1)
        analytics_service.record_analysis(analysis2)
        
        session = analytics_service.sessions[sample_session_id]
        assert session.total_analyses == 2
        assert session.semantic_analyses == 1
        assert session.total_processing_time == 3.0
        assert session.average_processing_time == 1.5
        assert session.total_characters_processed == 570  # 190 + 380
        assert session.average_text_length == 285.0
        assert session.average_similarity_score == 0.8  # Only from semantic analysis
        assert session.error_count == 1
        assert session.success_rate == 0.5
        
        # Check analysis type counts
        assert session.analysis_type_counts["semantic_alignment"] == 1
        assert session.analysis_type_counts["text_input"] == 1

    def test_add_feedback(self, analytics_service, sample_session_id):
        """Test adding user feedback"""
        analysis_id = str(uuid4())
        
        feedback = FeedbackItem(
            analysis_id=analysis_id,
            session_id=sample_session_id,
            feedback_type="rating",
            rating=4,
            expected_result="Expected output",
            actual_result="Actual output",
            comment="Good but could be better",
            is_helpful=True
        )
        
        analytics_service.add_feedback(feedback)
        
        # Check feedback stored
        feedback_list = analytics_service.feedback_items[sample_session_id]
        assert len(feedback_list) == 1
        assert feedback_list[0].analysis_id == analysis_id
        assert feedback_list[0].rating == 4
        
        # Check user session updated
        user_session = analytics_service.user_sessions[sample_session_id]
        assert user_session.feedback_provided == 1

    def test_get_session_analytics(self, analytics_service, sample_session_id):
        """Test retrieving session analytics"""
        # Add some analysis data
        analysis = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            analysis_type=AnalysisType.SEMANTIC_ALIGNMENT,
            source_text_length=100,
            target_text_length=95,
            processing_time_seconds=1.5,
            similarity_score=0.85
        )
        analytics_service.record_analysis(analysis)
        
        # Get analytics
        session_analytics = analytics_service.get_session_analytics(sample_session_id)
        
        assert session_analytics is not None
        assert session_analytics.session_id == sample_session_id
        assert session_analytics.total_analyses == 1
        assert session_analytics.average_similarity_score == 0.85

    def test_get_session_analytics_nonexistent(self, analytics_service):
        """Test retrieving analytics for nonexistent session"""
        result = analytics_service.get_session_analytics("nonexistent")
        assert result is None

    def test_get_system_metrics(self, analytics_service, sample_session_id):
        """Test system metrics generation"""
        # Add some data
        analysis = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            analysis_type=AnalysisType.SEMANTIC_ALIGNMENT,
            source_text_length=100,
            target_text_length=95,
            processing_time_seconds=1.5
        )
        analytics_service.record_analysis(analysis)
        
        metrics = analytics_service.get_system_metrics()
        
        assert isinstance(metrics, SystemMetrics)
        assert metrics.total_sessions >= 1
        assert metrics.total_analyses_today >= 1
        assert metrics.total_analyses_all_time >= 1
        assert metrics.average_response_time >= 0

    def test_export_analytics(self, analytics_service, sample_session_id):
        """Test analytics export functionality"""
        # Add some data
        analysis = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            analysis_type=AnalysisType.SEMANTIC_ALIGNMENT,
            source_text_length=100,
            target_text_length=95,
            processing_time_seconds=1.5
        )
        analytics_service.record_analysis(analysis)
        
        # Export all data
        export = analytics_service.export_analytics()
        
        assert export.session_count >= 1
        assert export.analysis_count >= 1
        assert len(export.sessions) >= 1
        assert export.system_metrics is not None
        
        # Export specific session
        specific_export = analytics_service.export_analytics([sample_session_id])
        assert specific_export.session_count == 1
        assert specific_export.sessions[0].session_id == sample_session_id

    def test_clear_session_data(self, analytics_service, sample_session_id):
        """Test clearing session data"""
        # Add some data
        analysis = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            analysis_type=AnalysisType.SEMANTIC_ALIGNMENT,
            source_text_length=100,
            target_text_length=95,
            processing_time_seconds=1.5
        )
        analytics_service.record_analysis(analysis)
        
        feedback = FeedbackItem(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            feedback_type="rating",
            rating=5,
            expected_result="Test",
            actual_result="Test"
        )
        analytics_service.add_feedback(feedback)
        
        # Verify data exists
        assert sample_session_id in analytics_service.sessions
        assert sample_session_id in analytics_service.user_sessions
        assert sample_session_id in analytics_service.analysis_records
        assert sample_session_id in analytics_service.feedback_items
        
        # Clear data
        cleared = analytics_service.clear_session_data(sample_session_id)
        assert cleared is True
        
        # Verify data cleared
        assert sample_session_id not in analytics_service.sessions
        assert sample_session_id not in analytics_service.user_sessions
        assert sample_session_id not in analytics_service.analysis_records
        assert sample_session_id not in analytics_service.feedback_items

    def test_session_timeout_cleanup(self, analytics_service):
        """Test automatic cleanup of expired sessions"""
        # Create session and manually set old timestamp
        session_id = analytics_service.create_session()
        old_time = datetime.now() - timedelta(hours=3)  # Older than timeout
        
        analytics_service.sessions[session_id].last_activity = old_time
        
        # Trigger cleanup by calling a method that performs cleanup
        analytics_service.get_system_metrics()
        
        # Session should be cleaned up
        assert session_id not in analytics_service.sessions

    def test_daily_counter_reset(self, analytics_service):
        """Test daily analysis counter reset"""
        # Set old date
        from datetime import date
        analytics_service.last_reset_date = date.today() - timedelta(days=1)
        analytics_service.daily_analyses_count = 100
        
        # Trigger counter update
        analytics_service._update_daily_counter()
        
        # Counter should reset
        assert analytics_service.daily_analyses_count == 0
        assert analytics_service.last_reset_date == date.today()

    def test_get_analytics_summary(self, analytics_service, sample_session_id):
        """Test analytics summary generation"""
        # Add some data
        analysis = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=sample_session_id,
            analysis_type=AnalysisType.SEMANTIC_ALIGNMENT,
            source_text_length=100,
            target_text_length=95,
            processing_time_seconds=1.5
        )
        analytics_service.record_analysis(analysis)
        
        summary = analytics_service.get_analytics_summary()
        
        assert "total_sessions" in summary
        assert "active_sessions" in summary
        assert "total_analyses" in summary
        assert "analyses_today" in summary
        assert "average_processing_time" in summary
        assert "system_uptime_hours" in summary
        
        assert summary["total_sessions"] >= 1
        assert summary["total_analyses"] >= 1

    def test_recent_analyses_limit(self, analytics_service, sample_session_id):
        """Test that recent analyses list is limited to 10 items"""
        # Add 15 analyses
        for i in range(15):
            analysis = AnalysisRecord(
                analysis_id=str(uuid4()),
                session_id=sample_session_id,
                analysis_type=AnalysisType.TEXT_INPUT,
                source_text_length=100,
                target_text_length=95,
                processing_time_seconds=1.0
            )
            analytics_service.record_analysis(analysis)
        
        session = analytics_service.sessions[sample_session_id]
        assert len(session.recent_analyses) == 10  # Should be limited to 10
        assert session.total_analyses == 15  # But total count should be correct

    def test_get_session_analyses_with_limit(self, analytics_service, sample_session_id):
        """Test getting session analyses with limit"""
        # Add 5 analyses
        for i in range(5):
            analysis = AnalysisRecord(
                analysis_id=f"analysis_{i}",
                session_id=sample_session_id,
                analysis_type=AnalysisType.TEXT_INPUT,
                source_text_length=100,
                target_text_length=95,
                processing_time_seconds=1.0
            )
            analytics_service.record_analysis(analysis)
        
        # Get limited results
        analyses = analytics_service.get_session_analyses(sample_session_id, limit=3)
        assert len(analyses) == 3
        
        # Get all results
        all_analyses = analytics_service.get_session_analyses(sample_session_id, limit=50)
        assert len(all_analyses) == 5

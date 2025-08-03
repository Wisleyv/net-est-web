"""
Analytics Service for NET-EST System
Provides session-based analytics without database dependency
"""

import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..models.analytics import (
    AnalysisRecord,
    AnalysisType,
    AnalyticsExport,
    FeedbackItem,
    SessionAnalytics,
    SystemMetrics,
    UserSession,
)


logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for managing analytics and metrics without database"""

    def __init__(self):
        # In-memory storage for current session
        self.sessions: Dict[str, SessionAnalytics] = {}
        self.user_sessions: Dict[str, UserSession] = {}
        self.analysis_records: Dict[str, List[AnalysisRecord]] = defaultdict(list)
        self.feedback_items: Dict[str, List[FeedbackItem]] = defaultdict(list)
        
        # System metrics
        self.system_start_time = time.time()
        self.total_analyses_count = 0
        self.daily_analyses_count = 0
        self.last_reset_date = datetime.now().date()
        
        # Session management
        self.session_timeout = timedelta(hours=2)  # Sessions expire after 2 hours
        
        logger.info("AnalyticsService initialized")

    def create_session(self, user_agent: Optional[str] = None, 
                      referrer: Optional[str] = None) -> str:
        """Create a new user session"""
        session_id = str(uuid4())
        
        # Create user session
        user_session = UserSession(
            session_id=session_id,
            user_agent=user_agent,
            referrer=referrer
        )
        self.user_sessions[session_id] = user_session
        
        # Create analytics session
        analytics_session = SessionAnalytics(
            session_id=session_id,
            start_time=datetime.now(),
            last_activity=datetime.now()
        )
        self.sessions[session_id] = analytics_session
        
        logger.info(f"Created new session: {session_id}")
        return session_id

    def record_analysis(self, analysis_record: AnalysisRecord) -> None:
        """Record an analysis operation"""
        session_id = analysis_record.session_id
        
        # Update daily counter
        self._update_daily_counter()
        self.total_analyses_count += 1
        self.daily_analyses_count += 1
        
        # Store analysis record
        self.analysis_records[session_id].append(analysis_record)
        
        # Update session analytics
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_activity = datetime.now()
            session.total_analyses += 1
            
            # Update performance metrics
            session.total_processing_time += analysis_record.processing_time_seconds
            session.average_processing_time = (
                session.total_processing_time / session.total_analyses
            )
            
            # Update content metrics
            text_length = analysis_record.source_text_length + analysis_record.target_text_length
            session.total_characters_processed += text_length
            session.average_text_length = (
                session.total_characters_processed / session.total_analyses
            )
            
            # Update semantic alignment metrics
            if analysis_record.analysis_type == AnalysisType.SEMANTIC_ALIGNMENT:
                session.semantic_analyses += 1
                if analysis_record.similarity_score is not None:
                    if session.average_similarity_score is None:
                        session.average_similarity_score = analysis_record.similarity_score
                    else:
                        # Update running average
                        current_total = session.average_similarity_score * (session.semantic_analyses - 1)
                        session.average_similarity_score = (
                            current_total + analysis_record.similarity_score
                        ) / session.semantic_analyses
                
                if analysis_record.alignment_count is not None:
                    session.total_alignments_found += analysis_record.alignment_count
            
            # Update error tracking
            if analysis_record.error_occurred:
                session.error_count += 1
                session.success_rate = (session.total_analyses - session.error_count) / session.total_analyses
            
            # Update analysis type counts
            analysis_type_str = analysis_record.analysis_type.value
            if analysis_type_str not in session.analysis_type_counts:
                session.analysis_type_counts[analysis_type_str] = 0
            session.analysis_type_counts[analysis_type_str] += 1
            
            # Add to recent analyses (keep only last 10)
            session.recent_analyses.append(analysis_record)
            if len(session.recent_analyses) > 10:
                session.recent_analyses = session.recent_analyses[-10:]
        
        # Update user session
        if session_id in self.user_sessions:
            user_session = self.user_sessions[session_id]
            user_session.last_seen_at = datetime.now()
            user_session.analyses_performed += 1
        
        logger.info(f"Recorded analysis: {analysis_record.analysis_id} for session {session_id}")

    def add_feedback(self, feedback: FeedbackItem) -> None:
        """Add user feedback"""
        session_id = feedback.session_id
        self.feedback_items[session_id].append(feedback)
        
        # Update user session feedback count
        if session_id in self.user_sessions:
            self.user_sessions[session_id].feedback_provided += 1
        
        logger.info(f"Added feedback for analysis {feedback.analysis_id}")

    def get_session_analytics(self, session_id: str) -> Optional[SessionAnalytics]:
        """Get analytics for a specific session"""
        self._cleanup_expired_sessions()
        return self.sessions.get(session_id)

    def get_session_feedback(self, session_id: str) -> List[FeedbackItem]:
        """Get feedback for a specific session"""
        return self.feedback_items.get(session_id, [])

    def get_session_analyses(self, session_id: str, limit: int = 50) -> List[AnalysisRecord]:
        """Get analysis records for a specific session"""
        analyses = self.analysis_records.get(session_id, [])
        return analyses[-limit:] if len(analyses) > limit else analyses

    def get_system_metrics(self) -> SystemMetrics:
        """Get system-wide metrics"""
        self._cleanup_expired_sessions()
        self._update_daily_counter()
        
        # Calculate active sessions
        active_sessions = len([s for s in self.sessions.values() 
                             if datetime.now() - s.last_activity < self.session_timeout])
        
        # Calculate average response time from recent analyses  
        recent_analyses = []
        for analyses in self.analysis_records.values():
            recent_analyses.extend(analyses[-10:])  # Last 10 per session
        
        avg_response_time = 0.0
        if recent_analyses:
            avg_response_time = sum(a.processing_time_seconds for a in recent_analyses) / len(recent_analyses)
        
        # Calculate error rate (last 24 hours)
        error_rate = 0.0
        recent_errors = 0
        recent_total = 0
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for analyses in self.analysis_records.values():
            for analysis in analyses:
                if analysis.timestamp >= cutoff_time:
                    recent_total += 1
                    if analysis.error_occurred:
                        recent_errors += 1
        
        if recent_total > 0:
            error_rate = recent_errors / recent_total
        
        # Popular analysis types
        popular_types = defaultdict(int)
        for session in self.sessions.values():
            for analysis_type, count in session.analysis_type_counts.items():
                popular_types[analysis_type] += count
        
        return SystemMetrics(
            total_sessions=len(self.sessions),
            active_sessions=active_sessions,
            total_analyses_today=self.daily_analyses_count,
            total_analyses_all_time=self.total_analyses_count,
            average_response_time=avg_response_time,
            system_uptime_seconds=time.time() - self.system_start_time,
            error_rate_24h=error_rate,
            popular_analysis_types=dict(popular_types)
        )

    def export_analytics(self, session_ids: Optional[List[str]] = None) -> AnalyticsExport:
        """Export analytics data for analysis or backup"""
        self._cleanup_expired_sessions()
        
        # Determine which sessions to export
        if session_ids is None:
            sessions_to_export = list(self.sessions.values())
        else:
            sessions_to_export = [self.sessions[sid] for sid in session_ids if sid in self.sessions]
        
        # Calculate date range
        if sessions_to_export:
            start_times = [s.start_time for s in sessions_to_export]
            date_range_start = min(start_times)
            date_range_end = max(s.last_activity for s in sessions_to_export)
        else:
            date_range_start = datetime.now()
            date_range_end = datetime.now()
        
        export = AnalyticsExport(
            export_id=str(uuid4()),
            session_count=len(sessions_to_export),
            analysis_count=sum(s.total_analyses for s in sessions_to_export),
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            sessions=sessions_to_export,
            system_metrics=self.get_system_metrics()
        )
        
        logger.info(f"Exported analytics: {export.export_id} with {export.session_count} sessions")
        return export

    def save_export_to_file(self, export: AnalyticsExport, file_path: Optional[Path] = None) -> Path:
        """Save analytics export to JSON file"""
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = Path(f"analytics_export_{timestamp}.json")
        
        export_data = export.model_dump(mode="json")
        
        # Convert datetime objects to ISO format for JSON serialization
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            return obj
        
        export_data = convert_datetime(export_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved analytics export to: {file_path}")
        return file_path

    def clear_session_data(self, session_id: str) -> bool:
        """Clear all data for a specific session"""
        cleared = False
        
        if session_id in self.sessions:
            del self.sessions[session_id]
            cleared = True
        
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
            cleared = True
        
        if session_id in self.analysis_records:
            del self.analysis_records[session_id]
            cleared = True
        
        if session_id in self.feedback_items:
            del self.feedback_items[session_id]
            cleared = True
        
        if cleared:
            logger.info(f"Cleared all data for session: {session_id}")
        
        return cleared

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions to free memory"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.clear_session_data(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def _update_daily_counter(self) -> None:
        """Reset daily counter if date has changed"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_analyses_count = 0
            self.last_reset_date = today
            logger.info("Reset daily analysis counter")

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get a quick summary of current analytics"""
        self._cleanup_expired_sessions()
        
        total_sessions = len(self.sessions)
        active_sessions = len([s for s in self.sessions.values() 
                             if datetime.now() - s.last_activity < timedelta(minutes=30)])
        
        total_analyses = sum(s.total_analyses for s in self.sessions.values())
        avg_processing_time = 0.0
        
        if self.sessions:
            avg_processing_time = sum(s.average_processing_time for s in self.sessions.values()) / len(self.sessions)
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_analyses": total_analyses,
            "analyses_today": self.daily_analyses_count,
            "average_processing_time": round(avg_processing_time, 3),
            "system_uptime_hours": round((time.time() - self.system_start_time) / 3600, 2),
            "memory_sessions_count": len(self.analysis_records),
            "last_cleanup": datetime.now().isoformat()
        }

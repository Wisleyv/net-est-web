"""
Analytics API endpoints for NET-EST System
Provides analytics and metrics functionality without database
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..models.analytics import (
    AnalysisRecord,
    AnalysisType,
    AnalyticsExport,
    FeedbackItem,
    SessionAnalytics,
    SystemMetrics,
)
from ..services.analytics_service import AnalyticsService


router = APIRouter(prefix="/analytics", tags=["analytics"])


# Pydantic models for API requests/responses
class CreateSessionRequest(BaseModel):
    """Request model for creating a new session"""
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


class CreateSessionResponse(BaseModel):
    """Response model for session creation"""
    session_id: str
    message: str


class RecordAnalysisRequest(BaseModel):
    """Request model for recording an analysis"""
    session_id: str
    analysis_type: AnalysisType
    source_text_length: int
    target_text_length: int
    processing_time_seconds: float
    similarity_score: Optional[float] = None
    alignment_count: Optional[int] = None
    confidence_level: Optional[str] = None
    error_occurred: bool = False
    error_message: Optional[str] = None


class AddFeedbackRequest(BaseModel):
    """Request model for adding user feedback"""
    session_id: str
    analysis_id: str
    feedback_type: str  # Changed from FeedbackType enum to string
    rating: Optional[int] = Field(None, ge=1, le=5)  # Make optional
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    comment: Optional[str] = None
    is_helpful: Optional[bool] = None


class ExportRequest(BaseModel):
    """Request model for analytics export"""
    session_ids: Optional[List[str]] = None
    include_system_metrics: bool = True


# Dependency for analytics service
def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance"""
    # In a real application, this would be injected or from a container
    # For now, we'll use a module-level instance
    if not hasattr(get_analytics_service, "_instance"):
        get_analytics_service._instance = AnalyticsService()
    return get_analytics_service._instance


@router.post("/session", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> CreateSessionResponse:
    """
    Create a new analytics session
    
    This endpoint creates a new session for tracking user analytics.
    A session ID is returned which should be used in subsequent requests.
    """
    try:
        session_id = analytics_service.create_session(
            user_agent=request.user_agent,
            referrer=request.referrer
        )
        
        return CreateSessionResponse(
            session_id=session_id,
            message="Session created successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.post("/analysis", status_code=201)
async def record_analysis(
    request: RecordAnalysisRequest,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, str]:
    """
    Record an analysis operation
    
    This endpoint records an analysis operation with its metrics.
    Used to track system usage and performance.
    """
    try:
        # Generate analysis ID
        from uuid import uuid4
        
        # Create analysis record
        analysis_record = AnalysisRecord(
            analysis_id=str(uuid4()),
            session_id=request.session_id,
            analysis_type=request.analysis_type,
            source_text_length=request.source_text_length,
            target_text_length=request.target_text_length,
            processing_time_seconds=request.processing_time_seconds,
            similarity_score=request.similarity_score,
            alignment_count=request.alignment_count,
            confidence_level=request.confidence_level,
            error_occurred=request.error_occurred,
            error_message=request.error_message
        )
        
        analytics_service.record_analysis(analysis_record)
        
        return {
            "message": "Analysis recorded successfully",
            "analysis_id": analysis_record.analysis_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record analysis: {str(e)}")


@router.post("/feedback", status_code=201)
async def add_feedback(
    request: AddFeedbackRequest,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, str]:
    """
    Add user feedback for an analysis
    
    This endpoint allows users to provide feedback on analysis results.
    Feedback is used for system improvement and quality assessment.
    """
    try:
        # Validate rating if provided
        if request.rating is not None and not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        feedback = FeedbackItem(
            session_id=request.session_id,
            analysis_id=request.analysis_id,
            feedback_type=request.feedback_type,
            rating=request.rating,
            expected_result=request.expected_result,
            actual_result=request.actual_result,
            comment=request.comment,
            is_helpful=request.is_helpful
        )
        
        analytics_service.add_feedback(feedback)
        
        return {"message": "Feedback added successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add feedback: {str(e)}")


@router.get("/session/{session_id}", response_model=SessionAnalytics)
async def get_session_analytics(
    session_id: str,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> SessionAnalytics:
    """
    Get analytics for a specific session
    
    Returns detailed analytics and metrics for the specified session.
    """
    session_analytics = analytics_service.get_session_analytics(session_id)
    
    if session_analytics is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return session_analytics


@router.get("/session/{session_id}/analyses", response_model=List[AnalysisRecord])
async def get_session_analyses(
    session_id: str,
    limit: int = 50,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> List[AnalysisRecord]:
    """
    Get analysis records for a specific session
    
    Returns a list of analysis records for the specified session.
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    analyses = analytics_service.get_session_analyses(session_id, limit)
    return analyses


@router.get("/session/{session_id}/feedback", response_model=List[FeedbackItem])
async def get_session_feedback(
    session_id: str,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> List[FeedbackItem]:
    """
    Get feedback for a specific session
    
    Returns all feedback items for the specified session.
    """
    feedback = analytics_service.get_session_feedback(session_id)
    return feedback


@router.get("/system/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> SystemMetrics:
    """
    Get system-wide metrics
    
    Returns comprehensive system metrics including performance,
    usage statistics, and operational data.
    """
    return analytics_service.get_system_metrics()


@router.get("/system/summary")
async def get_system_summary(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Get quick system summary
    
    Returns a condensed overview of system analytics.
    """
    return analytics_service.get_analytics_summary()


@router.post("/export", response_model=AnalyticsExport)
async def export_analytics(
    request: ExportRequest,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> AnalyticsExport:
    """
    Export analytics data
    
    Exports analytics data for specified sessions or all sessions.
    Useful for data analysis, reporting, and backup purposes.
    """
    try:
        export = analytics_service.export_analytics(request.session_ids)
        return export
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export analytics: {str(e)}")


@router.delete("/session/{session_id}", status_code=204)
async def clear_session_data(
    session_id: str,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> None:
    """
    Clear all data for a specific session
    
    Removes all analytics data associated with the specified session.
    This action cannot be undone.
    """
    cleared = analytics_service.clear_session_data(session_id)
    
    if not cleared:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/health")
async def analytics_health() -> Dict[str, str]:
    """
    Analytics service health check
    
    Simple health check endpoint for analytics service.
    """
    return {
        "status": "healthy",
        "service": "analytics",
        "timestamp": datetime.now().isoformat()
    }


# Optional endpoint for development/debugging
@router.get("/debug/sessions")
async def debug_sessions(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Debug endpoint showing all active sessions
    
    WARNING: This endpoint should be disabled in production.
    Returns information about all active sessions for debugging.
    """
    sessions = analytics_service.sessions
    return {
        "total_sessions": len(sessions),
        "session_ids": list(sessions.keys()),
        "sessions_summary": {
            sid: {
                "start_time": session.start_time.isoformat(),
                "total_analyses": session.total_analyses,
                "last_activity": session.last_activity.isoformat()
            }
            for sid, session in sessions.items()
        }
    }

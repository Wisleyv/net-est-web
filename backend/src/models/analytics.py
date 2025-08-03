"""
Analytics Models for NET-EST System
Handles analysis results and metrics without database dependency
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    """Types of analysis performed"""
    
    TEXT_INPUT = "text_input"
    SEMANTIC_ALIGNMENT = "semantic_alignment"
    FILE_PROCESSING = "file_processing"


class MetricType(str, Enum):
    """Types of metrics tracked"""
    
    PROCESSING_TIME = "processing_time"
    SIMILARITY_SCORE = "similarity_score"
    TEXT_LENGTH = "text_length"
    FILE_SIZE = "file_size"
    ALIGNMENT_COUNT = "alignment_count"
    CONFIDENCE_LEVEL = "confidence_level"


class AnalysisMetric(BaseModel):
    """Individual metric for an analysis"""
    
    type: MetricType
    value: float
    unit: str = Field(..., description="Unit of measurement (seconds, bytes, count, etc.)")
    timestamp: datetime = Field(default_factory=datetime.now)


class AnalysisRecord(BaseModel):
    """Record of a single analysis operation"""
    
    analysis_id: str = Field(..., description="Unique identifier for this analysis")
    session_id: str = Field(..., description="Session identifier")
    analysis_type: AnalysisType
    source_text_length: int = Field(0, description="Length of source text in characters")
    target_text_length: int = Field(0, description="Length of target text in characters")
    processing_time_seconds: float
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Analysis-specific results (all optional)
    similarity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    alignment_count: Optional[int] = Field(default=None, ge=0)
    confidence_level: Optional[str] = Field(default=None)
    
    # Additional metrics
    metrics: List[AnalysisMetric] = Field(default_factory=list)
    
    # User context (optional)
    user_agent: Optional[str] = None
    error_occurred: bool = False
    error_message: Optional[str] = None


class SessionAnalytics(BaseModel):
    """Analytics for a complete session"""
    
    session_id: str
    start_time: datetime
    last_activity: datetime
    total_analyses: int = 0
    
    # Performance metrics
    average_processing_time: float = 0.0
    total_processing_time: float = 0.0
    
    # Content metrics
    total_characters_processed: int = 0
    average_text_length: float = 0.0
    
    # Semantic alignment specific
    semantic_analyses: int = 0
    average_similarity_score: Optional[float] = None
    total_alignments_found: int = 0
    
    # Quality metrics
    success_rate: float = 1.0
    error_count: int = 0
    
    # Analysis type breakdown
    analysis_type_counts: Dict[str, int] = Field(default_factory=dict)
    
    # Recent analyses
    recent_analyses: List[AnalysisRecord] = Field(default_factory=list, description="Last 10 analyses")


class SystemMetrics(BaseModel):
    """System-wide metrics for monitoring"""
    
    total_sessions: int = 0
    active_sessions: int = 0
    total_analyses_today: int = 0
    total_analyses_all_time: int = 0
    
    # Performance indicators
    average_response_time: float = 0.0
    system_uptime_seconds: float = 0.0
    
    # Resource usage
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # Error tracking
    error_rate_24h: float = 0.0
    last_error_time: Optional[datetime] = None
    
    # Popular analysis types
    popular_analysis_types: Dict[str, int] = Field(default_factory=dict)
    
    # Generated timestamp
    generated_at: datetime = Field(default_factory=datetime.now)


class AnalyticsExport(BaseModel):
    """Export format for analytics data"""
    
    export_id: str
    session_count: int
    analysis_count: int
    date_range_start: datetime
    date_range_end: datetime
    
    # Aggregated data
    sessions: List[SessionAnalytics]
    system_metrics: SystemMetrics
    
    # Export metadata
    exported_at: datetime = Field(default_factory=datetime.now)
    format_version: str = "1.0"


class FeedbackItem(BaseModel):
    """User feedback on analysis results"""
    
    analysis_id: str
    session_id: str
    feedback_type: str = Field(..., description="Type of feedback (rating, correction, suggestion)")
    
    # Rating feedback (all optional)
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="1-5 star rating")
    
    # Correction feedback (all optional)
    expected_result: Optional[str] = Field(default=None, description="What the user expected")
    actual_result: Optional[str] = Field(default=None, description="What the system provided")
    
    # Textual feedback (optional)
    comment: Optional[str] = Field(default=None, max_length=1000)
    
    # Context (optional)
    is_helpful: Optional[bool] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.now)


class UserSession(BaseModel):
    """User session tracking"""
    
    session_id: str
    started_at: datetime = Field(default_factory=datetime.now)
    last_seen_at: datetime = Field(default_factory=datetime.now)
    
    # Session context
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    language: str = "pt-BR"
    
    # Activity tracking
    page_views: int = 0
    analyses_performed: int = 0
    feedback_provided: int = 0
    
    # Preferences (stored client-side, but tracked here)
    preferred_similarity_threshold: float = 0.7
    preferred_alignment_method: str = "cosine_similarity"
    
    # Status
    is_active: bool = True

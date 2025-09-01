"""
Feedback Models for M6: Feedback Capture & Persistence System

Models for capturing and managing user feedback on simplification strategies
to enable continuous improvement through human-in-loop learning.
"""

from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


class FeedbackAction(str, Enum):
    """Types of feedback actions users can provide"""
    CONFIRM = "confirm"
    REJECT = "reject"
    ADJUST = "adjust"


class FeedbackItem(BaseModel):
    """Individual feedback item from user interaction"""
    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique feedback identifier")
    session_id: str = Field(..., description="Analysis session ID for correlation")
    strategy_id: str = Field(..., description="Strategy identifier being rated")
    action: FeedbackAction = Field(..., description="User feedback action")
    note: Optional[str] = Field(None, description="Optional user note or comment")
    suggested_tag: Optional[str] = Field(None, description="Suggested improvement tag")
    timestamp: datetime = Field(default_factory=datetime.now, description="When feedback was provided")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional context metadata")

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class FeedbackSummary(BaseModel):
    """Aggregated feedback statistics for analysis and reporting"""
    total_feedback: int = Field(default=0, description="Total number of feedback items")
    confirm_count: int = Field(default=0, description="Number of confirm actions")
    reject_count: int = Field(default=0, description="Number of reject actions")
    adjust_count: int = Field(default=0, description="Number of adjust actions")
    strategy_feedback_counts: Dict[str, int] = Field(default_factory=dict, description="Feedback count per strategy")
    action_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution of feedback actions")
    average_feedback_per_session: float = Field(default=0.0, description="Average feedback items per session")
    most_feedback_strategy: Optional[str] = Field(None, description="Strategy with most feedback")
    recent_feedback_trend: List[Dict[str, Any]] = Field(default_factory=list, description="Recent feedback trends")
    generated_at: datetime = Field(default_factory=datetime.now, description="When summary was generated")

    @field_serializer('generated_at')
    def serialize_generated_at(self, value: datetime) -> str:
        return value.isoformat()


class FeedbackSubmissionRequest(BaseModel):
    """Request model for submitting feedback"""
    session_id: str = Field(..., description="Analysis session ID")
    strategy_id: str = Field(..., description="Strategy identifier")
    action: FeedbackAction = Field(..., description="Feedback action")
    note: Optional[str] = Field(None, max_length=500, description="Optional feedback note")
    suggested_tag: Optional[str] = Field(None, max_length=100, description="Suggested improvement tag")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class FeedbackSubmissionResponse(BaseModel):
    """Response model for feedback submission"""
    feedback_id: str = Field(..., description="Unique feedback identifier")
    status: str = Field(default="submitted", description="Submission status")
    message: str = Field(default="Feedback submitted successfully", description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Submission timestamp")

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class FeedbackCollectionPrompt(BaseModel):
    """Optional feedback prompt included in analysis responses"""
    enabled: bool = Field(default=True, description="Whether to show feedback prompt")
    session_id: str = Field(..., description="Session ID for feedback correlation")
    message: str = Field(
        default="Help improve our analysis! Rate the strategies above.",
        description="Prompt message to display"
    )
    strategies: List[Dict[str, str]] = Field(default_factory=list, description="Available strategies for feedback")
    timestamp: datetime = Field(default_factory=datetime.now, description="When prompt was generated")

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()
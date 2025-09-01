"""
Repositories package for M6: Feedback Capture & Persistence System

Provides pluggable storage backends for feedback data persistence.
"""

from .feedback_repository import FeedbackRepository, FileBasedFeedbackRepository

__all__ = [
    "FeedbackRepository",
    "FileBasedFeedbackRepository"
]
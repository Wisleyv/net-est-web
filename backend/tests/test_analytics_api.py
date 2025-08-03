"""
Tests for Analytics API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.main import app
from src.models.analytics import AnalysisType


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_analytics_service():
    """Create mock analytics service"""
    return Mock()


class TestAnalyticsAPI:
    """Test analytics API endpoints"""

    def test_analytics_health(self, client):
        """Test analytics health endpoint"""
        response = client.get("/analytics/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analytics"
        assert "timestamp" in data

    def test_create_session(self, client):
        """Test session creation endpoint"""
        request_data = {
            "user_agent": "Mozilla/5.0 Test Browser",
            "referrer": "https://test.com"
        }
        
        response = client.post("/analytics/session", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert data["message"] == "Session created successfully"
        assert len(data["session_id"]) > 0

    def test_create_session_minimal(self, client):
        """Test session creation with minimal data"""
        response = client.post("/analytics/session", json={})
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert data["message"] == "Session created successfully"

    def test_record_analysis(self, client):
        """Test recording analysis"""
        # First create a session
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        # Record analysis
        analysis_data = {
            "session_id": session_id,
            "analysis_type": "semantic_alignment",
            "source_text_length": 100,
            "target_text_length": 95,
            "processing_time_seconds": 1.5,
            "similarity_score": 0.85,
            "alignment_count": 12,
            "confidence_level": "high",
            "error_occurred": False
        }
        
        response = client.post("/analytics/analysis", json=analysis_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["message"] == "Analysis recorded successfully"
        assert "analysis_id" in data

    def test_record_analysis_with_error(self, client):
        """Test recording analysis with error"""
        # First create a session
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        # Record analysis with error
        analysis_data = {
            "session_id": session_id,
            "analysis_type": "text_input",
            "source_text_length": 100,
            "target_text_length": 0,
            "processing_time_seconds": 0.5,
            "error_occurred": True,
            "error_message": "Processing failed"
        }
        
        response = client.post("/analytics/analysis", json=analysis_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["message"] == "Analysis recorded successfully"

    def test_add_feedback(self, client):
        """Test adding feedback"""
        # First create a session and record analysis
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        analysis_data = {
            "session_id": session_id,
            "analysis_type": "semantic_alignment",
            "source_text_length": 100,
            "target_text_length": 95,
            "processing_time_seconds": 1.5
        }
        analysis_response = client.post("/analytics/analysis", json=analysis_data)
        analysis_id = analysis_response.json()["analysis_id"]
        
        # Add feedback
        feedback_data = {
            "session_id": session_id,
            "analysis_id": analysis_id,
            "feedback_type": "rating",
            "rating": 4,
            "comment": "Good result but could be improved",
            "is_helpful": True
        }
        
        response = client.post("/analytics/feedback", json=feedback_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["message"] == "Feedback added successfully"

    def test_add_feedback_invalid_rating(self, client):
        """Test adding feedback with invalid rating"""
        # First create a session
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        # Try to add feedback with invalid rating
        feedback_data = {
            "session_id": session_id,
            "analysis_id": "test_analysis",
            "feedback_type": "rating",
            "rating": 6,  # Invalid rating
            "comment": "Test feedback"
        }
        
        response = client.post("/analytics/feedback", json=feedback_data)
        # Pydantic validation returns 422 for constraint violations
        assert response.status_code == 422

    def test_get_session_analytics(self, client):
        """Test getting session analytics"""
        # First create a session and record analysis
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        analysis_data = {
            "session_id": session_id,
            "analysis_type": "semantic_alignment",
            "source_text_length": 100,
            "target_text_length": 95,
            "processing_time_seconds": 1.5,
            "similarity_score": 0.85
        }
        client.post("/analytics/analysis", json=analysis_data)
        
        # Get session analytics
        response = client.get(f"/analytics/session/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert data["total_analyses"] == 1
        assert data["average_similarity_score"] == 0.85

    def test_get_session_analytics_not_found(self, client):
        """Test getting analytics for nonexistent session"""
        response = client.get("/analytics/session/nonexistent")
        assert response.status_code == 404
        assert "Session not found or expired" in response.json()["detail"]

    def test_get_session_analyses(self, client):
        """Test getting session analyses"""
        # First create a session and record analyses
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        # Record multiple analyses
        for i in range(3):
            analysis_data = {
                "session_id": session_id,
                "analysis_type": "text_input",
                "source_text_length": 100 + i * 10,
                "target_text_length": 95 + i * 10,
                "processing_time_seconds": 1.0 + i * 0.5
            }
            client.post("/analytics/analysis", json=analysis_data)
        
        # Get session analyses
        response = client.get(f"/analytics/session/{session_id}/analyses")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert all(analysis["session_id"] == session_id for analysis in data)

    def test_get_session_analyses_with_limit(self, client):
        """Test getting session analyses with limit"""
        # First create a session and record analyses
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        # Record multiple analyses
        for i in range(5):
            analysis_data = {
                "session_id": session_id,
                "analysis_type": "text_input",
                "source_text_length": 100,
                "target_text_length": 95,
                "processing_time_seconds": 1.0
            }
            client.post("/analytics/analysis", json=analysis_data)
        
        # Get limited analyses
        response = client.get(f"/analytics/session/{session_id}/analyses?limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2

    def test_get_session_analyses_invalid_limit(self, client):
        """Test getting session analyses with invalid limit"""
        response = client.get("/analytics/session/test/analyses?limit=0")
        assert response.status_code == 400
        assert "Limit must be between 1 and 100" in response.json()["detail"]

    def test_get_session_feedback(self, client):
        """Test getting session feedback"""
        # First create a session, record analysis, and add feedback
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        analysis_data = {
            "session_id": session_id,
            "analysis_type": "semantic_alignment",
            "source_text_length": 100,
            "target_text_length": 95,
            "processing_time_seconds": 1.5
        }
        analysis_response = client.post("/analytics/analysis", json=analysis_data)
        analysis_id = analysis_response.json()["analysis_id"]
        
        feedback_data = {
            "session_id": session_id,
            "analysis_id": analysis_id,
            "feedback_type": "rating",
            "rating": 5,
            "comment": "Excellent result"
        }
        client.post("/analytics/feedback", json=feedback_data)
        
        # Get session feedback
        response = client.get(f"/analytics/session/{session_id}/feedback")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["analysis_id"] == analysis_id
        assert data[0]["rating"] == 5

    def test_get_system_metrics(self, client):
        """Test getting system metrics"""
        response = client.get("/analytics/system/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_sessions" in data
        assert "active_sessions" in data
        assert "total_analyses_today" in data
        assert "average_response_time" in data
        assert "system_uptime_seconds" in data

    def test_get_system_summary(self, client):
        """Test getting system summary"""
        response = client.get("/analytics/system/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_sessions" in data
        assert "active_sessions" in data
        assert "total_analyses" in data
        assert "average_processing_time" in data
        assert "system_uptime_hours" in data

    def test_export_analytics(self, client):
        """Test exporting analytics"""
        # First create some data
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        analysis_data = {
            "session_id": session_id,
            "analysis_type": "semantic_alignment",
            "source_text_length": 100,
            "target_text_length": 95,
            "processing_time_seconds": 1.5
        }
        client.post("/analytics/analysis", json=analysis_data)
        
        # Export analytics
        export_data = {"include_system_metrics": True}
        response = client.post("/analytics/export", json=export_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "export_id" in data
        assert data["session_count"] >= 1
        assert data["analysis_count"] >= 1
        assert "sessions" in data
        assert "system_metrics" in data

    def test_export_analytics_specific_sessions(self, client):
        """Test exporting analytics for specific sessions"""
        # First create multiple sessions
        session_ids = []
        for i in range(2):
            session_response = client.post("/analytics/session", json={})
            session_ids.append(session_response.json()["session_id"])
        
        # Export specific sessions
        export_data = {"session_ids": [session_ids[0]]}
        response = client.post("/analytics/export", json=export_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_count"] == 1

    def test_clear_session_data(self, client):
        """Test clearing session data"""
        # First create a session with data
        session_response = client.post("/analytics/session", json={})
        session_id = session_response.json()["session_id"]
        
        analysis_data = {
            "session_id": session_id,
            "analysis_type": "text_input",
            "source_text_length": 100,
            "target_text_length": 95,
            "processing_time_seconds": 1.0
        }
        client.post("/analytics/analysis", json=analysis_data)
        
        # Verify session exists
        response = client.get(f"/analytics/session/{session_id}")
        assert response.status_code == 200
        
        # Clear session data
        response = client.delete(f"/analytics/session/{session_id}")
        assert response.status_code == 204
        
        # Verify session no longer exists
        response = client.get(f"/analytics/session/{session_id}")
        assert response.status_code == 404

    def test_clear_session_data_not_found(self, client):
        """Test clearing nonexistent session data"""
        response = client.delete("/analytics/session/nonexistent")
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_debug_sessions(self, client):
        """Test debug sessions endpoint"""
        # First create some sessions
        for i in range(2):
            client.post("/analytics/session", json={})
        
        response = client.get("/analytics/debug/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_sessions" in data
        assert "session_ids" in data
        assert "sessions_summary" in data
        assert data["total_sessions"] >= 2

    def test_analytics_integration_flow(self, client):
        """Test complete analytics flow integration"""
        # 1. Create session
        session_response = client.post("/analytics/session", json={
            "user_agent": "Test Browser",
            "referrer": "https://test.com"
        })
        session_id = session_response.json()["session_id"]
        
        # 2. Record multiple analyses
        analyses = []
        for i in range(3):
            analysis_data = {
                "session_id": session_id,
                "analysis_type": "semantic_alignment",
                "source_text_length": 100 + i * 10,
                "target_text_length": 95 + i * 5,
                "processing_time_seconds": 1.0 + i * 0.2,
                "similarity_score": 0.8 + i * 0.05,
                "alignment_count": 10 + i * 2
            }
            analysis_response = client.post("/analytics/analysis", json=analysis_data)
            analyses.append(analysis_response.json()["analysis_id"])
        
        # 3. Add feedback for some analyses
        for i, analysis_id in enumerate(analyses[:2]):
            feedback_data = {
                "session_id": session_id,
                "analysis_id": analysis_id,
                "feedback_type": "rating",
                "rating": 4 + i,
                "comment": f"Feedback for analysis {i}",
                "is_helpful": True
            }
            client.post("/analytics/feedback", json=feedback_data)
        
        # 4. Verify session analytics
        analytics_response = client.get(f"/analytics/session/{session_id}")
        analytics_data = analytics_response.json()
        
        assert analytics_data["total_analyses"] == 3
        assert analytics_data["semantic_analyses"] == 3
        assert analytics_data["success_rate"] == 1.0
        assert analytics_data["error_count"] == 0
        
        # 5. Verify session analyses
        analyses_response = client.get(f"/analytics/session/{session_id}/analyses")
        analyses_data = analyses_response.json()
        assert len(analyses_data) == 3
        
        # 6. Verify session feedback
        feedback_response = client.get(f"/analytics/session/{session_id}/feedback")
        feedback_data = feedback_response.json()
        assert len(feedback_data) == 2
        
        # 7. Export analytics
        export_response = client.post("/analytics/export", json={})
        export_data = export_response.json()
        assert export_data["session_count"] >= 1
        assert export_data["analysis_count"] >= 3
        
        # 8. Check system metrics
        metrics_response = client.get("/analytics/system/metrics")
        metrics_data = metrics_response.json()
        assert metrics_data["total_sessions"] >= 1
        assert metrics_data["total_analyses_today"] >= 3

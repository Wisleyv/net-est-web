"""
Comprehensive tests for Semantic Alignment API endpoints
Tests all 8 API endpoints for semantic alignment functionality
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

# Import the FastAPI app
from src.main import app


class TestSemanticAlignmentAPI:
    """Test suite for Semantic Alignment API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def sample_alignment_data(self):
        """Sample data for alignment requests"""
        return {
            "source_paragraphs": [
                "A inteligência artificial está transformando o mundo.",
                "Os computadores podem processar informações rapidamente.",
                "A tecnologia blockchain é revolucionária.",
            ],
            "target_paragraphs": [
                "IA está mudando nossa sociedade profundamente.",
                "Máquinas processam dados com alta velocidade.",
                "Blockchain representa uma nova era tecnológica.",
                "A educação digital é fundamental hoje.",
            ],
            "similarity_threshold": 0.6,
            "alignment_method": "cosine_similarity",
            "max_alignments_per_source": 2,
        }

    @pytest.fixture
    def sample_embedding_data(self):
        """Sample data for embedding requests"""
        return {
            "texts": [
                "Primeira frase para gerar embeddings.",
                "Segunda frase para teste.",
                "Terceira frase com conteúdo diferente.",
            ],
            "model_name": "neuralmind/bert-base-portuguese-cased",
            "normalize": True,
        }

    def test_align_paragraphs_success(self, client, sample_alignment_data):
        """Test successful paragraph alignment via POST /semantic-alignment/align"""
        # Create a complete mock response
        mock_response = Mock()
        mock_response.success = True
        mock_response.alignment_result.aligned_pairs = []
        mock_response.alignment_result.unaligned_source_indices = []
        mock_response.alignment_result.unaligned_target_indices = []
        mock_response.alignment_result.unaligned_source_details = []
        mock_response.alignment_result.unaligned_target_details = []
        mock_response.alignment_result.similarity_matrix = Mock(
            source_count=3, target_count=4, matrix=[], method="cosine_similarity"
        )
        mock_response.alignment_result.alignment_stats = {"total_alignments": 0}
        mock_response.warnings = []
        mock_response.errors = []
        mock_response.processing_metadata = {}

        with patch("src.api.semantic_alignment.alignment_service.align_paragraphs") as mock_align:
            mock_align.return_value = mock_response
            
            response = client.post("/semantic-alignment/align", json=sample_alignment_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "alignment_result" in data

    def test_align_paragraphs_validation_error(self, client):
        """Test alignment with validation errors"""
        invalid_data = {
            "source_paragraphs": [],  # Empty source
            "target_paragraphs": ["Some text"],
            "similarity_threshold": 1.5,  # Invalid threshold
        }

        response = client.post("/semantic-alignment/align", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_align_paragraphs_empty_source(self, client):
        """Test alignment with empty source paragraphs"""
        data = {
            "source_paragraphs": [],
            "target_paragraphs": ["Some text"],
            "similarity_threshold": 0.5,
        }

        response = client.post("/semantic-alignment/align", json=data)
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_align_paragraphs_empty_target(self, client):
        """Test alignment with empty target paragraphs"""
        data = {
            "source_paragraphs": ["Some text"],
            "target_paragraphs": [],
            "similarity_threshold": 0.5,
        }

        response = client.post("/semantic-alignment/align", json=data)
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_generate_embeddings_success(self, client, sample_embedding_data):
        """Test successful embedding generation via POST /semantic-alignment/embeddings"""
        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 768] * 3
        mock_response.model_used = "neuralmind/bert-base-portuguese-cased"
        mock_response.embedding_dim = 768
        mock_response.processing_time = 0.25

        with patch("src.api.semantic_alignment.alignment_service.generate_embeddings") as mock_embed:
            mock_embed.return_value = mock_response
            
            response = client.post("/semantic-alignment/embeddings", json=sample_embedding_data)

        assert response.status_code == 200
        data = response.json()
        assert "embeddings" in data
        assert data["embedding_dim"] == 768
        assert len(data["embeddings"]) == 3

    def test_generate_embeddings_empty_texts(self, client):
        """Test embedding generation with empty texts list"""
        data = {
            "texts": [],
            "model_name": "neuralmind/bert-base-portuguese-cased",
        }

        response = client.post("/semantic-alignment/embeddings", json=data)
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_generate_embeddings_too_many_texts(self, client):
        """Test embedding generation with too many texts"""
        data = {
            "texts": ["text"] * 101,  # Over the limit
            "model_name": "neuralmind/bert-base-portuguese-cased",
        }

        response = client.post("/semantic-alignment/embeddings", json=data)
        assert response.status_code == 400
        assert "too many" in response.json()["detail"].lower()

    def test_get_health_status(self, client):
        """Test health status endpoint GET /semantic-alignment/health"""
        mock_status = {
            "service": "semantic_alignment",
            "ml_libraries_available": True,
            "model_loaded": False,
            "cache_size": 0,
            "config": {
                "model": "neuralmind/bert-base-portuguese-cased",
                "device": "cpu",
                "similarity_threshold": 0.7,
                "batch_size": 8,
            },
            "model_status": "not_loaded",
        }

        with patch("src.api.semantic_alignment.alignment_service.get_health_status") as mock_health:
            mock_health.return_value = mock_status
            
            response = client.get("/semantic-alignment/health")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "semantic_alignment"
        assert "ml_libraries_available" in data
        assert "config" in data

    def test_get_alignment_methods(self, client):
        """Test alignment methods endpoint GET /semantic-alignment/methods"""
        response = client.get("/semantic-alignment/methods")
        
        assert response.status_code == 200
        data = response.json()
        assert "methods" in data
        assert "COSINE_SIMILARITY" in data["methods"]
        assert "EUCLIDEAN_DISTANCE" in data["methods"]
        assert "DOT_PRODUCT" in data["methods"]

    def test_get_current_config(self, client):
        """Test get configuration endpoint GET /semantic-alignment/config"""
        response = client.get("/semantic-alignment/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "model" in data
        assert "similarity_threshold" in data
        assert "batch_size" in data
        assert "device" in data

    def test_update_config(self, client):
        """Test update configuration endpoint POST /semantic-alignment/config"""
        new_config = {
            "bertimbau_model": "neuralmind/bert-base-portuguese-cased",
            "similarity_threshold": 0.8,
            "max_sequence_length": 256,
            "batch_size": 16,
            "device": "cpu",
            "cache_embeddings": True,
            "confidence_thresholds": {
                "high": 0.85,
                "medium": 0.65,
                "low": 0.35,
            },
        }

        response = client.post("/semantic-alignment/config", json=new_config)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "new_config" in data
        assert data["new_config"]["similarity_threshold"] == 0.8

    def test_align_simple_success(self, client):
        """Test simplified alignment endpoint POST /semantic-alignment/align-simple"""
        # Create complete mock response
        mock_response = Mock()
        mock_response.success = True
        mock_response.alignment_result.aligned_pairs = []
        mock_response.alignment_result.unaligned_source_indices = []
        mock_response.alignment_result.unaligned_target_indices = []
        mock_response.alignment_result.unaligned_source_details = []
        mock_response.alignment_result.unaligned_target_details = []
        mock_response.alignment_result.similarity_matrix = Mock(
            source_count=1, target_count=1, matrix=[], method="cosine_similarity"
        )
        mock_response.alignment_result.alignment_stats = {"total_alignments": 0}
        mock_response.warnings = []
        mock_response.errors = []
        mock_response.processing_metadata = {}

        data = {
            "source_paragraphs": ["Source text"],
            "target_paragraphs": ["Target text"],
            "similarity_threshold": 0.7,
            "method": "cosine_similarity",
        }

        with patch("src.api.semantic_alignment.alignment_service.align_paragraphs") as mock_align:
            mock_align.return_value = mock_response
            
            response = client.post("/semantic-alignment/align-simple", json=data)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True

    def test_clear_embedding_cache(self, client):
        """Test cache clearing endpoint DELETE /semantic-alignment/cache"""
        mock_response = {
            "success": True,
            "message": "Cache cleared successfully. Removed 5 entries.",
            "cache_size_before": 5,
            "cache_size_after": 0,
        }

        with patch("src.api.semantic_alignment.alignment_service") as mock_service:
            mock_service.embedding_cache.cache = {"key1": "value1", "key2": "value2"}
            mock_service.embedding_cache.access_order = ["key1", "key2"]
            
            response = client.delete("/semantic-alignment/cache")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cache_size_before" in data

    def test_error_handling_service_exception(self, client, sample_alignment_data):
        """Test error handling when service raises exception"""
        with patch("src.api.semantic_alignment.alignment_service.align_paragraphs") as mock_align:
            mock_align.side_effect = Exception("Service error")
            
            response = client.post("/semantic-alignment/align", json=sample_alignment_data)

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    def test_error_handling_service_failure(self, client, sample_alignment_data):
        """Test error handling when service returns failure"""
        mock_response = Mock()
        mock_response.success = False
        mock_response.errors = ["Alignment failed", "Model error"]

        with patch("src.api.semantic_alignment.alignment_service.align_paragraphs") as mock_align:
            mock_align.return_value = mock_response
            
            response = client.post("/semantic-alignment/align", json=sample_alignment_data)

        assert response.status_code == 500
        assert "Alignment failed" in response.json()["detail"]

    def test_embedding_error_handling(self, client, sample_embedding_data):
        """Test error handling in embedding generation"""
        with patch("src.api.semantic_alignment.alignment_service.generate_embeddings") as mock_embed:
            mock_embed.side_effect = Exception("Embedding error")
            
            response = client.post("/semantic-alignment/embeddings", json=sample_embedding_data)

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

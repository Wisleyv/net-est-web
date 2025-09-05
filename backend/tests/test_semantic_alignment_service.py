"""
Comprehensive tests for Semantic Alignment Service
Tests the core business logic for paragraph alignment using BERTimbau embeddings
"""

import pytest
from unittest.mock import patch, Mock
import numpy as np

from src.models.semantic_alignment import (
    AlignmentRequest,
    AlignmentMethod,
    EmbeddingRequest,
    AlignmentConfiguration,
)
from src.services.semantic_alignment_service import SemanticAlignmentService


class TestSemanticAlignmentService:
    """Test suite for SemanticAlignmentService"""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing"""
        from src.core.config import settings as runtime_settings
        config = AlignmentConfiguration(
            bertimbau_model=runtime_settings.BERTIMBAU_MODEL,
            similarity_threshold=0.7,
            max_sequence_length=512,
            batch_size=8,
            device="cpu",
            cache_embeddings=True,
        )
        return SemanticAlignmentService(config)

    @pytest.fixture
    def sample_paragraphs(self):
        """Sample paragraphs for testing"""
        return {
            "source": [
                "A inteligência artificial está transformando o mundo.",
                "Os computadores podem processar informações rapidamente.",
                "A tecnologia blockchain é revolucionária.",
            ],
            "target": [
                "IA está mudando nossa sociedade profundamente.",
                "Máquinas processam dados com alta velocidade.",
                "Blockchain representa uma nova era tecnológica.",
                "A educação digital é fundamental hoje.",
            ],
        }

    def test_service_initialization(self, service):
        """Test service initialization"""
    from src.core.config import settings as runtime_settings
    assert service.config.bertimbau_model == runtime_settings.BERTIMBAU_MODEL
    assert service.config.similarity_threshold == 0.7
    assert service.model is None
    assert service.embedding_cache is not None
    assert service.executor is not None

    def test_service_initialization_with_defaults(self):
        """Test service initialization with default config"""
    service = SemanticAlignmentService()
    from src.core.config import settings as runtime_settings
    assert service.config.bertimbau_model == runtime_settings.BERTIMBAU_MODEL
    assert service.config.similarity_threshold == 0.7
    assert service.config.device == "cpu"

    @pytest.mark.asyncio
    async def test_generate_embeddings_fallback(self, service):
        """Test embedding generation with fallback when ML libraries not available"""
        from src.core.config import settings as runtime_settings
        request = EmbeddingRequest(
            texts=["Texto de teste", "Outro texto"],
            model_name=runtime_settings.BERTIMBAU_MODEL,
            normalize=True,
        )

        with patch("src.services.semantic_alignment_service.ML_AVAILABLE", False):
            response = await service.generate_embeddings(request)

        assert response.model_used == "fallback_random"
        assert response.embedding_dim == 768
        assert len(response.embeddings) == 2
        assert len(response.embeddings[0]) == 768
        assert response.processing_time >= 0

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_cache(self, service):
        """Test embedding generation with caching"""
        from src.core.config import settings as runtime_settings
        request = EmbeddingRequest(
            texts=["Texto repetido", "Novo texto", "Texto repetido"],
            model_name=runtime_settings.BERTIMBAU_MODEL,
            normalize=True,
        )

        # Mock fallback embeddings (since ML libraries might not be available)
        with patch("src.services.semantic_alignment_service.ML_AVAILABLE", False):
            response = await service.generate_embeddings(request)

        assert len(response.embeddings) == 3
        assert response.model_used == "fallback_random"
        assert response.embedding_dim == 768
        # Note: With fallback, embeddings are random so we can't test caching equality

    def test_compute_similarity_matrix_cosine(self, service):
        """Test cosine similarity matrix computation"""
        source_embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        target_embeddings = [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]

        with patch("src.services.semantic_alignment_service.ML_AVAILABLE", True), \
             patch("src.services.semantic_alignment_service.cosine_similarity") as mock_cosine:
            mock_cosine.return_value = np.array([[1.0, 0.0], [0.0, 0.0]])
            
            result = service._compute_similarity_matrix(
                source_embeddings, target_embeddings, AlignmentMethod.COSINE_SIMILARITY
            )

        assert result.shape == (2, 2)
        mock_cosine.assert_called_once()

    def test_compute_similarity_matrix_euclidean(self, service):
        """Test euclidean distance similarity matrix computation"""
        source_embeddings = [[1.0, 0.0], [0.0, 1.0]]
        target_embeddings = [[1.0, 0.0], [0.0, 1.0]]

        with patch("src.services.semantic_alignment_service.ML_AVAILABLE", True), \
             patch("src.services.semantic_alignment_service.euclidean_distances") as mock_euclidean:
            mock_euclidean.return_value = np.array([[0.0, 1.4], [1.4, 0.0]])
            
            result = service._compute_similarity_matrix(
                source_embeddings, target_embeddings, AlignmentMethod.EUCLIDEAN_DISTANCE
            )

        assert result.shape == (2, 2)
        mock_euclidean.assert_called_once()

    def test_determine_confidence(self, service):
        """Test confidence level determination"""
        assert service._determine_confidence(0.9) == "high"
        assert service._determine_confidence(0.7) == "medium"
        assert service._determine_confidence(0.4) == "low"
        assert service._determine_confidence(0.2) == "very_low"

    def test_find_alignments(self, service, sample_paragraphs):
        """Test alignment finding logic"""
        # Create a mock similarity matrix
        similarity_matrix = np.array([
            [0.9, 0.3, 0.1, 0.2],  # Source 0: strong match with target 0
            [0.2, 0.8, 0.2, 0.1],  # Source 1: strong match with target 1
            [0.1, 0.2, 0.9, 0.3],  # Source 2: strong match with target 2
        ])

        aligned_pairs, unaligned_source, unaligned_target = service._find_alignments(
            similarity_matrix,
            sample_paragraphs["source"],
            sample_paragraphs["target"],
            threshold=0.7,
            max_alignments_per_source=1,
            method=AlignmentMethod.COSINE_SIMILARITY,
        )

        assert len(aligned_pairs) == 3
        assert aligned_pairs[0].source_index == 0
        assert aligned_pairs[0].target_index == 0
        assert aligned_pairs[0].similarity_score == 0.9
        assert aligned_pairs[0].confidence == "high"
        
        assert len(unaligned_source) == 0  # All sources aligned
        assert 3 in unaligned_target  # Target 3 unaligned

    def test_create_unaligned_details(self, service, sample_paragraphs):
        """Test unaligned paragraph details creation"""
        similarity_matrix = np.array([
            [0.5, 0.3, 0.1, 0.2],
            [0.2, 0.4, 0.2, 0.1],
            [0.1, 0.2, 0.6, 0.3],
        ])

        unaligned_details = service._create_unaligned_details(
            unaligned_indices=[0, 1],
            paragraphs=sample_paragraphs["source"],
            similarity_matrix=similarity_matrix,
            is_source=True,
        )

        assert len(unaligned_details) == 2
        assert unaligned_details[0].index == 0
        assert unaligned_details[0].text == sample_paragraphs["source"][0]
        assert "below threshold" in unaligned_details[0].reason
        assert unaligned_details[0].nearest_similarity == 0.5

    @pytest.mark.asyncio
    async def test_align_paragraphs_success(self, service, sample_paragraphs):
        """Test successful paragraph alignment"""
        request = AlignmentRequest(
            source_paragraphs=sample_paragraphs["source"],
            target_paragraphs=sample_paragraphs["target"],
            similarity_threshold=0.5,
            alignment_method=AlignmentMethod.COSINE_SIMILARITY,
            max_alignments_per_source=2,
        )

        # Mock embedding generation
        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 768] * 7  # 3 source + 4 target
        mock_response.processing_time = 0.5
        mock_response.model_used = "test_model"

        with patch.object(service, "generate_embeddings", return_value=mock_response), \
             patch.object(service, "_compute_similarity_matrix") as mock_similarity:
            
            # Mock high similarity matrix
            mock_similarity.return_value = np.array([
                [0.9, 0.3, 0.1, 0.2],
                [0.2, 0.8, 0.2, 0.1],
                [0.1, 0.2, 0.9, 0.3],
            ])

            result = await service.align_paragraphs(request)

        assert result.success is True
        assert result.alignment_result is not None
        assert len(result.alignment_result.aligned_pairs) > 0
        assert result.alignment_result.alignment_stats["processing_time_seconds"] > 0

    @pytest.mark.asyncio
    async def test_align_paragraphs_empty_input(self, service):
        """Test alignment with empty input"""
        request = AlignmentRequest(
            source_paragraphs=[],
            target_paragraphs=["Some text"],
            similarity_threshold=0.5,
            alignment_method=AlignmentMethod.COSINE_SIMILARITY,
            max_alignments_per_source=1,
        )

        result = await service.align_paragraphs(request)

        assert result.success is False
        assert "required" in result.errors[0]

    @pytest.mark.asyncio
    async def test_align_paragraphs_error_handling(self, service, sample_paragraphs):
        """Test error handling in alignment process"""
        request = AlignmentRequest(
            source_paragraphs=sample_paragraphs["source"],
            target_paragraphs=sample_paragraphs["target"],
            similarity_threshold=0.5,
            alignment_method=AlignmentMethod.COSINE_SIMILARITY,
            max_alignments_per_source=2,
        )

        with patch.object(service, "generate_embeddings", side_effect=Exception("Test error")):
            result = await service.align_paragraphs(request)

        assert result.success is False
        assert "Test error" in str(result.errors[0])

    @pytest.mark.asyncio
    async def test_get_health_status(self, service):
        """Test health status reporting"""
        with patch("src.services.semantic_alignment_service.ML_AVAILABLE", True):
            status = await service.get_health_status()

        assert status["service"] == "semantic_alignment"
        assert "ml_libraries_available" in status
        assert "model_loaded" in status
        assert "cache_size" in status
        assert "config" in status

    @pytest.mark.asyncio
    async def test_get_health_status_no_ml(self, service):
        """Test health status when ML libraries unavailable"""
        with patch("src.services.semantic_alignment_service.ML_AVAILABLE", False):
            status = await service.get_health_status()

        assert status["ml_libraries_available"] is False
        assert status["model_status"] == "ml_libraries_not_available"

    def test_embedding_cache_functionality(self):
        """Test embedding cache operations"""
        from src.services.semantic_alignment_service import EmbeddingCache
        
        cache = EmbeddingCache(max_size=2)
        
        # Test setting and getting
        embedding = [0.1, 0.2, 0.3]
        cache.set("text1", "model1", embedding)
        assert cache.get("text1", "model1") == embedding
        
        # Test cache miss
        assert cache.get("text2", "model1") is None
        
        # Test LRU eviction
        cache.set("text2", "model1", [0.2, 0.3, 0.4])
        cache.set("text3", "model1", [0.3, 0.4, 0.5])  # Should evict text1
        
        assert cache.get("text1", "model1") is None
        assert cache.get("text2", "model1") == [0.2, 0.3, 0.4]
        assert cache.get("text3", "model1") == [0.3, 0.4, 0.5]

    def test_cache_key_generation(self):
        """Test cache key generation"""
        from src.services.semantic_alignment_service import EmbeddingCache
        
        cache = EmbeddingCache()
        key1 = cache._get_cache_key("text", "model")
        key2 = cache._get_cache_key("text", "model")
        key3 = cache._get_cache_key("different_text", "model")
        
        assert key1 == key2
        assert key1 != key3
        assert len(key1) == 32  # MD5 hex digest length

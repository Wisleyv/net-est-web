"""
Async tests for SemanticAlignmentService (small batch)
These tests are designed to be fast and avoid loading heavy ML models by
using the service's fallback path or mocking the embedding generation.
They will be reintroduced incrementally as part of the test restoration plan.
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch

from src.models.semantic_alignment import (
    AlignmentRequest,
    AlignmentMethod,
    EmbeddingRequest,
)
from src.services.semantic_alignment_service import SemanticAlignmentService


@pytest.mark.asyncio
async def test_generate_embeddings_fallback():
    """When ML libs are unavailable, the service should return fallback embeddings."""
    service = SemanticAlignmentService()

    request = EmbeddingRequest(
        texts=["Texto de teste", "Outro texto"],
        model_name=service.config.bertimbau_model,
        normalize=True,
    )

    with patch("src.services.semantic_alignment_service.ML_AVAILABLE", False):
        response = await service.generate_embeddings(request)

    assert response.model_used == "fallback_random"
    assert response.embedding_dim >= 1
    assert len(response.embeddings) == 2


@pytest.mark.asyncio
async def test_align_paragraphs_with_mocked_embeddings():
    """Test align_paragraphs success path by mocking embedding generation and similarity matrix."""
    service = SemanticAlignmentService()

    sample_source = [
        "A inteligência artificial está transformando o mundo.",
        "Os computadores podem processar informações rapidamente.",
    ]
    sample_target = [
        "IA está mudando nossa sociedade profundamente.",
        "Máquinas processam dados com alta velocidade.",
    ]

    request = AlignmentRequest(
        source_paragraphs=sample_source,
        target_paragraphs=sample_target,
        similarity_threshold=0.5,
        alignment_method=AlignmentMethod.COSINE_SIMILARITY,
        max_alignments_per_source=1,
    )

    # Build a mock embedding response: 2 source + 2 target
    mock_response = Mock()
    mock_response.embeddings = [[0.1] * 128] * 4
    mock_response.processing_time = 0.01
    mock_response.model_used = "test_model"

    # AsyncMock for generate_embeddings
    async_mock = AsyncMock(return_value=mock_response)

    # Mock similarity matrix (2x2) with clear diagonal matches
    sim_matrix = np.array([[0.9, 0.1], [0.1, 0.8]])

    with patch.object(service, "generate_embeddings", new=async_mock), \
         patch.object(service, "_compute_similarity_matrix", return_value=sim_matrix):
        result = await service.align_paragraphs(request)

    assert result.success is True
    assert result.alignment_result is not None
    assert len(result.alignment_result.aligned_pairs) >= 1

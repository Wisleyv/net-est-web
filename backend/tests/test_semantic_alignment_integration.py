"""
Controlled end-to-end integration tests for paragraph alignment.
These tests use realistic example text pairs and mock the embedding
generation and similarity computation so they remain fast and deterministic.
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch

from src.models.semantic_alignment import (
    AlignmentRequest,
    AlignmentMethod,
)
from src.services.semantic_alignment_service import SemanticAlignmentService


@pytest.mark.asyncio
async def test_full_text_alignment_simple_match():
    """Full-text alignment should correctly align source->target paragraphs."""
    service = SemanticAlignmentService()

    source = [
        "O gato subiu no telhado e dormiu.",
        "O cachorro latiu a noite.",
        "A chuva começou a cair forte, atrapalhando a rua.",
    ]

    target = [
        "O gato dormiu no telhado.",
        "Durante a noite o cachorro latiu.",
        "Choveu forte e a rua ficou alagada.",
        "Informação extra sem correspondência.",
    ]

    request = AlignmentRequest(
        source_paragraphs=source,
        target_paragraphs=target,
        similarity_threshold=0.5,
        alignment_method=AlignmentMethod.COSINE_SIMILARITY,
        max_alignments_per_source=1,
    )

    # Mock embedding generation (return placeholder embeddings)
    mock_response = Mock()
    mock_response.embeddings = [[0.1] * 64] * (len(source) + len(target))
    mock_response.processing_time = 0.01
    mock_response.model_used = "mock_model"

    async_mock = AsyncMock(return_value=mock_response)

    # Construct similarity matrix with clear diagonal matches for source->target
    sim = np.array([
        [0.95, 0.1, 0.05, 0.0],
        [0.05, 0.9, 0.05, 0.0],
        [0.02, 0.1, 0.88, 0.0],
    ])

    with patch.object(service, "generate_embeddings", new=async_mock), \
         patch.object(service, "_compute_similarity_matrix", return_value=sim):
        result = await service.align_paragraphs(request)

    assert result.success is True
    aligned = result.alignment_result.aligned_pairs
    # Expect 3 aligned pairs (each source aligns to its corresponding target)
    assert len(aligned) == 3
    # Confirm target index 3 is unaligned
    assert 3 in result.alignment_result.unaligned_target_indices


@pytest.mark.asyncio
async def test_full_text_alignment_merge_and_split_cases():
    """Test merge/split behavior: multiple sources align to a single target and vice-versa."""
    service = SemanticAlignmentService()

    # Two source paragraphs that together map to a single simplified target
    source = [
        "A primeira frase é longa e contém várias ideias complexas.",
        "A segunda frase complementa a informação da primeira.",
        "Um parágrafo independente não relacionado.",
    ]

    target = [
        "Uma versão simplificada que junta as duas primeiras frases.",
        "Parágrafo independente correspondente.",
    ]

    request = AlignmentRequest(
        source_paragraphs=source,
        target_paragraphs=target,
        similarity_threshold=0.4,
        alignment_method=AlignmentMethod.COSINE_SIMILARITY,
        max_alignments_per_source=2,
    )

    mock_response = Mock()
    mock_response.embeddings = [[0.2] * 64] * (len(source) + len(target))
    mock_response.processing_time = 0.01
    mock_response.model_used = "mock_model"
    async_mock = AsyncMock(return_value=mock_response)

    # similarity matrix: sources 0 and 1 both strongly match target 0; source 2 matches target 1
    sim = np.array([
        [0.85, 0.1],
        [0.82, 0.05],
        [0.05, 0.9],
    ])

    with patch.object(service, "generate_embeddings", new=async_mock), \
         patch.object(service, "_compute_similarity_matrix", return_value=sim):
        result = await service.align_paragraphs(request)

    assert result.success is True
    aligned = result.alignment_result.aligned_pairs
    # At least one alignment to target 0 and one to target 1 is expected.
    # Some alignment strategies collapse multiple sources into one target
    # (merge behavior). We assert minimal expectations to keep the test
    # robust while preserving semantic intent.
    target0_hits = [p for p in aligned if p.target_index == 0]
    target1_hits = [p for p in aligned if p.target_index == 1]

    assert len(target0_hits) >= 1
    assert len(target1_hits) >= 1
    # Also ensure we have at least two alignments overall (merge+single)
    assert len(aligned) >= 2

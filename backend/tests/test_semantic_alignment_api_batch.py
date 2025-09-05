"""
Small API endpoint test batch (TestClient + patched service methods).
These tests patch the alignment service methods to make API behavior
fast and deterministic for gating deployments.
"""

from types import SimpleNamespace
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.main import app
from src.core.config import settings as runtime_settings
from src.models.semantic_alignment import (
    AlignmentResponse,
    AlignmentResult,
    AlignmentMatrix,
    UnalignedParagraph,
    AlignedPair,
    EmbeddingResponse,
)

client = TestClient(app)


def sample_alignment_payload():
    return {
        "source_paragraphs": [
            "A inteligência artificial está transformando o mundo.",
            "Os computadores podem processar informações rapidamente.",
        ],
        "target_paragraphs": [
            "IA está mudando nossa sociedade profundamente.",
            "Máquinas processam dados com alta velocidade.",
        ],
        "similarity_threshold": 0.6,
        "alignment_method": "cosine_similarity",
        "max_alignments_per_source": 1,
    }


def test_align_endpoint_success():
    payload = sample_alignment_payload()

    # Build an AlignmentResult that matches the response model schema
    alignment_result = AlignmentResult(
        aligned_pairs=[],
        unaligned_source_indices=[],
        unaligned_target_indices=[1],
        unaligned_source_details=[],
        unaligned_target_details=[],
        similarity_matrix=AlignmentMatrix(source_count=2, target_count=2, matrix=[[0.0, 0.0], [0.0, 0.0]], method="cosine_similarity"),
        alignment_stats={"processing_time_seconds": 0.05},
    )

    response_obj = AlignmentResponse(
        success=True,
        alignment_result=alignment_result,
        warnings=[],
        errors=[],
        processing_metadata={},
    )

    with patch("src.api.semantic_alignment.alignment_service.align_paragraphs", return_value=response_obj):
        r = client.post("/semantic-alignment/align", json=payload)

    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "alignment_result" in data


def test_embeddings_endpoint_success():
    data = {"texts": ["frase 1", "frase 2"], "model_name": runtime_settings.BERTIMBAU_MODEL}

    resp = EmbeddingResponse(
        embeddings=[[0.1] * 64, [0.1] * 64],
        model_used=runtime_settings.BERTIMBAU_MODEL,
        embedding_dim=64,
        processing_time=0.01,
    )

    with patch("src.api.semantic_alignment.alignment_service.generate_embeddings", return_value=resp):
        r = client.post("/semantic-alignment/embeddings", json=data)

    assert r.status_code == 200
    payload = r.json()
    assert payload["embedding_dim"] == 64
    assert len(payload["embeddings"]) == 2


def test_health_endpoint_returns_status():
    mock_status = {
        "service": "semantic_alignment",
        "ml_libraries_available": True,
        "model_loaded": False,
        "cache_size": 0,
        "config": {"model": runtime_settings.BERTIMBAU_MODEL},
        "model_status": "not_loaded",
    }

    with patch("src.api.semantic_alignment.alignment_service.get_health_status", return_value=mock_status):
        r = client.get("/semantic-alignment/health")

    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "semantic_alignment"
    assert "config" in data


def test_methods_endpoint():
    r = client.get("/semantic-alignment/methods")
    assert r.status_code == 200
    data = r.json()
    assert "methods" in data

"""Snapshot tests for SentenceAlignmentService
Focus: regression detection for alignment outputs.
"""
import pytest
from src.services.sentence_alignment_service import SentenceAlignmentService
import json
import re

UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def _normalize(obj):
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize(x) for x in obj]
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, str) and UUID_RE.search(obj):
        return UUID_RE.sub("<uuid>", obj)
    return obj

@pytest.fixture
def service():
    return SentenceAlignmentService()

def test_alignment_basic_pairs_snapshot(service, snapshot):
    src = [
        "A inteligência artificial avança rapidamente.",
        "Computadores processam dados."
    ]
    tgt = [
        "IA avança rápido.",
        "Os computadores processam rapidamente os dados."
    ]
    result = service.align(src, tgt, threshold=0.2)
    # Store aligned pairs and similarity matrix in snapshot
    normalized = _normalize({
        "aligned": result.aligned,
        "similarity_matrix": result.similarity_matrix
    })
    serialized = json.dumps(normalized, ensure_ascii=False, sort_keys=True, indent=2)
    snapshot.assert_match(serialized, "sentence_alignment_snapshot")

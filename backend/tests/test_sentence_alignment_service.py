import pytest

from backend.src.services.sentence_alignment_service import SentenceAlignmentService
from backend.src.core.config import settings


def test_disabled_by_feature_flag(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_SENTENCE_ALIGNMENT", False)
    service = SentenceAlignmentService()
    result = service.align_paragraphs([("A.", "B.")])
    assert result == []


def test_align_paragraphs_basic(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_SENTENCE_ALIGNMENT", True)
    service = SentenceAlignmentService(similarity_threshold=0.1)

    paragraph_pairs = [
        ("This is a first sentence. This is a second sentence.",
         "This is a first sentence. Another sentence here."),
    ]

    result = service.align_paragraphs(paragraph_pairs)

    assert isinstance(result, list)
    assert len(result) == 1

    first = result[0]
    assert "source_sentences" in first and "target_sentences" in first and "alignments" in first

    # At least one aligned sentence should be present (the identical first sentence)
    aligned = [a for a in first["alignments"] if a.status == "aligned"]
    assert len(aligned) >= 1

    # Ensure alignment entries have expected attributes
    for a in first["alignments"]:
        assert hasattr(a, "status")
        assert isinstance(a.score, (float, int))


def test_empty_inputs(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_SENTENCE_ALIGNMENT", True)
    service = SentenceAlignmentService()
    result = service.align_paragraphs([])
    assert result == []

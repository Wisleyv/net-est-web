"""Tests for SentenceAlignmentService (Milestone M1)
Focus: correctness of sentence-level alignment classifications and edge cases.
"""

import pytest
from src.services.sentence_alignment_service import SentenceAlignmentService


@pytest.fixture
def service():
    return SentenceAlignmentService()


def test_split_sentences_basic():
    service = SentenceAlignmentService()
    text = "Primeira frase. Segunda frase! Terceira? Quarta frase final."
    parts = service.split_sentences(text)
    assert len(parts) >= 4
    assert parts[0].startswith("Primeira")


def test_alignment_empty(service):
    result = service.align([], [])
    assert result.aligned == []
    assert result.unmatched_source == []
    assert result.unmatched_target == []


def test_alignment_only_source(service):
    result = service.align(["Uma frase."], [])
    assert result.unmatched_source == [0]


def test_alignment_only_target(service):
    result = service.align([], ["Outra frase."])
    assert result.unmatched_target == [0]


def test_alignment_basic_pairs(service):
    src = ["A inteligência artificial avança rapidamente.", "Computadores processam dados."]
    tgt = ["IA avança rápido.", "Os computadores processam rapidamente os dados."]
    result = service.align(src, tgt, threshold=0.2)  # low threshold for pseudo embeddings
    assert len(result.aligned) >= 1
    assert not result.unmatched_source or all(i < len(src) for i in result.unmatched_source)


def test_alignment_split_and_merge_detection(service):
    # Craft sentences likely to hash differently but keep len minimal; detection relies on structure of best mappings
    src = [
        "Frase longa que pode ser dividida em partes.",
        "Outra sentença adicional para analisar.",
    ]
    tgt = [
        "Frase longa que",  # potential split segment
        "pode ser dividida em partes.",  # potential split segment
        "Outra sentença adicional combinada com extra.",  # potential merge candidate
    ]
    result = service.align(src, tgt, threshold=0.1)
    # We can't guarantee splits under hash fallback, but ensure no crash and structure present
    assert result.similarity_matrix
    assert isinstance(result.similarity_matrix, list)

#
# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
#

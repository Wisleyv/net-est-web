"""Portuguese-focused tests for improved simple_sentence_split heuristics."""

import pytest
from src.services.sentence_alignment_service import SentenceAlignmentService


def test_abbreviation_protection():
    service = SentenceAlignmentService()
    text = "Dr. Silva chegou. Ele falou com a Sra. Gomes. Depois, etc. foi usado."
    parts = service.split_sentences(text)
    # Expect 3 sentences, not splitting inside Dr. or Sra. or etc.
    assert len(parts) == 3
    assert parts[0].startswith("Dr. Silva")


def test_quotes_and_lowercase_after_colon():
    service = SentenceAlignmentService()
    text = "Ele disse: a explicação completa virá depois. 'Outra frase.' \"Mais uma!\""
    parts = service.split_sentences(text)
    # Colon split should separate, quotes preserved
    assert any("Outra frase" in p for p in parts)
    assert any("Mais uma" in p for p in parts)


def test_dialogue_dash():
    service = SentenceAlignmentService()
    text = "— Olá! — disse ela. — Tudo bem? Sim, tudo certo."
    parts = service.split_sentences(text)
    assert len(parts) >= 3


def test_edge_multiple_spaces():
    service = SentenceAlignmentService()
    text = "Primeira frase.   Segunda   frase!   Terceira?"
    parts = service.split_sentences(text)
    assert len(parts) == 3

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

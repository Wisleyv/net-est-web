import pytest

from src.services.micro_span_extractor import MicroSpanExtractor


def test_basic_extraction_order_and_normalization():
    extractor = MicroSpanExtractor(max_spans=3)
    sentence = "A complexa arquitetura modular permite extensibilidade robusta e manutenção eficiente do sistema."
    spans = extractor.extract(sentence)
    assert 1 <= len(spans) <= 3
    max_sal = max(s['salience'] for s in spans)
    assert abs(max_sal - 1.0) < 1e-6
    intervals = []
    for s in spans:
        for (os, oe) in intervals:
            assert not (s['end'] > os and s['start'] < oe)
        intervals.append((s['start'], s['end']))


def test_cache_reuse():
    extractor = MicroSpanExtractor(max_spans=2)
    sentence = "Processamento eficiente de linguagem natural facilita analise detalhada."  # >15 chars
    spans1 = extractor.extract(sentence)
    cache_size_before = len(extractor._cache)  # type: ignore
    spans2 = extractor.extract(sentence)
    cache_size_after = len(extractor._cache)  # type: ignore
    assert spans1 == spans2
    assert cache_size_before == cache_size_after


def test_short_sentence_returns_empty():
    extractor = MicroSpanExtractor()
    assert extractor.extract("Muito curto.") == []


def test_mode_switch_graceful():
    extractor = MicroSpanExtractor(mode="unknown-mode")
    spans = extractor.extract("Esta frase suficientemente longa deve simplesmente retornar lista vazia se modo desconhecido.")
    assert spans == []

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

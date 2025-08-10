import pytest
from src.services.salience_provider import SalienceProvider

SAMPLE_PT = """O estudante analisou cuidadosamente o complexo texto acadêmico e depois produziu uma versão simplificada do conteúdo original."""

def test_frequency_fallback_order_and_weights():
    sp = SalienceProvider(method='frequency')
    result = sp.extract(SAMPLE_PT, max_units=5)
    assert result.method == 'frequency'
    # Ensure units not empty and sorted by weight desc
    assert result.units, 'Expected at least one salient unit'
    weights = [u['weight'] for u in result.units]
    assert weights == sorted(weights, reverse=True)
    # Stopwords should not appear
    stopwords = {'o','do','uma','de','e'}
    assert not any(u['unit'] in stopwords for u in result.units)

@pytest.mark.skipif('keybert' not in globals(), reason='KeyBERT not installed in test env')
def test_keybert_optional(monkeypatch):
    sp = SalienceProvider(method='keybert')
    result = sp.extract(SAMPLE_PT, max_units=5)
    # If KeyBERT loads, method should be keybert; else fallback handled in provider logic
    assert result.method in {'keybert','frequency'}

@pytest.mark.skipif('yake' not in globals(), reason='YAKE not installed in test env')
def test_yake_optional(monkeypatch):
    sp = SalienceProvider(method='yake')
    result = sp.extract(SAMPLE_PT, max_units=5)
    assert result.method in {'yake','frequency'}


def test_empty_text():
    sp = SalienceProvider(method='frequency')
    result = sp.extract('', max_units=5)
    assert result.units == []

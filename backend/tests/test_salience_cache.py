from src.services.salience_provider import SalienceProvider

TEXT = "Este é um texto curto com termos repetidos texto texto termos."  # repeated terms

def test_salience_cache_same_object_reference():
    sp = SalienceProvider(method='frequency')
    first = sp.extract(TEXT, max_units=5)
    second = sp.extract(TEXT, max_units=5)
    # Should return identical (cached) object (pointer equality acceptable) or at least same content
    assert first.units == second.units
    # Force different max_units -> cache miss with possibly different length
    third = sp.extract(TEXT, max_units=3)
    assert len(third.units) <= 3
    assert len(first.units) >= len(third.units)

from src.services.salience_provider import SalienceProvider


def test_lru_eviction():
    # Small cache to force eviction
    sp = SalienceProvider(method='frequency')
    sp._cache_max = 3
    texts = [f"Frase repetida {i} com termos" for i in range(5)]
    for t in texts:
        sp.extract(t, max_units=5)
    # Cache size should not exceed 3
    assert len(sp._cache) == 3
    # The last three inserted (indices 2,3,4) should remain; first two should be evicted.
    expected_keys = {sp._make_cache_key(texts[i], 5) for i in range(2,5)}
    remaining_keys = set(sp._cache.keys())
    assert remaining_keys == expected_keys, f"LRU eviction failed. Expected keys for texts[2..4]; got {remaining_keys}"

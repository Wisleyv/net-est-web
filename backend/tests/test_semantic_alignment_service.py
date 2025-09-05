"""
Minimal synchronous tests for Semantic Alignment components.
This file intentionally contains only light-weight tests that don't
require ML backends so pytest can collect and run reliably while the
more extensive async/integration tests are being repaired.
"""

from src.services.semantic_alignment_service import EmbeddingCache
from src.core import config


def test_config_has_defaults():
    """Runtime settings should expose expected defaults used by the service."""
    assert hasattr(config.settings, "BERTIMBAU_MODEL")


def test_embedding_cache_set_get_and_eviction():
    """EmbeddingCache should store, retrieve and evict using LRU policy."""
    cache = EmbeddingCache(max_size=2)

    cache.set("t1", "m1", [0.1, 0.2, 0.3])
    assert cache.get("t1", "m1") == [0.1, 0.2, 0.3]

    # Miss
    assert cache.get("missing", "m1") is None

    # Cause eviction
    cache.set("t2", "m1", [0.2, 0.3, 0.4])
    cache.set("t3", "m1", [0.3, 0.4, 0.5])

    assert cache.get("t1", "m1") is None
    assert cache.get("t2", "m1") == [0.2, 0.3, 0.4]
    assert cache.get("t3", "m1") == [0.3, 0.4, 0.5]


def test_cache_key_generation_is_deterministic():
    """Cache key generation should be stable and produce an MD5 hex string."""
    cache = EmbeddingCache()
    k1 = cache._get_cache_key("some text", "model-a")
    k2 = cache._get_cache_key("some text", "model-a")
    k3 = cache._get_cache_key("other text", "model-a")

    assert k1 == k2
    assert k1 != k3
    assert isinstance(k1, str) and len(k1) == 32

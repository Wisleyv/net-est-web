"""LangExtract comparison feature tests

Focus: get_enhanced_features combines base salience + langextract result
and emits comparison metrics when available. We monkeypatch the internal
extraction and comparison to avoid external deps.
"""

from types import SimpleNamespace

from src.services.langextract_provider import LangExtractProvider


def _fake_base_result(units):
    return SimpleNamespace(units=units, method="frequency")


def _unit(unit, weight):
    # span/method fields not needed for this test shape
    return {"unit": unit, "weight": weight}


def test_get_enhanced_features_with_langextract_available(monkeypatch):
    provider = LangExtractProvider()

    # Simulate availability and enabled/active path
    provider.enabled = True
    provider.langextract_available = True
    provider.observation_mode = False

    # Monkeypatch extract_with_langextract to return deterministic results
    base = _fake_base_result([_unit("termo", 0.3), _unit("chave", 0.4)])
    enhanced = _fake_base_result([_unit("termo", 0.6), _unit("claro", 0.7)])

    def fake_extract_with_langextract(text, max_units, strategy_code=None):
        return base, enhanced

    def fake_get_comparison_metrics(base_res, le_res):
        return {
            "comparison_available": True,
            "overlap_score": 0.3333,
            "quality_improvement": 0.25,
        }

    monkeypatch.setattr(
        provider, "extract_with_langextract", fake_extract_with_langextract
    )
    monkeypatch.setattr(
        provider, "get_comparison_metrics", fake_get_comparison_metrics
    )

    features = provider.get_enhanced_features(
        text="Texto técnico complexo com termos e ideias.", strategy_code="SL+"
    )

    assert isinstance(features, dict)
    assert features["langextract_available"] is True
    assert features["base_salience_units"] == 2
    assert features["methods_overlap"] == 0.3333
    assert features["quality_improvement"] == 0.25
    assert features["salience_improvement"] == (
        features["langextract_avg_weight"]
        - features["base_avg_salience_weight"]
    )


def test_get_enhanced_features_without_langextract(monkeypatch):
    provider = LangExtractProvider()

    # Force unavailable path
    provider.langextract_available = False
    provider.observation_mode = True

    # Provide deterministic base result via monkeypatch
    base = _fake_base_result([_unit("conceito", 0.5)])

    def fake_extract_with_langextract(text, max_units, strategy_code=None):
        return base, None

    monkeypatch.setattr(
        provider, "extract_with_langextract", fake_extract_with_langextract
    )

    features = provider.get_enhanced_features(
        text="Texto simples com conceito central.", strategy_code="SL+"
    )

    assert isinstance(features, dict)
    assert features["langextract_available"] is False
    assert features["base_salience_units"] == 1
    # No comparison metrics present when LE is None
    assert "methods_overlap" not in features
    assert "quality_improvement" not in features

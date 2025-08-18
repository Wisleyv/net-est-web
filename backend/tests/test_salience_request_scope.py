import pytest

from backend.src.services.comparative_analysis_service import ComparativeAnalysisService
from backend.src.models.comparative_analysis import ComparativeAnalysisRequest, AnalysisOptions

def make_request_with_texts(source: str, target: str, salience_method: str | None = None):
    opts = AnalysisOptions()
    req = ComparativeAnalysisRequest(
        source_text=source,
        target_text=target,
        analysis_options=opts,
        hierarchical_output=False,
        salience_method=salience_method
    )
    return req


@pytest.mark.asyncio
async def test_salience_provider_request_scope_does_not_mutate_service_provider():
    svc = ComparativeAnalysisService()
    # record original shared provider method (could be 'frequency' by default)
    shared_provider = getattr(svc, "salience_provider", None)
    shared_method = getattr(shared_provider, "method", None) if shared_provider else None

    # Build a request that requests a different salience method (simulate override)
    src = "Este é um parágrafo de teste com conteúdo suficiente para validação. " * 3
    tgt = "Texto simplificado de exemplo com conteúdo suficiente para validação. " * 2

    req = make_request_with_texts(src, tgt, salience_method="keybert")

    # Call the internal hierarchy builder which contains the per-request provider selection.
    await svc._build_hierarchy_async(req)

    # After processing, the shared provider method should remain as before (no mutation)
    shared_provider_after = getattr(svc, "salience_provider", None)
    shared_method_after = getattr(shared_provider_after, "method", None) if shared_provider_after else None

    assert shared_method == shared_method_after, "Service-level salience_provider.method was mutated by request override"


@pytest.mark.asyncio
async def test_paragraph_salience_normalization_behavior():
    svc = ComparativeAnalysisService()

    # Two paragraphs: one with repeated keyword to produce higher raw salience,
    # another with less repetition. Ensure normalization scales max->1.0
    para1 = "Importante importante importante. " * 10
    para2 = "Conteúdo menos repetitivo e mais variado. " * 4

    src = para1 + "\n\n" + para2
    tgt = src

    req = make_request_with_texts(src, tgt, salience_method=None)
    req.analysis_options.include_salience = True
    req.hierarchical_output = True

    hierarchy = await svc._build_hierarchy_async(req)

    src_paras = hierarchy.get("source_paragraphs", [])
    assert len(src_paras) >= 2

    saliences = [p.confidence for p in src_paras if isinstance(p.confidence, (int, float))]
    assert any(isinstance(s, (int, float)) for s in saliences)

    numeric_sal = [s for s in saliences if isinstance(s, (int, float))]
    if numeric_sal:
        mx = max(numeric_sal)
        assert mx <= 1.0 + 1e-6
        assert numeric_sal[0] >= numeric_sal[1] - 1e-6


def test_feature_extractor_salience_score_without_provider():
    from backend.src.services.feature_extractor import FeatureExtractor

    fx = FeatureExtractor()
    short_text = "teste curto"
    score = fx.salience_score(short_text, provider=None)
    assert score is None or isinstance(score, float)
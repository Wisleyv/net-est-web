"""Tests for hierarchical_output flag (M2 incremental)
Validates presence/shape of hierarchy when requested and absence by default.
"""

import pytest
from datetime import datetime
from src.services.comparative_analysis_service import ComparativeAnalysisService
from src.models.comparative_analysis import ComparativeAnalysisRequest, AnalysisOptions


@pytest.mark.asyncio
async def test_hierarchical_output_included():
    service = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
    source_text="Primeira frase. Segunda frase adicional para atingir limite mínimo de caracteres exigido pelo modelo.",
    target_text="Primeira sentença simplificada e alongada para cumprir validação. Segunda frase adaptada igualmente estendida.",
        hierarchical_output=True,
        analysis_options=AnalysisOptions(
            include_lexical_analysis=False,
            include_syntactic_analysis=False,
            include_semantic_analysis=False,
            include_readability_metrics=False,
            include_strategy_identification=False,
        ),
    )
    resp = await service.perform_comparative_analysis(req)
    assert resp.hierarchical_analysis is not None
    h = resp.hierarchical_analysis
    assert h["hierarchy_version"] == "1.1"
    assert len(h["source_paragraphs"]) == 1
    assert len(h["target_paragraphs"]) == 1
    assert "sentences" in h["source_paragraphs"][0]
    # Updated expected alignment mode after semantic paragraph alignment integration
    assert h["metadata"]["alignment_mode"] == "semantic_paragraph + sentence_cosine"


@pytest.mark.asyncio
async def test_hierarchical_output_enabled_by_feature_flag():
    """Test that hierarchical output is enabled by default when feature flag is on"""
    service = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
    source_text="Texto origem com duas frases. Mais uma sentença extra para cumprir o requisito mínimo de comprimento.",
    target_text="Texto destino com duas frases simplificadas e também ampliadas para satisfazer a validação mínima.",
        analysis_options=AnalysisOptions(
            include_lexical_analysis=False,
            include_syntactic_analysis=False,
            include_semantic_analysis=False,
            include_readability_metrics=False,
            include_strategy_identification=False,
        ),
    )
    resp = await service.perform_comparative_analysis(req)
    # With feature flag enabled, hierarchical analysis should be present by default
    assert resp.hierarchical_analysis is not None
    h = resp.hierarchical_analysis
    assert h["hierarchy_version"] == "1.1"
    assert len(h["source_paragraphs"]) == 1
    assert len(h["target_paragraphs"]) == 1
    assert "sentences" in h["source_paragraphs"][0]


@pytest.mark.asyncio
async def test_hierarchical_output_with_micro_spans_version_bump():
    service = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
        source_text="Primeira frase longa suficiente para micro spans funcionar adequadamente. Segunda frase também extensa.",
        target_text="Primeira frase simplificada igualmente longa para ativar micro spans. Segunda frase adaptada também extensa.",
        hierarchical_output=True,
        analysis_options=AnalysisOptions(
            include_lexical_analysis=False,
            include_syntactic_analysis=False,
            include_semantic_analysis=False,
            include_readability_metrics=False,
            include_strategy_identification=False,
            include_micro_spans=True,
        ),
    )
    resp = await service.perform_comparative_analysis(req)
    h = resp.hierarchical_analysis
    assert h is not None
    assert h["hierarchy_version"] == "1.2"
    # Ensure micro_spans present in at least one sentence
    src_sentences = h["source_paragraphs"][0]["sentences"]
    assert any("micro_spans" in s and s["micro_spans"] for s in src_sentences)

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

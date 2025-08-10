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
        source_text="Primeira frase. Segunda frase.",
        target_text="Primeira sentença simplificada. Segunda frase adaptada.",
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
    assert h["metadata"]["alignment_mode"] == "naive_index_pairing"


@pytest.mark.asyncio
async def test_hierarchical_output_absent_by_default():
    service = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
        source_text="Texto origem com duas frases. Mais uma.",
        target_text="Texto destino com duas frases simplificadas. Outra.",
        analysis_options=AnalysisOptions(
            include_lexical_analysis=False,
            include_syntactic_analysis=False,
            include_semantic_analysis=False,
            include_readability_metrics=False,
            include_strategy_identification=False,
        ),
    )
    resp = await service.perform_comparative_analysis(req)
    assert resp.hierarchical_analysis is None

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

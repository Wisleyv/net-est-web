"""Tests for paragraph + sentence hierarchical alignment (M2 advanced)
Focus: multi-paragraph segmentation, alignment metadata, unmatched handling, split/merge relations.
"""

import pytest
from src.services.comparative_analysis_service import ComparativeAnalysisService
from src.models.comparative_analysis import ComparativeAnalysisRequest, AnalysisOptions

MULTI_SOURCE = (
    "Primeiro parágrafo com ideias complexas. Ainda continua.\n\n"
    "Segundo parágrafo com outra direção. Frase adicional.\n\n"
    "Terceiro parágrafo isolado."
)

MULTI_TARGET = (
    "Primeiro parágrafo com ideias simplificadas. Continua simplificado.\n\n"
    "Segundo parágrafo com direção modificada. Frase extra simplificada."
)

@pytest.mark.asyncio
async def test_paragraph_alignment_counts():
    service = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
        source_text=MULTI_SOURCE,
        target_text=MULTI_TARGET,
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
    h = resp.hierarchical_analysis
    assert h is not None
    # Source has 3 paragraphs; target 2
    assert len(h["source_paragraphs"]) == 3
    assert len(h["target_paragraphs"]) == 2
    # Metadata should list unaligned source or target paragraphs
    meta = h["metadata"]
    assert "paragraph_unaligned_source" in meta
    assert 2 in meta["paragraph_unaligned_source"]  # third source paragraph likely unaligned

@pytest.mark.asyncio
async def test_sentence_alignment_relations_present():
    service = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
        source_text="Parágrafo único. Segunda frase longa que pode ser dividida. Terceira.\n\nOutro bloco adicional.",
        target_text="Parágrafo único simplificado. Segunda frase dividida. Outra parte. Terceira simplificada.",
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
    h = resp.hierarchical_analysis
    assert h is not None
    # Check at least one source sentence has alignment list
    first_para = h["source_paragraphs"][0]
    aligned_any = any(isinstance(s.get("alignment"), list) and s["alignment"] for s in first_para["sentences"])
    assert aligned_any

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

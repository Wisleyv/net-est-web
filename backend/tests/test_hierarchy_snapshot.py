"""Snapshot-style structural test for hierarchical analysis JSON (M2).
We don't store an external snapshot file; instead we validate key invariant structure keys.
"""

import pytest
from src.services.comparative_analysis_service import ComparativeAnalysisService
from src.models.comparative_analysis import ComparativeAnalysisRequest, AnalysisOptions

TEXT_SRC = "Um parágrafo. Segunda sentença. Terceira sentença final."
TEXT_TGT = "Um parágrafo simplificado. Segunda sentença adaptada. Terceira sentença final reduzida."

EXPECTED_KEYS = {"hierarchy_version", "source_paragraphs", "target_paragraphs", "metadata"}
PARAGRAPH_KEYS = {"paragraph_id", "index", "role", "text", "sentences"}
SENTENCE_KEYS = {"sentence_id", "index", "text", "alignment"}

@pytest.mark.asyncio
async def test_hierarchy_structure_keys():
    service = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
        source_text=TEXT_SRC,
        target_text=TEXT_TGT,
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
    assert EXPECTED_KEYS.issubset(h.keys())
    assert len(h["source_paragraphs"]) == 1
    para = h["source_paragraphs"][0]
    assert PARAGRAPH_KEYS.issubset(para.keys())
    assert para["role"] == "source"
    assert para["sentences"]
    first_sentence = para["sentences"][0]
    assert SENTENCE_KEYS.issubset(first_sentence.keys())

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

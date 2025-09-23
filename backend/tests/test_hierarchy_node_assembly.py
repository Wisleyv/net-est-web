"""Hierarchy node assembly tests (micro-spans + offsets)

Covers:
- Paragraph → sentence assembly with alignment metadata present
- Optional micro-spans extraction wired when flags are enabled
- Salience normalization bounds [0,1]
- Sentence/micro-span offsets are within paragraph bounds
"""

import pytest
from src.services.comparative_analysis_service import (
    ComparativeAnalysisService,
)
from src.models.comparative_analysis import (
    ComparativeAnalysisRequest,
    AnalysisOptions,
)


@pytest.mark.asyncio
async def test_hierarchy_node_assembly_with_micro_spans_and_offsets():
    service = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
        source_text=(
            "Este é um texto de origem com frases suficientes para ativar o "
            "pipeline. A extração de micro spans deve encontrar unidades "
            "salientes legíveis."
        ),
        target_text=(
            "Este é um texto simplificado de destino com frases suficientes. "
            "Os micro spans também devem ser extraídos de modo consistente."
        ),
        hierarchical_output=True,
        analysis_options=AnalysisOptions(
            include_lexical_analysis=False,
            include_syntactic_analysis=False,
            include_semantic_analysis=False,
            include_readability_metrics=False,
            include_strategy_identification=False,
            include_salience=True,
            include_micro_spans=True,
        ),
    )

    resp = await service.perform_comparative_analysis(req)
    assert resp.hierarchical_analysis is not None
    h = resp.hierarchical_analysis

    # Basic structure
    assert h["hierarchy_version"] == "1.2"  # version bump with micro-spans
    assert isinstance(h["source_paragraphs"], list) and isinstance(
        h["target_paragraphs"], list
    )
    assert (
        len(h["source_paragraphs"]) >= 1
        and len(h["target_paragraphs"]) >= 1
    )

    src_p0 = h["source_paragraphs"][0]
    tgt_p0 = h["target_paragraphs"][0]

    assert src_p0["role"] == "source" and tgt_p0["role"] == "target"
    assert isinstance(src_p0.get("sentences"), list) and isinstance(
        tgt_p0.get("sentences"), list
    )
    assert len(src_p0["sentences"]) >= 1 and len(tgt_p0["sentences"]) >= 1

    # Salience normalization per sentence (if present) should be within [0,1]
    for s in src_p0["sentences"]:
        sal = s.get("salience")
        if isinstance(sal, (int, float)):
            assert 0.0 <= sal <= 1.0

    # Micro-spans present in at least one sentence and within bounds
    has_micro = False
    for s in src_p0["sentences"]:
        sent_text = s["text"]
        mspans = s.get("micro_spans") or []
        if mspans:
            has_micro = True
        for m in mspans:
            start = m.get("start")
            end = m.get("end")
            assert (
                isinstance(start, int)
                and isinstance(end, int)
                and 0 <= start < end <= len(sent_text)
            )
            msal = m.get("salience")
            if isinstance(msal, (int, float)):
                assert 0.0 <= msal <= 1.0
            # text slice sanity check
            assert sent_text[start:end] == m.get("text")

    assert has_micro, "expected at least one micro-span in source paragraph 0"

    # Metadata alignment mode should reflect semantic + cosine flow
    assert h["metadata"].get("alignment_mode") == (
        "semantic_paragraph + sentence_cosine"
    )

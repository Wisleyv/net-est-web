import pytest
import asyncio
from src.services.comparative_analysis_service import ComparativeAnalysisService
from src.models.comparative_analysis import ComparativeAnalysisRequest, AnalysisOptions

SOURCE = (
    "Parágrafo um com conceito importante.\n\nParágrafo dois com outro tema e detalhes adicionais." * 1
)
TARGET = (
    "Parágrafo um simplificado com conceito.\n\nSegundo parágrafo simplificado com tema." * 1
)

def test_salience_present_when_enabled():
    svc = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
        source_text=SOURCE,
        target_text=TARGET,
        hierarchical_output=True,
        analysis_options=AnalysisOptions(include_salience=True)
    )
    resp = asyncio.run(svc.perform_comparative_analysis(req))
    assert resp.hierarchical_analysis is not None
    # At least one sentence should have salience value not None
    src_paras = resp.hierarchical_analysis['source_paragraphs']
    assert any(any(s.get('salience') is not None for s in p['sentences']) for p in src_paras)

def test_salience_absent_when_disabled():
    svc = ComparativeAnalysisService()
    req = ComparativeAnalysisRequest(
        source_text=SOURCE,
        target_text=TARGET,
        hierarchical_output=True,
        analysis_options=AnalysisOptions(include_salience=False)
    )
    resp = asyncio.run(svc.perform_comparative_analysis(req))
    src_paras = resp.hierarchical_analysis['source_paragraphs']
    # All salience fields should be None when disabled
    assert all(p.get('salience') is None for p in src_paras)
    assert all(all(s.get('salience') is None for s in p['sentences']) for p in src_paras)

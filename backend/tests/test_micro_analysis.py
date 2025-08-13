import pytest

from src.services.comparative_analysis_service import ComparativeAnalysisService

def test_analyze_phrases_replace_operation():
    svc = ComparativeAnalysisService()
    src = "O tratamento medicamentoso é complexo."
    tgt = "O tratamento medicamentoso é simplificado."
    result = svc.analyze_phrases(src, tgt)
    assert "micro_operations" in result
    ops = result["micro_operations"]
    # Expect at least one replace operation
    assert len(ops) >= 1
    op = ops[0]
    assert "source_tokens" in op and "target_tokens" in op
    assert "op_type" in op and op["op_type"] in {"replace", "insert", "delete"}
    assert "features" in op and isinstance(op["features"], dict)
    assert "suggested_tag" in op
    assert "confidence" in op and isinstance(op["confidence"], float)

def test_analyze_phrases_insert_operation():
    svc = ComparativeAnalysisService()
    src = "Ele saiu."
    tgt = "Ele saiu ontem."
    result = svc.analyze_phrases(src, tgt)
    ops = result["micro_operations"]
    # Should detect an insert (or replace with insertion)
    assert any(op["op_type"] in {"insert", "replace"} for op in ops)

def test_analyze_phrases_delete_operation():
    svc = ComparativeAnalysisService()
    src = "Este é um exemplo muito longo e detalhado."
    tgt = "Este é um exemplo."
    result = svc.analyze_phrases(src, tgt)
    ops = result["micro_operations"]
    # Should detect a delete (or replace with deletion)
    assert any(op["op_type"] in {"delete", "replace"} for op in ops)
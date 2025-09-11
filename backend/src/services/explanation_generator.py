from __future__ import annotations
"""Minimal explanation generator mapping basic evidence to Portuguese rationale.
Scope (initial Phase 4f): provide simple template for a subset of strategy codes.
"""
from typing import List, Optional
from src.models.annotation import Annotation

# Strategy description templates (extend incrementally)
TEMPLATES = {
    'RP+': 'Fragmentação Sintática: redução média do comprimento das frases em {delta_tokens} tokens.',
    'SL+': 'Adequação de Vocabulário: substituições léxicas sugerem simplificação (confiança {confidence:.0%}).'
}

def generate_explanation(annotation: Annotation, feature_hints: Optional[dict] = None) -> Optional[str]:
    code = annotation.strategy_code
    tpl = TEMPLATES.get(code)
    if not tpl:
        return None
    feature_hints = feature_hints or {}
    # Simple heuristics from evidence strings if available
    delta_tokens = feature_hints.get('sentence_length_delta') or _infer_sentence_delta(annotation.evidence)
    confidence = annotation.confidence or 0.0
    try:
        return tpl.format(delta_tokens=delta_tokens, confidence=confidence)
    except Exception:
        return None

def _infer_sentence_delta(evidence: Optional[List[str]]):
    if not evidence:
        return '?'
    for e in evidence:
        if 'sent_len_delta=' in e:
            try:
                return int(e.split('sent_len_delta=')[1].split(';')[0])
            except Exception:
                continue
    return '?'

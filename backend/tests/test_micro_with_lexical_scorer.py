import json
from pathlib import Path

from src.strategies.stage_micro import MicroStageEvaluator
from src.strategies.lexical_complexity import LexicalComplexityScorer
from src.strategies.strategy_types import StrategyFeatures


def load_dummy_freq():
    p = Path(__file__).parent / "fixtures" / "dummy_freq.json"
    return json.loads(p.read_text())


def make_fake_features():
    return StrategyFeatures(
        length_ratio=1.0,
        word_count_ratio=1.0,
        sentence_count_ratio=1.0,
        avg_word_length_ratio=0.8,
        semantic_similarity=0.8,
        lexical_overlap=0.4,
        complexity_reduction=0.2,
        voice_change_score=0.0,
        explicitness_score=0.0,
        structure_change_score=0.0,
        pronoun_reduction_score=0.0,
        strategy_positions=[],
    )


def test_micro_detects_simplification_with_scorer():
    freq = load_dummy_freq()
    scorer = LexicalComplexityScorer(freq)
    evaluator = MicroStageEvaluator(lexical_scorer=scorer)

    src = "A utilização de terminologia complexa e palavras técnicas impede a compreensão."
    tgt = "Uso de palavras simples para facilitar a leitura."

    features = make_fake_features()
    evidences, _ = evaluator.evaluate(features, src, tgt, adaptive_thresholds=None)

    codes = [e.strategy_code for e in evidences]
    assert any(c == 'SL+' for c in codes)

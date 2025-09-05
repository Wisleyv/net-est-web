"""
Semantic integration tests: validate that meso/micro evaluators produce
expected simplification strategy labels for controlled text pairs.
Mocks features or uses a lightweight FeatureExtractor to create StrategyFeatures.
"""

import pytest
from src.strategies.stage_meso import MesoStageEvaluator
from src.strategies.stage_micro import MicroStageEvaluator
from src.strategies.strategy_types import StrategyFeatures


class DummySemanticModel:
    """Lightweight semantic model that returns highly similar embeddings for any inputs.
    Used to force semantic similarity computations to be high in tests.
    """
    def encode(self, texts, convert_to_tensor=True):
        # Return a simple identical vector for every input so cosine similarity is 1.0
        try:
            import torch
            dim = 8
            vec = [1.0] + [0.0] * (dim - 1)
            return torch.tensor([vec for _ in texts], dtype=torch.float32)
        except Exception:
            # Fallback: return list of lists (some code paths expect tensors)
            return [[1.0] + [0.0] * 7 for _ in texts]


def make_fake_features():
    # Minimal StrategyFeatures-like object; the real class may be a dataclass
    # Provide attributes accessed by evaluators: structure_change_score, length_ratio, etc.
    # Construct a full StrategyFeatures dataclass with reasonable values
    return StrategyFeatures(
        length_ratio=1.0,
        word_count_ratio=1.0,
        sentence_count_ratio=1.0,
    # avg_word_length_ratio is target_avg_len / source_avg_len; <1 indicates simplification
    avg_word_length_ratio=0.8,
        semantic_similarity=0.8,
        lexical_overlap=0.4,
        complexity_reduction=0.2,
        voice_change_score=0.1,
        explicitness_score=0.1,
        structure_change_score=0.6,
        pronoun_reduction_score=0.0,
        strategy_positions=[],
    )


def test_meso_detects_fragmentation():
    evaluator = MesoStageEvaluator(semantic_model=DummySemanticModel())
    features = make_fake_features()

    # Make source a single long sentence and target two sentences to trigger fragmentation
    source = (
        "Uma frase muito longa com várias cláusulas e informações complexas que normalmente seria dividida em várias partes "
        "mas aqui é mantida como uma única sentença para o teste"
    )
    target = "Uma frase curta. Outra frase curta."

    evidences, cont = evaluator.evaluate(features, source, target, adaptive_thresholds=None, complete_analysis_mode=True)

    codes = [e.strategy_code for e in evidences]
    # RP+ (fragmentation) should be among detected strategies for this pair
    assert any(c == 'RP+' for c in codes)


def test_micro_detects_lexical_simplification():
    evaluator = MicroStageEvaluator()
    features = make_fake_features()

    source = "A utilização de terminologia complexa e palavras técnicas impede a compreensão."
    target = "Uso de palavras simples para facilitar a leitura."

    evidences, _ = evaluator.evaluate(features, source, target)
    codes = [e.strategy_code for e in evidences]

    # Expect lexical simplification evidence (SL+)
    assert any(c == 'SL+' for c in codes)

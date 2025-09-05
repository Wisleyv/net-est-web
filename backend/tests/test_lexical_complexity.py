import json
from pathlib import Path

from src.strategies.lexical_complexity import LexicalComplexityScorer


def load_dummy_freq():
    p = Path(__file__).parent / "fixtures" / "dummy_freq.json"
    return json.loads(p.read_text())


def test_word_complexity_ordering():
    freq = load_dummy_freq()
    scorer = LexicalComplexityScorer(freq)

    c_usar = scorer.word_complexity("usar")
    c_utilizar = scorer.word_complexity("utilizar")

    assert c_utilizar > c_usar, f"Expected 'utilizar' to be more complex than 'usar' ({c_utilizar} <= {c_usar})"


def test_oov_handling_and_normalization():
    freq = load_dummy_freq()
    scorer = LexicalComplexityScorer(freq)

    known = scorer.word_complexity("informação")
    oov = scorer.word_complexity("quark")

    # Unknown word should be treated as rarer (higher complexity)
    assert oov >= known


def test_text_and_compare():
    freq = load_dummy_freq()
    scorer = LexicalComplexityScorer(freq)

    src = ["utilizar", "a"]
    tgt = ["usar", "a"]

    delta, simplified = scorer.compare(src, tgt, threshold=0.01)

    assert delta > 0
    assert simplified is True

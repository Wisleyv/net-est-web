import math
from collections import Counter
from functools import lru_cache
from typing import List, Dict, Optional, Tuple


class LexicalComplexityScorer:
    """Lean lexical complexity scorer: frequency + length + OOV handling + caching.

    Embedding-density and LM surprisal are intentionally left as optional plug-ins
    or stubs to be implemented later.
    """

    def __init__(
        self,
        frequency_dict: Dict[str, int],
        embedding_model: Optional[object] = None,
        oov_freq: int = 1,
    ):
        self.frequency_dict = Counter({k.lower(): int(v) for k, v in (frequency_dict or {}).items()})
        self.total_freq = sum(self.frequency_dict.values()) + max(1, oov_freq)
        self.embedding_model = embedding_model
        self.oov_freq = oov_freq

        # Simple cache for computed word complexities
        self._cache: Dict[str, float] = {}

    def word_frequency_score(self, word: str) -> float:
        """Higher information content = higher complexity.

        We use smoothed counts to avoid zero-probability for unseen words.
        """
        w = word.lower()
        freq = self.frequency_dict.get(w, 0) + self.oov_freq
        prob = freq / self.total_freq
        # information content; cap to avoid extreme values
        info = -math.log(max(prob, 1e-12))
        # normalize by a reasonable cap (log(total_freq)) to bring into ~[0,1]
        cap = math.log(max(self.total_freq, 2))
        return min(info / (cap + 1e-9), 1.0)

    def word_length_score(self, word: str) -> float:
        """Secondary heuristic: longer words are generally harder. Normalized."""
        # weight length lightly; normalize by expecting words up to 20 chars
        return min((len(word) * 0.1) / 2.0, 1.0)

    def embedding_density_score(self, word: str, k: int = 10) -> float:
        """Optional: words in sparse semantic neighborhoods are harder.

        Not implemented in the lean scorer — return 0.0 if no model, or raise
        NotImplementedError when an embedding_model is provided but not supported.
        """
        if not self.embedding_model:
            return 0.0
        raise NotImplementedError("Embedding-density scoring is not implemented in the lean scorer")

    def word_complexity(self, word: str, weights: Optional[Dict[str, float]] = None) -> float:
        """Combine signals into a single complexity score in [0,1]."""
        if not word:
            return 0.0

        w = word.lower()
        if w in self._cache:
            return self._cache[w]

        weights = weights or {"freq": 0.7, "length": 0.3, "embed": 0.0}

        f = self.word_frequency_score(word)
        l = self.word_length_score(word)
        e = self.embedding_density_score(word) if weights.get("embed", 0.0) > 0 else 0.0

        score = f * weights.get("freq", 0.7) + l * weights.get("length", 0.3) + e * weights.get("embed", 0.0)

        # Apply an OOV baseline so truly unseen words are treated as harder.
        if w not in self.frequency_dict:
            # Ensure OOV tokens have a high baseline complexity; keeps behavior
            # deterministic for tests and simpler to reason about in early stages.
            score = max(score, 0.9)

        # Clamp and cache
        score = max(0.0, min(1.0, score))
        self._cache[w] = score
        return score

    def text_complexity(self, tokens: List[str], **kwargs) -> float:
        """Average complexity across tokens in a text."""
        if not tokens:
            return 0.0
        scores = [self.word_complexity(t, **kwargs) for t in tokens if t]
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    def compare(self, source_tokens: List[str], target_tokens: List[str], threshold: float = 0.05) -> Tuple[float, bool]:
        """Compare source vs target complexity. Return (delta, simplified_bool).

        delta = avg_source - avg_target. If delta >= threshold, report simplification.
        This is a sentence-level, coarse comparison. For token-level alignment use
        more advanced logic outside this lean scorer.
        """
        src = self.text_complexity(source_tokens)
        tgt = self.text_complexity(target_tokens)
        delta = src - tgt
        return delta, delta >= threshold


__all__ = ["LexicalComplexityScorer"]

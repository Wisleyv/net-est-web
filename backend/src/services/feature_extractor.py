"""
Feature extractor scaffolding for hierarchical feature population.

Provides:
- FeatureExtractor class with methods:
    - extract_key_phrases(text): LangExtract placeholder (frequency + heuristic multiword)
    - sentence_pos_features(text): spaCy-based POS and simple linguistic features (falls back gracefully)
    - salience_score(text, provider=None): aggregate salience from provider or frequency heuristic

Designed to be lightweight and easily testable/mocked during unit tests.

Consumers:
- ComparativeAnalysisService will import FeatureExtractor and call its methods when building hierarchy
  to populate SentenceNode.key_phrases, SentenceNode.salience_score, PhraseNode.key_phrases, PhraseNode.features, etc.
"""
from __future__ import annotations

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

try:
    import spacy
    _has_spacy = True
except Exception:
    spacy = None  # type: ignore
    _has_spacy = False

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Orchestrates lightweight feature extraction. Designed so internals can be individually tested.
    """

    def __init__(self, nlp_model_name: str = "pt_core_news_sm"):
        self.nlp = None
        if _has_spacy:
            try:
                self.nlp = spacy.load(nlp_model_name)
                logger.info(f"spaCy model '{nlp_model_name}' loaded for feature extraction.")
            except Exception:
                logger.warning(f"spaCy model '{nlp_model_name}' not available, POS features disabled.")
                self.nlp = None
        else:
            logger.info("spaCy not installed - POS features disabled.")

    # -----------------------------
    # Key-phrase extraction (LangExtract placeholder)
    # -----------------------------
    def extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """
        Rudimentary key-phrase extractor as a LangExtract placeholder.
        Strategy:
        - Extract candidate ngrams (1..3) after simple tokenization.
        - Score by frequency * length_boost, penalize stopwords-only ngrams.
        - Return top-N normalized phrases.

        This is deterministic and easy to mock in tests. Replace with real LangExtract integration later.
        """
        if not text or not text.strip():
            return []

        tokens = self._tokenize(text)
        # Build ngrams 1..3
        ngram_counts: Counter = Counter()
        for n in (1, 2, 3):
            for i in range(len(tokens) - n + 1):
                ngram = tokens[i:i + n]
                # skip sequences that are entirely punctuation/stopwords
                if all(self._is_stopword_or_short(t) for t in ngram):
                    continue
                phrase = " ".join(ngram)
                ngram_counts[phrase] += 1

        if not ngram_counts:
            return []

        # Score function: frequency * length_boost (prefers multiword), longer phrases slightly favored
        scored = []
        for phrase, freq in ngram_counts.items():
            length_boost = 1.0 + 0.25 * len(phrase.split())
            score = freq * length_boost
            scored.append((score, phrase))

        scored.sort(reverse=True, key=lambda x: (x[0], -len(x[1])))
        top = [p for _, p in scored[:max_phrases]]
        # Normalize phrase spacing and case
        normalized = [self._normalize_phrase(p) for p in top]
        return normalized

    # -----------------------------
    # POS and linguistic features using spaCy (if available)
    # -----------------------------
    def sentence_pos_features(self, sentence: str) -> Dict[str, Any]:
        """
        Returns sentence-level linguistic features:
          - token_count, avg_word_length, syllable_estimate
          - pos_distribution: dict of POS tag -> count
          - lemma_set: unique lemmas (if available)
        Falls back to heuristic tokenization if spaCy is not loaded.
        """
        if not sentence:
            return {}

        toks = self._tokenize(sentence)
        token_count = len(toks)
        avg_word_len = sum(len(t) for t in toks) / token_count if token_count else 0

        # syllable estimate: vowel groups per token aggregated
        syllables = sum(self._count_syllables(t) for t in toks)
        syllable_est = syllables

        pos_distribution: Dict[str, int] = {}
        lemmas: List[str] = []

        if self.nlp:
            try:
                doc = self.nlp(sentence)
                for token in doc:
                    pos_distribution[token.pos_] = pos_distribution.get(token.pos_, 0) + 1
                    lemmas.append(token.lemma_.lower())
            except Exception as e:
                logger.debug(f"spaCy POS tagging failed: {e}")
                # fallback to heuristics below
                pos_distribution = {}
                lemmas = [t.lower() for t in toks]
        else:
            # Heuristic POS split by simple rules (nouns/verbs detection naive)
            verbs = {"é", "foi", "está", "são", "ser", "fazer", "fez", "faz"}
            for t in toks:
                tl = t.lower()
                if tl in verbs or tl.endswith("ar") or tl.endswith("er") or tl.endswith("ir"):
                    pos_distribution["VERB"] = pos_distribution.get("VERB", 0) + 1
                elif tl[0].isupper():
                    pos_distribution["PROPN"] = pos_distribution.get("PROPN", 0) + 1
                else:
                    pos_distribution["NOUN"] = pos_distribution.get("NOUN", 0) + 1
            lemmas = [t.lower() for t in toks]

        features = {
            "token_count": token_count,
            "avg_word_length": avg_word_len,
            "syllable_estimate": syllable_est,
            "pos_distribution": pos_distribution,
            "lemmas": list(dict.fromkeys(lemmas))[:20],  # unique lemmas, limited
        }
        return features

    # -----------------------------
    # Salience scoring: provider or frequency fallback
    # -----------------------------
    def salience_score(self, text: str, provider: Optional[Any] = None, max_units: int = 12) -> Optional[float]:
        """
        Return a normalized salience score in 0..1.
        If provider (SalienceProvider-like) is provided and has .extract(text, max_units),
        use it; otherwise use frequency-based heuristic.

        The method returns None only if text empty or an error occurs.
        """
        if not text or not text.strip():
            return None

        if provider is not None:
            try:
                res = provider.extract(text, max_units=max_units)
                units = getattr(res, "units", None)
                if units:
                    weights = [u.get("weight", 0.0) for u in units if isinstance(u, dict)]
                    if weights:
                        # normalize by max
                        m = max(weights)
                        if m > 0:
                            norm = sum(weights) / (len(weights) * m)
                            return float(norm)
                        return 0.0
                # fallback to 0.0 if no units
                return 0.0
            except Exception as e:
                logger.debug(f"Salience provider extract failed: {e}")

        # Frequency heuristic: take top key phrase frequency vs total ngrams
        toks = self._tokenize(text)
        if not toks:
            return None
        counts = Counter(toks)
        most_common_freq = counts.most_common(1)[0][1] if counts else 0
        # normalize by sentence length
        norm = most_common_freq / len(toks)
        # map heuristic into 0..1 with smoothing
        score = min(1.0, norm * 2.0)
        return float(score)

    # -----------------------------
    # Utilities
    # -----------------------------
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        # Keep accent characters, split words and keep contractions
        toks = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:'[A-Za-zÀ-ÖØ-öø-ÿ]+)?", text, flags=re.UNICODE)
        return toks

    @staticmethod
    def _count_syllables(word: str) -> int:
        # Very small heuristic: count vowel groups (Portuguese-friendly)
        w = word.lower()
        groups = re.findall(r"[aeiouáéíóúâêôãõü]+", w)
        return max(1, len(groups))

    @staticmethod
    def _is_stopword_or_short(token: str) -> bool:
        t = token.lower()
        if len(t) <= 2:
            return True
        stopwords = {
            "o", "a", "os", "as", "um", "uma", "de", "da", "do", "das", "dos",
            "e", "é", "que", "em", "para", "com", "se", "por", "ou", "mas",
            "no", "na", "nos", "nas", "um", "uma"
        }
        return t in stopwords

    @staticmethod
    def _normalize_phrase(phrase: str) -> str:
        # Normalize whitespace and lower-case (but keep accents)
        return re.sub(r"\s+", " ", phrase.strip()).lower()
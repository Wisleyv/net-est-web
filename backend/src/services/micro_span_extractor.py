"""MicroSpan Extractor (M4 Phase 1)
Heuristic ngram-based micro-span extraction for Portuguese sentences.

Design goals:
 - Deterministic scoring for stable tests.
 - Lightweight (regex tokenization + simple stats).
 - Overlap avoidance (keep highest score span when overlaps occur).
 - LRU cache to prevent recomputation on repeated sentences.

Scoring formula (per ngram):
  score = frequency * length_factor * position_factor * rarity_factor

Where:
  frequency      = raw count of lowercase ngram occurrences
  length_factor  = 1 + (len(ngram_tokens)-2) * 0.15   (bigrams baseline)
  position_factor= 1 - (abs(center_idx - mid_idx)/max(1, mid_idx)) * 0.4
  rarity_factor  = avg( 1 + (1/max_token_freq_adjusted) ) over tokens, capped

After scoring, top-K non-overlapping spans kept; scores normalized to max=1.0 and
exposed via 'salience' field (mapped onto MicroSpanNode.salience).
"""
from __future__ import annotations
from typing import List, Dict, Tuple
import re
import os
import hashlib
from collections import OrderedDict, defaultdict

try:
    # Reuse stopwords from salience provider if available
    from .salience_provider import PORTUGUESE_STOPWORDS as PT_STOPWORDS  # type: ignore
except Exception:  # pragma: no cover
    PT_STOPWORDS = set()


class MicroSpanExtractor:
    def __init__(self,
                 mode: str = "ngram-basic",
                 ngram_min: int = 2,
                 ngram_max: int = 4,
                 max_spans: int = 5):
        self.mode = mode
        self.ngram_min = ngram_min
        self.ngram_max = ngram_max
        self.max_spans = max_spans
        try:
            self._cache_max = int(os.getenv("MICRO_SPAN_CACHE_MAX", "256"))
        except ValueError:
            self._cache_max = 256
        # LRU cache (OrderedDict as manual implementation)
        self._cache = OrderedDict()  # type: ignore

    # Public API
    def extract(self, sentence: str) -> List[Dict]:
        if not sentence or len(sentence.strip()) < 15:
            return []
        key = self._make_key(sentence)
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached
        if self.mode == "ngram-basic":
            spans = self._extract_ngram_basic(sentence)
        else:
            spans = []
        self._cache[key] = spans
        if len(self._cache) > self._cache_max:
            while len(self._cache) > self._cache_max:
                self._cache.popitem(last=False)
        return spans

    # Internal helpers
    def _tokenize(self, text: str) -> List[Tuple[str,int,int]]:
        tokens = []
        for m in re.finditer(r"\b\w+\b", text, re.UNICODE):
            tokens.append((m.group(0), m.start(), m.end()))
        return tokens

    def _make_key(self, sentence: str) -> str:
        h = hashlib.md5(sentence.lower().encode('utf-8')).hexdigest()
        return f"{self.mode}:{self.ngram_min}-{self.ngram_max}:{self.max_spans}:{h}"

    def _extract_ngram_basic(self, sentence: str) -> List[Dict]:
        tokens = self._tokenize(sentence)
        if len(tokens) < self.ngram_min:
            return []
        # Build lowercase token list for frequency stats
        lower_tokens = [t[0].lower() for t in tokens]
        token_freq: Dict[str,int] = defaultdict(int)
        for t in lower_tokens:
            token_freq[t] += 1
        max_token_freq = max(token_freq.values()) if token_freq else 1

        candidates: List[Tuple[float,int,int,str]] = []  # (score,start,end,text)

        for n in range(self.ngram_min, self.ngram_max+1):
            for i in range(0, len(tokens)-n+1):
                slice_tokens = tokens[i:i+n]
                raw_words = [w for w,_,_ in slice_tokens]
                # Trim stopwords at boundaries
                while raw_words and raw_words[0].lower() in PT_STOPWORDS:
                    slice_tokens = slice_tokens[1:]
                    raw_words = raw_words[1:]
                while raw_words and raw_words and raw_words[-1].lower() in PT_STOPWORDS:
                    slice_tokens = slice_tokens[:-1]
                    raw_words = raw_words[:-1]
                if len(raw_words) < self.ngram_min:
                    continue
                # Basic filters
                if any(len(w) < 3 for w in raw_words):
                    continue
                ngram_text = " ".join(raw_words)
                # Frequency (count occurrences of exact lowercase sequence in lower_tokens sliding window)
                seq = [w.lower() for w in raw_words]
                freq = 0
                for j in range(0, len(lower_tokens)-len(seq)+1):
                    if lower_tokens[j:j+len(seq)] == seq:
                        freq += 1
                length_factor = 1 + (len(raw_words)-2) * 0.15
                # Position factor (centered preference)
                center_idx = i + (len(slice_tokens)-1)/2
                mid_idx = (len(tokens)-1)/2
                position_factor = 1 - (abs(center_idx - mid_idx)/max(1, mid_idx)) * 0.4
                rarity_vals = []
                for w in seq:
                    rarity_vals.append(1 + (1 / (token_freq[w]) ))
                rarity_factor = sum(rarity_vals)/len(rarity_vals)
                score = freq * length_factor * position_factor * rarity_factor
                start = slice_tokens[0][1]
                end = slice_tokens[-1][2]
                candidates.append((score, start, end, ngram_text))

        if not candidates:
            return []
        # Sort candidates by score desc, then earlier start, shorter span
        candidates.sort(key=lambda x: (-x[0], x[1], x[2]-x[1]))
        accepted: List[Tuple[float,int,int,str]] = []
        occupied: List[Tuple[int,int]] = []
        for cand in candidates:
            if len(accepted) >= self.max_spans:
                break
            _, s, e, _ = cand
            overlap = any(not (e <= os or s >= oe) for os, oe in occupied)
            if overlap:
                continue
            accepted.append(cand)
            occupied.append((s,e))

        if not accepted:
            return []
        max_score = max(a[0] for a in accepted) or 1.0
        spans: List[Dict] = []
        for idx, (score, s, e, text) in enumerate(accepted):
            spans.append({
                "span_id": f"ms-{s}-{e}",
                "text": sentence[s:e],
                "start": s,
                "end": e,
                "salience": score / max_score,
                "strategies": [],
                "method": self.mode,
            })
        return spans


__all__ = ["MicroSpanExtractor"]

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

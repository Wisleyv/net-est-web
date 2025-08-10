"""Salience Provider (Milestone M3)
Extracts salient units (key tokens/phrases) from Portuguese text with pluggable methods.
Methods hierarchy attempted in order:
 1. keybert  (if installed and method='keybert')
 2. yake     (if installed and method='yake')
 3. frequency (default fallback, language‑aware stopword filtering)

Returned units structure:
    [ { 'unit': str, 'weight': float, 'span': (start,end), 'method': str } ]

Deterministic fallback ensures reproducible tests.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import hashlib
from collections import OrderedDict
import os
import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

try:  # Optional imports
    from keybert import KeyBERT  # type: ignore
    _KEYBERT_AVAILABLE = True
except Exception:  # pragma: no cover
    _KEYBERT_AVAILABLE = False

try:  # Optional
    import yake  # type: ignore
    _YAKE_AVAILABLE = True
except Exception:  # pragma: no cover
    _YAKE_AVAILABLE = False

PORTUGUESE_STOPWORDS = set([
    # Core functional words (subset to keep list compact; extend as needed)
    'a','o','as','os','um','uma','uns','umas','de','do','da','dos','das','em','no','na','nos','nas','por','para','com',
    'sem','sob','sobre','entre','e','ou','mas','porque','que','quem','quando','onde','como','qual','quais',
    'se','sua','seu','seus','suas','meu','minha','meus','minhas','teu','tua','teus','tuas','este','esta','estes','estas',
    'isso','isto','aquele','aquela','aqueles','aquelas','era','ser','foi','são','está','estão','estar','será','seriam',
    'há','havia','ter','tem','têm','tinha','tinham','deve','devem','pode','podem','já','não','sim','ao','aos','à','às','lhe','lhes'
])

def _tokenize(text: str) -> List[Tuple[str,int,int]]:
    tokens = []
    for match in re.finditer(r"\b\w+\b", text, re.UNICODE):
        tokens.append((match.group(0), match.start(), match.end()))
    return tokens

@dataclass
class SalienceResult:
    units: List[Dict]
    method: str

class SalienceProvider:
    def __init__(self, method: str | None = None):
        env_method = os.getenv('SALIENCE_METHOD')
        self.method = (method or env_method or 'frequency').lower()
        self._keybert_model = None
        # LRU cache (OrderedDict preserves insertion order; we move keys on access)
        # key = md5(lower(text)) + method + max_units ; value = SalienceResult
        self._cache: "OrderedDict[str, SalienceResult]" = OrderedDict()
        try:
            self._cache_max = int(os.getenv('SALIENCE_CACHE_MAX', '512'))
        except ValueError:
            self._cache_max = 512
        # Allow override via init (mainly for tests)
        if isinstance(method, str) and method.startswith('frequency') and 'cache_max=' in method:
            # Not a public API; fallback heuristic if passed like 'frequency;cache_max=128'
            try:
                part = method.split('cache_max=')[1]
                self._cache_max = int(part)
            except Exception:
                pass
        if self.method == 'keybert' and _KEYBERT_AVAILABLE:
            try:
                self._keybert_model = KeyBERT()
            except Exception as e:  # pragma: no cover
                logger.warning(f"KeyBERT init failed, falling back to frequency: {e}")
                self.method = 'frequency'

    def extract(self, text: str, max_units: int = 15) -> SalienceResult:
        if not text.strip():
            return SalienceResult([], self.method)
        cache_key = self._make_cache_key(text, max_units)
        cached = self._cache.get(cache_key)
        if cached:
            # Mark as recently used
            self._cache.move_to_end(cache_key, last=True)
            return cached
        if self.method == 'keybert' and _KEYBERT_AVAILABLE and self._keybert_model:
            result = self._extract_keybert(text, max_units)
        elif self.method == 'yake' and _YAKE_AVAILABLE:
            result = self._extract_yake(text, max_units)
        else:
            result = self._extract_frequency(text, max_units)
        # Store in cache (shallow copy to prevent external mutation)
        self._cache[cache_key] = result
        # Enforce LRU capacity
        if len(self._cache) > self._cache_max:
            # Pop least recently used items until within limit
            while len(self._cache) > self._cache_max:
                self._cache.popitem(last=False)
        return result

    def _make_cache_key(self, text: str, max_units: int) -> str:
        h = hashlib.md5(text.lower().encode('utf-8')).hexdigest()
        return f"{self.method}:{max_units}:{h}"

    # --- Implementations ---
    def _extract_keybert(self, text: str, max_units: int) -> SalienceResult:
        try:
            kw = self._keybert_model.extract_keywords(text, top_n=max_units)
            units = []
            for phrase, score in kw:
                idx = text.lower().find(phrase.lower())
                if idx >= 0:
                    units.append({'unit': phrase, 'weight': float(score), 'span': (idx, idx+len(phrase)), 'method': 'keybert'})
            return SalienceResult(units, 'keybert')
        except Exception as e:  # pragma: no cover
            logger.error(f"KeyBERT extraction failed: {e}; falling back to frequency")
            return self._extract_frequency(text, max_units)

    def _extract_yake(self, text: str, max_units: int) -> SalienceResult:
        try:
            extractor = yake.KeywordExtractor(lan='pt', top=max_units)
            kws = extractor.extract_keywords(text)
            units = []
            for phrase, score in kws:
                idx = text.lower().find(phrase.lower())
                if idx >= 0:
                    # YAKE lower score = more important; invert
                    weight = 1 / (1 + score)
                    units.append({'unit': phrase, 'weight': float(weight), 'span': (idx, idx+len(phrase)), 'method': 'yake'})
            return SalienceResult(units, 'yake')
        except Exception as e:  # pragma: no cover
            logger.error(f"YAKE extraction failed: {e}; falling back to frequency")
            return self._extract_frequency(text, max_units)

    def _extract_frequency(self, text: str, max_units: int) -> SalienceResult:
        tokens = _tokenize(text)
        filtered = [t for t in tokens if t[0].lower() not in PORTUGUESE_STOPWORDS and len(t[0]) > 2]
        if not filtered:
            return SalienceResult([], 'frequency')
        counts = Counter(t[0].lower() for t in filtered)
        max_count = max(counts.values()) or 1
        units = []
        # Sort by freq then earlier position
        first_pos: Dict[str,int] = {}
        for tok, start, _ in filtered:
            key = tok.lower()
            if key not in first_pos:
                first_pos[key] = start
        ordered = sorted(counts.items(), key=lambda kv: (-kv[1], first_pos[kv[0]]))[:max_units]
        for term, cnt in ordered:
            pos = first_pos[term]
            units.append({'unit': term, 'weight': cnt / max_count, 'span': (pos, pos+len(term)), 'method': 'frequency'})
        return SalienceResult(units, 'frequency')

__all__ = [
    'SalienceProvider',
    'SalienceResult'
]

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

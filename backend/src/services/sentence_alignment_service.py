"""
Sentence alignment service (scaffold)

This module provides a lightweight, deterministic sentence-alignment scaffold to
support M1 (Sentence Alignment Layer). It is intentionally small and dependency-free
so it can be unit-tested and iterated on.

Behavior:
- If config.ENABLE_SENTENCE_ALIGNMENT is False, align_paragraphs returns an empty list.
- align_paragraphs receives a list of (source_paragraph, target_paragraph) tuples
  and returns a list of alignment results per paragraph pair with a simple
  sentence-splitting + token-overlap similarity heuristic.

This scaffold should be replaced by a more robust implementation (spaCy + embeddings)
in later iterations, but is suitable for early integration and visualization work.
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple

from importlib import util as _importlib_util

# Support both test import styles:
# - tests may import and monkeypatch `backend.src.core.config.settings`
# - other modules import `src.core.config.settings`
# Try to use whichever settings object is present so monkeypatches in tests take effect.
_backend_settings = None
try:
    # Prefer backend-style package when available (used by tests)
    spec = _importlib_util.find_spec("backend.src.core.config")
    if spec is not None:
        from backend.src.core.config import settings as _backend_settings  # type: ignore
except Exception:
    _backend_settings = None

try:
    from src.core.config import settings as _src_settings
except Exception:
    _src_settings = None

# Choose settings resolution at runtime
def _settings():
    return _backend_settings if _backend_settings is not None else _src_settings

# Backwards-compatible module-level alias:
# Some modules or legacy code in this package expect a top-level `settings` name.
# Provide a safe alias so accidental references to `settings` resolve without raising.
# This mirrors the resolution used by _settings() and yields None if no settings object is available.
try:
    settings = _settings()
except Exception:
    settings = None

# Common Portuguese abbreviations that should not split sentences when followed by a space.
# This list is intentionally small and can be extended as needed.
_ABBREVIATIONS = {
    "sr.", "sra.", "sr", "sra", "sr", "dr.", "dr", "dra.", "dra", "etc.", "etc", "jr.", "jr",
    "ms.", "ms", "st.", "st", "srta.", "srta"
}

def simple_sentence_split(text: str) -> List[str]:
    """
    Improved lightweight sentence splitter with basic abbreviation protection for PT-BR.

    Strategy:
    - Normalize whitespace.
    - Replace known abbreviations' trailing dots with a placeholder to avoid splitting on them.
    - Split on sentence-ending punctuation (., ?, !) when they appear at end-of-sentence.
    - Restore abbreviation placeholders back to their original form.
    - Trim and return non-empty pieces.

    This function intentionally remains dependency-free and deterministic for unit tests.
    """
    if not text:
        return []

    # Normalize whitespace
    t = " ".join(text.split())

    # Protect known abbreviations by replacing 'dr.' -> 'dr<ABBR>' (case-insensitive)
    # Build mapping for restore
    placeholder_map: Dict[str, str] = {}
    for abbr in _ABBREVIATIONS:
        # both dot and no-dot forms may appear; prefer matching with a literal dot in text
        if abbr.endswith("."):
            key = abbr
        else:
            key = abbr + "."
        lower_key = key.lower()
        placeholder = lower_key.replace(".", "<ABBR>")
        if lower_key in t.lower():
            # replace case-insensitive occurrences while preserving original case
            parts: List[str] = []
            i = 0
            tlower = t.lower()
            while True:
                idx = tlower.find(lower_key, i)
                if idx == -1:
                    parts.append(t[i:])
                    break
                # append the segment before the match, then the placeholder
                parts.append(t[i:idx])
                # capture the original-case substring so we can restore exact casing later
                original_substr = t[idx: idx + len(key)]
                parts.append(placeholder)
                i = idx + len(key)
                # store mapping from placeholder to the exact original substring found
                placeholder_map[placeholder] = original_substr
            t = "".join(parts)

    # Now split on sentence-ending punctuation followed by space and uppercase/lowercase start or line end.
    # Use regex to split on (?<=[.!?])\s+ but avoid splitting when placeholder present (we removed dots for abbr)
    import re
    # Split on punctuation that likely ends a sentence.
    pieces = re.split(r'(?<=[\.\?\!])\s+', t)

    # Restore placeholders
    restored: List[str] = []
    for p in pieces:
        for ph, original in placeholder_map.items():
            if ph in p:
                p = p.replace(ph, original)
        p = p.strip()
        if p:
            restored.append(p)
    return restored



@dataclass
class SentenceNode:
    id: int
    text: str


@dataclass
class SentenceAlignment:
    source_sentence_id: int
    target_sentence_id: int
    score: float
    status: str  # 'aligned', 'split', 'merged', 'unmatched'


class SentenceAlignmentService:
    """
    Simple sentence alignment service.

    Methods:
    - align_paragraphs(paragraph_pairs): Accepts List[Tuple[str, str]] and returns
      List[Dict] where each dict corresponds to a paragraph pair with sentence nodes
      and alignment tuples.
    """

    def __init__(self, similarity_threshold: float = None):
        # Use configured similarity threshold if not provided.
        # Resolve settings via the module-level _settings() helper so tests and different
        # import styles are supported. Provide a reasonable default if settings are absent.
        resolved = _settings()
        default_threshold = getattr(resolved, "SIMILARITY_THRESHOLD", 0.3) if resolved is not None else 0.3
        self.similarity_threshold = similarity_threshold or default_threshold

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """
        Very small sentence splitter based on punctuation. Keeps things deterministic.
        """
        if not text:
            return []
        # Normalize whitespace and split on punctuation marks that commonly end sentences.
        pieces = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".")]
        # Filter out empty strings
        return [p for p in pieces if p]

    @staticmethod
    def _token_set(text: str) -> set:
        return set(tok.lower() for tok in text.replace(",", " ").replace(";", " ").split() if tok.strip())

    def _similarity(self, a: str, b: str) -> float:
        """
        Simple Jaccard-like token overlap similarity.
        """
        ta = self._token_set(a)
        tb = self._token_set(b)
        if not ta or not tb:
            return 0.0
        inter = ta.intersection(tb)
        union = ta.union(tb)
        return len(inter) / len(union)

    def align_paragraphs(self, paragraph_pairs: List[Tuple[str, str]]) -> List[Dict]:
        """
        Align sentences for each paragraph pair.

        Returns:
          [
            {
              "source_sentences": [SentenceNode, ...],
              "target_sentences": [SentenceNode, ...],
              "alignments": [SentenceAlignment, ...]
            },
            ...
          ]
        """
        # Respect the feature flag (use _settings() resolver to support multiple import styles).
        resolved = _settings()
        if resolved is not None:
            enabled_flag = getattr(resolved, "ENABLE_SENTENCE_ALIGNMENT", True)
        else:
            # Default: enable sentence alignment to preserve prior behavior when no settings object exists.
            enabled_flag = True
        if not enabled_flag:
            # Return empty list to indicate sentence alignment is disabled
            return []

        results = []

        for p_index, (source_para, target_para) in enumerate(paragraph_pairs):
            src_sentences = self._split_sentences(source_para)
            tgt_sentences = self._split_sentences(target_para)

            src_nodes = [SentenceNode(id=i, text=txt) for i, txt in enumerate(src_sentences)]
            tgt_nodes = [SentenceNode(id=i, text=txt) for i, txt in enumerate(tgt_sentences)]

            alignments: List[SentenceAlignment] = []

            # Greedy 1:1 matching by best similarity above threshold
            used_tgt = set()
            for s in src_nodes:
                best_score = 0.0
                best_t = None
                for t in tgt_nodes:
                    if t.id in used_tgt:
                        continue
                    score = self._similarity(s.text, t.text)
                    if score > best_score:
                        best_score = score
                        best_t = t
                if best_t and best_score >= self.similarity_threshold:
                    alignments.append(SentenceAlignment(
                        source_sentence_id=s.id,
                        target_sentence_id=best_t.id,
                        score=round(best_score, 3),
                        status="aligned"
                    ))
                    used_tgt.add(best_t.id)
                else:
                    alignments.append(SentenceAlignment(
                        source_sentence_id=s.id,
                        target_sentence_id=-1,
                        score=round(best_score, 3),
                        status="unmatched"
                    ))

            # Any unmatched target sentences (not used) become unmatched alignments (reverse)
            for t in tgt_nodes:
                if t.id not in used_tgt:
                    alignments.append(SentenceAlignment(
                        source_sentence_id=-1,
                        target_sentence_id=t.id,
                        score=0.0,
                        status="unmatched"
                    ))

            results.append({
                "paragraph_index": p_index,
                "source_sentences": src_nodes,
                "target_sentences": tgt_nodes,
                "alignments": alignments
            })
 
        return results

    # Backwards-compatible align API used by higher-level services/tests.
    # Returns an object with attributes:
    #  - aligned: list of (src_idx, tgt_idx, score)
    #  - unmatched_source: list of source indices not aligned
    #  - unmatched_target: list of target indices not aligned
    #  - similarity_matrix: 2D list of similarity scores
    def align(self, source_sentences: List[str], target_sentences: List[str], threshold: float = None):
        """
        Align two lists of sentences and return a simple AlignmentResult-like object.

        This method provides the interface expected by ComparativeAnalysisService
        and the unit tests (an object with .aligned, .unmatched_source, .unmatched_target,
        .similarity_matrix). It's a thin wrapper around the logic in align_paragraphs.
        """
        th = threshold if threshold is not None else self.similarity_threshold

        # Build similarity matrix (source x target)
        sim_matrix: List[List[float]] = []
        for s in source_sentences:
            row = []
            for t in target_sentences:
                row.append(self._similarity(s, t))
            sim_matrix.append(row)

        aligned = []
        unmatched_source = []
        unmatched_target = set(range(len(target_sentences)))

        # Greedy matching: for each source, pick best target not yet used if above threshold
        used_targets = set()
        for i, row in enumerate(sim_matrix):
            best_j = None
            best_score = 0.0
            for j, score in enumerate(row):
                if j in used_targets:
                    continue
                if score > best_score:
                    best_score = score
                    best_j = j
            if best_j is not None and best_score >= th:
                aligned.append((i, best_j, round(best_score, 3)))
                used_targets.add(best_j)
                if best_j in unmatched_target:
                    unmatched_target.discard(best_j)
            else:
                unmatched_source.append(i)

        unmatched_target_list = sorted(list(unmatched_target))

        class AlignmentResult:
            def __init__(self, aligned, unmatched_source, unmatched_target, similarity_matrix):
                self.aligned = aligned
                self.unmatched_source = unmatched_source
                self.unmatched_target = unmatched_target
                self.similarity_matrix = similarity_matrix

        return AlignmentResult(aligned=aligned, unmatched_source=unmatched_source, unmatched_target=unmatched_target_list, similarity_matrix=sim_matrix)

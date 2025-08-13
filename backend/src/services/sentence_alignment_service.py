"""
Sentence Alignment Service (M1 scaffold)
Provides a lightweight, dependency-free sentence splitter and a simple
alignment routine used by unit tests and as a scaffold for the full
sentence alignment service described in the roadmap.

This implementation intentionally avoids heavy ML deps and provides
deterministic behavior suitable for tests and low-resource environments.
"""
from dataclasses import dataclass
from typing import List, Tuple, Any
import re
import hashlib
import logging

logger = logging.getLogger(__name__)


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def simple_sentence_split(text: str) -> List[str]:
    """
    Very small sentence splitter used in tests and as fallback.

    This implementation protects common Portuguese abbreviations (e.g. "Dr.",
    "Sra.", "Sr.", "etc.") so they are not treated as sentence boundaries.
    It scans the text and only splits on punctuation followed by whitespace when
    the preceding token is not a known abbreviation.
    """
    if not text:
        return []

    # Common Portuguese abbreviations to protect (lowercase for comparison)
    protected = {"dr.", "dra.", "sr.", "sra.", "srta.", "etc.", "e.g.", "i.e."}

    parts: list[str] = []
    start = 0
    for m in _SENTENCE_SPLIT_RE.finditer(text):
        end = m.start()
        # Extract token before punctuation
        segment = text[start:end + 1].strip()  # include punctuation
        # Find last token (word + punctuation) to check abbreviation
        last_token = re.findall(r"(\S+)$", segment)
        last = last_token[0].lower() if last_token else ""
        if last in protected:
            # Do not split here; continue scanning
            continue
        # Otherwise, finalize this sentence
        parts.append(segment)
        start = m.end()

    # Append remainder
    remainder = text[start:].strip()
    if remainder:
        parts.append(remainder)

    # Trim spaces and return
    return [p.strip() for p in parts if p.strip()]


def _token_set(text: str) -> set:
    """Return set of lowercase word tokens for a simple lexical similarity measure."""
    return set(tok.lower() for tok in _TOKEN_RE.findall(text))


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union > 0 else 0.0


@dataclass
class SentenceAlignmentResult:
    """
    Minimal result object used by tests:
      - aligned: list of tuples (src_idx, tgt_idx, score)
      - unmatched_source: list[int]
      - unmatched_target: list[int]
      - similarity_matrix: list[list[float]]   (matrix of shape S x T)
    """
    aligned: List[Tuple[int, int, float]]
    unmatched_source: List[int]
    unmatched_target: List[int]
    similarity_matrix: List[List[float]]


class SentenceAlignmentService:
    """
    Lightweight sentence alignment service.

    Methods
    -------
    align(source_paragraphs, target_paragraphs, threshold=0.5)
        Aligns paragraphs at the sentence level by splitting paragraphs into
        sentences and then computing a simple lexical similarity (Jaccard).
    """

    def __init__(self, max_sentences_per_paragraph: int = 50):
        self.max_sentences_per_paragraph = max_sentences_per_paragraph

    def _paragraph_to_sentences(self, paragraph: str) -> List[str]:
        sentences = simple_sentence_split(paragraph)
        if len(sentences) > self.max_sentences_per_paragraph:
            # defensive trimming to avoid blow-up in tests / edge cases
            return sentences[: self.max_sentences_per_paragraph]
        return sentences

    def align(
        self,
        source_paragraphs: List[str],
        target_paragraphs: List[str],
        threshold: float = 0.5,
    ) -> SentenceAlignmentResult:
        """
        Align sentences extracted from source_paragraphs to sentences from target_paragraphs.

        Returns a SentenceAlignmentResult where:
          - aligned contains (src_idx, tgt_idx, score) where src_idx/tgt_idx are
            sentence-global indices per paragraph order (flattened per paragraph).
          - unmatched_source/target are lists of indices (relative to flattened sentence list).
          - similarity_matrix is a S x T matrix as nested lists.
        """

        # Flatten sentences while keeping indices mapping
        src_sentences = []
        tgt_sentences = []

        for p in source_paragraphs:
            src_sentences.extend(self._paragraph_to_sentences(p))
        for p in target_paragraphs:
            tgt_sentences.extend(self._paragraph_to_sentences(p))

        S = len(src_sentences)
        T = len(tgt_sentences)

        if S == 0 and T == 0:
            return SentenceAlignmentResult(aligned=[], unmatched_source=[], unmatched_target=[], similarity_matrix=[])

        # Build token sets
        src_tokens = [_token_set(s) for s in src_sentences]
        tgt_tokens = [_token_set(t) for t in tgt_sentences]

        # Compute similarity matrix (S x T)
        similarity_matrix = [[0.0 for _ in range(T)] for _ in range(S)]
        for i in range(S):
            for j in range(T):
                similarity_matrix[i][j] = _jaccard(src_tokens[i], tgt_tokens[j])

        aligned = []
        matched_targets = set()
        unmatched_source = []
        # Greedy per-source matching: choose best target above threshold not already matched
        for i in range(S):
            row = similarity_matrix[i]
            best_j = None
            best_score = 0.0
            for j, score in enumerate(row):
                if j in matched_targets:
                    continue
                if score > best_score:
                    best_score = score
                    best_j = j
            if best_j is not None and best_score >= threshold:
                aligned.append((i, best_j, best_score))
                matched_targets.add(best_j)
            else:
                unmatched_source.append(i)

        unmatched_target = [j for j in range(T) if j not in matched_targets]

        # For debug/testing visibility, expose the matrix as plain nested lists
        return SentenceAlignmentResult(
            aligned=aligned,
            unmatched_source=unaligned_or_empty(unmatched_source),
            unmatched_target=unaligned_or_empty(unmatched_target),
            similarity_matrix=similarity_matrix,
        )


def unaligned_or_empty(lst: List[int]) -> List[int]:
    # helper to ensure lists are lists (keeps typing simple)
    return list(lst)

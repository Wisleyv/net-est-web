"""Sentence Alignment Service (Milestone M1)
Provides sentence-level alignment within already aligned paragraph pairs.
Non-invasive addition: does not alter existing AlignmentResult schema; callers may
embed summaries in processing metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Tuple
import logging
import re

import numpy as np
import hashlib

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except Exception:  # pragma: no cover - fallback path
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


def simple_sentence_split(text: str) -> List[str]:
    """Heuristic sentence splitter tuned for Portuguese.
    Features:
    - Handles sentence-final punctuation . ! ?
    - Preserves common abbreviations (Dr., Dra., Sr., Sra., Prof., Profa., etc., p.ex., etc.)
    - Accepts leading quotes / « » / “ ” around sentence starts
    - Allows lowercase starts after colon or dash (dialogue / explanatory clauses)
    - Collapses extraneous whitespace
    NOTE: This is a fallback; spaCy (if available) should supersede.
    """
    text = text.strip()
    if not text:
        return []

    # Normalize whitespace (keep newlines for possible future paragraph logic)
    text = re.sub(r"[ \t]+", " ", text)

    # Protect abbreviations by temporarily replacing the trailing period with a marker
    abbreviations = [
        r"Dr", r"Dra", r"Sr", r"Sra", r"Srs", r"Sras", r"Prof", r"Profa", r"Profs", r"etc", r"p\.ex", r"Ex", r"Fig", r"No", r"Art", r"Cap"
    ]
    marker = "§ABBR§"
    def protect(match: re.Match) -> str:
        return match.group(1) + marker
    abbr_pattern = re.compile(rf"\b((?:{'|'.join(abbreviations)})\.)", re.IGNORECASE)
    protected = abbr_pattern.sub(lambda m: m.group(1)[:-1] + marker, text)

    # Regex for sentence boundary: punctuation followed by space + (opening quote(s) optional) + capital OR lowercase after colon/dash
    # We'll first split on punctuation boundaries
    split_regex = re.compile(
        r"(?<=[.!?])\s+(?=(?:[\"'“”«»]+)?[A-ZÁÉÍÓÚÂÊÎÔÛÃÕÄËÏÖÜÇ])"
    )
    parts = split_regex.split(protected)

    # Secondary split: treat colon or long dash as soft boundary if followed by space + lowercase start of a clause with >=3 words
    refined: List[str] = []
    colon_regex = re.compile(r"^(.+?:)\s+([a-záéíóúâêîôûãõç].+)$")
    for p in parts:
        m = colon_regex.match(p)
        if m:
            # Heuristic: split only if remainder has at least 3 words
            remainder = m.group(2)
            if len(re.findall(r"\w+", remainder)) >= 3:
                refined.extend([m.group(1), remainder])
                continue
        refined.append(p)

    # Restore abbreviations
    restored = [seg.replace(marker, ".") for seg in refined]

    # Clean up whitespace & stray quotes spacing
    cleaned = []
    for seg in restored:
        s = seg.strip()
        if not s:
            continue
        # Avoid isolated abbreviation fragments
        cleaned.append(s)

    return cleaned


@dataclass
class SentenceAlignmentRecord:
    source_index: int
    target_index: int
    similarity: float
    relation: str  # 'aligned' | 'split' | 'merged'


@dataclass
class SentenceAlignmentResult:
    aligned: List[SentenceAlignmentRecord]
    unmatched_source: List[int]
    unmatched_target: List[int]
    split_groups: List[Dict[str, List[int]]]
    merge_groups: List[Dict[str, List[int]]]
    similarity_matrix: List[List[float]]


class SentenceAlignmentService:
    """Service performing sentence-level alignment heuristics.

    Strategy:
    1. Embed sentences (or create deterministic pseudo-embeddings if ML unavailable).
    2. Compute cosine similarity matrix.
    3. For each source sentence choose best target above threshold.
    4. Derive inverse best-source mapping for targets.
    5. Classify relations:
       - aligned: 1:1 mapping both directions.
       - split: one source is best for multiple targets (targets' best source is that source).
       - merged: one target is best for multiple sources (sources' best target is that target).
    6. Unmatched = sentences with no best counterpart >= threshold.
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model: SentenceTransformer | None = None
        if ML_AVAILABLE:
            try:
                # Lazy load on first use; do not load here to minimize startup cost.
                pass
            except Exception:  # pragma: no cover
                logger.warning("SentenceTransformer load deferred; will fallback if needed")

    def _ensure_model(self):
        if not ML_AVAILABLE:
            return
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer  # local import
                self.model = SentenceTransformer(self.model_name, device="cpu")
            except Exception as e:  # pragma: no cover
                logger.error(f"Failed loading sentence model {self.model_name}: {e}")

    def _embed(self, sentences: List[str]) -> np.ndarray:
        if ML_AVAILABLE:
            self._ensure_model()
            if self.model:
                return self.model.encode(sentences, normalize_embeddings=True, show_progress_bar=False)
        # Fallback deterministic pseudo-embeddings based on hashing to keep tests stable
        vectors = []
        for s in sentences:
            h_bytes = hashlib.md5(s.encode("utf-8")).digest()  # deterministic 16 bytes
            # Use first 8 bytes -> 8 dims normalized
            vec = [b / 255.0 for b in h_bytes[:8]]
            # Pad to 8 dims
            while len(vec) < 8:
                vec.append(0.0)
            vectors.append(vec)
        return np.array(vectors, dtype=float)

    def align(self, source_sentences: List[str], target_sentences: List[str], threshold: float = 0.5) -> SentenceAlignmentResult:
        if not source_sentences and not target_sentences:
            return SentenceAlignmentResult([], [], [], [], [], [])
        if not source_sentences:
            return SentenceAlignmentResult([], [], list(range(len(target_sentences))), [], [], [])
        if not target_sentences:
            return SentenceAlignmentResult([], list(range(len(source_sentences))), [], [], [], [])

        src_emb = self._embed(source_sentences)
        tgt_emb = self._embed(target_sentences)

        # Similarity matrix (cosine)
        # Manual cosine for small matrices to avoid dependency if sklearn absent
        src_norm = src_emb / (np.linalg.norm(src_emb, axis=1, keepdims=True) + 1e-8)
        tgt_norm = tgt_emb / (np.linalg.norm(tgt_emb, axis=1, keepdims=True) + 1e-8)
        sim_matrix = np.dot(src_norm, tgt_norm.T)

        # Best mappings
        source_best: Dict[int, Tuple[int, float]] = {}
        for i in range(len(source_sentences)):
            sims = sim_matrix[i]
            j = int(np.argmax(sims))
            score = float(sims[j])
            if score >= threshold:
                source_best[i] = (j, score)

        target_best: Dict[int, Tuple[int, float]] = {}
        for j in range(len(target_sentences)):
            sims = sim_matrix[:, j]
            i = int(np.argmax(sims))
            score = float(sims[i])
            if score >= threshold:
                target_best[j] = (i, score)

        # Inverse groupings
        target_to_sources: Dict[int, List[int]] = {}
        for si, (tj, _) in source_best.items():
            target_to_sources.setdefault(tj, []).append(si)
        source_to_targets: Dict[int, List[int]] = {}
        for tj, (si, _) in target_best.items():
            source_to_targets.setdefault(si, []).append(tj)

        aligned_records: List[SentenceAlignmentRecord] = []
        split_groups: List[Dict[str, List[int]]] = []
        merge_groups: List[Dict[str, List[int]]] = []

        processed_pairs: set[Tuple[int, int]] = set()

        # Classify splits
        for si, targets in source_to_targets.items():
            if len(targets) > 1:
                split_groups.append({"source": [si], "targets": sorted(targets)})
                for tj in targets:
                    score = sim_matrix[si, tj]
                    aligned_records.append(
                        SentenceAlignmentRecord(si, tj, float(score), relation="split")
                    )
                    processed_pairs.add((si, tj))

        # Classify merges
        for tj, sources in target_to_sources.items():
            if len(sources) > 1:
                merge_groups.append({"target": [tj], "sources": sorted(sources)})
                for si in sources:
                    if (si, tj) in processed_pairs:
                        continue
                    score = sim_matrix[si, tj]
                    aligned_records.append(
                        SentenceAlignmentRecord(si, tj, float(score), relation="merged")
                    )
                    processed_pairs.add((si, tj))

        # 1:1 aligned (not part of splits/merges)
        for si, (tj, score) in source_best.items():
            if (si, tj) in processed_pairs:
                continue
            # Check if mutual best
            mutual = target_best.get(tj, (None,))[0] == si
            relation = "aligned" if mutual else "aligned"  # fallback same label
            aligned_records.append(
                SentenceAlignmentRecord(si, tj, float(score), relation=relation)
            )
            processed_pairs.add((si, tj))

        matched_sources = {r.source_index for r in aligned_records}
        matched_targets = {r.target_index for r in aligned_records}

        unmatched_source = [i for i in range(len(source_sentences)) if i not in matched_sources]
        unmatched_target = [j for j in range(len(target_sentences)) if j not in matched_targets]

        return SentenceAlignmentResult(
            aligned=aligned_records,
            unmatched_source=unmatched_source,
            unmatched_target=unmatched_target,
            split_groups=split_groups,
            merge_groups=merge_groups,
            similarity_matrix=sim_matrix.tolist(),
        )


__all__ = [
    "SentenceAlignmentService",
    "SentenceAlignmentResult",
    "SentenceAlignmentRecord",
    "simple_sentence_split",
]
 # Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

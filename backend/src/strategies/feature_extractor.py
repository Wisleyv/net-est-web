"""
Feature Extractor for Strategy Detection
Shared component for extracting features from text pairs
"""

from typing import List, Dict, Optional, Tuple, Any
import re
import numpy as np
from sentence_transformers import util
import logging

class FeatureExtractor:
    """Extracts features for strategy detection"""

    def __init__(self, nlp_model=None, semantic_model=None):
        self.nlp = nlp_model
        self.semantic_model = semantic_model

    def extract_features(self, source_text: str, target_text: str):
        """Extract all relevant features from text pair"""
        # Basic text metrics
        length_ratio = len(target_text) / max(len(source_text), 1)

        source_words = self._tokenize_text(source_text)
        target_words = self._tokenize_text(target_text)
        word_count_ratio = len(target_words) / max(len(source_words), 1)

        source_sentences = self._split_into_sentences(source_text)
        target_sentences = self._split_into_sentences(target_text)
        sentence_count_ratio = len(target_sentences) / max(len(source_sentences), 1)

        # Word length analysis
        source_avg_len = float(np.mean([len(w) for w in source_words])) if source_words else 0.0
        target_avg_len = float(np.mean([len(w) for w in target_words])) if target_words else 0.0
        avg_word_length_ratio = target_avg_len / max(source_avg_len, 1.0)

        # Semantic features
        semantic_similarity = self._calculate_semantic_similarity(source_text, target_text)
        lexical_overlap = self._calculate_lexical_overlap(source_words, target_words)

        # Syntactic complexity
        complexity_reduction = self._calculate_complexity_reduction(source_text, target_text)
        voice_change_score = self._calculate_voice_change(source_text, target_text)

        # Content features
        explicitness_score = self._calculate_explicitness(source_text, target_text)
        structure_change_score = self._calculate_structure_change(source_text, target_text)
        pronoun_reduction_score = self._calculate_pronoun_reduction(source_text, target_text)

        # Position tracking (placeholder for now)
        strategy_positions = []

        from .strategy_types import StrategyFeatures
        return StrategyFeatures(
            length_ratio=length_ratio,
            word_count_ratio=word_count_ratio,
            sentence_count_ratio=sentence_count_ratio,
            avg_word_length_ratio=avg_word_length_ratio,
            semantic_similarity=semantic_similarity,
            lexical_overlap=lexical_overlap,
            complexity_reduction=complexity_reduction,
            voice_change_score=voice_change_score,
            explicitness_score=explicitness_score,
            structure_change_score=structure_change_score,
            pronoun_reduction_score=pronoun_reduction_score,
            strategy_positions=strategy_positions
        )

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using transformer model"""
        if not self.semantic_model:
            return self._calculate_lexical_overlap(
                self._tokenize_text(text1),
                self._tokenize_text(text2)
            )

        try:
            embeddings = self.semantic_model.encode([text1, text2], convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logging.warning(f"Error calculating semantic similarity: {e}")
            return self._calculate_lexical_overlap(
                self._tokenize_text(text1),
                self._tokenize_text(text2)
            )

    def _calculate_lexical_overlap(self, words1: List[str], words2: List[str]) -> float:
        """Calculate lexical overlap between word lists"""
        set1, set2 = set(words1), set(words2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / max(union, 1)

    def _calculate_complexity_reduction(self, source_text: str, target_text: str) -> float:
        """Calculate syntactic complexity reduction"""
        complexity_markers = ['que', 'quando', 'porque', 'embora', 'ainda que', 'foi', 'foram']

        source_complexity = sum(1 for marker in complexity_markers if marker in source_text.lower())
        target_complexity = sum(1 for marker in complexity_markers if marker in target_text.lower())

        if source_complexity == 0:
            return 0.0

        reduction = (source_complexity - target_complexity) / source_complexity
        return max(0.0, min(1.0, reduction))

    def _calculate_voice_change(self, source_text: str, target_text: str) -> float:
        """Calculate voice change (passive to active or vice versa)"""
        passive_markers = ['foi', 'foram', 'será', 'serão', 'sendo', 'sido']

        source_passive = sum(1 for marker in passive_markers if marker in source_text.lower())
        target_passive = sum(1 for marker in passive_markers if marker in target_text.lower())

        # Normalize by text length
        source_len = len(self._tokenize_text(source_text))
        target_len = len(self._tokenize_text(target_text))

        source_passive_ratio = source_passive / max(source_len, 1)
        target_passive_ratio = target_passive / max(target_len, 1)

        return abs(source_passive_ratio - target_passive_ratio)

    def _calculate_explicitness(self, source_text: str, target_text: str) -> float:
        """Calculate explicitness increase (addition of clarifying phrases)"""
        explicit_markers = ['por exemplo', 'isto é', 'ou seja', 'em outras palavras', 'quer dizer']

        source_explicit = sum(1 for marker in explicit_markers if marker in source_text.lower())
        target_explicit = sum(1 for marker in explicit_markers if marker in target_text.lower())

        # Check for length increase with explicit markers
        length_increase = len(target_text) / max(len(source_text), 1) - 1
        marker_increase = target_explicit - source_explicit

        return min(1.0, max(0.0, (length_increase * 0.5 + marker_increase * 0.5)))

    def _calculate_structure_change(self, source_text: str, target_text: str) -> float:
        """Calculate structural reorganization"""
        structure_markers = ['primeiro', 'segundo', 'depois', 'em seguida', 'finalmente', 'por fim']

        source_structure = sum(1 for marker in structure_markers if marker in source_text.lower())
        target_structure = sum(1 for marker in structure_markers if marker in target_text.lower())

        # Check for paragraph breaks
        source_breaks = source_text.count('\n')
        target_breaks = target_text.count('\n')

        structure_score = (target_structure - source_structure) / max(1, len(self._tokenize_text(target_text)))
        break_score = (target_breaks - source_breaks) / max(1, len(target_text))

        return min(1.0, max(0.0, structure_score + break_score))

    def _calculate_pronoun_reduction(self, source_text: str, target_text: str) -> float:
        """Calculate pronoun to noun substitution"""
        pronouns = ['ele', 'ela', 'eles', 'elas', 'isso', 'isto', 'aquilo', 'aquele', 'aquela']

        source_pronouns = sum(1 for pronoun in pronouns if pronoun in source_text.lower())
        target_pronouns = sum(1 for pronoun in pronouns if pronoun in target_text.lower())

        if source_pronouns == 0:
            return 0.0

        reduction = (source_pronouns - target_pronouns) / source_pronouns
        return max(0.0, min(1.0, reduction))

    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words"""
        if self.nlp:
            doc = self.nlp(text)
            return [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
        else:
            return re.findall(r'\b\w+\b', text.lower())

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]
        else:
            return re.split(r'(?<=[.!?])\s+', text)
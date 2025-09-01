"""
Shared data types for strategy detection cascade
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class StrategyFeatures:
    """Container for extracted features used in strategy detection"""
    # Text-level features
    length_ratio: float
    word_count_ratio: float
    sentence_count_ratio: float
    avg_word_length_ratio: float

    # Semantic features
    semantic_similarity: float
    lexical_overlap: float

    # Syntactic features
    complexity_reduction: float
    voice_change_score: float

    # Content features
    explicitness_score: float
    structure_change_score: float
    pronoun_reduction_score: float

    # Position tracking
    strategy_positions: List[Tuple[int, int]]  # (start, end) positions in target text

@dataclass
class StrategyEvidence:
    """Evidence supporting a detected strategy"""
    strategy_code: str
    confidence: float
    impact_level: str
    features: StrategyFeatures
    examples: List[Dict[str, str]]
    positions: List[Tuple[int, int]]
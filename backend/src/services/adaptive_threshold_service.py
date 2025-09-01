"""
Adaptive Threshold Service - Intelligent threshold adjustment for strategy detection
Dynamically adjusts detection thresholds based on text complexity and characteristics
"""

from typing import Dict, Any, Tuple
import logging
import re
try:
    from backend.src.models.strategy_models import STRATEGY_DESCRIPTIONS
except Exception:
    try:
        from models.strategy_models import STRATEGY_DESCRIPTIONS
    except Exception:
        from ..models.strategy_models import STRATEGY_DESCRIPTIONS

logger = logging.getLogger(__name__)

class AdaptiveThresholdService:
    """
    Service for calculating adaptive thresholds based on text analysis.
    Adjusts detection sensitivity based on text complexity, length, and linguistic features.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Base thresholds for different strategy types
        self.base_thresholds = {
            'macro': {
                'MT+': 0.75,   # Title optimization - needs clear title changes
                'RF+': 0.70,   # Global rewriting - significant structural change
                'RD+': 0.65,   # Content structuring - paragraph reorganization
            },
            'meso': {
                'RP+': 0.60,   # Sentence fragmentation - sentence splitting
                'DL+': 0.55,   # Positional reorganization - word order changes
                'MOD+': 0.80,  # Perspective reinterpretation - high confidence needed
                'IN+': 0.65,   # Insertion handling - parenthetical expressions
            },
            'micro': {
                'SL+': 0.50,   # Lexical simplification - word length reduction
                'TA+': 0.60,   # Referential clarity - pronoun handling
                'MV+': 0.65,   # Voice change - passive to active
                'EXP+': 0.55,  # Explicitness - information addition
            }
        }

        # Strategies excluded from automatic detection (manual only)
        self.manual_only_strategies = {'OM+', 'PRO+'}

    def calculate_adaptive_thresholds(self, source_text: str, target_text: str) -> Dict[str, float]:
        """
        Calculate adaptive thresholds based on text complexity analysis.

        Args:
            source_text: Original text
            target_text: Simplified text

        Returns:
            Dictionary of strategy codes to adaptive thresholds
        """
        # Analyze text complexity
        complexity_score = self._analyze_text_complexity(source_text, target_text)
        text_characteristics = self._analyze_text_characteristics(source_text, target_text)

        self.logger.debug(f"Text complexity score: {complexity_score:.3f}")
        self.logger.debug(f"Text characteristics: {text_characteristics}")

        # Calculate adaptive thresholds
        adaptive_thresholds = {}

        # Process macro strategies
        for strategy_code in self.base_thresholds['macro']:
            if strategy_code not in self.manual_only_strategies:
                base_threshold = self.base_thresholds['macro'][strategy_code]
                adaptive_thresholds[strategy_code] = self._adapt_macro_threshold(
                    base_threshold, complexity_score, text_characteristics
                )

        # Process meso strategies
        for strategy_code in self.base_thresholds['meso']:
            if strategy_code not in self.manual_only_strategies:
                base_threshold = self.base_thresholds['meso'][strategy_code]
                adaptive_thresholds[strategy_code] = self._adapt_meso_threshold(
                    base_threshold, complexity_score, text_characteristics
                )

        # Process micro strategies
        for strategy_code in self.base_thresholds['micro']:
            if strategy_code not in self.manual_only_strategies:
                base_threshold = self.base_thresholds['micro'][strategy_code]
                adaptive_thresholds[strategy_code] = self._adapt_micro_threshold(
                    base_threshold, complexity_score, text_characteristics
                )

        self.logger.info(f"Calculated adaptive thresholds for {len(adaptive_thresholds)} strategies")
        return adaptive_thresholds

    def _analyze_text_complexity(self, source_text: str, target_text: str) -> float:
        """
        Analyze overall text complexity on a scale of 0-1.
        Higher scores indicate more complex texts that may need lower thresholds.
        """
        complexity_factors = []

        # Factor 1: Average sentence length
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentences = self._split_into_sentences(target_text)

        if src_sentences:
            avg_src_length = sum(len(s.split()) for s in src_sentences) / len(src_sentences)
            complexity_factors.append(min(1.0, avg_src_length / 25.0))  # Normalize to 25 words

        # Factor 2: Lexical diversity (unique words / total words)
        src_words = re.findall(r'\b\w+\b', source_text.lower())
        if src_words:
            lexical_diversity = len(set(src_words)) / len(src_words)
            complexity_factors.append(lexical_diversity)

        # Factor 3: Technical term density
        technical_indicators = [
            'abordagem', 'integral', 'perspectivas', 'contemporâneas',
            'campo', 'estudos', 'práticas', 'clínicas', 'demanda',
            'transcenda', 'aspectos', 'biológicos', 'reconheça',
            'complexidade', 'interações', 'fisiológicos', 'sociais',
            'culturais', 'políticos', 'agravos', 'feminina', 'ancorados',
            'comum', 'população', 'especificidades', 'exigem', 'olhar',
            'técnico', 'crítico', 'tange', 'particularidades', 'reprodutivo',
            'doenças', 'ginecológicas', 'prevalentes', 'iniquidades',
            'gênero', 'estruturam', 'acesso', 'qualidade', 'cuidado'
        ]

        technical_count = sum(1 for word in src_words if word in technical_indicators)
        technical_density = technical_count / len(src_words) if src_words else 0
        complexity_factors.append(technical_density)

        # Factor 4: Structural complexity
        structural_indicators = ['que', 'enquanto', 'embora', 'porque', 'portanto']
        structural_count = sum(source_text.lower().count(indicator) for indicator in structural_indicators)
        structural_density = structural_count / len(src_words) if src_words else 0
        complexity_factors.append(min(1.0, structural_density * 10))  # Scale appropriately

        # Calculate weighted average
        if complexity_factors:
            weights = [0.3, 0.3, 0.25, 0.15]  # Sentence length, lexical diversity, technical terms, structure
            complexity_score = sum(f * w for f, w in zip(complexity_factors, weights))
            return min(1.0, max(0.0, complexity_score))

        return 0.5  # Default moderate complexity

    def _analyze_text_characteristics(self, source_text: str, target_text: str) -> Dict[str, Any]:
        """Analyze specific text characteristics for threshold adaptation"""
        characteristics = {}

        # Length characteristics
        src_words = len(re.findall(r'\b\w+\b', source_text))
        tgt_words = len(re.findall(r'\b\w+\b', target_text))
        characteristics['length_ratio'] = tgt_words / src_words if src_words > 0 else 1.0
        characteristics['compression_ratio'] = 1.0 - characteristics['length_ratio']

        # Sentence characteristics
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentences = self._split_into_sentences(target_text)
        characteristics['sentence_ratio'] = len(tgt_sentences) / len(src_sentences) if src_sentences else 1.0

        # Lexical characteristics
        src_avg_word_length = sum(len(word) for word in re.findall(r'\b\w+\b', source_text)) / src_words if src_words > 0 else 0
        tgt_avg_word_length = sum(len(word) for word in re.findall(r'\b\w+\b', target_text)) / tgt_words if tgt_words > 0 else 0
        characteristics['word_length_ratio'] = tgt_avg_word_length / src_avg_word_length if src_avg_word_length > 0 else 1.0

        return characteristics

    def _adapt_macro_threshold(self, base_threshold: float, complexity_score: float,
                              characteristics: Dict[str, Any]) -> float:
        """Adapt macro-level strategy thresholds"""
        # For complex texts, lower thresholds to catch more structural changes
        complexity_adjustment = (1.0 - complexity_score) * 0.15  # -0.15 to +0.15

        # Adjust based on compression ratio - more compression may indicate more changes
        compression_bonus = characteristics.get('compression_ratio', 0) * 0.1

        adapted_threshold = base_threshold - complexity_adjustment + compression_bonus
        return max(0.3, min(0.9, adapted_threshold))  # Keep within reasonable bounds

    def _adapt_meso_threshold(self, base_threshold: float, complexity_score: float,
                             characteristics: Dict[str, Any]) -> float:
        """Adapt meso-level strategy thresholds"""
        # Sentence-level strategies benefit from complexity awareness
        complexity_adjustment = (1.0 - complexity_score) * 0.2  # -0.2 to +0.2

        # Sentence ratio adjustment - fragmentation needs lower thresholds for high ratios
        sentence_ratio = characteristics.get('sentence_ratio', 1.0)
        sentence_adjustment = (sentence_ratio - 1.0) * 0.1 if sentence_ratio > 1.0 else 0

        adapted_threshold = base_threshold - complexity_adjustment - sentence_adjustment
        return max(0.25, min(0.85, adapted_threshold))

    def _adapt_micro_threshold(self, base_threshold: float, complexity_score: float,
                              characteristics: Dict[str, Any]) -> float:
        """Adapt micro-level strategy thresholds"""
        # Micro strategies are more sensitive to lexical changes
        complexity_adjustment = (1.0 - complexity_score) * 0.25  # -0.25 to +0.25

        # Word length ratio adjustment
        word_length_ratio = characteristics.get('word_length_ratio', 1.0)
        length_adjustment = (1.0 - word_length_ratio) * 0.15 if word_length_ratio < 1.0 else 0

        adapted_threshold = base_threshold - complexity_adjustment - length_adjustment
        return max(0.2, min(0.8, adapted_threshold))

    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences"""
        # Simple sentence splitting - can be enhanced with NLP
        sentences = re.split(r'[.!?]+\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def get_threshold_explanation(self, strategy_code: str, original_threshold: float,
                                adapted_threshold: float) -> str:
        """Generate explanation for threshold adaptation"""
        if abs(adapted_threshold - original_threshold) < 0.05:
            return f"Maintained base threshold for {strategy_code}"

        direction = "lowered" if adapted_threshold < original_threshold else "raised"
        change = abs(adapted_threshold - original_threshold)

        return (f"Adapted {strategy_code} threshold ({direction} by {change:.2f}) "
                f"based on text complexity analysis")

# Global instance
adaptive_threshold_service = AdaptiveThresholdService()
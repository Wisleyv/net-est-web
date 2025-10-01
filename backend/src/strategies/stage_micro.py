"""
Micro Stage Evaluator - Token/Phrase-level Strategy Detection
Handles word-level and phrase-level transformations (placeholder implementation)
"""

from typing import List, Dict, Optional, Tuple, Any
import logging
try:
    from backend.src.models.strategy_models import (
        SimplificationStrategy,
        SimplificationStrategyType,
        STRATEGY_DESCRIPTIONS,
        StrategyExample,
    )
except Exception:
    try:
        from models.strategy_models import (
            SimplificationStrategy,
            SimplificationStrategyType,
            STRATEGY_DESCRIPTIONS,
            StrategyExample,
        )
    except Exception:
        from ..models.strategy_models import (
            SimplificationStrategy,
            SimplificationStrategyType,
            STRATEGY_DESCRIPTIONS,
            StrategyExample,
        )
from .strategy_types import StrategyEvidence, StrategyFeatures

try:
    from .lexical_complexity import LexicalComplexityScorer
except Exception:
    try:
        from lexical_complexity import LexicalComplexityScorer
    except Exception:
        LexicalComplexityScorer = None

class MicroStageEvaluator:
    """
    Evaluates strategies at the micro/token level.
    Focuses on word-level and phrase-level transformations.
    This is a placeholder implementation for future expansion.
    """

    def __init__(self, nlp_model=None, semantic_model=None, lexical_scorer: Optional[object] = None):
        self.nlp = nlp_model
        self.semantic_model = semantic_model
        # lexical_scorer should implement word_complexity/text_complexity/compare
        self.lexical_scorer = lexical_scorer
        self.logger = logging.getLogger(__name__)

    def evaluate(self, features: StrategyFeatures, source_text: str, target_text: str, adaptive_thresholds: Optional[Dict[str, float]] = None) -> Tuple[List[StrategyEvidence], bool]:
        """
        Evaluate micro-level strategies.
        Returns (evidences, should_continue) - micro is always the final stage.
        """
        evidences = []
        should_continue = False  # Micro is the final stage

        self.logger.debug("MICRO STAGE - Starting micro-level evaluation")

        try:
            # SL+ - Lexical Simplification (word-level)
            sl_threshold = adaptive_thresholds.get('SL+', 0.50) if adaptive_thresholds else 0.50
            self.logger.debug(f"MICRO STAGE - Evaluating SL+ (Lexical Simplification) with threshold {sl_threshold}")
            sl_evidence = self._evaluate_lexical_simplification(features, source_text, target_text, sl_threshold)
            if sl_evidence:
                evidences.append(sl_evidence)
                self.logger.info(f"✅ SL+ detected with confidence {sl_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ SL+ not detected")

            # TA+ - Referential Clarity (pronoun handling)
            ta_threshold = adaptive_thresholds.get('TA+', 0.60) if adaptive_thresholds else 0.60
            self.logger.debug(f"MICRO STAGE - Evaluating TA+ (Referential Clarity) with threshold {ta_threshold}")
            ta_evidence = self._evaluate_referential_clarity(features, source_text, target_text, ta_threshold)
            if ta_evidence:
                evidences.append(ta_evidence)
                self.logger.info(f"✅ TA+ detected with confidence {ta_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ TA+ not detected")

            # MV+ - Voice Change (passive/active)
            mv_threshold = adaptive_thresholds.get('MV+', 0.65) if adaptive_thresholds else 0.65
            self.logger.debug(f"MICRO STAGE - Evaluating MV+ (Voice Change) with threshold {mv_threshold}")
            mv_evidence = self._evaluate_voice_change(features, source_text, target_text, mv_threshold)
            if mv_evidence:
                evidences.append(mv_evidence)
                self.logger.info(f"✅ MV+ detected with confidence {mv_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ MV+ not detected")

            # EXP+ - Explicitness (phrase-level additions)
            exp_threshold = adaptive_thresholds.get('EXP+', 0.55) if adaptive_thresholds else 0.55
            self.logger.debug(f"MICRO STAGE - Evaluating EXP+ (Explicitness) with threshold {exp_threshold}")
            exp_evidence = self._evaluate_explicitness(features, source_text, target_text, exp_threshold)
            if exp_evidence:
                evidences.append(exp_evidence)
                self.logger.info(f"✅ EXP+ detected with confidence {exp_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ EXP+ not detected")

        except Exception as e:
            self.logger.error(f"Error in micro stage evaluation: {e}")
            # Micro stage errors don't prevent completion

        return evidences, should_continue

    def _evaluate_lexical_simplification(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.50) -> Optional[StrategyEvidence]:
        """SL+ - Lexical Simplification - Word-level vocabulary changes"""
        # If a lexical_scorer is available, prefer token-level complexity comparison.
        src_words = self._tokenize_text(source_text)
        tgt_words = self._tokenize_text(target_text)

        if not src_words or not tgt_words:
            return None

        if self.lexical_scorer:
            try:
                delta, simplified = self.lexical_scorer.compare(src_words, tgt_words, threshold=0.02)
                if simplified:
                    # Map delta to a confidence value (keeps previous range behavior)
                    confidence = min(0.9, 0.5 + float(delta))
                    if confidence >= threshold:
                        impact = "alto" if delta > 0.15 else "médio"
                        sentence_spans = self._get_sentence_spans(target_text)
                        positions = self._select_distributed_spans(sentence_spans, 2)

                        return StrategyEvidence(
                            strategy_code='SL+',
                            confidence=confidence,
                            impact_level=impact,
                            features=features,
                            examples=[{
                                "original": " ".join(src_words[:6]),
                                "simplified": " ".join(tgt_words[:6]),
                                "delta": delta,
                            }],
                            positions=positions if positions else [(0, 10)],
                        )
            except Exception:
                # If scorer fails, fall back to length heuristic below
                pass

        # Fallback: original length-based heuristic (keeps existing behavior)
        if features.avg_word_length_ratio >= 1.0:
            return None  # No simplification if target words are longer

        # Calculate word-level changes
        import numpy as np
        src_avg_len = np.mean([len(w) for w in src_words])
        tgt_avg_len = np.mean([len(w) for w in tgt_words])

        if src_avg_len <= tgt_avg_len:
            return None

        # Calculate simplification impact
        reduction_ratio = (src_avg_len - tgt_avg_len) / src_avg_len

        if reduction_ratio < 0.05:  # Minimum threshold for SL+
            return None

        confidence = min(0.9, 0.5 + (reduction_ratio * 2.0))

        # Apply adaptive threshold
        if confidence >= threshold:
            impact = "alto" if reduction_ratio > 0.15 else "médio"

            # Calculate positions using a simple distribution approach
            sentence_spans = self._get_sentence_spans(target_text)
            positions = self._select_distributed_spans(sentence_spans, 2)

            return StrategyEvidence(
                strategy_code='SL+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=[{
                    "original": f"Palavras com média de {src_avg_len:.1f} caracteres",
                    "simplified": f"Palavras com média de {tgt_avg_len:.1f} caracteres",
                    "reduction_ratio": reduction_ratio
                }],
                positions=positions if positions else [(0, 10)]  # Fallback to default if no positions found
            )

    def _evaluate_referential_clarity(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.60) -> Optional[StrategyEvidence]:
        """TA+ - Referential Clarity - Pronoun to noun substitution"""
        if features.pronoun_reduction_score <= 0.0:
            return None

        confidence = min(0.9, features.pronoun_reduction_score)

        # Apply adaptive threshold
        if confidence >= threshold:
            impact = "médio"

            return StrategyEvidence(
                strategy_code='TA+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=[{
                    "original": "Uso de pronomes ambíguos",
                    "simplified": "Substituição por substantivos claros"
                }],
                positions=[]
            )

    def _evaluate_voice_change(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.65) -> Optional[StrategyEvidence]:
        """MV+ - Voice Change - Passive to active voice conversion"""
        if features.voice_change_score <= 0.1:
            return None

        confidence = min(0.85, features.voice_change_score)

        # Apply adaptive threshold
        if confidence >= threshold:
            impact = "médio"

            return StrategyEvidence(
                strategy_code='MV+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=[{
                    "original": "Voz passiva identificada",
                    "simplified": "Conversão para voz ativa"
                }],
                positions=[]
            )

    def _evaluate_explicitness(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.55) -> Optional[StrategyEvidence]:
        """EXP+ - Explicitness - Addition of clarifying phrases"""
        if features.explicitness_score <= 0.0:
            return None

        confidence = min(0.9, features.explicitness_score)

        # Apply adaptive threshold
        if confidence >= threshold:
            impact = "médio"

            return StrategyEvidence(
                strategy_code='EXP+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=[{
                    "original": "Informação implícita",
                    "simplified": "Adição de elementos explicativos"
                }],
                positions=[]
            )

    # Helper methods
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if self.nlp:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            if not sentences and text.strip():
                sentences = [text.strip()]
            return sentences
        else:
            import re
            text = text.replace('\n\n', ' [PARA] ')
            text = text.replace('\n', ' ')
            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            sentences = [s.replace(' [PARA] ', '\n\n') for s in sentences]
            if not sentences and text.strip():
                sentences = [text.strip()]
            return sentences

    def _get_sentence_spans(self, text: str) -> List[Dict[str, Any]]:
        """Return sentence texts with character spans for the target text."""
        if not text:
            return []

        if self.nlp:
            doc = self.nlp(text)
            spans: List[Dict[str, Any]] = []
            for sent in doc.sents:
                content = sent.text.strip()
                if not content:
                    continue
                start = sent.start_char
                end = sent.end_char
                while start < end and text[start].isspace():
                    start += 1
                while end > start and text[end - 1].isspace():
                    end -= 1
                spans.append({"text": content, "start": start, "end": end})
            if not spans:
                trimmed = text.strip()
                if trimmed:
                    start = text.find(trimmed)
                    spans.append({"text": trimmed, "start": start, "end": start + len(trimmed)})
            return spans

        import re

        pattern = re.compile(r'[^.!?]+(?:[.!?]+|$)', re.MULTILINE | re.DOTALL)
        spans: List[Dict[str, Any]] = []
        for match in pattern.finditer(text):
            fragment = match.group(0)
            stripped = fragment.strip()
            if not stripped:
                continue
            start = match.start()
            end = match.end()
            while start < end and text[start].isspace():
                start += 1
            while end > start and text[end - 1].isspace():
                end -= 1
            spans.append({"text": stripped, "start": start, "end": end})

        if not spans:
            trimmed = text.strip()
            if trimmed:
                start = text.find(trimmed)
                spans.append({"text": trimmed, "start": start, "end": start + len(trimmed)})
        return spans

    @staticmethod
    def _select_distributed_spans(spans: List[Dict[str, Any]], max_segments: int) -> List[Tuple[int, int]]:
        if not spans or max_segments <= 0:
            return []
        count = min(max_segments, len(spans))
        step = max(1, len(spans) // count)
        selected: List[Tuple[int, int]] = []
        for i in range(count):
            idx = min(i * step, len(spans) - 1)
            span = spans[idx]
            selected.append((span['start'], span['end']))
        return selected

    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words"""
        if self.nlp:
            doc = self.nlp(text)
            return [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
        else:
            import re
            return re.findall(r'\b\w+\b', text.lower())
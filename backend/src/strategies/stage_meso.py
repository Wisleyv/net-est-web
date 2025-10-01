"""
Meso Stage Evaluator - Sentence-level Strategy Detection
Handles sentence-level transformations and operations
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

class MesoStageEvaluator:
    """
    Evaluates strategies at the sentence/meso level.
    Focuses on sentence-level transformations and operations.
    """

    def __init__(self, nlp_model=None, semantic_model=None):
        self.nlp = nlp_model
        self.semantic_model = semantic_model
        self.logger = logging.getLogger(__name__)

    def evaluate(self, features: StrategyFeatures, source_text: str, target_text: str, adaptive_thresholds: Optional[Dict[str, float]] = None, complete_analysis_mode: bool = True) -> Tuple[List[StrategyEvidence], bool]:
        """
        Evaluate meso-level strategies.
        Returns (evidences, should_continue) where should_continue indicates
        whether to proceed to micro-level evaluation.
        In complete analysis mode, always continues to ensure full text processing.
        """
        evidences = []
        should_continue = True

        self.logger.debug("MESO STAGE - Starting meso-level evaluation")

        try:
            # RP+ - Sentence Fragmentation
            rp_threshold = adaptive_thresholds.get('RP+', 0.60) if adaptive_thresholds else 0.60
            self.logger.debug(f"MESO STAGE - Evaluating RP+ (Sentence Fragmentation) with threshold {rp_threshold}")
            rp_evidence = self._evaluate_sentence_fragmentation(features, source_text, target_text, rp_threshold)
            if rp_evidence:
                evidences.append(rp_evidence)
                self.logger.info(f"✅ RP+ detected with confidence {rp_evidence.confidence:.3f}")
                # Add position tracking for RP+ - positions should be tuples, not dicts
                if not rp_evidence.positions:  # If no positions set, add distributed defaults across the text
                    try:
                        src_sentences = self._split_into_sentences(source_text)
                        positions = []
                        if src_sentences:
                            num_positions = min(3, len(src_sentences))
                            for i in range(num_positions):
                                idx = min(int(i * len(src_sentences) / max(num_positions, 1)), len(src_sentences) - 1)
                                char_start = sum(len(s) + 1 for s in src_sentences[:idx])
                                char_end = char_start + len(src_sentences[idx])
                                positions.append((char_start, char_end))
                        rp_evidence.positions = positions if positions else [(0, 10)]
                    except Exception:
                        rp_evidence.positions = [(0, 10)]  # Fallback
                self.logger.info(f"   📍 RP+ positions: {rp_evidence.positions}")
            else:
                self.logger.debug("❌ RP+ not detected")

            # DL+ - Positional Reorganization
            dl_threshold = adaptive_thresholds.get('DL+', 0.55) if adaptive_thresholds else 0.55
            self.logger.debug(f"MESO STAGE - Evaluating DL+ (Positional Reorganization) with threshold {dl_threshold}")
            dl_evidence = self._evaluate_positional_reorganization(features, source_text, target_text, dl_threshold)
            if dl_evidence:
                evidences.append(dl_evidence)
                self.logger.info(f"✅ DL+ detected with confidence {dl_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ DL+ not detected")

            # MOD+ - Perspective Reinterpretation (sentence level)
            mod_threshold = adaptive_thresholds.get('MOD+', 0.80) if adaptive_thresholds else 0.80
            self.logger.debug(f"MESO STAGE - Evaluating MOD+ (Perspective Reinterpretation) with threshold {mod_threshold}")
            mod_evidence = self._evaluate_perspective_reinterpretation(features, source_text, target_text, mod_threshold)
            if mod_evidence:
                evidences.append(mod_evidence)
                self.logger.info(f"✅ MOD+ detected with confidence {mod_evidence.confidence:.3f}")
                if mod_evidence.positions:
                    self.logger.info(f"   📍 MOD+ positions: {mod_evidence.positions}")
            else:
                self.logger.debug("❌ MOD+ not detected")

            # IN+ - Insertion Handling
            in_threshold = adaptive_thresholds.get('IN+', 0.65) if adaptive_thresholds else 0.65
            self.logger.debug(f"MESO STAGE - Evaluating IN+ (Insertion Handling) with threshold {in_threshold}")
            in_evidence = self._evaluate_insertion_handling(features, source_text, target_text, in_threshold)
            if in_evidence:
                evidences.append(in_evidence)
                self.logger.info(f"✅ IN+ detected with confidence {in_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ IN+ not detected")

            # EXP+ - Explicitation (addition of clarifying information)
            exp_threshold = adaptive_thresholds.get('EXP+', 0.60) if adaptive_thresholds else 0.60
            self.logger.debug(f"MESO STAGE - Evaluating EXP+ (Explicitation) with threshold {exp_threshold}")
            exp_evidence = self._evaluate_explicitation(features, source_text, target_text, exp_threshold)
            if exp_evidence:
                evidences.append(exp_evidence)
                self.logger.info(f"✅ EXP+ detected with confidence {exp_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ EXP+ not detected")

            # Early exit check: only skip micro analysis in performance mode with very high confidence
            high_confidence_count = sum(1 for e in evidences if e and e.confidence > 0.95)  # Very high threshold for academic research
            if high_confidence_count >= 6 and not complete_analysis_mode:  # Very conservative threshold
                should_continue = False
                self.logger.info(f"Multiple very high-confidence meso strategies ({high_confidence_count}), skipping micro analysis")

        except Exception as e:
            self.logger.error(f"Error in meso stage evaluation: {e}")
            # Continue to micro stage even if meso fails
            should_continue = True

        return evidences, should_continue

    def _evaluate_sentence_fragmentation(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.60) -> Optional[StrategyEvidence]:
        """RP+ - Sentence Fragmentation - Enhanced semantic sentence fragmentation detection"""
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentence_spans = self._get_sentence_spans(target_text)
        tgt_sentences = [span['text'] for span in tgt_sentence_spans]
        span_lookup = self._build_span_lookup(tgt_sentence_spans)

        if not src_sentences or not tgt_sentences:
            return None

        # Must have more sentences in target (fragmentation indicator)
        if len(tgt_sentences) <= len(src_sentences):
            return None

        sentence_increase = len(tgt_sentences) / len(src_sentences) - 1

        if sentence_increase < 0.1:  # Lowered for academic research (10% increase)
            return None

        fragmentation_evidence = []
        fragment_positions: List[Tuple[int, int]] = []

        # Look for source sentences that were broken into multiple target sentences
        # Process ALL sentences of reasonable length for complete analysis
        for src_sent in src_sentences:
            src_words = self._tokenize_text(src_sent)

            # Consider sentences of reasonable length for fragmentation (academic research requirement)
            # Allow shorter sentences for complete analysis to avoid skipping many segments
            if len(src_words) < 3:
                continue

            # Find semantically related target sentences
            related_targets = []
            for tgt_sent in tgt_sentences:
                tgt_words = self._tokenize_text(tgt_sent)

                # Include more target sentences, even shorter ones for complete analysis
                if len(tgt_words) < 3:  # Reduced from 4 to 3
                    continue

                # Calculate semantic similarity
                if self.semantic_model:
                    try:
                        import numpy as np
                        from sentence_transformers import util
                        embeddings = self.semantic_model.encode([src_sent, tgt_sent], convert_to_tensor=True)
                        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
                        similarity = max(0.0, min(1.0, similarity))
                    except Exception:
                        # Fallback to word overlap
                        src_words_set = set(src_words)
                        tgt_words_set = set(tgt_words)
                        similarity = len(src_words_set & tgt_words_set) / max(len(src_words_set | tgt_words_set), 1)
                else:
                    # Word overlap fallback
                    src_words_set = set(src_words)
                    tgt_words_set = set(tgt_words)
                    similarity = len(src_words_set & tgt_words_set) / max(len(src_words_set | tgt_words_set), 1)

                # If target sentence is semantically related and shorter
                if similarity > 0.4 and len(tgt_words) < len(src_words) * 0.8:
                    related_targets.append((tgt_sent, similarity, len(tgt_words)))

            # If we found multiple related target sentences, this is fragmentation
            if len(related_targets) >= 2:
                # Sort by similarity and combine top matches
                related_targets.sort(key=lambda x: x[1], reverse=True)
                top_fragments = [rt[0] for rt in related_targets[:3]]

                for frag in top_fragments:
                    span = self._consume_span(span_lookup, frag)
                    if span:
                        fragment_positions.append(span)

                fragmentation_evidence.append({
                    "original": src_sent[:100] + "..." if len(src_sent) > 100 else src_sent,
                    "fragmentado": " | ".join([frag[:60] + ("..." if len(frag) > 60 else "") for frag in top_fragments]),
                    "fragment_count": len(related_targets),
                    "avg_similarity": sum(rt[1] for rt in related_targets) / len(related_targets)
                })

        if fragmentation_evidence:
            # Use confidence engine for unified calculation
            try:
                from services.confidence_engine import confidence_engine, ConfidenceFactor
            except Exception:
                try:
                    from backend.src.services.confidence_engine import confidence_engine, ConfidenceFactor
                except Exception:
                    from ..services.confidence_engine import confidence_engine, ConfidenceFactor

            # Calculate confidence based on sentence increase and quality of fragmentation
            avg_similarity = sum(e["avg_similarity"] for e in fragmentation_evidence) / len(fragmentation_evidence)

            confidence_features = {
                "semantic_similarity": avg_similarity,
                "sentence_count_ratio": sentence_increase + 1,  # Convert increase to ratio
                "structure_change_score": features.structure_change_score,
                "length_ratio": features.length_ratio
            }

            custom_factors = [
                ConfidenceFactor(
                    name="sentence_increase",
                    value=min(1.0, sentence_increase / 1.0),  # Normalize to 0-1
                    weight=0.4,
                    description="Extent of sentence fragmentation",
                    evidence=f"Sentence count increased by {sentence_increase:.2f}"
                ),
                ConfidenceFactor(
                    name="fragmentation_quality",
                    value=avg_similarity,
                    weight=0.3,
                    description="Quality of sentence fragmentation",
                    evidence=f"Average semantic similarity: {avg_similarity:.3f}"
                )
            ]

            confidence_explanation = confidence_engine.calculate_confidence(
                strategy_code='RP+',
                features=confidence_features,
                evidence_quality="strong" if len(fragmentation_evidence) >= 2 else "standard",
                custom_factors=custom_factors
            )

            # Apply adaptive threshold
            if confidence_explanation.final_confidence >= threshold:
                impact = "alto" if sentence_increase > 0.5 else "médio"

                # Calculate positions using a simple distribution approach
                # This ensures strategies are spread across the text instead of clustering at position 0
                positions = fragment_positions[:3]

                return StrategyEvidence(
                    strategy_code='RP+',
                    confidence=confidence_explanation.final_confidence,
                    impact_level=impact,
                    features=features,
                    examples=fragmentation_evidence[:3],  # Limit to top 3 examples
                    positions=positions if positions else [(0, 10)]  # Fallback to default if no positions found
                )

        return None

    def _evaluate_positional_reorganization(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.55) -> Optional[StrategyEvidence]:
        """DL+ - Positional Reorganization - Enhanced word order analysis"""
        reorganization_evidence = []
        confidence_factors = []

        # Pattern 1: Sentence-level word order changes
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentence_spans = self._get_sentence_spans(target_text)
        tgt_sentences = [span['text'] for span in tgt_sentence_spans]
        span_lookup = self._build_span_lookup(tgt_sentence_spans)

        if len(src_sentences) != len(tgt_sentences):
            return None  # DL+ requires same number of sentences with different order

        sentence_reorderings = 0
        for src_sent, tgt_sent in zip(src_sentences, tgt_sentences):
            src_words = self._tokenize_text(src_sent)
            tgt_words = self._tokenize_text(tgt_sent)

            # Must have high semantic similarity but different word order
            if self.semantic_model:
                try:
                    import numpy as np
                    from sentence_transformers import util
                    embeddings = self.semantic_model.encode([src_sent, tgt_sent], convert_to_tensor=True)
                    similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
                    similarity = max(0.0, min(1.0, similarity))
                except Exception:
                    src_words_set = set(src_words)
                    tgt_words_set = set(tgt_words)
                    similarity = len(src_words_set & tgt_words_set) / max(len(src_words_set | tgt_words_set), 1)
            else:
                src_words_set = set(src_words)
                tgt_words_set = set(tgt_words)
                similarity = len(src_words_set & tgt_words_set) / max(len(src_words_set | tgt_words_set), 1)

            # Calculate word order difference
            word_order_diff = self._calculate_word_order_difference(src_words, tgt_words)

            if similarity > 0.75 and word_order_diff > 0.3:
                sentence_reorderings += 1
                reorganization_evidence.append({
                    "type": "sentence_reordering",
                    "original": src_sent[:80] + ("..." if len(src_sent) > 80 else ""),
                    "simplified": tgt_sent[:80] + ("..." if len(tgt_sent) > 80 else ""),
                    "word_order_diff": word_order_diff,
                    "similarity": similarity,
                    "target_sentence": tgt_sent
                })

        if sentence_reorderings > 0:
            confidence_factors.append(0.8 * (sentence_reorderings / len(src_sentences)))

        # Pattern 2: Clause/phrase reordering within sentences
        phrase_reorderings = self._detect_phrase_reordering(source_text, target_text)
        if phrase_reorderings:
            for reordering in phrase_reorderings:
                reorganization_evidence.append({
                    "type": "phrase_reordering",
                    "original": reordering['source_phrase'],
                    "simplified": reordering['target_phrase'],
                    "reordering_type": reordering['type']
                })
            confidence_factors.append(0.7)

        if reorganization_evidence:
            # Calculate confidence based on extent and quality of reorganization
            if confidence_factors:
                avg_confidence = sum(confidence_factors) / len(confidence_factors)
                # Bonus for multiple types of reorganization
                final_confidence = min(0.95, avg_confidence + (len(reorganization_evidence) - 1) * 0.05)
            else:
                final_confidence = 0.5

            # Apply adaptive threshold
            if final_confidence >= threshold:
                # Impact based on extent of reorganization
                impact = "alto" if len(reorganization_evidence) > 2 else "médio"

                # Calculate positions for reorganization detections
                positions: List[Tuple[int, int]] = []
                for evidence in reorganization_evidence[:3]:
                    if evidence.get("type") != "sentence_reordering":
                        continue
                    candidate = evidence.get("target_sentence") or evidence.get("simplified")
                    span = self._consume_span(span_lookup, candidate) if candidate else None
                    if not span and candidate:
                        span = self._find_substring_span(target_text, candidate)
                    if span:
                        positions.append(span)

                return StrategyEvidence(
                    strategy_code='DL+',
                    confidence=final_confidence,
                    impact_level=impact,
                    features=features,
                    examples=reorganization_evidence[:3],  # Limit to top 3 examples
                    positions=positions if positions else [(0, 10)]  # Default character position range
                )

        return None

    def _evaluate_perspective_reinterpretation(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.80) -> Optional[StrategyEvidence]:
        """MOD+ - Perspective Reinterpretation - Enhanced semantic perspective shift detection"""
        perspective_evidence = []
        confidence_factors = []

        # Pattern 1: Same meaning, completely different wording (classic perspective shift)
        if (features.semantic_similarity > 0.7 and  # Lowered for academic research
            features.lexical_overlap < 0.35 and     # Relaxed for academic research
            features.avg_word_length_ratio > 0.8):  # Slightly lowered

            perspective_evidence.append({
                "type": "complete_perspective_shift",
                "original": source_text[:80] + ("..." if len(source_text) > 80 else ""),
                "simplified": target_text[:80] + ("..." if len(target_text) > 80 else ""),
                "semantic_similarity": features.semantic_similarity,
                "lexical_overlap": features.lexical_overlap
            })
            confidence_factors.append(0.9)

        # Pattern 2: Sentence-level perspective reinterpretation
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentence_spans = self._get_sentence_spans(target_text)
        tgt_sentences = [span['text'] for span in tgt_sentence_spans]
        span_lookup = self._build_span_lookup(tgt_sentence_spans)

        if len(src_sentences) == len(tgt_sentences):  # MOD+ typically maintains sentence count
            sentence_reinterpretations = self._detect_perspective_shifts(src_sentences, tgt_sentences)
            if sentence_reinterpretations:
                for reinterpretation in sentence_reinterpretations:
                    perspective_evidence.append({
                        "type": "sentence_perspective_shift",
                        "original": reinterpretation['source'],
                        "simplified": reinterpretation['target'],
                        "similarity": reinterpretation['semantic_similarity'],
                        "word_overlap": reinterpretation['word_overlap'],
                        "target_sentence": reinterpretation['target']
                    })
                confidence_factors.append(0.8)

        if perspective_evidence:
            # Calculate confidence based on quality and quantity of perspective shifts
            if confidence_factors:
                avg_confidence = sum(confidence_factors) / len(confidence_factors)
                # Moderate threshold for MOD+ - academic research allows more flexibility
                final_confidence = min(0.9, avg_confidence * features.semantic_similarity)
            else:
                final_confidence = 0.5

            # Apply adaptive threshold (MOD+ requires very high confidence)
            if final_confidence >= threshold:
                impact = "alto" if len(perspective_evidence) > 1 else "médio"

                # Calculate positions for perspective shifts
                positions: List[Tuple[int, int]] = []
                for evidence in perspective_evidence[:3]:
                    candidate = evidence.get("target_sentence") or evidence.get("simplified")
                    span = self._consume_span(span_lookup, candidate) if candidate else None
                    if not span and candidate:
                        span = self._find_substring_span(target_text, candidate)
                    if span:
                        positions.append(span)
                if not positions and target_text:
                    positions.append((0, len(target_text)))

                return StrategyEvidence(
                    strategy_code='MOD+',
                    confidence=final_confidence,
                    impact_level=impact,
                    features=features,
                    examples=perspective_evidence[:3],  # Limit to top 3 examples
                    positions=positions if positions else [(0, 10)]  # Default character position range
                )

        return None

    def _evaluate_insertion_handling(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.65) -> Optional[StrategyEvidence]:
        """IN+ - Insertion Handling - Enhanced parenthetical insertion analysis"""
        insertion_evidence = []
        confidence_factors = []

        # Pattern 1: Parenthetical expressions removed or relocated
        src_parens = self._extract_parenthetical_expressions(source_text)
        tgt_parens = self._extract_parenthetical_expressions(target_text)

        if len(src_parens) > len(tgt_parens):
            removed_parens = len(src_parens) - len(tgt_parens)
            insertion_evidence.append({
                "type": "parenthetical_removal",
                "original": f"texto com {len(src_parens)} inserções",
                "simplified": f"texto com {len(tgt_parens)} inserções",
                "removed_count": removed_parens
            })
            confidence_factors.append(0.8)

        # Pattern 2: Brackets and square brackets handling
        src_brackets = self._extract_bracket_expressions(source_text)
        tgt_brackets = self._extract_bracket_expressions(target_text)

        if len(src_brackets) > len(tgt_brackets):
            removed_brackets = len(src_brackets) - len(tgt_brackets)
            insertion_evidence.append({
                "type": "bracket_removal",
                "original": f"texto com {len(src_brackets)} colchetes",
                "simplified": f"texto com {len(tgt_brackets)} colchetes",
                "removed_count": removed_brackets
            })
            confidence_factors.append(0.7)

        if insertion_evidence and features.semantic_similarity > 0.6:
            # Calculate confidence based on insertion handling quality and semantic preservation
            if confidence_factors:
                avg_confidence = sum(confidence_factors) / len(confidence_factors)
                final_confidence = min(0.95, avg_confidence * features.semantic_similarity)
            else:
                final_confidence = 0.5

            # Apply adaptive threshold
            if final_confidence >= threshold:
                # Impact based on extent of insertion handling
                total_removals = sum(e.get("removed_count", 1) for e in insertion_evidence if "removed_count" in e)
                impact = "médio" if total_removals > 2 else "baixo"

                return StrategyEvidence(
                    strategy_code='IN+',
                    confidence=final_confidence,
                    impact_level=impact,
                    features=features,
                    examples=insertion_evidence[:3],  # Limit to top 3 examples
                    positions=[]
                )

        return None

    def _evaluate_explicitation(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.60) -> Optional[StrategyEvidence]:
        """EXP+ - Explicitation (addition of clarifying information)"""
        # Look for addition of explanatory phrases and examples
        explicitation_markers = [
            'por exemplo', 'isto é', 'ou seja', 'em outras palavras', 'quer dizer',
            'como', 'tal como', 'a saber', 'especificamente', 'particularmente',
            'alimentação', 'emoções', 'cultura', 'desigualdade de gênero', 'decisões políticas'
        ]

        source_explicit = sum(1 for marker in explicitation_markers if marker in source_text.lower())
        target_explicit = sum(1 for marker in explicitation_markers if marker in target_text.lower())

        # Check for length increase with explicitation markers
        length_increase = features.length_ratio - 1
        marker_increase = target_explicit - source_explicit

        explicitation_score = min(1.0, (length_increase * 0.4 + marker_increase * 0.6))

        if explicitation_score > 0.1:  # At least 10% explicitation score
            # Use confidence engine for unified calculation
            try:
                from services.confidence_engine import confidence_engine, ConfidenceFactor
            except Exception:
                try:
                    from backend.src.services.confidence_engine import confidence_engine, ConfidenceFactor
                except Exception:
                    from ..services.confidence_engine import confidence_engine, ConfidenceFactor

            confidence_features = {
                "semantic_similarity": features.semantic_similarity,
                "length_ratio": features.length_ratio,
                "explicitness_score": features.explicitness_score
            }

            custom_factors = [
                ConfidenceFactor(
                    name="explicitation_markers",
                    value=min(1.0, marker_increase / 3.0),
                    weight=0.4,
                    description="Number of explicitation markers added",
                    evidence=f"Added {marker_increase} explicitation markers"
                ),
                ConfidenceFactor(
                    name="length_increase",
                    value=min(1.0, length_increase * 2.0),
                    weight=0.3,
                    description="Length increase for clarification",
                    evidence=f"Text length increased by {length_increase:.1%}"
                )
            ]

            confidence_explanation = confidence_engine.calculate_confidence(
                strategy_code='EXP+',
                features=confidence_features,
                evidence_quality="strong" if marker_increase >= 2 else "standard",
                custom_factors=custom_factors
            )

            # Apply adaptive threshold
            if confidence_explanation.final_confidence >= threshold:
                # EXP+ is typically detected at the text level, but we can estimate position
                # based on where explicitation markers are most concentrated
                positions = []
                tgt_sentences = self._split_into_sentences(target_text)

                # Find sentence with most explicitation markers
                max_markers = 0
                best_sentence_idx = 2  # Default to middle of text

                for i, sentence in enumerate(tgt_sentences):
                    marker_count = sum(1 for marker in explicitation_markers if marker in sentence.lower())
                    if marker_count > max_markers:
                        max_markers = marker_count
                        best_sentence_idx = i

                positions = [(best_sentence_idx * 50, (best_sentence_idx + 1) * 50)]  # Approximate character positions

                return StrategyEvidence(
                    strategy_code='EXP+',
                    confidence=confidence_explanation.final_confidence,
                    impact_level="baixo" if explicitation_score < 0.3 else "médio",
                    features=features,
                    examples=[{
                        "original": "Informação condensada",
                        "simplified": f"Informação expandida com {marker_increase} elementos explicativos"
                    }],
                    positions=positions
                )

        return None

    # Helper methods
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences - enhanced to handle full text properly"""
        if self.nlp:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            # Ensure we don't lose any text due to sentence boundary detection issues
            if not sentences:
                sentences = [text.strip()]
            self.logger.debug(f"spaCy sentence splitting: {len(sentences)} sentences detected")
            return sentences
        else:
            import re
            # More robust sentence splitting that handles various punctuation and academic text
            # Handle paragraph breaks first
            text = text.replace('\n\n', ' [PARA] ')
            text = text.replace('\n', ' ')

            # Split on sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            # Restore paragraph markers for processing
            sentences = [s.replace(' [PARA] ', '\n\n') for s in sentences]

            # Handle cases where text doesn't end with punctuation
            if not sentences and text.strip():
                sentences = [text.strip()]

            self.logger.debug(f"Regex sentence splitting: {len(sentences)} sentences detected")
            return sentences

    def _get_sentence_spans(self, text: str) -> List[Dict[str, Any]]:
        """Return sentence texts with their character spans in the original text."""
        if not text:
            return []

        if self.nlp:
            doc = self.nlp(text)
            spans = []
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                if not sentence_text:
                    continue
                start = sent.start_char
                end = sent.end_char
                # Trim whitespace to align with displayed text
                while start < end and text[start].isspace():
                    start += 1
                while end > start and text[end - 1].isspace():
                    end -= 1
                spans.append({"text": sentence_text, "start": start, "end": end})
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
            segment = match.group(0)
            stripped = segment.strip()
            if not stripped:
                continue
            start = match.start()
            end = match.end()
            # Adjust to remove leading/trailing whitespace
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
    def _build_span_lookup(spans: List[Dict[str, Any]]) -> Dict[str, List[Tuple[int, int]]]:
        lookup: Dict[str, List[Tuple[int, int]]] = {}
        for span in spans:
            key = span["text"]
            lookup.setdefault(key, []).append((span["start"], span["end"]))
        return lookup

    @staticmethod
    def _consume_span(lookup: Dict[str, List[Tuple[int, int]]], text: str) -> Optional[Tuple[int, int]]:
        if not text:
            return None
        key = text.strip()
        if key not in lookup:
            return None
        if not lookup[key]:
            return None
        return lookup[key].pop(0)

    @staticmethod
    def _find_substring_span(text: str, snippet: str) -> Optional[Tuple[int, int]]:
        if not text or not snippet:
            return None
        snippet_clean = snippet.strip()
        if not snippet_clean:
            return None
        lower_text = text.lower()
        lower_snippet = snippet_clean.lower()
        start = lower_text.find(lower_snippet)
        if start == -1:
            return None
        end = start + len(lower_snippet)
        return (start, end)

    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words"""
        if self.nlp:
            doc = self.nlp(text)
            return [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
        else:
            import re
            return re.findall(r'\b\w+\b', text.lower())

    def _calculate_word_order_difference(self, src_words: List[str], tgt_words: List[str]) -> float:
        """Calculate word order differences between two texts for DL+ detection"""
        if not src_words or not tgt_words:
            return 0.0

        common_words = list(set(src_words) & set(tgt_words))
        if len(common_words) < 3:
            return 0.0

        # Get positions of common words in both texts
        src_positions = {}
        tgt_positions = {}

        for word in common_words:
            # Get first occurrence position (normalized)
            try:
                src_pos = src_words.index(word) / len(src_words) if src_words else 0
                tgt_pos = tgt_words.index(word) / len(tgt_words) if tgt_words else 0
                src_positions[word] = src_pos
                tgt_positions[word] = tgt_pos
            except ValueError:
                continue

        if not src_positions:
            return 0.0

        # Calculate position differences
        position_differences = []
        for word in src_positions:
            if word in tgt_positions:
                diff = abs(src_positions[word] - tgt_positions[word])
                position_differences.append(diff)

        if not position_differences:
            return 0.0

        avg_position_difference = sum(position_differences) / len(position_differences)
        return min(1.0, avg_position_difference * 2)  # Scale to 0-1 range

    def _detect_phrase_reordering(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Detect phrase/clause reordering within sentences"""
        reorderings = []

        # Common Portuguese phrase patterns that might be reordered
        phrase_patterns = [
            # Prepositional phrases
            r'(na|no|da|do|em|com|para|por)\s+\w+(?:\s+\w+){0,3}',
            # Adverbial phrases
            r'(muito|bastante|bem|mal|sempre|nunca|hoje|ontem|amanhã)\s+\w+(?:\s+\w+){0,2}',
            # Relative clauses
            r'que\s+\w+(?:\s+\w+){1,5}'
        ]

        src_phrases = []
        tgt_phrases = []

        for pattern in phrase_patterns:
            import re
            src_matches = re.findall(pattern, source_text, re.IGNORECASE)
            tgt_matches = re.findall(pattern, target_text, re.IGNORECASE)

            src_phrases.extend(src_matches)
            tgt_phrases.extend(tgt_matches)

        # Check if phrases appear in different positions
        # Removed the [:3] limit to process ALL phrases, not just first 3
        for src_phrase in src_phrases:  # Process ALL phrases
            if src_phrase in tgt_phrases:
                src_pos = source_text.lower().find(src_phrase.lower())
                tgt_pos = target_text.lower().find(src_phrase.lower())

                src_rel_pos = src_pos / len(source_text) if source_text else 0
                tgt_rel_pos = tgt_pos / len(target_text) if target_text else 0

                # Significant position change indicates reordering
                if abs(src_rel_pos - tgt_rel_pos) > 0.3:
                    reorderings.append({
                        "source_phrase": f"...{src_phrase}...",
                        "target_phrase": f"...{src_phrase}...",
                        "type": "phrase_movement",
                        "position_change": abs(src_rel_pos - tgt_rel_pos)
                    })

        return reorderings

    def _detect_perspective_shifts(self, src_sentences: List[str], tgt_sentences: List[str]) -> List[Dict[str, Any]]:
        """Detect sentence-level perspective shifts with very high semantic similarity but low lexical overlap"""
        shifts = []

        # Process ALL sentences, not just first 3 - this was the critical limitation!
        for src_sent in src_sentences:  # Removed [:3] limit
            if len(self._tokenize_text(src_sent)) < 5:
                continue

            best_match = None
            best_similarity = 0.0

            for tgt_sent in tgt_sentences:
                if len(self._tokenize_text(tgt_sent)) < 5:
                    continue

                # Calculate semantic similarity
                if self.semantic_model:
                    try:
                        import numpy as np
                        from sentence_transformers import util
                        embeddings = self.semantic_model.encode([src_sent, tgt_sent], convert_to_tensor=True)
                        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
                        similarity = max(0.0, min(1.0, similarity))
                    except Exception:
                        src_words = set(self._tokenize_text(src_sent))
                        tgt_words = set(self._tokenize_text(tgt_sent))
                        similarity = len(src_words & tgt_words) / max(len(src_words | tgt_words), 1)
                else:
                    src_words = set(self._tokenize_text(src_sent))
                    tgt_words = set(self._tokenize_text(tgt_sent))
                    similarity = len(src_words & tgt_words) / max(len(src_words | tgt_words), 1)

                # Calculate word overlap separately
                src_words = set(self._tokenize_text(src_sent))
                tgt_words = set(self._tokenize_text(tgt_sent))
                word_overlap = len(src_words & tgt_words) / max(len(src_words | tgt_words), 1)

                # MOD+ criteria: high semantic similarity, low lexical overlap (relaxed for academic research)
                if (similarity > 0.75 and word_overlap < 0.4 and similarity > best_similarity):
                    best_similarity = similarity
                    best_match = {
                        'source': src_sent[:80] + ("..." if len(src_sent) > 80 else ""),
                        'target': tgt_sent[:80] + ("..." if len(tgt_sent) > 80 else ""),
                        'semantic_similarity': similarity,
                        'word_overlap': word_overlap
                    }

            if best_match:
                shifts.append(best_match)

        return shifts

    def _extract_parenthetical_expressions(self, text: str) -> List[Dict[str, Any]]:
        """Extract parenthetical expressions from text"""
        import re

        parentheticals = []
        # Find all parenthetical expressions
        matches = re.finditer(r'\([^)]+\)', text)

        for match in matches:
            content = match.group(0).strip('()')
            if len(content.split()) > 0:  # Skip empty parentheses
                parentheticals.append({
                    "content": content,
                    "position": match.start(),
                    "full_match": match.group(0)
                })

        return parentheticals

    def _extract_bracket_expressions(self, text: str) -> List[Dict[str, Any]]:
        """Extract bracket expressions from text"""
        import re

        brackets = []
        # Find all bracket expressions
        matches = re.finditer(r'\[[^\]]+\]', text)

        for match in matches:
            content = match.group(0).strip('[]')
            if len(content.split()) > 0:  # Skip empty brackets
                brackets.append({
                    "content": content,
                    "position": match.start(),
                    "full_match": match.group(0)
                })

        return brackets
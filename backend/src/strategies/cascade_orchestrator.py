"""
Cascade Orchestrator - Coordinates staged strategy detection with early exit pruning
"""

from typing import List, Dict, Optional, Tuple, Any
import time
import logging
try:
    from src.models.strategy_models import SimplificationStrategy
except Exception:
    try:
        from ..models.strategy_models import SimplificationStrategy
    except Exception:
        from models.strategy_models import SimplificationStrategy
from .strategy_types import StrategyEvidence, StrategyFeatures
from .feature_extractor import FeatureExtractor
from .stage_macro import MacroStageEvaluator
from .stage_meso import MesoStageEvaluator
from .stage_micro import MicroStageEvaluator

class CascadeOrchestrator:
    """
    Orchestrates the cascade detection process with performance optimizations.
    Implements early exit pruning to avoid unnecessary computation.
    """

    def __init__(self, nlp_model=None, semantic_model=None, enable_performance_logging=True, complete_analysis_mode=None):
        # Initialize logger first
        self.logger = logging.getLogger(__name__)

        self.nlp = nlp_model
        self.semantic_model = semantic_model
        self.enable_performance_logging = enable_performance_logging

        # Auto-detect academic research context and force complete analysis mode
        # This ensures full-text processing for research scenarios
        if complete_analysis_mode is None:
            # Default to complete analysis for academic research reliability
            self.complete_analysis_mode = True
            self.logger.info("🎯 Auto-enabled complete analysis mode for academic research reliability")
        else:
            self.complete_analysis_mode = complete_analysis_mode

        # Initialize adaptive threshold service
        try:
            from src.services.adaptive_threshold_service import adaptive_threshold_service
        except Exception:
            try:
                from ..services.adaptive_threshold_service import adaptive_threshold_service
            except Exception:
                from services.adaptive_threshold_service import adaptive_threshold_service
        self.adaptive_threshold_service = adaptive_threshold_service

        # Initialize stage evaluators
        self.macro_evaluator = MacroStageEvaluator(nlp_model, semantic_model)
        self.meso_evaluator = MesoStageEvaluator(nlp_model, semantic_model)
        self.micro_evaluator = MicroStageEvaluator(nlp_model, semantic_model)

        # Initialize feature extractor
        self.feature_extractor = FeatureExtractor(nlp_model, semantic_model)

        # Initialize LangExtract provider for enhanced confidence
        try:
            try:
                from src.services.langextract_provider import langextract_provider
            except Exception:
                try:
                    from ..services.langextract_provider import langextract_provider
                except Exception:
                    from services.langextract_provider import langextract_provider
            self.langextract_provider = langextract_provider
            self.logger.info("✅ LangExtract provider initialized")
        except (ImportError, AttributeError, Exception) as e:
            self.langextract_provider = None
            self.logger.info(f"ℹ️ LangExtract provider not available: {e}")

    def detect_strategies(self, source_text: str, target_text: str) -> List[SimplificationStrategy]:
        """
        Main cascade detection method with performance monitoring and adaptive thresholds.
        """
        start_time = time.time() if self.enable_performance_logging else None

        try:
            # Step 1: Extract features once for all stages
            self.logger.info("CASCADE - Step 1: Extracting features")
            features = self.feature_extractor.extract_features(source_text, target_text)

            # Step 1.5: Calculate adaptive thresholds based on text complexity
            self.logger.info("CASCADE - Step 1.5: Calculating adaptive thresholds")
            adaptive_thresholds = self.adaptive_threshold_service.calculate_adaptive_thresholds(
                source_text, target_text
            )
            self.logger.info(f"CASCADE - Adaptive thresholds calculated for {len(adaptive_thresholds)} strategies")

            # Step 2: Macro-level evaluation (paragraph/document level)
            self.logger.info("CASCADE - Step 2: Starting macro-level evaluation")
            macro_evidences, should_continue_macro = self.macro_evaluator.evaluate(
                features, source_text, target_text, adaptive_thresholds, self.complete_analysis_mode
            )
            self.logger.info(f"CASCADE - Macro stage completed: {len(macro_evidences)} strategies detected")

            all_evidences = macro_evidences

            # Step 3: Meso-level evaluation (sentence level) - ALWAYS run for complete analysis
            if self.complete_analysis_mode:
                self.logger.info("CASCADE - Step 3: Starting meso-level evaluation (complete mode)")
                meso_evidences, should_continue_meso = self.meso_evaluator.evaluate(
                    features, source_text, target_text, adaptive_thresholds
                )
                all_evidences.extend(meso_evidences)
                self.logger.info(f"CASCADE - Meso stage completed: {len(meso_evidences)} strategies detected")

                # Step 4: Micro-level evaluation (token/phrase level) - ALWAYS run for complete analysis
                self.logger.info("CASCADE - Step 4: Starting micro-level evaluation (complete mode)")
                micro_evidences, _ = self.micro_evaluator.evaluate(
                    features, source_text, target_text, adaptive_thresholds
                )
                all_evidences.extend(micro_evidences)
                self.logger.info(f"CASCADE - Micro stage completed: {len(micro_evidences)} strategies detected")
            else:
                # Legacy performance mode with early exits
                if should_continue_macro:
                    self.logger.info("CASCADE - Step 3: Starting meso-level evaluation")
                    meso_evidences, should_continue_meso = self.meso_evaluator.evaluate(
                        features, source_text, target_text, adaptive_thresholds, self.complete_analysis_mode
                    )
                    all_evidences.extend(meso_evidences)
                    self.logger.info(f"CASCADE - Meso stage completed: {len(meso_evidences)} strategies detected, continue={should_continue_meso}")

                    # Step 4: Micro-level evaluation (token/phrase level) - only if needed
                    if should_continue_meso:
                        self.logger.info("CASCADE - Step 4: Starting micro-level evaluation")
                        micro_evidences, _ = self.micro_evaluator.evaluate(
                            features, source_text, target_text, adaptive_thresholds
                        )
                        all_evidences.extend(micro_evidences)
                        self.logger.info(f"CASCADE - Micro stage completed: {len(micro_evidences)} strategies detected")
                    else:
                        self.logger.info("CASCADE - Skipping micro-level evaluation")
                else:
                    self.logger.info("CASCADE - Skipping meso and micro-level evaluation")

            # Step 5: Filter out manual-only strategies (OM+, PRO+) from automatic detection
            filtered_evidences = [
                evidence for evidence in all_evidences
                if evidence.strategy_code not in self.adaptive_threshold_service.manual_only_strategies
            ]

            if len(filtered_evidences) < len(all_evidences):
                excluded_count = len(all_evidences) - len(filtered_evidences)
                self.logger.info(f"CASCADE - Excluded {excluded_count} manual-only strategies from automatic detection")

            # Step 6: Convert evidences to strategies
            strategies = []
            for evidence in filtered_evidences:
                strategy = self._evidence_to_strategy(evidence, features, source_text, target_text)
                if strategy:
                    # Log strategy detection for debugging
                    self.logger.info(f"🎯 Strategy detected: {strategy.sigla} (confidence: {strategy.confianca:.3f})")
                    if hasattr(strategy, 'targetPosition') and strategy.targetPosition:
                        self.logger.info(f"   📍 Position: {strategy.targetPosition}")
                    strategies.append(strategy)
                else:
                    self.logger.warning(f"❌ Failed to convert evidence to strategy: {evidence.strategy_code}")

            # Log performance metrics
            if self.enable_performance_logging and start_time is not None:
                elapsed = time.time() - start_time
                self.logger.info(f"🎯 Cascade detection completed in {elapsed:.3f}s")
                self.logger.info(f"📊 Detected {len(strategies)} strategies across {len(all_evidences)} evidences")

            return strategies

        except Exception as e:
            self.logger.error(f"❌ Error in cascade detection: {e}")
            # Return empty list on error - let calling code handle fallback
            return []

    def _evidence_to_strategy(self, evidence: StrategyEvidence, features: StrategyFeatures, source_text: str = "", target_text: str = "") -> Optional[SimplificationStrategy]:
        """Convert StrategyEvidence to SimplificationStrategy with enhanced confidence and position tracking"""
        try:
            from src.models.strategy_models import STRATEGY_DESCRIPTIONS, SimplificationStrategyType, StrategyExample
        except Exception:
            try:
                from ..models.strategy_models import STRATEGY_DESCRIPTIONS, SimplificationStrategyType, StrategyExample
            except Exception:
                from models.strategy_models import STRATEGY_DESCRIPTIONS, SimplificationStrategyType, StrategyExample
        try:
            from src.services.confidence_engine import confidence_engine
        except Exception:
            try:
                from ..services.confidence_engine import confidence_engine
            except Exception:
                from services.confidence_engine import confidence_engine

        strategy_info = STRATEGY_DESCRIPTIONS.get(evidence.strategy_code, {})

        # Convert examples to plain dicts to avoid Pydantic validation issues when
        # different modules may import StrategyExample from different paths.
        exemplos_objs = []
        for ex in evidence.examples:
            if isinstance(ex, dict):
                exemplos_objs.append({
                    "original": ex.get("original", ""),
                    "simplified": ex.get("simplified", ex.get("fragmentado", "")),
                })
            else:
                try:
                    exemplos_objs.append({
                        "original": getattr(ex, "original", ""),
                        "simplified": getattr(ex, "simplified", getattr(ex, "fragmentado", "")),
                    })
                except Exception:
                    exemplos_objs.append({
                        "original": str(ex),
                        "simplified": "",
                    })

        # Ensure impacto is a valid literal
        impacto_literal = evidence.impact_level if evidence.impact_level in ("baixo", "médio", "alto") else "médio"

        # Convert position tuples to sentence indices for frontend compatibility
        target_position = None
        source_position = None

        if evidence.positions and len(evidence.positions) > 0:
            # Use the first position tuple (start, end) from the evidence
            start_pos, end_pos = evidence.positions[0]

            # Convert character positions to sentence indices
            target_sentences = self._split_text_into_sentences(target_text) if target_text else []
            source_sentences = self._split_text_into_sentences(source_text) if source_text else []

            target_sentence_idx = self._find_sentence_index_for_position(start_pos, target_sentences)
            source_sentence_idx = self._find_sentence_index_for_position(start_pos, source_sentences)

            if target_sentence_idx is not None:
                target_position = {"sentence": target_sentence_idx, "type": "sentence"}
            if source_sentence_idx is not None:
                source_position = {"sentence": source_sentence_idx, "type": "sentence"}

            self.logger.info(f"🎯 Position tracking for {evidence.strategy_code}: target_sentence={target_sentence_idx}, source_sentence={source_sentence_idx}")

        # Calculate enhanced confidence with explanation
        feature_dict = {
            "semantic_similarity": features.semantic_similarity,
            "lexical_overlap": features.lexical_overlap,
            "structure_change_score": features.structure_change_score,
            "length_ratio": features.length_ratio,
            "word_count_ratio": features.word_count_ratio,
            "sentence_count_ratio": features.sentence_count_ratio,
            "avg_word_length_ratio": features.avg_word_length_ratio,
            "complexity_reduction": features.complexity_reduction,
            "voice_change_score": features.voice_change_score,
            "explicitness_score": features.explicitness_score,
            "pronoun_reduction_score": features.pronoun_reduction_score
        }

        # Check if LangExtract should be used for enhanced confidence
        use_langextract = (
            self.langextract_provider and
            self.langextract_provider.should_use_langextract(evidence.strategy_code)
        )

        langextract_features = None
        if use_langextract:
            # Get LangExtract features for enhanced confidence
            combined_text = f"{source_text} {target_text}"  # Combine for better analysis
            langextract_features = self.langextract_provider.get_enhanced_features(
                combined_text,
                evidence.strategy_code
            )

        # Calculate confidence with optional LangExtract enhancement
        confidence_explanation = confidence_engine.calculate_confidence(
            strategy_code=evidence.strategy_code,
            features=feature_dict,
            evidence_quality="strong" if len(evidence.examples) > 2 else "standard",
            use_langextract=use_langextract,
            langextract_features=langextract_features
        )

        # Convert explanation to dictionary for JSON serialization
        explanation_dict = {
            "final_confidence": confidence_explanation.final_confidence,
            "confidence_level": confidence_explanation.confidence_level.value,
            "factor_breakdown": confidence_explanation.get_factor_breakdown(),
            "top_contributors": confidence_explanation.get_top_contributors(),
            "recommendations": confidence_explanation.recommendations,
            "evidence_quality": confidence_explanation.evidence_quality,
            "calculation_method": confidence_explanation.calculation_method,
            "langextract_used": use_langextract,
            "langextract_available": langextract_features is not None if use_langextract else False,
            "salience_improvement": langextract_features.get('salience_improvement', 0.0) if langextract_features else 0.0
        }

        return SimplificationStrategy(
            sigla=evidence.strategy_code,
            nome=strategy_info.get("nome", "Estratégia Desconhecida"),
            descricao=strategy_info.get("descricao", ""),
            tipo=strategy_info.get("tipo", SimplificationStrategyType.SEMANTIC),
            impacto=impacto_literal,
            confianca=float(confidence_explanation.final_confidence),
            exemplos=exemplos_objs,
            confidence_explanation=explanation_dict,
            confidence_level=confidence_explanation.confidence_level.value,
            evidence_quality=confidence_explanation.evidence_quality,
            # Add position information for frontend compatibility
            targetPosition=target_position,
            sourcePosition=source_position
        )

    def _split_text_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for position tracking"""
        if not text:
            return []

        # Use spaCy if available for better sentence splitting
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            # Fallback to simple regex-based splitting
            import re
            sentences = re.split(r'[.!?]+\s+', text)
            return [s.strip() for s in sentences if s.strip()]

    def _find_sentence_index_for_position(self, char_position: int, sentences: List[str]) -> Optional[int]:
        """Find which sentence contains the given character position"""
        if not sentences:
            return None

        # Reconstruct the original text to properly map positions
        reconstructed_text = ""
        sentence_positions = []

        for i, sentence in enumerate(sentences):
            start_pos = len(reconstructed_text)
            reconstructed_text += sentence
            end_pos = len(reconstructed_text)

            sentence_positions.append((start_pos, end_pos))

            # Add space/punctuation between sentences (except for the last one)
            if i < len(sentences) - 1:
                reconstructed_text += " "

        # Now find which sentence contains the character position
        for i, (start_pos, end_pos) in enumerate(sentence_positions):
            if start_pos <= char_position < end_pos:
                return i

        return None
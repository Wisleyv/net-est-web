"""
Macro Stage Evaluator - Paragraph-level Strategy Detection
Handles high-level structural changes and global transformations
"""

from typing import List, Dict, Optional, Tuple, Any
import logging
try:
    # Prefer absolute imports when backend/src is on sys.path or package is installed
    from backend.src.models.strategy_models import (
        SimplificationStrategy,
        SimplificationStrategyType,
        STRATEGY_DESCRIPTIONS,
        StrategyExample,
    )
except Exception:
    try:
        # Try alternate top-level import layout
        from models.strategy_models import (
            SimplificationStrategy,
            SimplificationStrategyType,
            STRATEGY_DESCRIPTIONS,
            StrategyExample,
        )
    except Exception:
        # Fallback for pytest with PYTHONPATH=backend/src
        from ..models.strategy_models import (
            SimplificationStrategy,
            SimplificationStrategyType,
            STRATEGY_DESCRIPTIONS,
            StrategyExample,
        )
from .strategy_types import StrategyEvidence, StrategyFeatures

class MacroStageEvaluator:
    """
    Evaluates strategies at the paragraph/macro level.
    Focuses on structural changes that affect the entire text organization.
    """

    def __init__(self, nlp_model=None, semantic_model=None):
        self.nlp = nlp_model
        self.semantic_model = semantic_model
        self.logger = logging.getLogger(__name__)

    def evaluate(self, features: StrategyFeatures, source_text: str, target_text: str, adaptive_thresholds: Optional[Dict[str, float]] = None, complete_analysis_mode: bool = True) -> Tuple[List[StrategyEvidence], bool]:
        """
        Evaluate macro-level strategies.
        Returns (evidences, should_continue) where should_continue indicates
        whether to proceed to meso-level evaluation.
        In complete analysis mode, always continues to ensure full text processing.
        """
        evidences = []
        should_continue = True

        # Debug logging for feature values
        self.logger.debug(f"MACRO STAGE - Features: semantic_sim={features.semantic_similarity:.3f}, "
                         f"lexical_overlap={features.lexical_overlap:.3f}, "
                         f"structure_change={features.structure_change_score:.3f}")

        try:
            # RD+ - Content Structuring and Flow
            rd_threshold = adaptive_thresholds.get('RD+', 0.65) if adaptive_thresholds else 0.65
            self.logger.debug(f"MACRO STAGE - Evaluating RD+ (Content Structuring) with threshold {rd_threshold}")
            rd_evidence = self._evaluate_content_structuring(features, source_text, target_text, rd_threshold)
            if rd_evidence:
                evidences.append(rd_evidence)
                self.logger.info(f"✅ RD+ detected with confidence {rd_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ RD+ not detected")

            # MT+ - Title Optimization
            mt_threshold = adaptive_thresholds.get('MT+', 0.75) if adaptive_thresholds else 0.75
            self.logger.debug(f"MACRO STAGE - Evaluating MT+ (Title Optimization) with threshold {mt_threshold}")
            mt_evidence = self._evaluate_title_optimization(features, source_text, target_text, mt_threshold)
            if mt_evidence:
                evidences.append(mt_evidence)
                self.logger.info(f"✅ MT+ detected with confidence {mt_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ MT+ not detected")

            # RF+ - Global Rewriting (high-level check)
            rf_threshold = adaptive_thresholds.get('RF+', 0.70) if adaptive_thresholds else 0.70
            self.logger.debug(f"MACRO STAGE - Evaluating RF+ (Global Rewriting) with threshold {rf_threshold}")
            rf_evidence = self._evaluate_global_rewriting(features, source_text, target_text, rf_threshold)
            if rf_evidence:
                evidences.append(rf_evidence)
                self.logger.info(f"✅ RF+ detected with confidence {rf_evidence.confidence:.3f}")

                # Only skip meso analysis in performance mode and for extremely high confidence
                if rf_evidence.confidence > 0.98 and not complete_analysis_mode:  # Increased threshold for academic research
                    should_continue = False
                    self.logger.info("RF+ confidence > 0.98, skipping meso-level analysis for performance")
            else:
                self.logger.debug("❌ RF+ not detected")

            # OM+ - Content Omission (removal of complex/unnecessary content)
            om_threshold = adaptive_thresholds.get('OM+', 0.65) if adaptive_thresholds else 0.65
            self.logger.debug(f"MACRO STAGE - Evaluating OM+ (Content Omission) with threshold {om_threshold}")
            om_evidence = self._evaluate_content_omission(features, source_text, target_text, om_threshold)
            if om_evidence:
                evidences.append(om_evidence)
                self.logger.info(f"✅ OM+ detected with confidence {om_evidence.confidence:.3f}")
            else:
                self.logger.debug("❌ OM+ not detected")

            # Early exit check: if we have multiple very high-confidence macro strategies,
            # the text has undergone major structural changes
            high_confidence_count = sum(1 for e in evidences if e and e.confidence > 0.95)  # Increased threshold for academic research
            if high_confidence_count >= 4 and not complete_analysis_mode:  # Increased count requirement
                should_continue = False
                self.logger.info(f"Multiple very high-confidence macro strategies ({high_confidence_count}), skipping meso analysis")

        except Exception as e:
            self.logger.error(f"Error in macro stage evaluation: {e}")
            # Continue to meso stage even if macro fails
            should_continue = True

        return evidences, should_continue

    def _evaluate_content_structuring(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.65) -> Optional[StrategyEvidence]:
        """RD+ - Content Structuring and Flow Organization"""
        structuring_indicators = []

        # Check for paragraph reorganization
        src_paragraphs = self._split_into_paragraphs(source_text)
        tgt_paragraphs = self._split_into_paragraphs(target_text)

        if len(tgt_paragraphs) > len(src_paragraphs) and features.semantic_similarity > 0.7:
            paragraph_increase = len(tgt_paragraphs) / len(src_paragraphs)
            structuring_indicators.append({
                "type": "paragraph_reorganization",
                "ratio": paragraph_increase,
                "description": f"Parágrafos aumentaram de {len(src_paragraphs)} para {len(tgt_paragraphs)}"
            })

        # Check for discourse markers addition
        discourse_markers = self._count_discourse_markers(target_text) - self._count_discourse_markers(source_text)
        if discourse_markers > 0:
            structuring_indicators.append({
                "type": "discourse_markers",
                "count": discourse_markers,
                "description": f"Adicionados {discourse_markers} marcadores de discurso"
            })

        # Check for section headers
        src_headers = self._count_section_headers(source_text)
        tgt_headers = self._count_section_headers(target_text)

        if tgt_headers > src_headers:
            structuring_indicators.append({
                "type": "section_headers",
                "count": tgt_headers - src_headers,
                "description": f"Adicionados {tgt_headers - src_headers} cabeçalhos de seção"
            })

        if structuring_indicators:
            # Use confidence engine for unified calculation
            try:
                from services.confidence_engine import confidence_engine
            except Exception:
                try:
                    from backend.src.services.confidence_engine import confidence_engine
                except Exception:
                    from ..services.confidence_engine import confidence_engine

            # Prepare features for confidence calculation
            confidence_features = {
                "semantic_similarity": features.semantic_similarity,
                "structure_change_score": features.structure_change_score,
                "sentence_count_ratio": len(tgt_paragraphs) / max(len(src_paragraphs), 1),
                "length_ratio": features.length_ratio
            }

            # Add custom factor for structuring indicators
            try:
                from services.confidence_engine import ConfidenceFactor
            except Exception:
                try:
                    from backend.src.services.confidence_engine import ConfidenceFactor
                except Exception:
                    from ..services.confidence_engine import ConfidenceFactor
            custom_factors = [
                ConfidenceFactor(
                    name="structuring_indicators",
                    value=min(1.0, len(structuring_indicators) / 3.0),
                    weight=0.2,
                    description="Number of structuring indicators detected",
                    evidence=f"Found {len(structuring_indicators)} structuring indicators"
                )
            ]

            confidence_explanation = confidence_engine.calculate_confidence(
                strategy_code='RD+',
                features=confidence_features,
                evidence_quality="strong" if len(structuring_indicators) >= 2 else "standard",
                custom_factors=custom_factors
            )

            # Apply adaptive threshold
            if confidence_explanation.final_confidence >= threshold:
                return StrategyEvidence(
                    strategy_code='RD+',
                    confidence=confidence_explanation.final_confidence,
                    impact_level="alto" if confidence_explanation.final_confidence > 0.7 else "médio",
                    features=features,
                    examples=[{
                        "original": f"Texto com {len(src_paragraphs)} parágrafos",
                        "structured": f"Reorganizado em {len(tgt_paragraphs)} parágrafos com marcadores de discurso"
                    }],
                    positions=[]
                )

        return None

    def _evaluate_title_optimization(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.75) -> Optional[StrategyEvidence]:
        """MT+ - Title Optimization"""
        src_lines = [line.strip() for line in source_text.split('\n') if line.strip()]
        tgt_lines = [line.strip() for line in target_text.split('\n') if line.strip()]

        self.logger.debug(f"MT+ - Source lines: {len(src_lines)}, Target lines: {len(tgt_lines)}")

        if not src_lines or not tgt_lines:
            return None

        title_optimizations = []

        # Check for new titles added
        src_titles = self._identify_titles(src_lines)
        tgt_titles = self._identify_titles(tgt_lines)

        self.logger.debug(f"MT+ - Source titles: {src_titles}, Target titles: {tgt_titles}")

        if len(tgt_titles) > len(src_titles):
            new_titles = tgt_titles[len(src_titles):]
            title_optimizations.extend([{
                "type": "title_addition",
                "title": title,
                "description": f"Novo título adicionado: {title[:50]}..."
            } for title in new_titles])

        # Check for title reformulation
        for i, (src_title, tgt_title) in enumerate(zip(src_titles, tgt_titles)):
            if src_title != tgt_title and len(tgt_title) > 0:
                title_optimizations.append({
                    "type": "title_reformulation",
                    "original": src_title,
                    "optimized": tgt_title,
                    "description": "Título reformulado para maior clareza"
                })

        self.logger.debug(f"MT+ - Title optimizations found: {len(title_optimizations)}")

        if title_optimizations:
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
                "structure_change_score": features.structure_change_score,
                "length_ratio": features.length_ratio
            }

            custom_factors = [
                ConfidenceFactor(
                    name="title_optimizations",
                    value=min(1.0, len(title_optimizations) / 3.0),
                    weight=0.3,
                    description="Number of title optimizations detected",
                    evidence=f"Found {len(title_optimizations)} title optimizations"
                )
            ]

            confidence_explanation = confidence_engine.calculate_confidence(
                strategy_code='MT+',
                features=confidence_features,
                evidence_quality="strong" if len(title_optimizations) >= 2 else "standard",
                custom_factors=custom_factors
            )

            # Apply adaptive threshold
            if confidence_explanation.final_confidence >= threshold:
                return StrategyEvidence(
                    strategy_code='MT+',
                    confidence=confidence_explanation.final_confidence,
                    impact_level="médio",
                    features=features,
                    examples=[{
                        "original": opt.get("original", "Texto sem título"),
                        "simplified": opt.get("optimized", opt.get("title", "Título otimizado"))
                    } for opt in title_optimizations[:2]],
                    positions=[]
                )

        return None

    def _evaluate_global_rewriting(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.60) -> Optional[StrategyEvidence]:
        """RF+ - Global Rewriting (macro-level check)"""
        # RF+ requires significant structural change with semantic preservation
        # Lower thresholds to detect more realistic rewriting patterns
        structural_change = (
            features.structure_change_score > 0.2 and  # Lowered from 0.4
            features.semantic_similarity > 0.65 and    # Lowered from 0.75
            features.lexical_overlap < 0.6             # Raised from 0.4
        )

        self.logger.debug(f"RF+ - Structural change check: structure={features.structure_change_score:.3f} > 0.4, "
                         f"semantic={features.semantic_similarity:.3f} > 0.75, "
                         f"lexical={features.lexical_overlap:.3f} < 0.4, "
                         f"result={structural_change}")

        if structural_change:
            # Use confidence engine for unified calculation
            try:
                from services.confidence_engine import confidence_engine
            except Exception:
                try:
                    from backend.src.services.confidence_engine import confidence_engine
                except Exception:
                    from ..services.confidence_engine import confidence_engine

            confidence_features = {
                "semantic_similarity": features.semantic_similarity,
                "lexical_overlap": features.lexical_overlap,
                "structure_change_score": features.structure_change_score,
                "length_ratio": features.length_ratio
            }

            confidence_explanation = confidence_engine.calculate_confidence(
                strategy_code='RF+',
                features=confidence_features,
                evidence_quality="strong"
            )

            # Apply adaptive threshold
            if confidence_explanation.final_confidence >= threshold:
                return StrategyEvidence(
                    strategy_code='RF+',
                    confidence=confidence_explanation.final_confidence,
                    impact_level="alto",
                    features=features,
                    examples=[{
                        "original": source_text[:60] + "..." if len(source_text) > 60 else source_text,
                        "simplified": target_text[:60] + "..." if len(target_text) > 60 else target_text
                    }],
                    positions=[]
                )

        return None

    def _evaluate_content_omission(self, features: StrategyFeatures, source_text: str, target_text: str, threshold: float = 0.65) -> Optional[StrategyEvidence]:
        """OM+ - Content Omission (removal of complex/unnecessary content)"""
        # Check for significant length reduction with semantic preservation
        length_reduction = 1 - features.length_ratio

        # Look for removal of complex academic/technical terms
        complex_terms = [
            'abordagem integral', 'perspectivas contemporâneas', 'campo de estudos',
            'práticas clínicas', 'processos fisiológicos', 'interações entre fatores',
            'fisiológicos, sociais, culturais e políticos', 'ancorados em fatores',
            'olhar técnico e crítico', 'particularidades do ciclo reprodutivo',
            'doenças ginecológicas', 'iniquidades de gênero', 'acesso e qualidade do cuidado'
        ]

        removed_terms = []
        for term in complex_terms:
            if term in source_text.lower() and term not in target_text.lower():
                removed_terms.append(term)

        # Check for removal of academic connectors
        academic_connectors = [
            'enquanto', 'demanda', 'transcenda', 'reconheça', 'especificidades',
            'exigem', 'tange', 'estruturam'
        ]

        removed_connectors = []
        for connector in academic_connectors:
            if connector in source_text.lower() and connector not in target_text.lower():
                removed_connectors.append(connector)

        omission_indicators = removed_terms + removed_connectors

        if omission_indicators and length_reduction > 0.1:  # At least 10% length reduction
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
                "lexical_overlap": features.lexical_overlap
            }

            custom_factors = [
                ConfidenceFactor(
                    name="omitted_content",
                    value=min(1.0, len(omission_indicators) / 5.0),
                    weight=0.4,
                    description="Number of complex terms/academic connectors removed",
                    evidence=f"Removed {len(omission_indicators)} complex elements"
                ),
                ConfidenceFactor(
                    name="length_reduction",
                    value=min(1.0, length_reduction * 2.0),
                    weight=0.3,
                    description="Extent of content reduction",
                    evidence=f"Text reduced by {length_reduction:.1%}"
                )
            ]

            confidence_explanation = confidence_engine.calculate_confidence(
                strategy_code='OM+',
                features=confidence_features,
                evidence_quality="strong" if len(omission_indicators) >= 3 else "standard",
                custom_factors=custom_factors
            )

            # Apply adaptive threshold
            if confidence_explanation.final_confidence >= threshold:
                return StrategyEvidence(
                    strategy_code='OM+',
                    confidence=confidence_explanation.final_confidence,
                    impact_level="médio" if length_reduction < 0.3 else "alto",
                    features=features,
                    examples=[{
                        "original": f"Texto com {len(omission_indicators)} elementos complexos",
                        "simplified": f"Conteúdo simplificado removendo elementos acadêmicos"
                    }],
                    positions=[]
                )

        return None

    # Helper methods
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs if paragraphs else [text]

    def _count_discourse_markers(self, text: str) -> int:
        """Count discourse markers and connectives"""
        markers = [
            'primeiro', 'segundo', 'depois', 'então', 'portanto',
            'porém', 'contudo', 'além disso', 'também', 'finalmente'
        ]
        return sum(text.lower().count(marker) for marker in markers)

    def _count_section_headers(self, text: str) -> int:
        """Count section headers and organizational markers"""
        lines = text.split('\n')
        headers = 0

        for line in lines:
            line = line.strip()
            if (line.endswith(':') and len(line) < 60) or \
               (line.isupper() and len(line) > 3) or \
               any(marker in line.lower() for marker in ['capítulo', 'seção', 'parte']):
                headers += 1

        return headers

    def _identify_titles(self, lines: List[str]) -> List[str]:
        """Identify potential titles in text lines"""
        titles = []
        for line in lines:
            # Title indicators - more flexible detection
            if (line.isupper() and len(line) > 3) or \
               (line.endswith(':') and len(line) < 60) or \
               (line.istitle() and len(line) < 80) or \
               (len(line) < 80 and len(line) > 10 and not any(word in line.lower() for word in ['que', 'como', 'para', 'com', 'em', 'de', 'da', 'do', 'das', 'dos'])):
                titles.append(line)
        return titles
"""Feature Extraction Service - Module 3 Bridge Implementation
Connects semantic alignment results to tag classification system
"""

import uuid
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

import textstat
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
try:
    # Prefer absolute 'src' package path used by test runner (PYTHONPATH=backend/src)
    from src.models.feature_extraction import (
        FeatureExtractionRequest,
        FeatureExtractionResponse,
        TagAnnotation,
        TagType,
        TagConfiguration,
        UserConfiguration,
        DiscourseFeatures,
        TagEvidence,
        ConfidenceLevel
    )
    from src.models.semantic_alignment import AlignmentResponse, AlignedPair
except Exception:
    # Fallback to relative imports when module executed in package context
    from ..models.feature_extraction import (
        FeatureExtractionRequest,
        FeatureExtractionResponse,
        TagAnnotation,
        TagType,
        TagConfiguration,
        UserConfiguration,
        DiscourseFeatures,
        TagEvidence,
        ConfidenceLevel
    )
    from ..models.semantic_alignment import AlignmentResponse, AlignedPair

logger = logging.getLogger(__name__)


class FeatureExtractionService:
    """Service for extracting discourse features and classifying simplification strategies"""
    
    def __init__(self):
        self.nlp = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        
        try:
            # Load spaCy Portuguese model for advanced analysis
            self.nlp = spacy.load("pt_core_news_sm")
            logger.info("SpaCy Portuguese model loaded for feature extraction")
        except OSError:
            logger.warning("SpaCy Portuguese model not found, using basic feature extraction")

    async def extract_features_and_classify(
        self, 
        request: FeatureExtractionRequest
    ) -> FeatureExtractionResponse:
        """Main entry point for feature extraction and classification"""
        
        start_time = time.time()
        annotations: List[TagAnnotation] = []
        
        try:
            # Parse alignment data
            alignment_data = request.alignment_data
            aligned_pairs = alignment_data.get('aligned_pairs', [])
            unaligned_source_indices = alignment_data.get('unaligned_source_indices', [])
            source_paragraphs = alignment_data.get('source_paragraphs', [])
            target_paragraphs = alignment_data.get('target_paragraphs', [])
            
            logger.info(f"Processing {len(aligned_pairs)} aligned pairs and {len(unaligned_source_indices)} unaligned paragraphs")
            
            # Process aligned pairs for transformation tags
            for pair in aligned_pairs:
                if isinstance(pair, dict):
                    source_idx = pair.get('source_idx')
                    target_idx = pair.get('target_idx')
                    source_text = pair.get('source_text', '')
                    target_text = pair.get('target_text', '')
                    similarity_score = pair.get('similarity_score', 0.0)
                else:
                    # Handle AlignedPair object
                    source_idx = pair.source_idx
                    target_idx = pair.target_idx
                    source_text = pair.source_text
                    target_text = pair.target_text
                    similarity_score = pair.similarity_score
                
                # Extract discourse features for this pair
                features = self._extract_discourse_features(source_text, target_text, similarity_score)
                
                # Apply heuristic rules to determine tags
                if request.apply_heuristic_rules:
                    pair_annotations = self._apply_heuristic_classification(
                        features, 
                        [source_idx], 
                        [target_idx], 
                        request.user_config
                    )
                    annotations.extend(pair_annotations)
            
            # Process unaligned source paragraphs (only if OM+ is enabled)
            if request.user_config.tag_config[TagType.OM_PLUS].active and unaligned_source_indices:
                om_annotations = self._process_unaligned_paragraphs(
                    unaligned_source_indices,
                    source_paragraphs,
                    request.user_config
                )
                annotations.extend(om_annotations)
            
            # Calculate analysis metrics
            confidence_distribution = self._calculate_confidence_distribution(annotations)
            tag_distribution = self._calculate_tag_distribution(annotations)
            
            # Calculate reduction ratios
            total_source_words = sum(len(p.split()) for p in source_paragraphs if p)
            total_target_words = sum(len(p.split()) for p in target_paragraphs if p)
            actual_reduction = 1.0 - (total_target_words / max(total_source_words, 1))
            expected_reduction = request.user_config.expected_reduction_ratio
            
            # Generate warnings and recommendations
            warnings, recommendations = self._generate_insights(
                annotations, 
                actual_reduction, 
                expected_reduction, 
                request.user_config
            )
            
            processing_time = time.time() - start_time
            
            # Ensure user_config_used is a plain dict to avoid cross-module Pydantic instance issues
            user_config_payload = request.user_config.model_dump() if hasattr(request.user_config, 'model_dump') else getattr(request.user_config, 'dict', lambda: request.user_config)()

            return FeatureExtractionResponse(
                success=True,
                annotated_data=annotations,
                total_annotations=len(annotations),
                confidence_distribution=confidence_distribution,
                tag_distribution=tag_distribution,
                processing_time=processing_time,
                features_extracted=len(aligned_pairs),
                average_confidence=sum(a.confidence for a in annotations) / max(len(annotations), 1),
                reduction_ratio_achieved=actual_reduction,
                reduction_ratio_expected=expected_reduction,
                warnings=warnings,
                recommendations=recommendations,
                user_config_used=user_config_payload
            )
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            user_config_payload = request.user_config.model_dump() if hasattr(request.user_config, 'model_dump') else getattr(request.user_config, 'dict', lambda: request.user_config)()

            return FeatureExtractionResponse(
                success=False,
                annotated_data=[],
                total_annotations=0,
                confidence_distribution={ConfidenceLevel.HIGH: 0, ConfidenceLevel.MEDIUM: 0, ConfidenceLevel.LOW: 0},
                tag_distribution={},
                processing_time=time.time() - start_time,
                features_extracted=0,
                average_confidence=0.0,
                reduction_ratio_achieved=0.0,
                reduction_ratio_expected=request.user_config.expected_reduction_ratio,
                warnings=[f"Feature extraction failed: {str(e)}"],
                recommendations=["Please check input data and try again"],
                user_config_used=user_config_payload
            )

    def _extract_discourse_features(
        self, 
        source_text: str, 
        target_text: str, 
        similarity_score: float
    ) -> DiscourseFeatures:
        """Extract discourse-level features from aligned paragraph pair"""
        
        # Basic text metrics
        source_words = len(source_text.split())
        target_words = len(target_text.split())
        source_chars = len(source_text)
        target_chars = len(target_text)
        
        # Calculate reduction ratios
        word_reduction = 1.0 - (target_words / max(source_words, 1))
        char_reduction = 1.0 - (target_chars / max(source_chars, 1))
        
        # Readability analysis
        try:
            source_readability = textstat.flesch_reading_ease(source_text)
            target_readability = textstat.flesch_reading_ease(target_text)
            readability_change = target_readability - source_readability
        except:
            readability_change = 0.0
        
        # Sentence analysis
        source_sentences = source_text.count('.') + source_text.count('!') + source_text.count('?')
        target_sentences = target_text.count('.') + target_text.count('!') + target_text.count('?')
        
        avg_source_sentence_length = source_words / max(source_sentences, 1)
        avg_target_sentence_length = target_words / max(target_sentences, 1)
        sentence_length_change = avg_target_sentence_length - avg_source_sentence_length
        
        # Advanced features if spaCy is available
        if self.nlp:
            try:
                source_doc = self.nlp(source_text)
                target_doc = self.nlp(target_text)
                
                # Lexical density (content words / total words)
                source_content_words = sum(1 for token in source_doc if not token.is_stop and token.is_alpha)
                target_content_words = sum(1 for token in target_doc if not token.is_stop and token.is_alpha)
                
                source_lexical_density = source_content_words / max(source_words, 1)
                target_lexical_density = target_content_words / max(target_words, 1)
                lexical_density_change = target_lexical_density - source_lexical_density
                
                # Vocabulary complexity (avg word length of content words)
                source_complex_words = [token.text for token in source_doc if not token.is_stop and len(token.text) > 6]
                target_complex_words = [token.text for token in target_doc if not token.is_stop and len(token.text) > 6]
                
                vocab_complexity_change = len(target_complex_words) / max(len(source_complex_words), 1) - 1.0
                
                # Syntactic complexity (dependency depth)
                source_depths = [self._calculate_dependency_depth(token) for token in source_doc]
                target_depths = [self._calculate_dependency_depth(token) for token in target_doc]
                
                avg_source_depth = sum(source_depths) / max(len(source_depths), 1)
                avg_target_depth = sum(target_depths) / max(len(target_depths), 1)
                syntactic_complexity_change = avg_target_depth - avg_source_depth
                
            except Exception as e:
                logger.warning(f"Advanced feature extraction failed: {e}")
                lexical_density_change = 0.0
                vocab_complexity_change = 0.0
                syntactic_complexity_change = 0.0
        else:
            lexical_density_change = 0.0
            vocab_complexity_change = 0.0
            syntactic_complexity_change = 0.0
        
        return DiscourseFeatures(
            word_reduction_ratio=word_reduction,
            character_reduction_ratio=char_reduction,
            readability_change=readability_change,
            complexity_reduction=abs(readability_change),  # Positive change indicates simplification
            lexical_density_change=lexical_density_change,
            vocabulary_complexity_change=vocab_complexity_change,
            sentence_length_change=sentence_length_change,
            syntactic_complexity_change=syntactic_complexity_change,
            semantic_similarity=similarity_score,
            information_preservation=min(similarity_score + 0.2, 1.0)  # Conservative estimate
        )

    def _apply_heuristic_classification(
        self,
        features: DiscourseFeatures,
        source_indices: List[int],
        target_indices: List[int],
        user_config: UserConfiguration
    ) -> List[TagAnnotation]:
        """Apply heuristic rules to classify simplification strategies based on official tag definitions"""
        
        annotations = []
        
        # SL+ (Adequação de Vocabulário) - Vocabulary adaptation
        # "Substituição de termos difíceis, técnicos ou raros por sinônimos mais simples, comuns ou hiperônimos"
        if user_config.tag_config[TagType.SL_PLUS].active:
            sl_evidence = []
            sl_score = 0.0
            
            # Evidence: vocabulary complexity reduction (difficult → simple terms)
            if features.vocabulary_complexity_change < -0.15:
                sl_evidence.append(TagEvidence(
                    feature_name="vocabulary_simplification",
                    evidence_value=abs(features.vocabulary_complexity_change),
                    threshold_met=True,
                    contribution_score=0.4
                ))
                sl_score += 0.4
            
            # Evidence: readability improvement due to simpler vocabulary
            if features.readability_change > 8.0:
                sl_evidence.append(TagEvidence(
                    feature_name="readability_improvement_vocabulary",
                    evidence_value=features.readability_change,
                    threshold_met=True,
                    contribution_score=0.3
                ))
                sl_score += 0.3
            
            # Evidence: word reduction with high semantic preservation (synonym substitution)
            if 0.1 < features.word_reduction_ratio < 0.4 and features.semantic_similarity > 0.75:
                sl_evidence.append(TagEvidence(
                    feature_name="lexical_substitution_pattern",
                    evidence_value=features.semantic_similarity,
                    threshold_met=True,
                    contribution_score=0.3
                ))
                sl_score += 0.3
            
            if sl_evidence:
                final_sl_score = min(sl_score * user_config.tag_config[TagType.SL_PLUS].weight, 1.0)
                if final_sl_score >= user_config.confidence_thresholds[ConfidenceLevel.LOW]:
                    annotations.append(TagAnnotation(
                        id=str(uuid.uuid4()),
                        tag=TagType.SL_PLUS,
                        confidence=final_sl_score,
                        confidence_level=self._determine_confidence_level(final_sl_score, user_config),
                        source_indices=source_indices,
                        target_indices=target_indices,
                        evidence=sl_evidence,
                        features=features
                    ))
        
        # RP+ (Fragmentação Sintática) - Syntactic fragmentation  
        # "Divisão de períodos extensos ou complexos em sentenças mais curtas e diretas"
        if user_config.tag_config[TagType.RP_PLUS].active:
            rp_evidence = []
            rp_score = 0.0
            
            # Evidence: sentence length reduction (complex → shorter sentences)
            if features.sentence_length_change < -3.0:
                rp_evidence.append(TagEvidence(
                    feature_name="sentence_fragmentation",
                    evidence_value=abs(features.sentence_length_change),
                    threshold_met=True,
                    contribution_score=0.5
                ))
                rp_score += 0.5
            
            # Evidence: syntactic complexity reduction
            if features.syntactic_complexity_change < -0.5:
                rp_evidence.append(TagEvidence(
                    feature_name="syntactic_simplification",
                    evidence_value=abs(features.syntactic_complexity_change),
                    threshold_met=True,
                    contribution_score=0.3
                ))
                rp_score += 0.3
            
            if rp_evidence:
                final_rp_score = min(rp_score * user_config.tag_config[TagType.RP_PLUS].weight, 1.0)
                if final_rp_score >= user_config.confidence_thresholds[ConfidenceLevel.LOW]:
                    annotations.append(TagAnnotation(
                        id=str(uuid.uuid4()),
                        tag=TagType.RP_PLUS,
                        confidence=final_rp_score,
                        confidence_level=self._determine_confidence_level(final_rp_score, user_config),
                        source_indices=source_indices,
                        target_indices=target_indices,
                        evidence=rp_evidence,
                        features=features
                    ))
        
        # RF+ (Reescrita Global) - Global rewriting
        # "Estratégia abrangente que integra múltiplos procedimentos de simplificação"
        if user_config.tag_config[TagType.RF_PLUS].active:
            rf_evidence = []
            rf_score = 0.0
            
            # Evidence: significant overall transformation (multiple changes)
            transformation_indicators = 0
            
            if features.word_reduction_ratio > 0.25:  # Significant word reduction
                transformation_indicators += 1
            if features.readability_change > 10.0:  # Major readability improvement
                transformation_indicators += 1
            if abs(features.sentence_length_change) > 2.0:  # Sentence structure changes
                transformation_indicators += 1
            if abs(features.lexical_density_change) > 0.1:  # Lexical density changes
                transformation_indicators += 1
            if features.vocabulary_complexity_change < -0.1:  # Vocabulary simplification
                transformation_indicators += 1
            
            # RF+ requires multiple types of changes (global rewriting)
            if transformation_indicators >= 3:
                rf_evidence.append(TagEvidence(
                    feature_name="multiple_transformation_types",
                    evidence_value=float(transformation_indicators),
                    threshold_met=True,
                    contribution_score=0.6
                ))
                rf_score += 0.6
            
            # Evidence: substantial text reduction with good semantic preservation
            if features.word_reduction_ratio > 0.4 and features.semantic_similarity > 0.65:
                rf_evidence.append(TagEvidence(
                    feature_name="comprehensive_rewriting",
                    evidence_value=features.word_reduction_ratio,
                    threshold_met=True,
                    contribution_score=0.4
                ))
                rf_score += 0.4
            
            if rf_evidence:
                final_rf_score = min(rf_score * user_config.tag_config[TagType.RF_PLUS].weight, 1.0)
                if final_rf_score >= user_config.confidence_thresholds[ConfidenceLevel.LOW]:
                    annotations.append(TagAnnotation(
                        id=str(uuid.uuid4()),
                        tag=TagType.RF_PLUS,
                        confidence=final_rf_score,
                        confidence_level=self._determine_confidence_level(final_rf_score, user_config),
                        source_indices=source_indices,
                        target_indices=target_indices,
                        evidence=rf_evidence,
                        features=features
                    ))
        
        # EXP+ (Explicitação e Detalhamento) - Explicitation and detailing
        # "Adição de informações, exemplos ou paráfrases para esclarecer conteúdos implícitos"
        if user_config.tag_config[TagType.EXP_PLUS].active:
            exp_evidence = []
            exp_score = 0.0
            
            # Evidence: text expansion with semantic similarity (adding explanations)
            if features.word_reduction_ratio < -0.1 and features.semantic_similarity > 0.7:  # Negative = expansion
                exp_evidence.append(TagEvidence(
                    feature_name="content_expansion",
                    evidence_value=abs(features.word_reduction_ratio),
                    threshold_met=True,
                    contribution_score=0.5
                ))
                exp_score += 0.5
            
            # Evidence: readability improvement through clarification
            if features.readability_change > 5.0 and features.word_reduction_ratio < 0:
                exp_evidence.append(TagEvidence(
                    feature_name="clarification_expansion",
                    evidence_value=features.readability_change,
                    threshold_met=True,
                    contribution_score=0.3
                ))
                exp_score += 0.3
            
            if exp_evidence:
                final_exp_score = min(exp_score * user_config.tag_config[TagType.EXP_PLUS].weight, 1.0)
                if final_exp_score >= user_config.confidence_thresholds[ConfidenceLevel.LOW]:
                    annotations.append(TagAnnotation(
                        id=str(uuid.uuid4()),
                        tag=TagType.EXP_PLUS,
                        confidence=final_exp_score,
                        confidence_level=self._determine_confidence_level(final_exp_score, user_config),
                        source_indices=source_indices,
                        target_indices=target_indices,
                        evidence=exp_evidence,
                        features=features
                    ))
        
        # MOD+ (Reinterpretação Perspectiva) - Perspective reinterpretation
        # "Reformulação semântica para adaptar o conteúdo ao repertório do público"
        if user_config.tag_config[TagType.MOD_PLUS].active:
            mod_evidence = []
            mod_score = 0.0
            
            # Evidence: semantic changes with moderate similarity (perspective shift)
            if 0.5 < features.semantic_similarity < 0.8 and features.readability_change > 8.0:
                mod_evidence.append(TagEvidence(
                    feature_name="semantic_adaptation",
                    evidence_value=1.0 - features.semantic_similarity,
                    threshold_met=True,
                    contribution_score=0.4
                ))
                mod_score += 0.4
            
            # Evidence: vocabulary changes for audience adaptation
            if features.vocabulary_complexity_change < -0.2:
                mod_evidence.append(TagEvidence(
                    feature_name="audience_vocabulary_adaptation",
                    evidence_value=abs(features.vocabulary_complexity_change),
                    threshold_met=True,
                    contribution_score=0.3
                ))
                mod_score += 0.3
            
            if mod_evidence:
                final_mod_score = min(mod_score * user_config.tag_config[TagType.MOD_PLUS].weight, 1.0)
                if final_mod_score >= user_config.confidence_thresholds[ConfidenceLevel.LOW]:
                    annotations.append(TagAnnotation(
                        id=str(uuid.uuid4()),
                        tag=TagType.MOD_PLUS,
                        confidence=final_mod_score,
                        confidence_level=self._determine_confidence_level(final_mod_score, user_config),
                        source_indices=source_indices,
                        target_indices=target_indices,
                        evidence=mod_evidence,
                        features=features
                    ))
        
        return annotations

    def _process_unaligned_paragraphs(
        self,
        unaligned_indices: List[int],
        source_paragraphs: List[str],
        user_config: UserConfiguration
    ) -> List[TagAnnotation]:
        """Process unaligned source paragraphs for OM+ (Supressão Seletiva)
        
        OM+ Definition: "Exclusão de elementos redundantes, ambíguos, idiomáticos ou 
        periféricos que não comprometem o núcleo do conteúdo e atrapalham a compreensão"
        
        Note: OM+ is applied only when manually activated by the user, not by default
        """
        
        annotations = []
        
        if not user_config.tag_config[TagType.OM_PLUS].active:
            return annotations
        
        for source_idx in unaligned_indices:
            if source_idx < len(source_paragraphs):
                source_text = source_paragraphs[source_idx]
                
                # Evidence for selective suppression (OM+)
                om_evidence = [
                    TagEvidence(
                        feature_name="content_omission",  
                        evidence_value=1.0,
                        threshold_met=True,
                        contribution_score=0.7
                    ),
                    TagEvidence(
                        feature_name="redundant_content_removal",
                        evidence_value=len(source_text.split()) / 100.0,  # Text length as complexity indicator
                        threshold_met=True,
                        contribution_score=0.3
                    )
                ]
                
                # Create features for omitted content (complete reduction)
                features = DiscourseFeatures(
                    word_reduction_ratio=1.0,  # Complete omission
                    character_reduction_ratio=1.0,
                    readability_change=0.0,  # No readability change (content removed)
                    complexity_reduction=0.0,
                    lexical_density_change=0.0,
                    vocabulary_complexity_change=0.0,
                    sentence_length_change=0.0,
                    syntactic_complexity_change=0.0,
                    semantic_similarity=0.0,  # No semantic similarity (content omitted)
                    information_preservation=0.0  # Information not preserved (intentionally omitted)
                )
                
                final_om_score = min(0.7 * user_config.tag_config[TagType.OM_PLUS].weight, 1.0)
                
                annotations.append(TagAnnotation(
                    id=str(uuid.uuid4()),
                    tag=TagType.OM_PLUS,
                    confidence=final_om_score,
                    confidence_level=self._determine_confidence_level(final_om_score, user_config),
                    source_indices=[source_idx],
                    target_indices=[],  # No target for omitted content
                    evidence=om_evidence,
                    features=features
                ))
        
        return annotations

    def _calculate_dependency_depth(self, token) -> int:
        """Calculate dependency depth for syntactic complexity"""
        depth = 0
        current = token
        while current.head != current:
            depth += 1
            current = current.head
            if depth > 10:  # Prevent infinite loops
                break
        return depth

    def _determine_confidence_level(
        self, 
        confidence: float, 
        user_config: UserConfiguration
    ) -> ConfidenceLevel:
        """Determine categorical confidence level"""
        if confidence >= user_config.confidence_thresholds[ConfidenceLevel.HIGH]:
            return ConfidenceLevel.HIGH
        elif confidence >= user_config.confidence_thresholds[ConfidenceLevel.MEDIUM]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _calculate_confidence_distribution(
        self, 
        annotations: List[TagAnnotation]
    ) -> Dict[ConfidenceLevel, int]:
        """Calculate distribution of confidence levels"""
        distribution = {level: 0 for level in ConfidenceLevel}
        for annotation in annotations:
            distribution[annotation.confidence_level] += 1
        return distribution

    def _calculate_tag_distribution(
        self, 
        annotations: List[TagAnnotation]
    ) -> Dict[TagType, int]:
        """Calculate distribution of tag types"""
        distribution = defaultdict(int)
        for annotation in annotations:
            distribution[annotation.tag] += 1
        return dict(distribution)

    def _generate_insights(
        self,
        annotations: List[TagAnnotation],
        actual_reduction: float,
        expected_reduction: float,
        user_config: UserConfiguration
    ) -> Tuple[List[str], List[str]]:
        """Generate warnings and recommendations based on analysis"""
        
        warnings = []
        recommendations = []
        
        # Check reduction ratio
        if actual_reduction < expected_reduction - user_config.reduction_tolerance:
            warnings.append(
                f"Text reduction ({actual_reduction:.1%}) is below expected level ({expected_reduction:.1%})"
            )
            recommendations.append("Consider enabling OM+ tag or increasing simplification strategies")
        
        # Check if no annotations were found
        if not annotations:
            warnings.append("No simplification strategies detected")
            recommendations.append("Review text pair for actual simplification or adjust confidence thresholds")
        
        # Check confidence distribution
        high_confidence = sum(1 for a in annotations if a.confidence_level == ConfidenceLevel.HIGH)
        if high_confidence == 0 and len(annotations) > 0:
            warnings.append("No high-confidence tag assignments found")
            recommendations.append("Consider manual review of detected strategies")
        
        return warnings, recommendations

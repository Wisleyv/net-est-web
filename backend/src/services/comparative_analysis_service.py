"""
Comparative Analysis Service - Phase 2.B.5 Implementation
Service for analyzing differences between source and simplified texts
"""

import re
import uuid
import math
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

import textstat
import spacy
from difflib import SequenceMatcher

from ..models.comparative_analysis import (
    ComparativeAnalysisRequest,
    ComparativeAnalysisResponse,
    SimplificationStrategy,
    SimplificationStrategyType,
    ReadabilityMetrics,
    ReadabilityMetric,
    LexicalAnalysis,
    SyntacticAnalysis,
    SemanticAnalysis,
    AnalysisHistoryItem
)

logger = logging.getLogger(__name__)


class ComparativeAnalysisService:
    """Service for performing comparative text analysis"""
    
    def __init__(self):
        self.analysis_history: List[AnalysisHistoryItem] = []
        try:
            # Load spaCy model for advanced analysis
            self.nlp = spacy.load("pt_core_news_sm")
            logger.info("SpaCy Portuguese model loaded successfully")
        except OSError:
            logger.warning("SpaCy Portuguese model not found, using basic analysis")
            self.nlp = None

    async def perform_comparative_analysis(
        self, 
        request: ComparativeAnalysisRequest
    ) -> ComparativeAnalysisResponse:
        """Perform comprehensive comparative analysis"""
        start_time = datetime.now()
        analysis_id = str(uuid.uuid4())
        
        try:
            # Basic metrics
            source_length = len(request.source_text)
            target_length = len(request.target_text)
            compression_ratio = target_length / source_length if source_length > 0 else 0
            
            # Initialize response
            response = ComparativeAnalysisResponse(
                analysis_id=analysis_id,
                timestamp=start_time,
                source_text=request.source_text,
                target_text=request.target_text,
                source_length=source_length,
                target_length=target_length,
                compression_ratio=compression_ratio,
                overall_score=0,
                overall_assessment="",
                strategies_count=0,
                semantic_preservation=0,
                readability_improvement=0,
                processing_time=0
            )
            
            # Perform requested analyses
            if request.analysis_options.include_lexical_analysis:
                response.lexical_analysis = self._perform_lexical_analysis(
                    request.source_text, request.target_text
                )
            
            if request.analysis_options.include_syntactic_analysis:
                response.syntactic_analysis = self._perform_syntactic_analysis(
                    request.source_text, request.target_text
                )
            
            if request.analysis_options.include_semantic_analysis:
                response.semantic_analysis = self._perform_semantic_analysis(
                    request.source_text, request.target_text
                )
            
            if request.analysis_options.include_readability_metrics:
                response.readability_metrics = self._calculate_readability_metrics(
                    request.source_text, request.target_text
                )
            
            if request.analysis_options.include_strategy_identification:
                response.simplification_strategies = self._identify_simplification_strategies(
                    request.source_text, request.target_text
                )
                response.strategies_count = len(response.simplification_strategies)
            
            # Generate highlighted differences
            response.highlighted_differences = self._generate_highlighted_differences(
                request.source_text, request.target_text
            )
            
            # Calculate overall metrics
            response.overall_score = self._calculate_overall_score(response)
            response.overall_assessment = self._generate_assessment(response)
            response.semantic_preservation = self._calculate_semantic_preservation(response)
            response.readability_improvement = self._calculate_readability_improvement(response)
            
            # Calculate processing time
            end_time = datetime.now()
            response.processing_time = (end_time - start_time).total_seconds()
            
            # Store in history
            history_item = AnalysisHistoryItem(
                analysis_id=analysis_id,
                timestamp=start_time,
                source_length=source_length,
                target_length=target_length,
                overall_score=response.overall_score,
                strategies_count=response.strategies_count,
                semantic_preservation=response.semantic_preservation,
                readability_improvement=response.readability_improvement
            )
            self.analysis_history.append(history_item)
            
            logger.info(f"Comparative analysis completed: {analysis_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in comparative analysis: {str(e)}")
            raise

    def _perform_lexical_analysis(self, source_text: str, target_text: str) -> LexicalAnalysis:
        """Perform lexical analysis comparing word usage"""
        # Tokenize texts
        source_words = self._tokenize_text(source_text)
        target_words = self._tokenize_text(target_text)
        
        # Calculate metrics
        source_unique = len(set(source_words))
        target_unique = len(set(target_words))
        
        # Calculate vocabulary overlap
        source_set = set(source_words)
        target_set = set(target_words)
        overlap = len(source_set.intersection(target_set))
        vocab_overlap = overlap / len(source_set.union(target_set)) if source_set.union(target_set) else 0
        
        # Calculate complexity (average word length)
        source_complexity = sum(len(word) for word in source_words) / len(source_words) if source_words else 0
        target_complexity = sum(len(word) for word in target_words) / len(target_words) if target_words else 0
        
        complexity_reduction = (source_complexity - target_complexity) / source_complexity if source_complexity > 0 else 0
        
        # Find substitutions
        substitutions = self._find_word_substitutions(source_text, target_text)
        
        return LexicalAnalysis(
            source_unique_words=source_unique,
            target_unique_words=target_unique,
            source_complexity=source_complexity,
            target_complexity=target_complexity,
            vocabulary_overlap=vocab_overlap,
            complexity_reduction=complexity_reduction,
            substitutions=substitutions
        )

    def _perform_syntactic_analysis(self, source_text: str, target_text: str) -> SyntacticAnalysis:
        """Perform syntactic analysis comparing sentence structure"""
        # Split into sentences
        source_sentences = self._split_sentences(source_text)
        target_sentences = self._split_sentences(target_text)
        
        # Calculate average sentence lengths
        source_avg_len = sum(len(s.split()) for s in source_sentences) / len(source_sentences) if source_sentences else 0
        target_avg_len = sum(len(s.split()) for s in target_sentences) / len(target_sentences) if target_sentences else 0
        
        # Calculate clause metrics (simplified - based on punctuation)
        source_clauses = self._count_clauses(source_text)
        target_clauses = self._count_clauses(target_text)
        
        source_avg_clause = len(source_text.split()) / source_clauses if source_clauses > 0 else 0
        target_avg_clause = len(target_text.split()) / target_clauses if target_clauses > 0 else 0
        
        # Calculate ratios
        simplification_ratio = target_avg_len / source_avg_len if source_avg_len > 0 else 1
        clause_reduction = (source_clauses - target_clauses) / source_clauses if source_clauses > 0 else 0
        
        # Identify structural changes
        structural_changes = self._identify_structural_changes(source_text, target_text)
        
        return SyntacticAnalysis(
            source_avg_sentence_length=source_avg_len,
            target_avg_sentence_length=target_avg_len,
            source_avg_clause_length=source_avg_clause,
            target_avg_clause_length=target_avg_clause,
            sentence_simplification_ratio=simplification_ratio,
            clause_reduction=max(0, clause_reduction),
            structural_changes=structural_changes
        )

    def _perform_semantic_analysis(self, source_text: str, target_text: str) -> SemanticAnalysis:
        """Perform semantic analysis comparing meaning preservation"""
        # Calculate semantic similarity using simple metrics
        similarity = self._calculate_text_similarity(source_text, target_text)
        
        # Estimate meaning preservation (based on content overlap)
        meaning_preservation = min(100, similarity * 100)
        
        # Calculate information loss
        information_loss = max(0, 100 - meaning_preservation)
        
        # Identify concept simplifications
        concept_simplifications = self._identify_concept_simplifications(source_text, target_text)
        
        return SemanticAnalysis(
            semantic_similarity=similarity,
            meaning_preservation=meaning_preservation,
            information_loss=information_loss,
            concept_simplification=concept_simplifications
        )

    def _calculate_readability_metrics(self, source_text: str, target_text: str) -> ReadabilityMetrics:
        """Calculate various readability metrics"""
        # Flesch Reading Ease
        source_flesch = textstat.flesch_reading_ease(source_text)
        target_flesch = textstat.flesch_reading_ease(target_text)
        flesch_improvement = target_flesch - source_flesch
        
        # Flesch-Kincaid Grade Level
        source_fk = textstat.flesch_kincaid_grade(source_text)
        target_fk = textstat.flesch_kincaid_grade(target_text)
        fk_improvement = source_fk - target_fk
        
        # Automated Readability Index
        source_ari = textstat.automated_readability_index(source_text)
        target_ari = textstat.automated_readability_index(target_text)
        ari_improvement = source_ari - target_ari
        
        # Coleman-Liau Index
        source_cli = textstat.coleman_liau_index(source_text)
        target_cli = textstat.coleman_liau_index(target_text)
        cli_improvement = source_cli - target_cli
        
        # Gunning Fog Index
        source_fog = textstat.gunning_fog(source_text)
        target_fog = textstat.gunning_fog(target_text)
        fog_improvement = source_fog - target_fog
        
        return ReadabilityMetrics(
            flesch_reading_ease=ReadabilityMetric(
                label="Flesch Reading Ease",
                source=source_flesch,
                target=target_flesch,
                improvement=flesch_improvement,
                description="Higher scores indicate easier reading"
            ),
            flesch_kincaid_grade=ReadabilityMetric(
                label="Flesch-Kincaid Grade",
                source=source_fk,
                target=target_fk,
                improvement=fk_improvement,
                description="Grade level required to understand the text"
            ),
            automated_readability_index=ReadabilityMetric(
                label="Automated Readability Index",
                source=source_ari,
                target=target_ari,
                improvement=ari_improvement,
                description="Grade level based on character count"
            ),
            coleman_liau_index=ReadabilityMetric(
                label="Coleman-Liau Index",
                source=source_cli,
                target=target_cli,
                improvement=cli_improvement,
                description="Grade level based on characters per word"
            ),
            gunning_fog=ReadabilityMetric(
                label="Gunning Fog Index",
                source=source_fog,
                target=target_fog,
                improvement=fog_improvement,
                description="Grade level based on sentence and syllable complexity"
            )
        )

    def _identify_simplification_strategies(
        self, source_text: str, target_text: str
    ) -> List[SimplificationStrategy]:
        """Identify simplification strategies used"""
        strategies = []
        
        # Lexical simplification
        if self._has_lexical_simplification(source_text, target_text):
            strategies.append(SimplificationStrategy(
                name="Lexical Simplification",
                type=SimplificationStrategyType.LEXICAL,
                description="Complex words replaced with simpler alternatives",
                impact="high",
                confidence=0.8,
                examples=self._find_word_substitutions(source_text, target_text)[:3]
            ))
        
        # Syntactic simplification
        if self._has_syntactic_simplification(source_text, target_text):
            strategies.append(SimplificationStrategy(
                name="Sentence Shortening",
                type=SimplificationStrategyType.SYNTACTIC,
                description="Long sentences broken into shorter ones",
                impact="medium",
                confidence=0.7,
                examples=[]
            ))
        
        # Content reduction
        if len(target_text) < len(source_text) * 0.8:
            strategies.append(SimplificationStrategy(
                name="Content Reduction",
                type=SimplificationStrategyType.STRUCTURAL,
                description="Non-essential information removed",
                impact="medium",
                confidence=0.6,
                examples=[]
            ))
        
        return strategies

    def _generate_highlighted_differences(
        self, source_text: str, target_text: str
    ) -> List[Dict[str, str]]:
        """Generate highlighted differences for UI display"""
        # Use SequenceMatcher to find differences
        matcher = SequenceMatcher(None, source_text.split(), target_text.split())
        differences = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                source_segment = ' '.join(source_text.split()[i1:i2])
                target_segment = ' '.join(target_text.split()[j1:j2])
                
                differences.append({
                    'type': tag,
                    'source': source_segment,
                    'target': target_segment
                })
        
        return differences[:10]  # Limit to first 10 differences

    # Helper methods
    def _tokenize_text(self, text: str) -> List[str]:
        """Simple text tokenization"""
        return re.findall(r'\b\w+\b', text.lower())

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _count_clauses(self, text: str) -> int:
        """Count clauses based on punctuation"""
        clause_markers = [',', ';', ':', '(', ')']
        clause_count = 1  # Start with 1 for the main clause
        for marker in clause_markers:
            clause_count += text.count(marker)
        return clause_count

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using word overlap"""
        words1 = set(self._tokenize_text(text1))
        words2 = set(self._tokenize_text(text2))
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0

    def _find_word_substitutions(self, source_text: str, target_text: str) -> List[Dict[str, str]]:
        """Find word substitutions between texts"""
        # This is a simplified implementation
        # In practice, you'd use more sophisticated alignment algorithms
        source_words = self._tokenize_text(source_text)
        target_words = self._tokenize_text(target_text)
        
        substitutions = []
        # Simple heuristic: find unique words in source that might have been replaced
        source_unique = set(source_words) - set(target_words)
        target_unique = set(target_words) - set(source_words)
        
        # Match by length similarity (very basic)
        for s_word in list(source_unique)[:5]:
            for t_word in list(target_unique):
                if abs(len(s_word) - len(t_word)) <= 2 and len(s_word) > 4:
                    substitutions.append({
                        'source': s_word,
                        'target': t_word,
                        'type': 'lexical_substitution'
                    })
                    target_unique.discard(t_word)
                    break
        
        return substitutions

    def _identify_structural_changes(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Identify structural changes in the text"""
        changes = []
        
        source_sentences = len(self._split_sentences(source_text))
        target_sentences = len(self._split_sentences(target_text))
        
        if target_sentences > source_sentences:
            changes.append({
                'type': 'sentence_splitting',
                'description': f'Sentences increased from {source_sentences} to {target_sentences}',
                'impact': 'Improved readability through shorter sentences'
            })
        
        return changes

    def _identify_concept_simplifications(self, source_text: str, target_text: str) -> List[Dict[str, str]]:
        """Identify concept simplifications"""
        # This is a placeholder for more sophisticated concept analysis
        return [
            {
                'concept': 'Technical terminology',
                'simplification': 'Replaced with common language'
            }
        ]

    def _has_lexical_simplification(self, source_text: str, target_text: str) -> bool:
        """Check if lexical simplification occurred"""
        source_avg_word_len = sum(len(word) for word in self._tokenize_text(source_text)) / len(self._tokenize_text(source_text))
        target_avg_word_len = sum(len(word) for word in self._tokenize_text(target_text)) / len(self._tokenize_text(target_text))
        
        return target_avg_word_len < source_avg_word_len * 0.9

    def _has_syntactic_simplification(self, source_text: str, target_text: str) -> bool:
        """Check if syntactic simplification occurred"""
        source_sentences = self._split_sentences(source_text)
        target_sentences = self._split_sentences(target_text)
        
        if not source_sentences or not target_sentences:
            return False
        
        source_avg_len = sum(len(s.split()) for s in source_sentences) / len(source_sentences)
        target_avg_len = sum(len(s.split()) for s in target_sentences) / len(target_sentences)
        
        return target_avg_len < source_avg_len * 0.8

    def _calculate_overall_score(self, response: ComparativeAnalysisResponse) -> int:
        """Calculate overall simplification quality score"""
        score = 0
        factors = 0
        
        if response.readability_metrics:
            # Readability improvement contributes 40%
            flesch_improvement = response.readability_metrics.flesch_reading_ease.improvement
            if flesch_improvement > 0:
                score += min(40, flesch_improvement * 2)
            factors += 40
        
        if response.semantic_analysis:
            # Semantic preservation contributes 30%
            score += response.semantic_analysis.meaning_preservation * 0.3
            factors += 30
        
        if response.strategies_count > 0:
            # Strategy identification contributes 30%
            score += min(30, response.strategies_count * 10)
            factors += 30
        
        return int(score * 100 / factors) if factors > 0 else 50

    def _generate_assessment(self, response: ComparativeAnalysisResponse) -> str:
        """Generate overall assessment text"""
        score = response.overall_score
        
        if score >= 80:
            return "Excellent simplification with strong readability improvement and meaning preservation"
        elif score >= 60:
            return "Good simplification with noticeable improvements in readability"
        elif score >= 40:
            return "Moderate simplification with some readability gains"
        else:
            return "Limited simplification effectiveness"

    def _calculate_semantic_preservation(self, response: ComparativeAnalysisResponse) -> float:
        """Calculate semantic preservation percentage"""
        if response.semantic_analysis:
            return response.semantic_analysis.meaning_preservation
        return 75.0  # Default estimate

    def _calculate_readability_improvement(self, response: ComparativeAnalysisResponse) -> float:
        """Calculate readability improvement percentage"""
        if response.readability_metrics:
            flesch_improvement = response.readability_metrics.flesch_reading_ease.improvement
            return max(0, min(100, flesch_improvement))
        return 0.0

    async def get_analysis_history(self) -> List[AnalysisHistoryItem]:
        """Get analysis history"""
        return self.analysis_history.copy()

    async def export_analysis(self, analysis_id: str, format: str) -> Dict[str, Any]:
        """Export analysis results"""
        # Find analysis in history
        analysis = next((a for a in self.analysis_history if a.analysis_id == analysis_id), None)
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        # For now, return basic export data
        return {
            "analysis_id": analysis_id,
            "format": format,
            "export_url": f"/exports/{analysis_id}.{format}",
            "created_at": datetime.now().isoformat()
        }

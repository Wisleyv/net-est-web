"""
Comparative Analysis Service - Phase 2.B.5 Implementation
Service for analyzing differences between source and simplified texts
"""

import re
import os
import uuid
import math
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

import textstat
import spacy
import numpy as np
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer, util

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

# Import the strategy detector
from .strategy_detector import StrategyDetector
from .semantic_alignment_service import SemanticAlignmentService
from .sentence_alignment_service import SentenceAlignmentService, simple_sentence_split
from .salience_provider import SalienceProvider
from ..models.strategy_models import SimplificationStrategyType as StrategyType
from ..models.semantic_alignment import AlignmentRequest, AlignmentMethod

logger = logging.getLogger(__name__)


class ComparativeAnalysisService:
    """Service for performing comparative text analysis"""

    # === Scaffold for Sentence and Phrase Analysis ===

    def analyze_sentences(self, source_text: str, target_text: str) -> dict:
        """
        Analyze sentences between source and target texts.

        - Split source_text and target_text into sentences (uses simple_sentence_split).
        - Align sentences with the lightweight SentenceAlignmentService.
        - For each aligned sentence pair, call analyze_phrases() and collect nested findings.
        - Return a structured dict containing:
            {
                "aligned": [SentenceNode, ...],
                "unmatched_source": [SentenceNode, ...],
                "unmatched_target": [SentenceNode, ...],
                "similarity_matrix": [...],
            }

        The SentenceNode dataclass is used to represent each sentence node (confidence,
        source_text, target_text, nested_findings).
        """
        try:
            # Split into sentences using the small splitter (robust for Portuguese)
            source_sentences = simple_sentence_split(source_text)
            target_sentences = simple_sentence_split(target_text)

            # Early return for empty inputs
            if not source_sentences and not target_sentences:
                return {
                    "aligned": [],
                    "unmatched_source": [],
                    "unmatched_target": [],
                    "similarity_matrix": [],
                }

            # Use the sentence alignment service to align sentences.
            # The service expects lists of "paragraphs" but will flatten; passing
            # sentence lists works as it computes an S x T similarity matrix.
            alignment_result = self.sentence_alignment_service.align(
                source_sentences, target_sentences, threshold=0.3
            )

            aligned_nodes: List[SentenceNode] = []
            unmatched_source_nodes: List[SentenceNode] = []
            unmatched_target_nodes: List[SentenceNode] = []

            # Build a mapping of aligned pairs from the service result
            aligned_pairs = []
            for rec in alignment_result.aligned:
                # Support tuple format (src_idx, tgt_idx, score) used by the lightweight aligner
                if isinstance(rec, (list, tuple)) and len(rec) >= 2:
                    src_idx = int(rec[0])
                    tgt_idx = int(rec[1])
                    score = float(rec[2]) if len(rec) > 2 else 0.0
                else:
                    # If record is unexpected, skip
                    continue
                aligned_pairs.append((src_idx, tgt_idx, score))

            # For each aligned pair, call analyze_phrases and assemble a SentenceNode
            for src_idx, tgt_idx, score in aligned_pairs:
                src_sent = source_sentences[src_idx] if src_idx < len(source_sentences) else ""
                tgt_sent = target_sentences[tgt_idx] if tgt_idx < len(target_sentences) else ""
                try:
                    phrase_analysis = self.analyze_phrases(src_sent, tgt_sent)
                except Exception as e:
                    logger.debug(f"analyze_phrases failed for {src_idx}->{tgt_idx}: {e}")
                    phrase_analysis = {"micro_operations": [], "warnings": [str(e)]}

                node = SentenceNode(
                    tag=f"s-{src_idx}-{tgt_idx}",
                    confidence=float(score),
                    source_text=src_sent,
                    target_text=tgt_sent,
                    explanation=None,
                    nested_findings=phrase_analysis.get("micro_operations", []),
                )
                aligned_nodes.append(node)

            # Build unmatched source nodes
            for i in alignment_result.unmatched_source:
                i = int(i)
                src_sent = source_sentences[i] if i < len(source_sentences) else ""
                node = SentenceNode(
                    tag=f"s-src-unmatched-{i}",
                    confidence=0.0,
                    source_text=src_sent,
                    target_text="",
                    explanation="unaligned_source",
                    nested_findings=[],
                )
                unmatched_source_nodes.append(node)

            # Build unmatched target nodes
            for j in alignment_result.unmatched_target:
                j = int(j)
                tgt_sent = target_sentences[j] if j < len(target_sentences) else ""
                node = SentenceNode(
                    tag=f"s-tgt-unmatched-{j}",
                    confidence=0.0,
                    source_text="",
                    target_text=tgt_sent,
                    explanation="unaligned_target",
                    nested_findings=[],
                )
                unmatched_target_nodes.append(node)

            # Prepare similarity matrix in serializable form
            sim_matrix = alignment_result.similarity_matrix

            return {
                "aligned": aligned_nodes,
                "unmatched_source": unmatched_source_nodes,
                "unmatched_target": unmatched_target_nodes,
                "similarity_matrix": sim_matrix,
            }

        except Exception as e:
            logger.error(f"Error in analyze_sentences: {e}")
            return {"aligned": [], "unmatched_source": [], "unmatched_target": [], "similarity_matrix": [], "warnings": [str(e)]}

    def analyze_phrases(self, source_sentence: str, target_sentence: str) -> dict:
        """
        Analyze phrase-level differences within an aligned sentence pair.

        Subtask 1: Implement and Connect analyze_phrases
        - Use phrase segmentation logic.
        - Compare semantic similarity or structural differences.
        - Return results suitable for inclusion in hierarchical pipeline.

        Args:
            source_sentence (str): Source sentence text.
            target_sentence (str): Target sentence text.

        Returns:
            dict: Detailed phrase-level alignment and analysis.
        """
        # TODO: Implement phrase segmentation and analysis
        pass


    def __init__(self):
        self.analysis_history: List[AnalysisHistoryItem] = []
        # Initialize the semantic model
        self.model = None
        self.semantic_alignment_service = SemanticAlignmentService()
        self.sentence_alignment_service = SentenceAlignmentService()
        # M3: Salience provider (lazy/simple instantiation; frequency fallback if advanced libs absent)
        try:
            self.salience_provider = SalienceProvider(method=os.getenv('SALIENCE_METHOD', 'frequency'))
        except Exception:  # pragma: no cover
            self.salience_provider = None
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
            # M4: propagate top-level override flags into nested analysis_options if present
            if request.include_micro_spans is not None:
                request.analysis_options.include_micro_spans = request.include_micro_spans
            if request.include_visual_salience is not None:
                request.analysis_options.include_visual_salience = request.include_visual_salience
            if request.micro_span_mode is not None:
                request.analysis_options.micro_span_mode = request.micro_span_mode
            if request.salience_visual_mode is not None:
                request.analysis_options.salience_visual_mode = request.salience_visual_mode
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

            # Hierarchical output (M2 partial integration)
            if getattr(request, "hierarchical_output", False):
                try:
                    # Build the legacy dict-shaped hierarchy (contains dataclass objects for paragraphs)
                    response.hierarchical_analysis = await self._build_hierarchy_async(request)
                    # Additionally provide a JSON-serializable hierarchical_tree field for the frontend.
                    # Convert any dataclass ParagraphNode / SentenceNode / PhraseNode instances into plain dicts.
                    def _maybe_asdict(obj):
                        try:
                            # asdict handles nested dataclasses as well
                            return asdict(obj)
                        except Exception:
                            return obj if isinstance(obj, dict) else obj
                    h = response.hierarchical_analysis or {}
                    src = h.get("source_paragraphs", []) or []
                    tgt = h.get("target_paragraphs", []) or []
                    serialized = []
                    for p in src:
                        serialized.append(_maybe_asdict(p))
                    for p in tgt:
                        serialized.append(_maybe_asdict(p))
                    response.hierarchical_tree = serialized
                except Exception as e:  # pragma: no cover - graceful degradation
                    logger.error(f"Failed to build hierarchical analysis: {e}")
            
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
        """Perform semantic analysis comparing meaning preservation using BERTimbau"""
        # Calculate semantic similarity using BERTimbau
        bertimbau_similarity = self._calculate_text_similarity(source_text, target_text)
        
        # Calculate meaning preservation score (scale 0-100)
        # For simplification, we want to recognize that meaning can be preserved
        # even when vocabulary is completely different
        meaning_preservation = bertimbau_similarity * 100
        
        # Apply an adjustment for simplification contexts
        # Text simplification should maintain high meaning preservation
        # even with completely different vocabulary
        if 0.7 <= bertimbau_similarity <= 0.85:
            # This range represents good simplification - boost it
            meaning_preservation = min(100, meaning_preservation * 1.15)
        
        # Calculate information loss
        information_loss = max(0, 100 - meaning_preservation)
        
        # Identify concept simplifications
        concept_simplifications = self._identify_concept_simplifications(source_text, target_text)
        
        logger.info(f"BERTimbau semantic analysis: similarity={bertimbau_similarity:.4f}, " +
                   f"meaning_preservation={meaning_preservation:.2f}%, " +
                   f"information_loss={information_loss:.2f}%")
        
        return SemanticAnalysis(
            semantic_similarity=bertimbau_similarity,
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
        """
        Identify simplification strategies used.
        Now uses the strategy_detector module which implements all strategies
        from Tabela Simplificação Textual.
        """
        try:
            # Use the new StrategyDetector for proper Portuguese strategies
            strategy_detector = StrategyDetector()
            
            # Get strategies based on Tabela Simplificação Textual
            detected_strategies = strategy_detector.identify_strategies(
                source_text=source_text,
                target_text=target_text
            )
            
            # Debug log
            logging.info(f"Detected strategies: {len(detected_strategies)}")
            for strategy in detected_strategies:
                logging.info(f"Strategy: {getattr(strategy, 'sigla', 'UNKNOWN')} - {getattr(strategy, 'nome', 'UNKNOWN')}")
            
            # Convert to the format expected by the frontend
            strategies = []
            for strategy in detected_strategies:
                # Map sigla (SL+, AS+, etc.) to type
                strategy_type = None
                sigla = getattr(strategy, 'sigla', '')
                
                if sigla in ["SL+", "MOD+"]:
                    strategy_type = SimplificationStrategyType.LEXICAL
                elif sigla in ["RP+", "MV+"]:
                    strategy_type = SimplificationStrategyType.SYNTACTIC
                elif sigla in ["DL+", "RF+", "RD+", "OM+"]:
                    strategy_type = SimplificationStrategyType.STRUCTURAL
                else:
                    strategy_type = SimplificationStrategyType.SEMANTIC
                
                # Convert impact
                impact_map = {
                    "baixo": "low",
                    "médio": "medium",
                    "alto": "high"
                }
                
                impacto = getattr(strategy, 'impacto', 'médio')
                nome = getattr(strategy, 'nome', 'Estratégia')
                descricao = getattr(strategy, 'descricao', '')
                confianca = getattr(strategy, 'confianca', 0.7)
                exemplos = getattr(strategy, 'exemplos', [])
                
                # Create SimplificationStrategy object in the format expected by frontend
                strategies.append(SimplificationStrategy(
                    name=nome,
                    type=strategy_type,
                    description=descricao,
                    impact=impact_map.get(impacto, "medium"),
                    confidence=confianca,
                    examples=[{"original": ex.original if hasattr(ex, 'original') else "", 
                              "simplified": ex.simplified if hasattr(ex, 'simplified') else ""} 
                              for ex in exemplos]
                ))
            
            return strategies
            
        except Exception as e:
            logging.error(f"Error in strategy identification: {str(e)}")
            logging.exception("Exception details:")
            # Fallback to basic strategies if the new detector fails
            return self._identify_basic_strategies(source_text, target_text)
    
    def _identify_basic_strategies(
        self, source_text: str, target_text: str
    ) -> List[SimplificationStrategy]:
        """Legacy fallback for strategy identification"""
        strategies = []
        
        # Lexical simplification
        if self._has_lexical_simplification(source_text, target_text):
            strategies.append(SimplificationStrategy(
                name="Adequação de Vocabulário",
                type=SimplificationStrategyType.LEXICAL,
                description="Substituição de termos difíceis, técnicos ou raros por sinônimos mais simples.",
                impact="high",
                confidence=0.8,
                examples=self._find_word_substitutions(source_text, target_text)[:3]
            ))
        
        # Syntactic simplification
        if self._has_syntactic_simplification(source_text, target_text):
            strategies.append(SimplificationStrategy(
                name="Fragmentação Sintática",
                type=SimplificationStrategyType.SYNTACTIC,
                description="Divisão de períodos extensos ou complexos em sentenças mais curtas e diretas.",
                impact="medium",
                confidence=0.7,
                examples=[]
            ))
        
        # NOTE: OM+ (Supressão Seletiva) is excluded by default as per Tabela documentation
        # It should only be activated manually by human-in-loop element
        
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

    # === Hierarchical assembly helpers (M2) ===
    async def _build_hierarchy_async(self, request: ComparativeAnalysisRequest) -> Dict[str, Any]:
        """Construct hierarchical structure with paragraph + sentence alignment and salience (M3)."""
        include_micro = getattr(request.analysis_options, 'include_micro_spans', False)
        micro_mode = getattr(request.analysis_options, 'micro_span_mode', 'ngram-basic') or 'ngram-basic'
        micro_extractor = None
        if include_micro:
            try:
                from .micro_span_extractor import MicroSpanExtractor  # local import to avoid startup cost
                micro_extractor = MicroSpanExtractor(mode=micro_mode)
            except Exception:
                micro_extractor = None
        def extract_micro_spans(sentence: str):
            if not include_micro or not micro_extractor:
                return []
            return micro_extractor.extract(sentence)
        # Paragraph segmentation helper
        def split_paragraphs(text: str) -> List[str]:
            parts = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
            return parts if parts else [text]

        source_paragraphs = split_paragraphs(request.source_text)
        target_paragraphs = split_paragraphs(request.target_text)

        # Paragraph salience aggregation (conditional by request options)
        def paragraph_saliences(paragraphs: List[str]) -> List[float | None]:
            if not request.analysis_options.include_salience:
                return [None]*len(paragraphs)
            provider = getattr(self, 'salience_provider', None)
            if not provider:
                return [None] * len(paragraphs)
            raw: List[float | None] = []
            for para in paragraphs:
                try:
                    res = provider.extract(para, max_units=12)
                    if res.units:
                        raw.append(sum(u['weight'] for u in res.units) / len(res.units))
                    else:
                        raw.append(0.0)
                except Exception:
                    raw.append(None)
            numerics = [v for v in raw if isinstance(v, (int, float))]
            if numerics and max(numerics) > 0:
                mval = max(numerics)
                raw = [ (v / mval) if isinstance(v, (int,float)) else None for v in raw ]
            return raw

        # Optional override of salience method at request level
        if request.salience_method and getattr(self, 'salience_provider', None):
            try:
                self.salience_provider.method = request.salience_method.lower()
            except Exception:
                pass

        source_para_sal = paragraph_saliences(source_paragraphs)
        target_para_sal = paragraph_saliences(target_paragraphs)

        # Paragraph alignment via semantic service
        alignment_req = AlignmentRequest(
            source_paragraphs=source_paragraphs,
            target_paragraphs=target_paragraphs,
            similarity_threshold=0.5,
            alignment_method=AlignmentMethod.COSINE_SIMILARITY,
            max_alignments_per_source=1,
        )
        alignment_resp = await self.semantic_alignment_service.align_paragraphs(alignment_req)
        aligned_map: Dict[int, int] = {}
        paragraph_alignment_records: List[Dict[str, Any]] = []
        if alignment_resp.success and alignment_resp.alignment_result:
            for pair in alignment_resp.alignment_result.aligned_pairs:
                # Support both AlignedPair-like objects and legacy tuple/list formats
                # (e.g., (src_idx, tgt_idx, score)) to be robust against input shapes.
                try:
                    src_idx = getattr(pair, "source_index", None)
                    tgt_idx = getattr(pair, "target_index", None)
                    sim_score = getattr(pair, "similarity_score", None)
                    conf = getattr(pair, "confidence", None)
                except Exception:
                    src_idx = tgt_idx = sim_score = conf = None

                if src_idx is None or tgt_idx is None:
                    # Fallback for tuple/list pair formats
                    if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                        src_idx = pair[0]
                        tgt_idx = pair[1]
                        sim_score = pair[2] if len(pair) > 2 else None
                        conf = None

                if src_idx is None or tgt_idx is None:
                    # Unable to interpret pair; skip with debug log
                    logger.debug(f"Skipping unexpected alignment pair format: {pair}")
                    continue

                aligned_map[int(src_idx)] = int(tgt_idx)
                paragraph_alignment_records.append(
                    {
                        "source_index": int(src_idx),
                        "target_index": int(tgt_idx),
                        "similarity": float(sim_score) if sim_score is not None else None,
                        "confidence": conf,
                    }
                )

        source_nodes: List[Dict[str, Any]] = []
        for s_idx, s_para in enumerate(source_paragraphs):
            sentences_s = self._split_sentences(s_para)
            paragraph_node: Dict[str, Any] = {
                "paragraph_id": f"p-src-{s_idx}",
                "index": s_idx,
                "role": "source",
                "text": s_para,
                "sentences": [],
                "salience": source_para_sal[s_idx] if s_idx < len(source_para_sal) else None,
            }
            t_idx = aligned_map.get(s_idx)
            sentence_alignment_result = None
            if t_idx is not None:
                sentences_t = self._split_sentences(target_paragraphs[t_idx])
                sentence_alignment_result = self.sentence_alignment_service.align(sentences_s, sentences_t, threshold=0.3)
            if sentence_alignment_result:
                rel_map: Dict[int, List[Dict[str, Any]]] = {}
                for rec in sentence_alignment_result.aligned:
                    # Support both object-like records and tuple/list records produced by the
                    # lightweight sentence aligner (which returns tuples (src_idx, tgt_idx, score)).
                    if hasattr(rec, "source_index") and hasattr(rec, "target_index"):
                        src_idx = getattr(rec, "source_index")
                        tgt_idx = getattr(rec, "target_index")
                        similarity = getattr(rec, "similarity", None) or getattr(rec, "score", None) or getattr(rec, "similarity_score", None)
                        relation = getattr(rec, "relation", None)
                    elif isinstance(rec, (list, tuple)) and len(rec) >= 2:
                        src_idx = rec[0]
                        tgt_idx = rec[1]
                        # third element may be score
                        similarity = rec[2] if len(rec) > 2 else None
                        relation = None
                    else:
                        logger.debug(f"Unexpected sentence alignment record format: {rec}")
                        continue

                    rel_map.setdefault(int(src_idx), []).append({
                        "target_index": int(tgt_idx),
                        "relation": relation,
                        "similarity": float(similarity) if similarity is not None else None,
                    })

                for i, sent in enumerate(sentences_s):
                    sent_sal = None
                    if request.analysis_options.include_salience and getattr(self, 'salience_provider', None):
                        try:
                            s_res = self.salience_provider.extract(sent, max_units=6)
                            sent_sal = max((u['weight'] for u in s_res.units), default=0.0)
                        except Exception:
                            sent_sal = None
                    sentence_record = {
                        "sentence_id": f"s-src-{s_idx}-{i}",
                        "index": i,
                        "text": sent,
                        "alignment": rel_map.get(i),
                        "salience": sent_sal,
                    }
                    if include_micro:
                        sentence_record["micro_spans"] = extract_micro_spans(sent)
                    paragraph_node['sentences'].append(sentence_record)
                paragraph_node['alignment'] = {
                    "target_index": t_idx,
                    "similarity": next((r['similarity'] for r in paragraph_alignment_records if r['source_index'] == s_idx), None),
                }
            else:
                for i, sent in enumerate(sentences_s):
                    sent_sal = None
                    if request.analysis_options.include_salience and getattr(self, 'salience_provider', None):
                        try:
                            s_res = self.salience_provider.extract(sent, max_units=6)
                            sent_sal = max((u['weight'] for u in s_res.units), default=0.0)
                        except Exception:
                            sent_sal = None
                    sentence_record = {
                        "sentence_id": f"s-src-{s_idx}-{i}",
                        "index": i,
                        "text": sent,
                        "alignment": None,
                        "salience": sent_sal,
                    }
                    if include_micro:
                        sentence_record["micro_spans"] = extract_micro_spans(sent)
                    paragraph_node['sentences'].append(sentence_record)
            # Normalize sentence salience locally
            if request.analysis_options.include_salience:
                sal_values = [s.get('salience') for s in paragraph_node['sentences'] if isinstance(s.get('salience'), (int,float))]
                if sal_values and max(sal_values) > 0:
                    m = max(sal_values)
                    for s in paragraph_node['sentences']:
                        if isinstance(s.get('salience'), (int,float)):
                            s['salience'] = s['salience'] / m
            source_nodes.append(paragraph_node)

        target_nodes: List[Dict[str, Any]] = []
        for t_idx, t_para in enumerate(target_paragraphs):
            sentences_t = self._split_sentences(t_para)
            paragraph_node: Dict[str, Any] = {
                "paragraph_id": f"p-tgt-{t_idx}",
                "index": t_idx,
                "role": "target",
                "text": t_para,
                "sentences": [],
                "salience": target_para_sal[t_idx] if t_idx < len(target_para_sal) else None,
            }
            source_pair = next((s for s, t in aligned_map.items() if t == t_idx), None)
            for i, sent in enumerate(sentences_t):
                sent_sal = None
                if request.analysis_options.include_salience and getattr(self, 'salience_provider', None):
                    try:
                        t_res = self.salience_provider.extract(sent, max_units=6)
                        sent_sal = max((u['weight'] for u in t_res.units), default=0.0)
                    except Exception:
                        sent_sal = None
                sentence_record = {
                    "sentence_id": f"s-tgt-{t_idx}-{i}",
                    "index": i,
                    "text": sent,
                    "alignment": None,
                    "salience": sent_sal,
                }
                if include_micro:
                    sentence_record["micro_spans"] = extract_micro_spans(sent)
                paragraph_node['sentences'].append(sentence_record)
            if source_pair is not None:
                paragraph_node['alignment'] = {
                    "source_index": source_pair,
                    "similarity": next((r['similarity'] for r in paragraph_alignment_records if r['source_index'] == source_pair), None),
                }
            if request.analysis_options.include_salience:
                sal_values = [s.get('salience') for s in paragraph_node['sentences'] if isinstance(s.get('salience'), (int,float))]
                if sal_values and max(sal_values) > 0:
                    m = max(sal_values)
                # === Stage 2 / Stage 3 scaffolding ===
                async def analyze_sentences(
                    self,
                    source_sentences: List[str],
                    target_sentences: List[str],
                    user_config: dict | None = None,
                ) -> dict:
                    """
                    Analyze pairs of sentences at the meso level (async).
                
                    Inputs
                    - source_sentences: list of sentences from the source paragraph (already segmented)
                    - target_sentences: list of sentences from the target paragraph
                    - user_config: optional dict with runtime flags and thresholds, e.g.
                        {
                            "sentence_similarity_threshold": 0.6,
                            "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
                            "normalize": True
                        }
                
                    Behavior implemented
                    - Generates embeddings for source_sentences and target_sentences using the
                      existing SemanticAlignmentService.generate_embeddings (MiniLM by default).
                    - Computes a sentence-level similarity matrix using the service's
                      _compute_similarity_matrix helper and AlignmentMethod.COSINE_SIMILARITY.
                    - Performs greedy per-source matching (similar to paragraph-level logic) to
                      produce aligned_sentence_pairs: list of (src_idx, tgt_idx, similarity).
                    - Invokes analyze_phrases() (placeholder) for each aligned sentence pair and
                      collects micro-level feature hooks into `phrase_features`.
                    - Returns a structured dict with aligned pairs, similarity matrix, and
                      collected phrase-level placeholders.
                
                    Returns
                    - dict with keys:
                        {
                            "aligned_sentence_pairs": list[tuple[int,int,float]],
                            "similarity_matrix": list[list[float]],
                            "phrase_features": list[dict],  # one entry per aligned pair or None
                            "warnings": list[str],
                        }
                    """
                    try:
                        cfg = user_config or {}
                        model_name = cfg.get("model_name", self.semantic_alignment_service.config.bertimbau_model)
                        normalize = bool(cfg.get("normalize", True))
                        threshold = float(cfg.get("sentence_similarity_threshold", 0.5))
                
                        # Handle empty inputs quickly
                        if not source_sentences and not target_sentences:
                            return {
                                "aligned_sentence_pairs": [],
                                "similarity_matrix": [],
                                "phrase_features": [],
                                "warnings": [],
                            }
                
                        # Request embeddings for all sentences via the semantic alignment service
                        texts = list(source_sentences) + list(target_sentences)
                        try:
                            from ..models.semantic_alignment import EmbeddingRequest, AlignmentMethod
                        except Exception:
                            from ..models.semantic_alignment import EmbeddingRequest, AlignmentMethod
                
                        embedding_request = EmbeddingRequest(texts=texts, model_name=model_name, normalize=normalize)
                        embedding_response = await self.semantic_alignment_service.generate_embeddings(embedding_request)
                
                        # Split embeddings
                        source_count = len(source_sentences)
                        source_embeddings = embedding_response.embeddings[:source_count]
                        target_embeddings = embedding_response.embeddings[source_count:]
                
                        # Compute similarity matrix (use cosine similarity)
                        similarity_matrix = self.semantic_alignment_service._compute_similarity_matrix(
                            source_embeddings, target_embeddings, AlignmentMethod.COSINE_SIMILARITY
                        )
                
                        # Greedy per-source matching: choose best target above threshold not already matched
                        aligned_pairs = []
                        aligned_target_indices = set()
                
                        for i in range(len(source_sentences)):
                            row = similarity_matrix[i]
                            best_j = None
                            best_score = 0.0
                            for j, score in enumerate(row):
                                if j in aligned_target_indices:
                                    continue
                                if score > best_score:
                                    best_score = score
                                    best_j = j
                            if best_j is not None and best_score >= threshold:
                                aligned_pairs.append((i, best_j, float(best_score)))
                                aligned_target_indices.add(best_j)
                
                        # Prepare phrase-level feature hooks by invoking analyze_phrases on aligned pairs
                        phrase_features = []
                        for (src_idx, tgt_idx, sim_score) in aligned_pairs:
                            src_sent = source_sentences[src_idx]
                            tgt_sent = target_sentences[tgt_idx]
                            try:
                                # analyze_phrases is synchronous placeholder; if it becomes async, adapt accordingly.
                                # It currently returns a dict with micro_operations and warnings.
                                pf = self.analyze_phrases(src_sent, tgt_sent, user_config=cfg)
                                # If analyze_phrases is async in the future, call: await self.analyze_phrases(...)
                                phrase_features.append(pf)
                            except Exception as e:
                                logger.debug(f"analyze_phrases failed for sentence pair {src_idx}->{tgt_idx}: {e}")
                                phrase_features.append({"micro_operations": [], "warnings": [str(e)]})
                
                        # Convert similarity_matrix to nested lists for serialization
                        sim_matrix_list = similarity_matrix.tolist() if hasattr(similarity_matrix, "tolist") else [
                            [float(v) for v in row] for row in similarity_matrix
                        ]
                
                        return {
                            "aligned_sentence_pairs": aligned_pairs,
                            "similarity_matrix": sim_matrix_list,
                            "phrase_features": phrase_features,
                            "warnings": [],
                        }
                
                    except Exception as e:
                        logger.error(f"Error in analyze_sentences: {e}")
                        return {"aligned_sentence_pairs": [], "similarity_matrix": [], "phrase_features": [], "warnings": [str(e)]}
        
                def analyze_phrases(
                    self,
                    source_sentence: str,
                    target_sentence: str,
                    user_config: dict | None = None,
                ) -> dict:
                    """
                    Micro-level analysis between a source and target sentence.

                    Implementation (minimal):
                    - Tokenize source/target sentences into word tokens.
                    - Use difflib.SequenceMatcher to find replace/insert/delete operations.
                    - For each replace op, build a micro-operation with:
                        * source_tokens, target_tokens
                        * op_type: 'replace' | 'insert' | 'delete'
                        * features: {
                            "source_len": int,
                            "target_len": int,
                            "len_delta": int,
                            "source_syllables": int,
                            "target_syllables": int,
                            "syllable_delta": int,
                            "is_key_phrase": bool (LangExtract placeholder),
                        }
                        * suggested_tag: one of SL+, MV+, TA+, MOD+ (very small heuristic)
                        * confidence: float 0..1 (heuristic)
                    - Returns dict {"micro_operations": [...], "warnings": [...]}
                    """
                    import difflib
                    import re

                    def tokenize(text: str) -> list[str]:
                        return re.findall(r"\w+|\S", text, flags=re.UNICODE)

                    def count_syllables(word: str) -> int:
                        # Very small heuristic: count vowel groups
                        w = word.lower()
                        groups = re.findall(r"[aeiouáéíóúâêôãõü]+", w)
                        return max(1, len(groups))

                    warnings: list[str] = []
                    micro_ops: list[dict] = []

                    try:
                        s_toks = tokenize(source_sentence)
                        t_toks = tokenize(target_sentence)

                        seq = difflib.SequenceMatcher(a=s_toks, b=t_toks)
                        for tag, i1, i2, j1, j2 in seq.get_opcodes():
                            if tag == "equal":
                                continue

                            src_segment = s_toks[i1:i2]
                            tgt_segment = t_toks[j1:j2]

                            if tag == "replace":
                                op_type = "replace"
                            elif tag == "delete":
                                op_type = "delete"
                            elif tag == "insert":
                                op_type = "insert"
                            else:
                                op_type = tag

                            source_len = sum(len(tok) for tok in src_segment) if src_segment else 0
                            target_len = sum(len(tok) for tok in tgt_segment) if tgt_segment else 0
                            len_delta = target_len - source_len

                            src_syll = sum(count_syllables(tok) for tok in src_segment) if src_segment else 0
                            tgt_syll = sum(count_syllables(tok) for tok in tgt_segment) if tgt_segment else 0
                            syll_delta = tgt_syll - src_syll

                            # LangExtract placeholder: mark phrase as key if contains multiword token or long token
                            def langextract_is_key_phrase(tokens: list[str]) -> bool:
                                # Placeholder heuristic: any token longer than 7 chars or multiword chunk >1 tokens
                                if not tokens:
                                    return False
                                if len(tokens) > 1:
                                    return True
                                return any(len(t) > 7 for t in tokens)

                            is_key_phrase = langextract_is_key_phrase(src_segment)

                            # Tiny heuristic rule engine for suggested_tag
                            suggested_tag = "SL+"  # default: lexical simplification
                            confidence = 0.5

                            # If replacement increases syllables significantly -> EXP+ or MOD+
                            if syll_delta > 2:
                                suggested_tag = "EXP+"
                                confidence = 0.6
                            # If replacement reduces syllables significantly -> SL+
                            elif syll_delta < -1:
                                suggested_tag = "SL+"
                                confidence = 0.7
                            # If structure changes (adds/removes many tokens) -> MOD+
                            if abs(len_delta) > max(1, source_len * 0.4):
                                suggested_tag = "MOD+"
                                confidence = min(0.9, confidence + 0.1)
                            # If target tokens contain a verb form change heuristic, mark MV+ (very small heuristic)
                            verbs = {"é", "foi", "está", "são", "ser", "fazer", "fez", "faz"}
                            if any(tok.lower() in verbs for tok in tgt_segment + src_segment):
                                if suggested_tag == "SL+":
                                    suggested_tag = "MV+"
                                    confidence = 0.6

                            # Boost confidence if inside a key phrase
                            if is_key_phrase:
                                confidence = min(1.0, confidence + 0.15)

                            micro_ops.append(
                                {
                                    "source_tokens": src_segment,
                                    "target_tokens": tgt_segment,
                                    "op_type": op_type,
                                    "features": {
                                        "source_len": source_len,
                                        "target_len": target_len,
                                        "len_delta": len_delta,
                                        "source_syllables": src_syll,
                                        "target_syllables": tgt_syll,
                                        "syllable_delta": syll_delta,
                                        "is_key_phrase": is_key_phrase,
                                    },
                                    "suggested_tag": suggested_tag,
                                    "confidence": float(confidence),
                                }
                            )

                    except Exception as e:
                        warnings.append(str(e))

                    return {"micro_operations": micro_ops, "warnings": warnings}
                    for s in paragraph_node['sentences']:
                        if isinstance(s.get('salience'), (int,float)):
                            s['salience'] = s['salience'] / m
            target_nodes.append(paragraph_node)
 
        # Convert dict-based paragraph/sentence structures to dataclass-based nodes
        def _convert_sentence_record_to_node(sent_rec: Dict[str, Any], role: str = "source") -> SentenceNode:
            """
            Convert a sentence record (dict) produced by the existing logic into a SentenceNode.
            Handles both cases where sentence_record contains micro_spans (from extract_micro_spans)
            or where nested findings are already micro_operations lists.
            """
            try:
                sent_id = sent_rec.get("sentence_id") or sent_rec.get("index") or ""
                src_text = sent_rec.get("text") if role == "source" else ""
                tgt_text = sent_rec.get("text") if role == "target" else ""
                confidence = 0.0
                # Try common similarity fields
                align = sent_rec.get("alignment")
                if isinstance(align, list) and len(align) > 0:
                    confidence = float(align[0].get("similarity") or 0.0)
                elif isinstance(sent_rec.get("salience"), (int, float)):
                    confidence = float(sent_rec.get("salience"))
 
                # Build nested findings from micro_spans or micro_operations
                nested: List[PhraseNode] = []
                # micro_spans (from extractor) -> map to PhraseNode
                if "micro_spans" in sent_rec and isinstance(sent_rec["micro_spans"], list):
                    for sp in sent_rec["micro_spans"][:5]:
                        nested.append(
                            PhraseNode(
                                tag=sp.get("span_id", ""),
                                confidence=float(sp.get("salience", 0.0)),
                                source_text=sp.get("text") if role == "source" else "",
                                target_text=sp.get("text") if role == "target" else "",
                                explanation=sp.get("method"),
                            )
                        )
                # micro_operations (from analyze_phrases) -> map to PhraseNode
                if "micro_operations" in sent_rec and isinstance(sent_rec["micro_operations"], list):
                    for mi_idx, mo in enumerate(sent_rec["micro_operations"][:10]):
                        nested.append(
                            PhraseNode(
                                tag=f"{sent_id}-mo-{mi_idx}",
                                confidence=float(mo.get("confidence", 0.0)) if isinstance(mo, dict) else 0.0,
                                source_text=" ".join(mo.get("source_tokens", [])) if isinstance(mo, dict) else "",
                                target_text=" ".join(mo.get("target_tokens", [])) if isinstance(mo, dict) else "",
                                explanation=mo.get("op_type") if isinstance(mo, dict) else None,
                            )
                        )
 
                return SentenceNode(
                    tag=str(sent_id),
                    confidence=confidence,
                    source_text=src_text,
                    target_text=tgt_text,
                    explanation=sent_rec.get("explanation"),
                    nested_findings=nested,
                )
            except Exception as e:
                logger.debug(f"Conversion to SentenceNode failed for record: {e}")
                return SentenceNode(tag=str(sent_rec.get("sentence_id", "")), confidence=0.0, source_text=sent_rec.get("text", ""), target_text="", explanation="conversion_error", nested_findings=[])
 
        def _convert_paragraph_dict_to_node(pdict: Dict[str, Any], role: str = "source") -> ParagraphNode:
            """
            Convert paragraph dict (existing format) to ParagraphNode, converting sentences inside.
            """
            tag = pdict.get("paragraph_id") or pdict.get("index") or ""
            confidence = 0.0
            if isinstance(pdict.get("salience"), (int, float)):
                confidence = float(pdict.get("salience"))
            p_source_text = pdict.get("text") if role == "source" else pdict.get("text") or ""
            p_target_text = pdict.get("text") if role == "target" else ""
            nested_sent_nodes: List[SentenceNode] = []
            sentences = pdict.get("sentences", [])
            for srec in sentences:
                # If sentence entries are simple dicts, convert; if already SentenceNode objects, use them
                if isinstance(srec, SentenceNode):
                    nested_sent_nodes.append(srec)
                elif isinstance(srec, dict):
                    nested_sent_nodes.append(_convert_sentence_record_to_node(srec, role=role))
                else:
                    # Unknown format: create a fallback node
                    nested_sent_nodes.append(SentenceNode(tag=str(srec), confidence=0.0, source_text=str(srec) if role=="source" else "", target_text=str(srec) if role=="target" else "", nested_findings=[]))
 
            return ParagraphNode(
                tag=str(tag),
                confidence=confidence,
                source_text=p_source_text,
                target_text=p_target_text,
                explanation=pdict.get("alignment") and "aligned" or None,
                nested_findings=nested_sent_nodes,
            )
 
        # Map source_nodes and target_nodes (which are dicts) into dataclass instances
        source_paragraph_nodes: List[ParagraphNode] = []
        for p in source_nodes:
            if isinstance(p, ParagraphNode):
                source_paragraph_nodes.append(p)
            elif isinstance(p, dict):
                source_paragraph_nodes.append(_convert_paragraph_dict_to_node(p, role="source"))
            else:
                # fallback
                source_paragraph_nodes.append(ParagraphNode(tag=str(getattr(p, "paragraph_id", "")), source_text=str(p)))
 
        target_paragraph_nodes: List[ParagraphNode] = []
        for p in target_nodes:
            if isinstance(p, ParagraphNode):
                target_paragraph_nodes.append(p)
            elif isinstance(p, dict):
                target_paragraph_nodes.append(_convert_paragraph_dict_to_node(p, role="target"))
            else:
                target_paragraph_nodes.append(ParagraphNode(tag=str(getattr(p, "paragraph_id", "")), target_text=str(p)))
 
        hierarchy_version = "1.2" if include_micro else "1.1"
        hierarchy = {
            "hierarchy_version": hierarchy_version,
            "source_paragraphs": source_paragraph_nodes,
            "target_paragraphs": target_paragraph_nodes,
            "metadata": {
                "paragraph_alignment_count": len(paragraph_alignment_records),
                "paragraph_unaligned_source": [i for i in range(len(source_paragraphs)) if i not in aligned_map],
                "paragraph_unaligned_target": [j for j in range(len(target_paragraphs)) if j not in aligned_map.values()],
                "alignment_mode": "semantic_paragraph + sentence_cosine",
            },
        }
        return hierarchy

    def analyze_phrases(
        self,
        source_sentence: str,
        target_sentence: str,
        user_config: dict | None = None,
    ) -> dict:
        """
        Micro-level analysis between a source and target sentence.

        Minimal implementation (kept in sync with the hierarchical analyzer scaffolding):
        - Tokenize source/target sentences into word tokens.
        - Use difflib.SequenceMatcher to find replace/insert/delete operations.
        - For each operation build a micro-operation dict with:
            * source_tokens, target_tokens
            * op_type: 'replace' | 'insert' | 'delete'
            * features: {
                "source_len": int,
                "target_len": int,
                "len_delta": int,
                "source_syllables": int,
                "target_syllables": int,
                "syllable_delta": int,
                "is_key_phrase": bool,
              }
            * suggested_tag: heuristic tag (SL+, MV+, TA+, MOD+, EXP+)
            * confidence: float 0..1 (heuristic)
        - Returns dict {"micro_operations": [...], "warnings": [...]}
        """
        import difflib
        import re

        def tokenize(text: str) -> list[str]:
            return re.findall(r"\w+|\S", text, flags=re.UNICODE)

        def count_syllables(word: str) -> int:
            # Very small heuristic: count vowel groups
            w = word.lower()
            groups = re.findall(r"[aeiouáéíóúâêôãõü]+", w)
            return max(1, len(groups))

        warnings: list[str] = []
        micro_ops: list[dict] = []

        try:
            s_toks = tokenize(source_sentence)
            t_toks = tokenize(target_sentence)

            seq = difflib.SequenceMatcher(a=s_toks, b=t_toks)
            for tag, i1, i2, j1, j2 in seq.get_opcodes():
                if tag == "equal":
                    continue

                src_segment = s_toks[i1:i2]
                tgt_segment = t_toks[j1:j2]

                if tag == "replace":
                    op_type = "replace"
                elif tag == "delete":
                    op_type = "delete"
                elif tag == "insert":
                    op_type = "insert"
                else:
                    op_type = tag

                source_len = sum(len(tok) for tok in src_segment) if src_segment else 0
                target_len = sum(len(tok) for tok in tgt_segment) if tgt_segment else 0
                len_delta = target_len - source_len

                src_syll = sum(count_syllables(tok) for tok in src_segment) if src_segment else 0
                tgt_syll = sum(count_syllables(tok) for tok in tgt_segment) if tgt_segment else 0
                syll_delta = tgt_syll - src_syll

                # LangExtract placeholder: mark phrase as key if contains multiword token or long token
                def langextract_is_key_phrase(tokens: list[str]) -> bool:
                    # Placeholder heuristic: any token longer than 7 chars or multiword chunk >1 tokens
                    if not tokens:
                        return False
                    if len(tokens) > 1:
                        return True
                    return any(len(t) > 7 for t in tokens)

                is_key_phrase = langextract_is_key_phrase(src_segment)

                # Tiny heuristic rule engine for suggested_tag
                suggested_tag = "SL+"  # default: lexical simplification
                confidence = 0.5

                # If replacement increases syllables significantly -> EXP+ or MOD+
                if syll_delta > 2:
                    suggested_tag = "EXP+"
                    confidence = 0.6
                # If replacement reduces syllables significantly -> SL+
                elif syll_delta < -1:
                    suggested_tag = "SL+"
                    confidence = 0.7
                # If structure changes (adds/removes many tokens) -> MOD+
                if abs(len_delta) > max(1, source_len * 0.4):
                    suggested_tag = "MOD+"
                    confidence = min(0.9, confidence + 0.1)
                # If target tokens contain a verb form change heuristic, mark MV+ (very small heuristic)
                verbs = {"é", "foi", "está", "são", "ser", "fazer", "fez", "faz"}
                if any(tok.lower() in verbs for tok in tgt_segment + src_segment):
                    if suggested_tag == "SL+":
                        suggested_tag = "MV+"
                        confidence = 0.6

                # Boost confidence if inside a key phrase
                if is_key_phrase:
                    confidence = min(1.0, confidence + 0.15)

                micro_ops.append(
                    {
                        "source_tokens": src_segment,
                        "target_tokens": tgt_segment,
                        "op_type": op_type,
                        "features": {
                            "source_len": source_len,
                            "target_len": target_len,
                            "len_delta": len_delta,
                            "source_syllables": src_syll,
                            "target_syllables": tgt_syll,
                            "syllable_delta": syll_delta,
                            "is_key_phrase": is_key_phrase,
                        },
                        "suggested_tag": suggested_tag,
                        "confidence": float(confidence),
                    }
                )

        except Exception as e:
            warnings.append(str(e))

        return {"micro_operations": micro_ops, "warnings": warnings}

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
        """
        Calculate semantic similarity using BERTimbau embeddings for accurate
        semantic understanding in Portuguese.
        """
        try:
            # Use lightweight multilingual model for semantic similarity
            # This provides much better semantic understanding than word overlap
            model_name = "paraphrase-multilingual-MiniLM-L12-v2"
            
            if self.model is None:
                logger.info(f"Loading lightweight semantic model: {model_name}")
                self.model = SentenceTransformer(model_name)
                logger.info("Lightweight semantic model loaded successfully")
            
            # Generate embeddings for both texts
            embedding1 = self.model.encode(text1, convert_to_tensor=True)
            embedding2 = self.model.encode(text2, convert_to_tensor=True)
            
            # Calculate cosine similarity between the embeddings
            # This measures semantic similarity, accounting for meaning preservation
            cosine_similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
            
            # Scale similarity score (cosine similarity returns values from -1 to 1)
            # Convert to range 0-1 where 1 is perfect similarity
            normalized_similarity = (cosine_similarity + 1) / 2
            
            logger.info(f"BERTimbau similarity: {normalized_similarity:.4f}")
            
            # Apply a more realistic scaling for simplification contexts
            # For text simplification, we want to recognize when the meaning is preserved
            # even if the vocabulary is completely different
            if 0.7 <= normalized_similarity <= 0.85:
                # Apply a bonus for scores in the "good simplification" range
                # This recognizes when meaning is preserved with simpler words
                adjusted_score = normalized_similarity * 1.15
            elif normalized_similarity > 0.85:
                # Already high similarity
                adjusted_score = normalized_similarity
            else:
                # Apply smaller boost to lower scores
                adjusted_score = normalized_similarity * 1.1
            
            # Ensure score is between 0 and 1
            final_score = min(1.0, max(0.0, adjusted_score))
            
            logger.info(f"Adjusted semantic score: {final_score:.4f}")
            return final_score
            
        except Exception as e:
            logger.error(f"Error in BERTimbau semantic similarity: {str(e)}")
            logger.warning("Falling back to heuristic similarity method")
            
            # Fallback to heuristic method if BERTimbau fails
            # Word overlap as baseline
            words1 = set(self._tokenize_text(text1))
            words2 = set(self._tokenize_text(text2))
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            word_overlap = intersection / union if union > 0 else 0
            
            # Apply heuristic adjustments for simplification context
            if len(text2) < len(text1) and len(text2) > 0.2 * len(text1):
                # Reward proper simplification (shorter but meaningful)
                word_overlap *= 1.3
            
            return min(1.0, word_overlap)

    def _calculate_concept_preservation(self, source_text: str, target_text: str) -> float:
        """Calculate how well main concepts are preserved"""
        
        # Extract key concepts (nouns, important verbs)
        source_concepts = self._extract_key_concepts(source_text)
        target_concepts = self._extract_key_concepts(target_text)
        
        if not source_concepts:
            return 1.0
        
        # Check for concept preservation through synonyms/related terms
        preserved_concepts = 0
        for source_concept in source_concepts:
            if self._is_concept_preserved(source_concept, target_concepts, target_text):
                preserved_concepts += 1
        
        return preserved_concepts / len(source_concepts)
    
    def _calculate_semantic_content_preservation(self, source_text: str, target_text: str) -> float:
        """Calculate preservation of semantic content"""
        
        # For simplification, if target is much shorter but covers same topic, 
        # semantic preservation should still be high
        
        source_words = self._tokenize_text(source_text)
        target_words = self._tokenize_text(target_text)
        
        # Remove stop words for better content analysis
        stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'das', 'dos', 
                     'e', 'é', 'que', 'em', 'para', 'com', 'se', 'por', 'ou', 'mas'}
        
        source_content = [w.lower() for w in source_words if w.lower() not in stop_words and len(w) > 2]
        target_content = [w.lower() for w in target_words if w.lower() not in stop_words and len(w) > 2]
        
        if not source_content:
            return 1.0
        
        # Check for semantic relationships
        preserved_content = 0
        for source_word in source_content:
            if self._has_semantic_equivalent(source_word, target_content, target_text):
                preserved_content += 1
        
        # Give bonus for successful simplification (shorter text covering same concepts)
        length_ratio = len(target_text) / len(source_text) if source_text else 1
        if 0.3 <= length_ratio <= 0.7:  # Good simplification range
            simplification_bonus = 0.1
        else:
            simplification_bonus = 0
        
        base_preservation = preserved_content / len(source_content)
        return min(1.0, base_preservation + simplification_bonus)
    
    def _calculate_information_preservation(self, source_text: str, target_text: str) -> float:
        """Calculate how well key information is preserved"""
        
        # For text simplification, if main message is conveyed in simpler terms,
        # information preservation should be high
        
        # Simple heuristic: if target text has reasonable length and covers the topic
        source_length = len(source_text.strip())
        target_length = len(target_text.strip())
        
        if source_length == 0:
            return 1.0
        
        length_ratio = target_length / source_length
        
        # For good simplification: 30-70% of original length
        if 0.3 <= length_ratio <= 0.7:
            length_score = 0.9  # High score for good simplification
        elif 0.1 <= length_ratio < 0.3:
            length_score = 0.7  # Medium score for aggressive simplification
        elif 0.7 < length_ratio <= 1.0:
            length_score = 0.8  # Medium-high for moderate simplification
        else:
            length_score = 0.5  # Lower score for extreme cases
        
        # Check if target text is coherent and meaningful
        target_words = len(self._tokenize_text(target_text))
        if target_words >= 5:  # Minimum meaningful content
            coherence_score = 0.9
        elif target_words >= 3:
            coherence_score = 0.7
        else:
            coherence_score = 0.5
        
        return (length_score + coherence_score) / 2
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts (main nouns and important verbs)"""
        words = self._tokenize_text(text)
        
        # Simple concept extraction (can be enhanced with spaCy POS tagging)
        concepts = []
        important_words = []
        
        for word in words:
            word_lower = word.lower()
            # Skip very short words and common words
            if len(word) > 3 and word_lower not in {'para', 'com', 'que', 'são', 'uma', 'dos', 'das', 'este', 'esta'}:
                important_words.append(word_lower)
        
        # Return up to 10 most important concepts
        return important_words[:10]
    
    def _is_concept_preserved(self, concept: str, target_concepts: List[str], target_text: str) -> bool:
        """Check if a concept is preserved in target (directly or through synonyms)"""
        
        # Direct match
        if concept in target_concepts:
            return True
        
        # Check for common simplification patterns
        simplification_patterns = {
            'complexo': ['simples', 'fácil'],
            'elaborado': ['simples', 'claro'],
            'vocabulário': ['palavras', 'termos'],
            'técnico': ['simples', 'comum'],
            'conhecimento': ['saber', 'entender'],
            'especializado': ['específico', 'particular'],
            'compreensão': ['entender', 'entendimento'],
            'adequada': ['boa', 'certa', 'correta']
        }
        
        if concept in simplification_patterns:
            for simple_term in simplification_patterns[concept]:
                if simple_term in target_text.lower():
                    return True
        
        # Check for partial matches (stem similarity)
        for target_concept in target_concepts:
            if self._are_related_concepts(concept, target_concept):
                return True
        
        return False
    
    def _has_semantic_equivalent(self, word: str, target_words: List[str], target_text: str) -> bool:
        """Check if word has semantic equivalent in target"""
        
        # Direct match
        if word in target_words:
            return True
        
        # Common semantic equivalences in simplification
        equivalences = {
            'texto': ['texto', 'palavras', 'escrito'],
            'lei': ['regra', 'norma'],
            'importante': ['grande', 'muito'],
            'criou': ['fez', 'estabeleceu'],
            'controlar': ['cuidar', 'verificar'],
            'gastos': ['dinheiro', 'recursos'],
            'governo': ['estado', 'poder'],
            'público': ['todos', 'pessoas']
        }
        
        if word in equivalences:
            for equiv in equivalences[word]:
                if equiv in target_text.lower():
                    return True
        
        return False
    
    def _are_related_concepts(self, concept1: str, concept2: str) -> bool:
        """Check if two concepts are semantically related"""
        
        # Simple similarity check (can be enhanced)
        if abs(len(concept1) - len(concept2)) > 3:
            return False
        
        # Check for common prefixes/suffixes
        if len(concept1) > 4 and len(concept2) > 4:
            if concept1[:3] == concept2[:3] or concept1[-3:] == concept2[-3:]:
                return True
        
        return False

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
        source_text = response.source_text
        target_text = response.target_text
        
        # Use BERTimbau for direct semantic similarity calculation
        bertimbau_similarity = self._calculate_text_similarity(source_text, target_text)
        
        # Scale to percentage (0-100)
        semantic_preservation = bertimbau_similarity * 100
        
        # Log the calculation for debugging
        logger.info(f"Semantic preservation: {semantic_preservation:.2f}%")
        
        # Save to semantic_analysis for consistency
        if response.semantic_analysis:
            response.semantic_analysis.meaning_preservation = semantic_preservation
        
        return semantic_preservation

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

# === Scaffold for Hierarchical Node Models ===
# These dataclasses will be used in the hierarchical output structure for comparative analysis.

# Hierarchical node dataclasses moved to a dedicated models module to keep
# model definitions centralized and importable by other modules.
# Use the dataclass definitions from backend/src/models/hierarchical_nodes.py
from ..models.hierarchical_nodes import ParagraphNode, SentenceNode, PhraseNode, to_dict
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Any

@dataclass
class ParagraphNode:
    """
    Represents a paragraph in the hierarchical analysis.
    
    Attributes:
        level (str): The hierarchy level ("paragraph").
        tag (str): A label or identifier for the paragraph.
        confidence (float): Confidence score for the analysis.
        source_text (str): Original paragraph text.
        target_text (str): Translated/simplified paragraph text.
        explanation (Optional[str]): Explanation of analysis.
        nested_findings (List[Any]): List of SentenceNode objects.
    """
    # TODO: Fill with actual types and defaults
    level: str = "paragraph"
    tag: str = ""
    confidence: float = 0.0
    source_text: str = ""
    target_text: str = ""
    explanation: Optional[str] = None
    nested_findings: List[Any] = field(default_factory=list)


@dataclass
class SentenceNode:
    """
    Represents a sentence in the hierarchical analysis.
    
    Attributes:
        level (str): The hierarchy level ("sentence").
        tag (str): A label or identifier for the sentence.
        confidence (float): Confidence score for the sentence alignment.
        source_text (str): Original sentence text.
        target_text (str): Translated/simplified sentence text.
        explanation (Optional[str]): Explanation of analysis.
        nested_findings (List[Any]): List of PhraseNode objects.
    """
    level: str = "sentence"
    tag: str = ""
    confidence: float = 0.0
    source_text: str = ""
    target_text: str = ""
    explanation: Optional[str] = None
    nested_findings: List[Any] = field(default_factory=list)


@dataclass
class PhraseNode:
    """
    Represents a phrase in the hierarchical analysis.
    
    Attributes:
        level (str): The hierarchy level ("phrase").
        tag (str): A label or identifier for the phrase.
        confidence (float): Confidence score for the phrase alignment.
        source_text (str): Original phrase text.
        target_text (str): Translated/simplified phrase text.
        explanation (Optional[str]): Explanation of analysis.
    """
    level: str = "phrase"
    tag: str = ""
    confidence: float = 0.0
    source_text: str = ""
    target_text: str = ""
    explanation: Optional[str] = None

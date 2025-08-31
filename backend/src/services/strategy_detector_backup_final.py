"""
Enhanced Strategy Detection Implementation for NET-EST
Refactored to use cascade architecture for improved performance and modularity
"""

from typing import List, Dict, Optional, Tuple, Any
import re
from ..models.strategy_models import SimplificationStrategy, SimplificationStrategyType, STRATEGY_DESCRIPTIONS, StrategyExample
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer, util
import logging
from dataclasses import dataclass
from ..strategies import CascadeOrchestrator

# Enhanced feature extraction classes
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

class FeatureExtractor:
    """Extracts features for strategy detection"""

    def __init__(self, nlp_model=None, semantic_model=None):
        self.nlp = nlp_model
        self.semantic_model = semantic_model

    def extract_features(self, source_text: str, target_text: str) -> StrategyFeatures:
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

# Legacy methods removed - now using cascade architecture
# Keeping fallback methods for backward compatibility
        """Classify strategies based on extracted features"""
        evidences = []
        
        for strategy_code, classifier_func in self.strategy_rules.items():
            try:
                evidence = classifier_func(features, source_text, target_text)
                if evidence:
                    logging.info(f"Strategy {strategy_code}: confidence={evidence.confidence:.3f}")
                    if evidence.confidence > 0.4:  # Lower threshold for more lenient detection during development
                        evidences.append(evidence)
                        logging.info(f"✅ Accepted strategy {strategy_code} with confidence {evidence.confidence:.3f}")
                    else:
                        logging.info(f"❌ Rejected strategy {strategy_code}: confidence {evidence.confidence:.3f} below threshold")
                else:
                    logging.debug(f"Strategy {strategy_code}: no evidence found")
            except Exception as e:
                logging.error(f"Error in {strategy_code} detection: {e}")
        
        # Sort by confidence
        evidences.sort(key=lambda x: x.confidence, reverse=True)
        logging.info(f"Final evidences: {len(evidences)} strategies above threshold")
        return evidences
    
    def _classify_lexical_simplification(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """SL+ - Simplificação Lexical using semantic similarity + linguistic complexity analysis"""
        
        # Split into sentences for granular analysis
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentences = self._split_into_sentences(target_text)
        
        if not src_sentences or not tgt_sentences:
            return None
        
        simplification_evidence = []
        
        for src_sent in src_sentences:
            if len(self._tokenize_text(src_sent)) < 3:  # Skip very short sentences
                continue
                
            # Find semantically similar target sentence
            best_match = None
            best_similarity = 0.0
            
            for tgt_sent in tgt_sentences:
                if not _model_cache.get('semantic_model'):
                    # Fallback to lexical overlap when no semantic model
                    src_words = set(self._tokenize_text(src_sent))
                    tgt_words = set(self._tokenize_text(tgt_sent))
                    similarity = len(src_words & tgt_words) / max(len(src_words | tgt_words), 1)
                else:
                    try:
                        embeddings = _model_cache['semantic_model'].encode([src_sent, tgt_sent], convert_to_tensor=True)
                        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
                        similarity = max(0.0, min(1.0, similarity))
                    except Exception:
                        src_words = set(self._tokenize_text(src_sent))
                        tgt_words = set(self._tokenize_text(tgt_sent))
                        similarity = len(src_words & tgt_words) / max(len(src_words | tgt_words), 1)
                
                if similarity > best_similarity and similarity > 0.7:
                    best_similarity = similarity
                    best_match = tgt_sent
            
            if best_match and best_similarity > 0.75:
                # Calculate linguistic complexity reduction
                src_complexity = self._calculate_linguistic_complexity(src_sent)
                tgt_complexity = self._calculate_linguistic_complexity(best_match)
                
                if src_complexity > 0:
                    complexity_reduction = (src_complexity - tgt_complexity) / src_complexity
                    
                    # High semantic similarity + complexity reduction = SL+
                    if complexity_reduction > 0.15:
                        simplification_evidence.append({
                            "original": src_sent[:80] + "..." if len(src_sent) > 80 else src_sent,
                            "simplified": best_match[:80] + "..." if len(best_match) > 80 else best_match,
                            "similarity": best_similarity,
                            "complexity_reduction": complexity_reduction
                        })
        
        if simplification_evidence:
            avg_complexity_reduction = sum(e["complexity_reduction"] for e in simplification_evidence) / len(simplification_evidence)
            confidence = min(0.95, 0.6 + (avg_complexity_reduction * 1.5))
            
            return StrategyEvidence(
                strategy_code='SL+',
                confidence=confidence,
                impact_level="alto" if avg_complexity_reduction > 0.3 else "médio",
                features=features,
                examples=simplification_evidence[:3],  # Limit to top 3 examples
                positions=[]
            )
        
        return None
    
    def _classify_sentence_fragmentation(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """RP+ - Fragmentação Sintática - Enhanced semantic sentence fragmentation detection"""
        
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentences = self._split_into_sentences(target_text)
        
        if not src_sentences or not tgt_sentences:
            return None
            
        # Must have more sentences in target (fragmentation indicator)
        if len(tgt_sentences) <= len(src_sentences):
            return None
            
        sentence_increase = len(tgt_sentences) / len(src_sentences) - 1
        
        if sentence_increase < 0.2:  # At least 20% increase in sentence count
            return None
        
        fragmentation_evidence = []
        
        # Look for long source sentences that were broken into multiple target sentences
        for src_sent in src_sentences:
            src_words = self._tokenize_text(src_sent)
            
            # Only consider long sentences as candidates for fragmentation
            if len(src_words) < 12:
                continue
                
            # Find semantically related target sentences
            related_targets = []
            for tgt_sent in tgt_sentences:
                tgt_words = self._tokenize_text(tgt_sent)
                
                # Skip very short target sentences
                if len(tgt_words) < 4:
                    continue
                    
                # Calculate semantic similarity
                if _model_cache.get('semantic_model'):
                    try:
                        embeddings = _model_cache['semantic_model'].encode([src_sent, tgt_sent], convert_to_tensor=True)
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
                
                fragmentation_evidence.append({
                    "original": src_sent[:100] + "..." if len(src_sent) > 100 else src_sent,
                    "fragmentado": " | ".join([frag[:60] + ("..." if len(frag) > 60 else "") for frag in top_fragments]),
                    "fragment_count": len(related_targets),
                    "avg_similarity": sum(rt[1] for rt in related_targets) / len(related_targets)
                })
        
        if fragmentation_evidence:
            # Calculate confidence based on sentence increase and quality of fragmentation
            avg_similarity = sum(e["avg_similarity"] for e in fragmentation_evidence) / len(fragmentation_evidence)
            confidence = min(0.95, 0.5 + (sentence_increase * 0.8) + (avg_similarity * 0.4))
            
            impact = "alto" if sentence_increase > 0.5 else "médio"
            
            return StrategyEvidence(
                strategy_code='RP+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=fragmentation_evidence[:3],  # Limit to top 3 examples
                positions=[]
            )
        
        return None
    
    def _classify_global_rewriting(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """RF+ - Reescrita Global - Only for extensive rewrites, not simple lexical substitutions"""
        # More restrictive: very low lexical overlap AND significant structural changes
        if (features.lexical_overlap < 0.25 and
            features.semantic_similarity > 0.7 and
            features.structure_change_score > 0.3):
            confidence = features.semantic_similarity * (1 - features.lexical_overlap) * features.structure_change_score
            impact = "alto"
            
            return StrategyEvidence(
                strategy_code='RF+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=[{"original": source_text[:50] + "...", "simplified": target_text[:50] + "..."}],
                positions=[]
            )
        return None
    
    def _classify_meaning_change(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """AS+ - Alteração de Sentido"""
        if 0.3 < features.semantic_similarity < 0.7:
            confidence = 1 - abs(features.semantic_similarity - 0.5) * 2
            impact = "médio"
            
            return StrategyEvidence(
                strategy_code='AS+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=[{"original": "sentido original", "simplified": "sentido alterado"}],
                positions=[]
            )
        return None
    
    def _classify_positional_reorganization(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """DL+ - Reorganização Posicional - Enhanced word order analysis"""
        
        reorganization_evidence = []
        confidence_factors = []
        
        # Pattern 1: Sentence-level word order changes
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentences = self._split_into_sentences(target_text)
        
        if len(src_sentences) != len(tgt_sentences):
            return None  # DL+ requires same number of sentences with different order
            
        sentence_reorderings = 0
        for src_sent, tgt_sent in zip(src_sentences, tgt_sentences):
            src_words = self._tokenize_text(src_sent)
            tgt_words = self._tokenize_text(tgt_sent)
            
            # Must have high semantic similarity but different word order
            if _model_cache.get('semantic_model'):
                try:
                    embeddings = _model_cache['semantic_model'].encode([src_sent, tgt_sent], convert_to_tensor=True)
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
                    "similarity": similarity
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
        
        # Pattern 3: Subject-verb-object reordering
        svo_reorderings = self._detect_svo_reordering(source_text, target_text)
        if svo_reorderings:
            for reordering in svo_reorderings:
                reorganization_evidence.append({
                    "type": "syntactic_reordering",
                    "original": reordering['original'],
                    "simplified": reordering['reordered'],
                    "transformation": reordering['transformation']
                })
            confidence_factors.append(0.75)
        
        # Pattern 4: Temporal/spatial expression reordering
        temporal_reorderings = self._detect_temporal_reordering(source_text, target_text)
        if temporal_reorderings:
            for reordering in temporal_reorderings:
                reorganization_evidence.append({
                    "type": "temporal_reordering",
                    "original": "expressão temporal no final",
                    "simplified": "expressão temporal no início",
                    "expression": reordering['expression']
                })
            confidence_factors.append(0.6)
        
        if reorganization_evidence:
            # Calculate confidence based on extent and quality of reorganization
            if confidence_factors:
                avg_confidence = sum(confidence_factors) / len(confidence_factors)
                # Bonus for multiple types of reorganization
                final_confidence = min(0.95, avg_confidence + (len(reorganization_evidence) - 1) * 0.05)
            else:
                final_confidence = 0.5
            
            # Impact based on extent of reorganization
            impact = "alto" if len(reorganization_evidence) > 2 else "médio"
            
            return StrategyEvidence(
                strategy_code='DL+',
                confidence=final_confidence,
                impact_level=impact,
                features=features,
                examples=reorganization_evidence[:3],  # Limit to top 3 examples
                positions=[]
            )
        
        return None
    
    def _classify_explicitness(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """EXP+ - Explicitação e Detalhamento - Enhanced contextual explanation detection"""
        
        explicitness_evidence = []
        confidence_factors = []
        
        # Pattern 1: Parenthetical explanations added
        parenthetical_additions = self._find_parenthetical_additions(source_text, target_text)
        if parenthetical_additions:
            for addition in parenthetical_additions:
                explicitness_evidence.append({
                    "type": "parenthetical_explanation",
                    "original": "termo técnico",
                    "simplified": f"termo técnico ({addition['explanation']})",
                    "quality": addition['quality_score']
                })
            confidence_factors.append(0.8)
        
        # Pattern 2: Specialized term expansions
        term_expansions = self._find_specialized_term_expansions(source_text, target_text)
        if term_expansions:
            for expansion in term_expansions:
                explicitness_evidence.append({
                    "type": "term_expansion",
                    "original": expansion['term'],
                    "simplified": f"{expansion['term']} com contexto expandido",
                    "expansion_ratio": expansion['expansion_ratio']
                })
            confidence_factors.append(0.7)
        
        # Pattern 3: Contextual glosses and definitions
        contextual_glosses = self._find_contextual_glosses(source_text, target_text)
        if contextual_glosses:
            for gloss in contextual_glosses:
                explicitness_evidence.append({
                    "type": "contextual_gloss",
                    "original": gloss['term'],
                    "simplified": f"{gloss['term']}: {gloss['definition']}",
                    "pattern": gloss['full_match']
                })
            confidence_factors.append(0.75)
        
        # Pattern 4: Example additions (por exemplo, como)
        example_additions = self._find_example_additions(source_text, target_text)
        if example_additions:
            for example in example_additions:
                explicitness_evidence.append({
                    "type": "example_addition",
                    "original": "conceito abstrato",
                    "simplified": f"conceito com exemplo: {example['example_text']}",
                    "marker": example['marker']
                })
            confidence_factors.append(0.6)
        
        # Pattern 5: Clarifying phrase additions (isto é, ou seja, quer dizer)
        clarifying_additions = self._find_clarifying_additions(source_text, target_text)
        if clarifying_additions:
            for clarification in clarifying_additions:
                explicitness_evidence.append({
                    "type": "clarifying_phrase",
                    "original": "ideia implícita",
                    "simplified": f"ideia, {clarification['marker']} {clarification['clarification']}",
                    "marker": clarification['marker']
                })
            confidence_factors.append(0.7)
        
        if explicitness_evidence:
            # Calculate confidence based on quality and quantity of explicitness
            if confidence_factors:
                avg_confidence = sum(confidence_factors) / len(confidence_factors)
                # Bonus for multiple types of explicitness
                final_confidence = min(0.95, avg_confidence + (len(explicitness_evidence) - 1) * 0.05)
            else:
                final_confidence = 0.5
            
            # Impact based on extent of explicitness
            impact = "alto" if len(explicitness_evidence) > 2 else "médio"
            
            return StrategyEvidence(
                strategy_code='EXP+',
                confidence=final_confidence,
                impact_level=impact,
                features=features,
                examples=explicitness_evidence[:3],  # Limit to top 3 examples
                positions=[]
            )
        
        return None
    
    def _classify_insertion_handling(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """IN+ - Manejo de Inserções - Enhanced parenthetical insertion analysis"""
        
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
        
        # Pattern 3: Inline citations and references removal
        src_citations = self._extract_citation_patterns(source_text)
        tgt_citations = self._extract_citation_patterns(target_text)
        
        if len(src_citations) > len(tgt_citations):
            removed_citations = len(src_citations) - len(tgt_citations)
            insertion_evidence.append({
                "type": "citation_removal",
                "original": f"texto com {len(src_citations)} citações",
                "simplified": f"texto com {len(tgt_citations)} citações",
                "removed_count": removed_citations
            })
            confidence_factors.append(0.6)
        
        # Pattern 4: Appositive expressions simplification
        src_appositives = self._extract_appositive_expressions(source_text)
        tgt_appositives = self._extract_appositive_expressions(target_text)
        
        if len(src_appositives) > len(tgt_appositives):
            removed_appositives = len(src_appositives) - len(tgt_appositives)
            insertion_evidence.append({
                "type": "appositive_removal",
                "original": "texto com apostos explicativos",
                "simplified": "texto sem apostos",
                "removed_count": removed_appositives
            })
            confidence_factors.append(0.75)
        
        # Pattern 5: Integration of insertions into main text
        integrated_insertions = self._detect_insertion_integration(source_text, target_text)
        if integrated_insertions:
            for integration in integrated_insertions:
                insertion_evidence.append({
                    "type": "insertion_integration",
                    "original": integration['original_form'],
                    "simplified": integration['integrated_form'],
                    "integration_type": integration['type']
                })
            confidence_factors.append(0.8)
        
        if insertion_evidence and features.semantic_similarity > 0.6:
            # Calculate confidence based on insertion handling quality and semantic preservation
            if confidence_factors:
                avg_confidence = sum(confidence_factors) / len(confidence_factors)
                final_confidence = min(0.95, avg_confidence * features.semantic_similarity)
            else:
                final_confidence = 0.5
            
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
    
    def _classify_perspective_reinterpretation(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """MOD+ - Reinterpretação Perspectiva - Enhanced semantic perspective shift detection"""
        
        perspective_evidence = []
        confidence_factors = []
        
        # Pattern 1: Same meaning, completely different wording (classic perspective shift)
        if (features.semantic_similarity > 0.85 and
            features.lexical_overlap < 0.25 and
            features.avg_word_length_ratio > 0.85):  # Similar complexity, different perspective
            
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
        tgt_sentences = self._split_into_sentences(target_text)
        
        if len(src_sentences) == len(tgt_sentences):  # MOD+ typically maintains sentence count
            sentence_reinterpretations = self._detect_perspective_shifts(src_sentences, tgt_sentences)
            if sentence_reinterpretations:
                for reinterpretation in sentence_reinterpretations:
                    perspective_evidence.append({
                        "type": "sentence_perspective_shift",
                        "original": reinterpretation['source'],
                        "simplified": reinterpretation['target'],
                        "similarity": reinterpretation['semantic_similarity'],
                        "word_overlap": reinterpretation['word_overlap']
                    })
                confidence_factors.append(0.8)
        
        # Pattern 3: Voice/agency perspective changes (active/passive, personal/impersonal)
        voice_changes = self._detect_voice_perspective_changes(source_text, target_text)
        if voice_changes:
            for change in voice_changes:
                perspective_evidence.append({
                    "type": "voice_perspective_change",
                    "original": change['source_pattern'],
                    "simplified": change['target_pattern'],
                    "change_type": change['transformation']
                })
            confidence_factors.append(0.7)
        
        # Pattern 4: Temporal/modal perspective shifts (certainty, time frame, viewpoint)
        modal_changes = self._detect_modal_perspective_changes(source_text, target_text)
        if modal_changes:
            for change in modal_changes:
                perspective_evidence.append({
                    "type": "modal_perspective_change",
                    "original": f"modalidade: {change['source_modality']}",
                    "simplified": f"modalidade: {change['target_modality']}",
                    "change_description": change['description']
                })
            confidence_factors.append(0.6)
        
        if perspective_evidence:
            # Calculate confidence based on quality and quantity of perspective shifts
            if confidence_factors:
                avg_confidence = sum(confidence_factors) / len(confidence_factors)
                # High threshold for MOD+ - must be very confident it's perspective shift, not other strategies
                final_confidence = min(0.95, avg_confidence * features.semantic_similarity)
            else:
                final_confidence = 0.5
            
            # Only accept if confidence is very high (MOD+ is distinct from other strategies)
            if final_confidence > 0.75:
                impact = "alto" if len(perspective_evidence) > 1 else "médio"
                
                return StrategyEvidence(
                    strategy_code='MOD+',
                    confidence=final_confidence,
                    impact_level=impact,
                    features=features,
                    examples=perspective_evidence[:3],  # Limit to top 3 examples
                    positions=[]
                )
        
        return None
    
    def _classify_title_optimization(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """MT+ - Otimização de Títulos - Enhanced title structure analysis"""
        
        src_lines = [line.strip() for line in source_text.split('\n') if line.strip()]
        tgt_lines = [line.strip() for line in target_text.split('\n') if line.strip()]
        
        if not src_lines or not tgt_lines:
            return None
            
        title_evidence = []
        confidence_factors = []
        
        # Pattern 1: New titles added in target (most common)
        src_title_lines = self._identify_title_lines(src_lines)
        tgt_title_lines = self._identify_title_lines(tgt_lines)
        
        if len(tgt_title_lines) > len(src_title_lines):
            # New titles were added
            new_titles = tgt_title_lines[len(src_title_lines):]
            for title in new_titles:
                title_evidence.append({
                    "type": "title_addition",
                    "original": "texto sem título",
                    "optimized": f"TÍTULO: {title}"
                })
            confidence_factors.append(0.8)
        
        # Pattern 2: Existing titles reformulated for clarity
        for i, (src_title, tgt_title) in enumerate(zip(src_title_lines, tgt_title_lines)):
            if src_title != tgt_title:
                # Check if target title is clearer/more accessible
                src_words = len(self._tokenize_text(src_title))
                tgt_words = len(self._tokenize_text(tgt_title))
                
                # Title optimization often makes titles shorter and clearer
                if tgt_words <= src_words and len(tgt_title) > 0:
                    title_evidence.append({
                        "type": "title_reformulation",
                        "original": src_title,
                        "optimized": tgt_title
                    })
                    confidence_factors.append(0.7)
        
        # Pattern 3: Section headers introduced for better organization
        section_headers = self._find_section_headers(tgt_lines)
        if section_headers and not self._find_section_headers(src_lines):
            for header in section_headers[:2]:  # Limit to first 2
                title_evidence.append({
                    "type": "section_header",
                    "original": "texto corrido",
                    "optimized": f"Seção: {header}"
                })
            confidence_factors.append(0.6)
        
        # Pattern 4: Explicit topic headers for content organization
        if len(tgt_lines) > len(src_lines):
            # Look for new organizational structure
            potential_headers = [line for line in tgt_lines if self._is_topic_header(line)]
            if potential_headers:
                for header in potential_headers[:2]:
                    title_evidence.append({
                        "type": "topic_organization",
                        "original": "conteúdo sem estrutura",
                        "optimized": f"Tópico: {header}"
                    })
                confidence_factors.append(0.5)
        
        if title_evidence:
            avg_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            
            # Higher confidence for multiple title optimizations
            final_confidence = min(0.95, avg_confidence + (len(title_evidence) - 1) * 0.1)
            
            impact = "médio" if len(title_evidence) > 1 else "baixo"
            
            return StrategyEvidence(
                strategy_code='MT+',
                confidence=final_confidence,
                impact_level=impact,
                features=features,
                examples=title_evidence[:3],  # Limit to top 3 examples
                positions=[]
            )
        
        return None
        
    def _identify_title_lines(self, lines: List[str]) -> List[str]:
        """Identify lines that appear to be titles"""
        titles = []
        for line in lines:
            # Check various title indicators
            if (line.isupper() and len(line) > 3 or  # ALL CAPS
                line.endswith(':') or  # Ends with colon
                (len(line) < 60 and line.istitle() and not line.endswith('.')) or  # Title case, short, no period
                any(marker in line.lower() for marker in ['título:', 'capítulo', 'seção'])  # Explicit markers
            ):
                titles.append(line)
        return titles
        
    def _find_section_headers(self, lines: List[str]) -> List[str]:
        """Find section headers in text"""
        headers = []
        for line in lines:
            # Look for numbered sections, bullet points, or other organizational markers
            if (re.match(r'^\d+\.', line) or  # Numbered sections
                re.match(r'^[A-Z]\)', line) or  # Lettered sections
                line.startswith('•') or line.startswith('-') or  # Bullet points
                re.match(r'^\d+\s*-', line)  # Numbered with dash
            ):
                headers.append(line)
        return headers
        
    def _is_topic_header(self, line: str) -> bool:
        """Check if a line serves as a topic header"""
        line_words = len(self._tokenize_text(line))
        return (
            line_words <= 8 and  # Short enough to be a header
            line_words >= 2 and  # Long enough to be meaningful
            not line.endswith('.') and  # Headers typically don't end with periods
            len(line) < 80  # Not too long
        )
    
    def _classify_content_structuring(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """RD+ - Estruturação de Conteúdo - Enhanced content flow and organization detection"""
        
        structuring_evidence = []
        confidence_factors = []
        
        # Pattern 1: Addition of numbered lists or bullet points
        src_lists = self._find_list_structures(source_text)
        tgt_lists = self._find_list_structures(target_text)
        
        if len(tgt_lists) > len(src_lists):
            new_lists = len(tgt_lists) - len(src_lists)
            structuring_evidence.append({
                "type": "list_introduction",
                "original": "texto corrido sem listas",
                "structured": f"Adicionadas {new_lists} listas organizacionais",
                "count": new_lists
            })
            confidence_factors.append(0.8)
        
        # Pattern 2: Introduction of discourse markers and connectives
        src_connectives = self._count_discourse_markers(source_text)
        tgt_connectives = self._count_discourse_markers(target_text)
        
        if tgt_connectives > src_connectives * 1.3:  # At least 30% increase
            marker_increase = tgt_connectives - src_connectives
            structuring_evidence.append({
                "type": "discourse_markers",
                "original": "texto sem conectivos explícitos",
                "structured": f"Adicionados {marker_increase} conectivos organizacionais",
                "improvement": marker_increase
            })
            confidence_factors.append(0.7)
        
        # Pattern 3: Paragraph reorganization for better flow
        src_paragraphs = len([p for p in source_text.split('\n\n') if p.strip()])
        tgt_paragraphs = len([p for p in target_text.split('\n\n') if p.strip()])
        
        if tgt_paragraphs > src_paragraphs and features.semantic_similarity > 0.7:
            paragraph_increase = tgt_paragraphs - src_paragraphs
            structuring_evidence.append({
                "type": "paragraph_organization",
                "original": f"texto em {src_paragraphs} parágrafos",
                "structured": f"reorganizado em {tgt_paragraphs} parágrafos",
                "improvement": paragraph_increase
            })
            confidence_factors.append(0.6)
        
        # Pattern 4: Introduction of section breaks and headers
        src_sections = self._count_section_breaks(source_text)
        tgt_sections = self._count_section_breaks(target_text)
        
        if tgt_sections > src_sections:
            section_increase = tgt_sections - src_sections
            structuring_evidence.append({
                "type": "section_organization",
                "original": "texto sem divisões claras",
                "structured": f"Adicionadas {section_increase} divisões de seção",
                "improvement": section_increase
            })
            confidence_factors.append(0.7)
        
        # Pattern 5: Sequential organization (primeiro, segundo, depois, etc.)
        src_sequential = self._count_sequential_markers(source_text)
        tgt_sequential = self._count_sequential_markers(target_text)
        
        if tgt_sequential > src_sequential:
            sequential_increase = tgt_sequential - src_sequential
            structuring_evidence.append({
                "type": "sequential_organization",
                "original": "sem marcadores sequenciais",
                "structured": f"Adicionados {sequential_increase} marcadores sequenciais",
                "improvement": sequential_increase
            })
            confidence_factors.append(0.8)
        
        if structuring_evidence:
            # Calculate confidence based on multiple structuring improvements
            avg_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            
            # Bonus for multiple types of structuring
            final_confidence = min(0.95, avg_confidence + (len(structuring_evidence) - 1) * 0.05)
            
            # Impact based on extent of restructuring
            total_improvements = sum(e.get("improvement", e.get("count", 1)) for e in structuring_evidence)
            impact = "alto" if total_improvements > 3 else "médio"
            
            return StrategyEvidence(
                strategy_code='RD+',
                confidence=final_confidence,
                impact_level=impact,
                features=features,
                examples=structuring_evidence[:3],  # Limit to top 3 examples
                positions=[]
            )
        
        return None
    
    def _find_list_structures(self, text: str) -> List[Dict[str, Any]]:
        """Find numbered lists, bullet points, and other list structures"""
        lists = []
        lines = text.split('\n')
        
        current_list = []
        list_type = None
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_list:
                    lists.append({"type": list_type, "items": current_list})
                    current_list = []
                    list_type = None
                continue
                
            # Numbered lists
            if re.match(r'^\d+[\.\)]\s+', line):
                if list_type != "numbered":
                    if current_list:
                        lists.append({"type": list_type, "items": current_list})
                    current_list = [line]
                    list_type = "numbered"
                else:
                    current_list.append(line)
            # Bullet points
            elif re.match(r'^[\-\*\•]\s+', line):
                if list_type != "bullet":
                    if current_list:
                        lists.append({"type": list_type, "items": current_list})
                    current_list = [line]
                    list_type = "bullet"
                else:
                    current_list.append(line)
            # Lettered lists
            elif re.match(r'^[a-zA-Z][\.\)]\s+', line):
                if list_type != "lettered":
                    if current_list:
                        lists.append({"type": list_type, "items": current_list})
                    current_list = [line]
                    list_type = "lettered"
                else:
                    current_list.append(line)
            else:
                if current_list:
                    lists.append({"type": list_type, "items": current_list})
                    current_list = []
                    list_type = None
        
        if current_list:
            lists.append({"type": list_type, "items": current_list})
        
        return lists
    
    def _count_discourse_markers(self, text: str) -> int:
        """Count discourse markers and connectives"""
        markers = [
            # Sequential
            'primeiro', 'segundo', 'terceiro', 'em primeiro lugar', 'em segundo lugar',
            'inicialmente', 'posteriormente', 'finalmente', 'por fim', 'por último',
            
            # Additive
            'além disso', 'também', 'igualmente', 'da mesma forma', 'similarmente',
            'adicionalmente', 'ainda', 'outrossim',
            
            # Contrastive
            'porém', 'contudo', 'entretanto', 'no entanto', 'todavia', 'mas',
            'por outro lado', 'em contrapartida', 'apesar disso',
            
            # Causal
            'portanto', 'assim', 'consequentemente', 'por isso', 'devido a isso',
            'como resultado', 'dessa forma', 'por conseguinte',
            
            # Explanatory
            'ou seja', 'isto é', 'por exemplo', 'como por exemplo', 'a saber'
        ]
        
        count = 0
        text_lower = text.lower()
        for marker in markers:
            count += text_lower.count(marker)
        
        return count
    
    def _count_section_breaks(self, text: str) -> int:
        """Count section breaks and headers"""
        breaks = 0
        
        # Double line breaks (paragraph separations)
        breaks += text.count('\n\n')
        
        # Section headers (lines ending with ':')
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.endswith(':') and len(line) < 50:
                breaks += 1
        
        # Numbered section headers
        for line in lines:
            if re.match(r'^\d+\.?\s+[A-Z]', line.strip()):
                breaks += 1
        
        return breaks
    
    def _count_sequential_markers(self, text: str) -> int:
        """Count sequential organization markers"""
        sequential_markers = [
            'primeiro', 'segundo', 'terceiro', 'quarto', 'quinto',
            'primeiramente', 'segundamente', 'inicialmente',
            'posteriormente', 'em seguida', 'depois', 'então',
            'finalmente', 'por fim', 'por último', 'para concluir'
        ]
        
        count = 0
        text_lower = text.lower()
        for marker in sequential_markers:
            count += text_lower.count(marker)
        
        return count
    
    def _classify_referential_clarity(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """TA+ - Clareza Referencial"""
        if features.pronoun_reduction_score > 0.3:
            confidence = features.pronoun_reduction_score
            impact = "médio"
            
            return StrategyEvidence(
                strategy_code='TA+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=[{"original": "ele fez isso", "simplified": "João fez a tarefa"}],
                positions=[]
            )
        return None
    
    def _classify_voice_change(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """MV+ - Alteração da Voz Verbal"""
        if features.voice_change_score > 0.2:
            confidence = features.voice_change_score
            impact = "médio"
            
            return StrategyEvidence(
                strategy_code='MV+',
                confidence=confidence,
                impact_level=impact,
                features=features,
                examples=[{"original": "foi feito", "simplified": "fez"}],
                positions=[]
            )
        return None
    
    def _classify_selective_omission(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """OM+ - Omissão Seletiva - Requires human validation for content omission decisions"""
        
        # Only detect OM+ if explicitly enabled (disabled by default as per documentation)
        if not getattr(self, 'enable_om_detection', False):
            logging.debug("OM+ detection disabled - requires human validation")
            return None
        
        # OM+ detection framework - flags potential cases for human annotation
        omission_candidates = []
        confidence_factors = []
        
        # Pattern 1: Significant length reduction with semantic preservation
        length_reduction = 1 - (len(target_text) / max(len(source_text), 1))
        if (length_reduction > 0.3 and features.semantic_similarity > 0.7):
            omission_candidates.append({
                "type": "length_reduction_with_semantic_preservation",
                "original": f"texto de {len(source_text)} caracteres",
                "simplified": f"texto de {len(target_text)} caracteres",
                "reduction_ratio": length_reduction,
                "semantic_similarity": features.semantic_similarity,
                "requires_human_validation": True
            })
            confidence_factors.append(0.6)  # Lower confidence - needs human validation
        
        # Pattern 2: Sentence omission detection
        src_sentences = self._split_into_sentences(source_text)
        tgt_sentences = self._split_into_sentences(target_text)
        
        if len(src_sentences) > len(tgt_sentences):
            sentence_omission_ratio = (len(src_sentences) - len(tgt_sentences)) / len(src_sentences)
            if sentence_omission_ratio > 0.2:  # At least 20% of sentences omitted
                omission_candidates.append({
                    "type": "sentence_omission",
                    "original": f"{len(src_sentences)} frases originais",
                    "simplified": f"{len(tgt_sentences)} frases mantidas",
                    "omission_ratio": sentence_omission_ratio,
                    "requires_human_validation": True
                })
                confidence_factors.append(0.7)
        
        # Pattern 3: Paragraph omission detection
        src_paragraphs = [p for p in source_text.split('\n\n') if p.strip()]
        tgt_paragraphs = [p for p in target_text.split('\n\n') if p.strip()]
        
        if len(src_paragraphs) > len(tgt_paragraphs):
            paragraph_omission_ratio = (len(src_paragraphs) - len(tgt_paragraphs)) / len(src_paragraphs)
            if paragraph_omission_ratio > 0.25:
                omission_candidates.append({
                    "type": "paragraph_omission",
                    "original": f"{len(src_paragraphs)} parágrafos originais",
                    "simplified": f"{len(tgt_paragraphs)} parágrafos mantidos",
                    "omission_ratio": paragraph_omission_ratio,
                    "requires_human_validation": True
                })
                confidence_factors.append(0.65)
        
        # Pattern 4: Detail/elaboration omission
        detail_markers = ['por exemplo', 'como', 'isto é', 'ou seja', 'especificamente', 'detalhadamente']
        src_details = sum(1 for marker in detail_markers if marker in source_text.lower())
        tgt_details = sum(1 for marker in detail_markers if marker in target_text.lower())
        
        if src_details > tgt_details:
            detail_omission_ratio = (src_details - tgt_details) / max(src_details, 1)
            if detail_omission_ratio > 0.3:
                omission_candidates.append({
                    "type": "detail_elaboration_omission",
                    "original": f"texto com {src_details} elaborações",
                    "simplified": f"texto com {tgt_details} elaborações",
                    "omission_ratio": detail_omission_ratio,
                    "requires_human_validation": True
                })
                confidence_factors.append(0.5)
        
        if omission_candidates:
            # Calculate confidence - always lower for OM+ due to need for human validation
            avg_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.4
            final_confidence = min(0.8, avg_confidence)  # Cap at 0.8 - human validation required
            
            # Add human validation flag to all examples
            for candidate in omission_candidates:
                candidate["human_validation_required"] = True
                candidate["validation_notes"] = "OM+ requires human expert to validate content omission decisions"
            
            return StrategyEvidence(
                strategy_code='OM+',
                confidence=final_confidence,
                impact_level="médio",  # Impact assessment requires human judgment
                features=features,
                examples=omission_candidates[:3],  # Limit to top 3 examples
                positions=[]
            )
        
        return None
    
    def _classify_problem_processing(self, features: StrategyFeatures, source_text: str, target_text: str) -> Optional[StrategyEvidence]:
        """PRO+ - Processamento de Problemas - Human annotation only (as per canonical documentation)"""
        
        # PRO+ is exclusively for human annotation - only detect if explicitly allowed
        if not getattr(self, 'pro_tag_allowed', False):
            logging.debug("PRO+ is for human annotation only - automatic detection disabled")
            return None
        
        # PRO+ framework for human annotators - provides structure for annotation
        problem_processing_indicators = []
        
        # Framework Pattern 1: Problem statement identification
        problem_indicators = [
            'problema', 'questão', 'dificuldade', 'desafio', 'obstáculo',
            'como resolver', 'como solucionar', 'qual é o problema', 'qual a questão'
        ]
        
        src_problems = sum(1 for indicator in problem_indicators if indicator in source_text.lower())
        tgt_problems = sum(1 for indicator in problem_indicators if indicator in target_text.lower())
        
        if src_problems > 0 or tgt_problems > 0:
            problem_processing_indicators.append({
                "type": "problem_statement_framework",
                "original": f"contexto com {src_problems} indicadores de problema",
                "simplified": f"contexto com {tgt_problems} indicadores de problema",
                "annotation_required": True,
                "human_guidance": "Avalie se houve processamento de problemas: identificação, análise, ou resolução"
            })
        
        # Framework Pattern 2: Solution/resolution markers
        solution_indicators = [
            'solução', 'resolução', 'resposta', 'alternativa', 'opção',
            'para resolver', 'para solucionar', 'a solução é', 'resolve-se'
        ]
        
        src_solutions = sum(1 for indicator in solution_indicators if indicator in source_text.lower())
        tgt_solutions = sum(1 for indicator in solution_indicators if indicator in target_text.lower())
        
        if src_solutions > 0 or tgt_solutions > 0:
            problem_processing_indicators.append({
                "type": "solution_framework",
                "original": f"contexto com {src_solutions} indicadores de solução",
                "simplified": f"contexto com {tgt_solutions} indicadores de solução",
                "annotation_required": True,
                "human_guidance": "Avalie se houve processamento de soluções: apresentação, explicação, ou simplificação"
            })
        
        # Framework Pattern 3: Process/method indicators
        process_indicators = [
            'processo', 'método', 'procedimento', 'etapa', 'passo',
            'primeiro', 'segundo', 'depois', 'em seguida', 'finalmente'
        ]
        
        src_processes = sum(1 for indicator in process_indicators if indicator in source_text.lower())
        tgt_processes = sum(1 for indicator in process_indicators if indicator in target_text.lower())
        
        if src_processes > 0 or tgt_processes > 0:
            problem_processing_indicators.append({
                "type": "process_method_framework",
                "original": f"contexto com {src_processes} indicadores de processo",
                "simplified": f"contexto com {tgt_processes} indicadores de processo",
                "annotation_required": True,
                "human_guidance": "Avalie se houve processamento de métodos: estruturação, sequenciamento, ou simplificação de processos"
            })
        
        # PRO+ only returns evidence when human annotation is explicitly enabled
        if problem_processing_indicators:
            # Very low confidence - this is for human annotation framework only
            framework_confidence = 0.3  # Low confidence indicates need for human judgment
            
            # Add human annotation guidance to all indicators
            for indicator in problem_processing_indicators:
                indicator["strategy_code"] = "PRO+"
                indicator["annotation_instruction"] = "Estratégia PRO+ requer anotação humana especializada para validação"
                indicator["evaluation_criteria"] = [
                    "Houve identificação de problemas?",
                    "Houve processamento/análise de problemas?",
                    "Houve apresentação de soluções?",
                    "Houve simplificação do processo de resolução?"
                ]
            
            return StrategyEvidence(
                strategy_code='PRO+',
                confidence=framework_confidence,
                impact_level="baixo",  # Low impact until human validation
                features=features,
                examples=problem_processing_indicators[:3],
                positions=[]
            )
        
        return None

    # === Infrastructure Helper Methods for Semantic Detection ===
    
    def _calculate_linguistic_complexity(self, text: str) -> float:
        """Calculate linguistic complexity using multiple measures"""
        if not text.strip():
            return 0.0
            
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        # Lexical complexity (average word length)
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        # Sentence length complexity
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Try to use spaCy for more sophisticated analysis
        if _model_cache.get('nlp'):
            try:
                doc = _model_cache['nlp'](text)
                
                # Syntactic complexity (dependency depth)
                def get_depth(token):
                    if not list(token.children):
                        return 0
                    return 1 + max(get_depth(child) for child in token.children)
                
                syntactic_complexity = 0
                if list(doc.sents):
                    depths = [get_depth(token) for token in doc if token.dep_ == "ROOT"]
                    syntactic_complexity = sum(depths) / len(depths) if depths else 0
                
                # Morphological complexity (complex POS tags)
                complex_pos = {"VERB", "ADJ", "ADV", "NOUN"}
                morphological_complexity = len([t for t in doc if t.pos_ in complex_pos]) / len(doc) if len(doc) > 0 else 0
                
                # Weighted combination
                return (avg_word_length * 0.3) + (avg_sentence_length * 0.01) + (syntactic_complexity * 0.4) + (morphological_complexity * 0.3)
                
            except Exception as e:
                logging.warning(f"Error in spaCy complexity analysis: {e}")
        
        # Fallback to simple measures
        return (avg_word_length * 0.4) + (avg_sentence_length * 0.01)
    
    def _calculate_contextual_coherence(self, text: str, context: str) -> float:
        """Calculate how well text fits semantically within the context"""
        if not _model_cache.get('semantic_model') or not text.strip() or not context.strip():
            return 0.5  # Neutral score when no model available
        
        try:
            embeddings = _model_cache['semantic_model'].encode([text, context], convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logging.warning(f"Error calculating contextual coherence: {e}")
            return 0.5
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if _model_cache.get('nlp'):
            try:
                doc = _model_cache['nlp'](text)
                return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            except Exception:
                pass
        # Fallback to simple splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words"""
        if _model_cache.get('nlp'):
            try:
                doc = _model_cache['nlp'](text)
                return [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
            except Exception:
                pass
        # Fallback to simple tokenization
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
    
    def _extract_term_context(self, text: str, term: str, window: int = 15) -> str:
        """Extract context around a term for EXP+ analysis"""
        if not text or not term:
            return ""
        
        words = text.split()
        term_positions = [i for i, word in enumerate(words) if term.lower() in word.lower()]
        
        if not term_positions:
            return ""
        
        pos = term_positions[0]
        start = max(0, pos - window)
        end = min(len(words), pos + window + 1)
        
        return " ".join(words[start:end])
    
    def _find_parenthetical_additions(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Find parenthetical explanations added in target text for EXP+ detection"""
        import re
        
        # Find parentheses in target that aren't in source
        src_parens = set(re.findall(r'\([^)]+\)', source_text))
        tgt_parens = set(re.findall(r'\([^)]+\)', target_text))
        
        new_parens = tgt_parens - src_parens
        
        parenthetical_evidence = []
        for paren_text in new_parens:
            # Remove parentheses for analysis
            clean_text = paren_text.strip('()')
            
            # Check if it's explanatory (not just random addition)
            explanatory_patterns = [
                "ou seja", "isto é", "também conhecido", "significa",
                "por exemplo", "como", "que é", "definido como"
            ]
            
            is_explanatory = any(pattern in clean_text.lower() for pattern in explanatory_patterns)
            
            # Also consider length and content quality
            if len(clean_text.split()) > 1 or is_explanatory:
                parenthetical_evidence.append({
                    "type": "parenthetical",
                    "explanation": clean_text,
                    "quality_score": 0.8 if is_explanatory else 0.6,
                    "original_form": paren_text
                })
        
        return parenthetical_evidence
    
    def _find_specialized_term_expansions(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Find specialized terms that were expanded with explanations for EXP+"""
        if not _model_cache.get('nlp'):
            return []
        
        try:
            src_doc = _model_cache['nlp'](source_text)
            tgt_doc = _model_cache['nlp'](target_text)
            
            # Find potential specialized terms (uncommon words, proper nouns, technical terms)
            src_specialized = {
                token.text.lower() for token in src_doc
                if token.pos_ in ["PROPN", "NOUN"] and len(token.text) > 6 and not token.is_stop
            }
            
            expansions = []
            for term in src_specialized:
                if term in target_text.lower():
                    # Look for expanded explanations around the term in target
                    term_context_src = self._extract_term_context(source_text, term, window=10)
                    term_context_tgt = self._extract_term_context(target_text, term, window=20)
                    
                    # Check if target context is significantly longer (expansion)
                    if len(term_context_tgt) > len(term_context_src) * 1.3:
                        expansions.append({
                            "type": "term_expansion",
                            "term": term,
                            "source_context": term_context_src,
                            "target_context": term_context_tgt,
                            "expansion_ratio": len(term_context_tgt) / max(len(term_context_src), 1),
                            "quality_score": 0.7
                        })
            
            return expansions
            
        except Exception as e:
            logging.warning(f"Error in specialized term expansion detection: {e}")
            return []
    
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
            src_matches = re.findall(pattern, source_text, re.IGNORECASE)
            tgt_matches = re.findall(pattern, target_text, re.IGNORECASE)
            
            src_phrases.extend(src_matches)
            tgt_phrases.extend(tgt_matches)
        
        # Check if phrases appear in different positions
        for src_phrase in src_phrases[:3]:  # Limit to avoid performance issues
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
    
    def _detect_svo_reordering(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Detect subject-verb-object reordering using spaCy if available"""
        if not _model_cache.get('nlp'):
            return []
        
        try:
            src_doc = _model_cache['nlp'](source_text)
            tgt_doc = _model_cache['nlp'](target_text)
            
            reorderings = []
            
            # Analyze sentence structure for both texts
            src_sents = list(src_doc.sents)
            tgt_sents = list(tgt_doc.sents)
            
            for src_sent, tgt_sent in zip(src_sents[:3], tgt_sents[:3]):  # Limit for performance
                src_structure = self._extract_sentence_structure(src_sent)
                tgt_structure = self._extract_sentence_structure(tgt_sent)
                
                if (src_structure and tgt_structure and 
                    src_structure['pattern'] != tgt_structure['pattern'] and
                    len(set(src_structure['elements']) & set(tgt_structure['elements'])) >= 2):
                    
                    reorderings.append({
                        "original": src_sent.text[:80] + ("..." if len(src_sent.text) > 80 else ""),
                        "reordered": tgt_sent.text[:80] + ("..." if len(tgt_sent.text) > 80 else ""),
                        "transformation": f"{src_structure['pattern']} → {tgt_structure['pattern']}"
                    })
            
            return reorderings
            
        except Exception as e:
            logging.warning(f"Error in SVO reordering detection: {e}")
            return []
    
    def _extract_sentence_structure(self, sent) -> Optional[Dict[str, Any]]:
        """Extract basic sentence structure (subject, verb, object)"""
        try:
            structure = {"elements": [], "pattern": ""}
            
            # Find main syntactic roles
            subject = None
            verb = None
            obj = None
            
            for token in sent:
                if token.dep_ in ["nsubj", "nsubjpass"]:
                    subject = token.text.lower()
                elif token.dep_ == "ROOT" and token.pos_ == "VERB":
                    verb = token.text.lower()
                elif token.dep_ in ["dobj", "obj"]:
                    obj = token.text.lower()
            
            # Create pattern representation
            if subject:
                structure["elements"].append(subject)
                structure["pattern"] += "S"
            if verb:
                structure["elements"].append(verb)
                structure["pattern"] += "V"
            if obj:
                structure["elements"].append(obj)
                structure["pattern"] += "O"
            
            return structure if structure["pattern"] else None
            
        except Exception:
            return None
    
    def _detect_temporal_reordering(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Detect temporal/spatial expression reordering"""
        temporal_expressions = [
            r'\b(hoje|ontem|amanhã|sempre|nunca|agora|então|depois|antes|durante)\b',
            r'\b(em \d{4}|no \w+|na \w+|desde|até|por \w+ tempo)\b',
            r'\b(inicialmente|posteriormente|finalmente|primeiro|segundo)\b'
        ]
        
        reorderings = []
        
        for pattern in temporal_expressions:
            src_matches = [(m.group(), m.start()) for m in re.finditer(pattern, source_text, re.IGNORECASE)]
            tgt_matches = [(m.group(), m.start()) for m in re.finditer(pattern, target_text, re.IGNORECASE)]
            
            for src_expr, src_pos in src_matches:
                for tgt_expr, tgt_pos in tgt_matches:
                    if src_expr.lower() == tgt_expr.lower():
                        src_rel_pos = src_pos / len(source_text) if source_text else 0
                        tgt_rel_pos = tgt_pos / len(target_text) if target_text else 0
                        
                        # Check if temporal expression moved significantly
                        if abs(src_rel_pos - tgt_rel_pos) > 0.4:
                            reorderings.append({
                                "expression": src_expr,
                                "src_position": "início" if src_rel_pos < 0.3 else "meio" if src_rel_pos < 0.7 else "fim",
                                "tgt_position": "início" if tgt_rel_pos < 0.3 else "meio" if tgt_rel_pos < 0.7 else "fim",
                                "position_change": abs(src_rel_pos - tgt_rel_pos)
                            })
                        break
        
        return reorderings[:3]  # Limit results
    
    def _find_contextual_glosses(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Find contextual glosses and definitions for EXP+"""
        import re
        
        # Look for definition patterns: "X, que é Y", "X (Y)", "X: Y", etc.
        gloss_patterns = [
            r'(\w+),?\s*que\s+(?:é|são|significa|representam?)\s+([^,.]+)',
            r'(\w+)\s*\(([^)]+)\)',
            r'(\w+):\s*([^,.]+)',
            r'(\w+),?\s*ou\s+seja,?\s*([^,.]+)',
            r'(\w+),?\s*isto\s+é,?\s*([^,.]+)'
        ]
        
        glosses = []
        for pattern in gloss_patterns:
            matches = re.finditer(pattern, target_text, re.IGNORECASE)
            for match in matches:
                # Only include if this gloss pattern is not in source
                if match.group(0) not in source_text:
                    glosses.append({
                        "type": "contextual_gloss",
                        "term": match.group(1),
                        "definition": match.group(2),
                        "full_match": match.group(0),
                        "quality_score": 0.75
                    })
        
        return glosses

    def _find_example_additions(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Find example additions in target text"""
        example_markers = [
            "por exemplo", "como por exemplo", "como", "tal como",
            "a saber", "nomeadamente", "designadamente"
        ]
        
        examples = []
        for marker in example_markers:
            # Find instances in target that aren't in source
            src_count = source_text.lower().count(marker)
            tgt_count = target_text.lower().count(marker)
            
            if tgt_count > src_count:
                # Extract the example text after the marker
                import re
                pattern = rf"{re.escape(marker)}\s*[,:]?\s*([^.!?;]+)"
                matches = re.finditer(pattern, target_text, re.IGNORECASE)
                
                for match in matches:
                    if match.group(0) not in source_text:
                        examples.append({
                            "marker": marker,
                            "example_text": match.group(1)[:60] + ("..." if len(match.group(1)) > 60 else ""),
                            "full_match": match.group(0)
                        })
        
        return examples
    
    def _find_clarifying_additions(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Find clarifying phrase additions"""
        clarifying_markers = [
            "isto é", "ou seja", "quer dizer", "em outras palavras",
            "melhor dizendo", "por outras palavras", "vale dizer"
        ]
        
        clarifications = []
        for marker in clarifying_markers:
            src_count = source_text.lower().count(marker)
            tgt_count = target_text.lower().count(marker)
            
            if tgt_count > src_count:
                # Extract clarification after marker
                import re
                pattern = rf"{re.escape(marker)}\s*[,:]?\s*([^.!?;]+)"
                matches = re.finditer(pattern, target_text, re.IGNORECASE)
                
                for match in matches:
                    if match.group(0) not in source_text:
                        clarifications.append({
                            "marker": marker,
                            "clarification": match.group(1)[:60] + ("..." if len(match.group(1)) > 60 else ""),
                            "full_match": match.group(0)
                        })
        
        return clarifications
    
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
    
    def _extract_citation_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Extract citation patterns from text"""
        import re
        
        citations = []
        
        # Common citation patterns
        citation_patterns = [
            r'\([A-Z][a-z]+,?\s+\d{4}\)',  # (Author, Year)
            r'\([A-Z]+\s*\d{4}\)',         # (AUTHOR Year)
            r'\[\d+\]',                    # [1]
            r'\(\d+\)',                    # (1)
            r'\([A-Za-z]+\s+et\s+al\.?,?\s+\d{4}\)'  # (Author et al., Year)
        ]
        
        for pattern in citation_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                citations.append({
                    "content": match.group(0),
                    "position": match.start(),
                    "pattern_type": "citation"
                })
        
        return citations
    
    def _extract_appositive_expressions(self, text: str) -> List[Dict[str, Any]]:
        """Extract appositive expressions (explanatory phrases set off by commas)"""
        import re
        
        appositives = []
        
        # Look for patterns like "Name, explanation, continued text"
        appositive_pattern = r',\s+([^,]{10,80}),\s+'
        
        matches = re.finditer(appositive_pattern, text)
        for match in matches:
            appositive_content = match.group(1).strip()
            
            # Check if it looks like an appositive (explanatory)
            if (not appositive_content.lower().startswith(('que', 'quando', 'onde', 'como')) and
                len(appositive_content.split()) >= 2):
                
                appositives.append({
                    "content": appositive_content,
                    "position": match.start(),
                    "full_match": match.group(0)
                })
        
        return appositives
    
    def _detect_insertion_integration(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Detect insertions that were integrated into the main text"""
        integrations = []
        
        # Find parenthetical content in source that appears integrated in target
        src_parens = self._extract_parenthetical_expressions(source_text)
        
        for paren in src_parens:
            paren_content = paren['content']
            
            # Check if this content appears in target without parentheses
            if (paren_content in target_text and 
                f"({paren_content})" not in target_text and
                len(paren_content.split()) >= 2):
                
                integrations.append({
                    "original_form": f"texto ({paren_content})",
                    "integrated_form": f"texto {paren_content}",
                    "type": "parenthetical_integration",
                    "content": paren_content
                })
        
        # Find bracket content in source that appears integrated in target
        src_brackets = self._extract_bracket_expressions(source_text)
        
        for bracket in src_brackets:
            bracket_content = bracket['content']
            
            # Check if this content appears in target without brackets
            if (bracket_content in target_text and 
                f"[{bracket_content}]" not in target_text and
                len(bracket_content.split()) >= 2):
                
                integrations.append({
                    "original_form": f"texto [{bracket_content}]",
                    "integrated_form": f"texto {bracket_content}",
                    "type": "bracket_integration",
                    "content": bracket_content
                })
        
        return integrations[:3]  # Limit results
    
    def _detect_perspective_shifts(self, src_sentences: List[str], tgt_sentences: List[str]) -> List[Dict[str, Any]]:
        """Detect sentence-level perspective shifts with very high semantic similarity but low lexical overlap"""
        shifts = []
        
        for src_sent in src_sentences[:3]:  # Limit for performance
            if len(self._tokenize_text(src_sent)) < 5:
                continue
                
            best_match = None
            best_similarity = 0.0
            
            for tgt_sent in tgt_sentences:
                if len(self._tokenize_text(tgt_sent)) < 5:
                    continue
                    
                # Calculate semantic similarity
                if _model_cache.get('semantic_model'):
                    try:
                        embeddings = _model_cache['semantic_model'].encode([src_sent, tgt_sent], convert_to_tensor=True)
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
                
                # MOD+ criteria: very high semantic similarity, low lexical overlap
                if (similarity > 0.85 and word_overlap < 0.3 and similarity > best_similarity):
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
    
    def _detect_voice_perspective_changes(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Detect voice and agency perspective changes (active/passive, personal/impersonal)"""
        changes = []
        
        # Pattern 1: Active to passive voice changes
        active_patterns = [
            r'(\w+)\s+(fez|faz|criou|criará|desenvolveu|desenvolve)\s+(\w+)',
            r'(\w+)\s+(disse|diz|afirmou|afirma|declarou|declara)\s+',
            r'(\w+)\s+(escreveu|escreve|publicou|publica)\s+'
        ]
        
        passive_patterns = [
            r'(\w+)\s+(foi|é|será)\s+(feito|feita|criado|criada|desenvolvido|desenvolvida)',
            r'(foi|é|será)\s+(dito|dita|afirmado|afirmada|declarado|declarada)',
            r'(\w+)\s+(foi|é|será)\s+(escrito|escrita|publicado|publicada)'
        ]
        
        # Check for active to passive transformation
        src_has_active = any(re.search(pattern, source_text, re.IGNORECASE) for pattern in active_patterns)
        tgt_has_passive = any(re.search(pattern, target_text, re.IGNORECASE) for pattern in passive_patterns)
        
        if src_has_active and tgt_has_passive and not any(re.search(pattern, source_text, re.IGNORECASE) for pattern in passive_patterns):
            changes.append({
                "source_pattern": "voz ativa (sujeito executa ação)",
                "target_pattern": "voz passiva (ação executada no sujeito)",
                "transformation": "active_to_passive"
            })
        
        # Pattern 2: Passive to active voice changes
        src_has_passive = any(re.search(pattern, source_text, re.IGNORECASE) for pattern in passive_patterns)
        tgt_has_active = any(re.search(pattern, target_text, re.IGNORECASE) for pattern in active_patterns)
        
        if src_has_passive and tgt_has_active and not any(re.search(pattern, source_text, re.IGNORECASE) for pattern in active_patterns):
            changes.append({
                "source_pattern": "voz passiva (ação executada no sujeito)",
                "target_pattern": "voz ativa (sujeito executa ação)",
                "transformation": "passive_to_active"
            })
        
        # Pattern 3: Personal to impersonal perspective
        personal_pronouns = ['eu', 'nós', 'você', 'vocês', 'meu', 'nosso', 'seu']
        impersonal_markers = ['pode-se', 'deve-se', 'é possível', 'é necessário', 'é importante']
        
        src_personal = any(pronoun in source_text.lower() for pronoun in personal_pronouns)
        tgt_impersonal = any(marker in target_text.lower() for marker in impersonal_markers)
        
        if src_personal and tgt_impersonal:
            changes.append({
                "source_pattern": "perspectiva pessoal (pronomes pessoais)",
                "target_pattern": "perspectiva impessoal (construções impessoais)",
                "transformation": "personal_to_impersonal"
            })
        
        return changes
    
    def _detect_modal_perspective_changes(self, source_text: str, target_text: str) -> List[Dict[str, Any]]:
        """Detect modal and temporal perspective changes"""
        changes = []
        
        # Modal patterns for certainty levels
        certain_modals = ['certamente', 'definitivamente', 'com certeza', 'é fato que', 'é certo que']
        uncertain_modals = ['talvez', 'possivelmente', 'pode ser que', 'é possível que', 'provavelmente']
        necessity_modals = ['deve', 'precisa', 'é necessário', 'é obrigatório', 'tem que']
        possibility_modals = ['pode', 'poderia', 'é possível', 'seria possível', 'talvez']
        
        # Check for certainty perspective changes
        src_certain = any(modal in source_text.lower() for modal in certain_modals)
        tgt_uncertain = any(modal in target_text.lower() for modal in uncertain_modals)
        
        if src_certain and tgt_uncertain:
            changes.append({
                "source_modality": "alta certeza",
                "target_modality": "incerteza/possibilidade",
                "description": "mudança de perspectiva: certeza para incerteza"
            })
        
        # Check for necessity to possibility changes
        src_necessity = any(modal in source_text.lower() for modal in necessity_modals)
        tgt_possibility = any(modal in target_text.lower() for modal in possibility_modals)
        
        if src_necessity and tgt_possibility:
            changes.append({
                "source_modality": "necessidade/obrigação",
                "target_modality": "possibilidade/opção",
                "description": "mudança de perspectiva: obrigação para possibilidade"
            })
        
        # Temporal perspective changes
        past_markers = ['foi', 'eram', 'havia', 'aconteceu', 'ocorreu']
        present_markers = ['é', 'são', 'há', 'acontece', 'ocorre']
        future_markers = ['será', 'serão', 'haverá', 'acontecerá', 'ocorrerá']
        
        src_past = any(marker in source_text.lower() for marker in past_markers)
        tgt_present = any(marker in target_text.lower() for marker in present_markers)
        
        if src_past and tgt_present and not any(marker in source_text.lower() for marker in present_markers):
            changes.append({
                "source_modality": "perspectiva passada",
                "target_modality": "perspectiva presente",
                "description": "mudança temporal: passado para presente"
            })
        
        return changes

# Global model cache for performance
_model_cache = {
    'nlp': None,
    'semantic_model': None,
    'initialized': False
}

def _initialize_models():
    """Initialize models once and cache them globally"""
    global _model_cache
    
    if _model_cache['initialized']:
        return _model_cache['nlp'], _model_cache['semantic_model']
    
    # Try to load spaCy model
    try:
        _model_cache['nlp'] = spacy.load("pt_core_news_sm")
        logging.info("✅ spaCy Portuguese model loaded successfully")
    except (OSError, ImportError) as e:
        logging.warning(f"⚠️ spaCy model not available: {e}")
        _model_cache['nlp'] = None
    
    # Try to load lightweight sentence transformer model
    try:
        # Use the fast, lightweight multilingual model recommended in hybrid approach
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        logging.info(f"🚀 Loading lightweight semantic model: {model_name}")
        _model_cache['semantic_model'] = SentenceTransformer(model_name)
        logging.info("✅ Lightweight SentenceTransformer model loaded successfully")
    except Exception as e:
        logging.warning(f"⚠️ SentenceTransformer model not available: {e}")
        logging.info("📝 Falling back to heuristic-only detection")
        _model_cache['semantic_model'] = None
    
    _model_cache['initialized'] = True
    return _model_cache['nlp'], _model_cache['semantic_model']


class StrategyDetector:
    """Enhanced class for detecting simplification strategies using cascade architecture"""

    def __init__(self):
        # Use cached models for performance
        self.nlp, self.semantic_model = _initialize_models()

        # Initialize cascade orchestrator
        self.cascade_orchestrator = CascadeOrchestrator(
            nlp_model=self.nlp,
            semantic_model=self.semantic_model,
            enable_performance_logging=True
        )

        # Special flags for OM+ and PRO+
        self.enable_om_detection = False  # Disabled by default as per documentation
        self.pro_tag_allowed = False  # PRO+ is for human annotation only
    
    def identify_strategies(self, source_text: str, target_text: str) -> List[SimplificationStrategy]:
        """Enhanced strategy identification using cascade architecture"""
        if not source_text or not target_text:
            return []

        try:
            # Use cascade orchestrator for improved performance and modularity
            strategies = self.cascade_orchestrator.detect_strategies(source_text, target_text)
            logging.info(f"✅ Detected {len(strategies)} strategies using cascade architecture")

            return strategies

        except Exception as e:
            logging.error(f"❌ Error in cascade strategy detection: {e}")
            # Fallback to original heuristic detection
            return self._fallback_detection(source_text, target_text)
    
    def _evidence_to_strategy(self, evidence: StrategyEvidence) -> Optional[SimplificationStrategy]:
        """Convert StrategyEvidence to SimplificationStrategy"""
        strategy_info = STRATEGY_DESCRIPTIONS.get(evidence.strategy_code, {})
        
        # Convert examples to StrategyExample objects
        exemplos_objs = []
        for ex in evidence.examples:
            if isinstance(ex, dict):
                exemplos_objs.append(
                    StrategyExample(
                        original=ex.get("original", ""),
                        simplified=ex.get("simplified", ex.get("fragmentado", ""))
                    )
                )
        
        # Ensure impacto is a valid literal
        impacto_literal = evidence.impact_level if evidence.impact_level in ("baixo", "médio", "alto") else "médio"
        
        return SimplificationStrategy(
            sigla=evidence.strategy_code,
            nome=strategy_info.get("nome", "Estratégia Desconhecida"),
            descricao=strategy_info.get("descricao", ""),
            tipo=strategy_info.get("tipo", SimplificationStrategyType.SEMANTIC),
            impacto=impacto_literal,
            confianca=float(evidence.confidence),
            exemplos=exemplos_objs
        )
    
    def _fallback_detection(self, source_text: str, target_text: str) -> List[SimplificationStrategy]:
        """Fallback to original heuristic detection if enhanced approach fails"""
        logging.info("🔄 Using fallback heuristic detection")
        strategies = []
        
        # Quick heuristic checks
        quick_strategies = self._detect_quick_strategies(source_text, target_text)
        strategies.extend(quick_strategies)
        
        return strategies
    
    def _detect_quick_strategies(self, source_text: str, target_text: str) -> List[SimplificationStrategy]:
        """Fast heuristic-based strategy detection (no ML models)"""
        strategies = []
        
        # SL+ (Adequação de Vocabulário) - Quick word length check
        if self._has_lexical_simplification(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="SL+",
                impacto="alto" if self._get_lexical_simplification_impact(source_text, target_text) > 0.7 else "médio",
                confianca=0.85,
                exemplos=self._find_lexical_substitutions(source_text, target_text)
            ))
        
        # RP+ (Fragmentação Sintática) - Quick sentence count check
        if self._has_sentence_fragmentation(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="RP+",
                impacto="alto" if self._get_sentence_fragmentation_impact(source_text, target_text) > 0.6 else "médio",
                confianca=0.8,
                exemplos=self._find_sentence_splits(source_text, target_text)
            ))
        
        # RF+ (Reescrita Global) - Quick lexical overlap check
        if self._has_global_rewriting(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="RF+",
                impacto="alto",
                confianca=0.8,
                exemplos=self._find_global_rewriting_examples(source_text, target_text)
            ))
        
        return strategies
    
    def _detect_ml_strategies(self, source_text: str, target_text: str) -> List[SimplificationStrategy]:
        """ML-based strategy detection (more expensive)"""
        strategies = []
        
        # Only check a few key strategies that need semantic analysis
        # MOD+ (Reinterpretação Perspectiva) - Requires semantic similarity
        if self._has_perspective_reinterpretation(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="MOD+",
                impacto="alto",
                confianca=0.85,
                exemplos=self._find_perspective_shifts(source_text, target_text)
            ))
        
        # AS+ (Alteração de Sentido) - Requires semantic similarity
        if self._has_meaning_change(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="AS+",
                impacto="médio",
                confianca=0.7,
                exemplos=self._find_meaning_change_examples(source_text, target_text)
            ))
        
        return strategies
    
    # --- Placeholder/heuristic methods for missing strategies ---
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using the lightweight model"""
        if not self.semantic_model:
            # Fallback to simple word overlap when no model available
            words1 = set(self._tokenize_text(text1.lower()))
            words2 = set(self._tokenize_text(text2.lower()))
            overlap = len(words1.intersection(words2))
            union = len(words1.union(words2))
            return overlap / max(union, 1)
        
        try:
            # Use the fast MiniLM model for semantic similarity
            embeddings = self.semantic_model.encode([text1, text2], convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
            return max(0.0, min(1.0, similarity))  # Ensure value is between 0 and 1
        except Exception as e:
            logging.warning(f"Error calculating semantic similarity: {e}")
            # Fallback to word overlap
            words1 = set(self._tokenize_text(text1.lower()))
            words2 = set(self._tokenize_text(text2.lower()))
            overlap = len(words1.intersection(words2))
            union = len(words1.union(words2))
            return overlap / max(union, 1)

    def _has_meaning_change(self, source_text, target_text):
        # Use optimized semantic similarity calculation
        similarity = self._calculate_semantic_similarity(source_text, target_text)
        return similarity < 0.7
    def _find_meaning_change_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_positional_reorganization(self, source_text, target_text):
        # Heuristic: major sentence order change
        src_sents = self._split_into_sentences(source_text)
        tgt_sents = self._split_into_sentences(target_text)
        return src_sents != tgt_sents and len(src_sents) == len(tgt_sents)
    def _find_positional_reorganization_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_explicitness(self, source_text, target_text):
        # Heuristic: target longer and contains e.g. 'por exemplo', 'isto é'
        return len(target_text) > len(source_text) * 1.1 and any(x in target_text.lower() for x in ["por exemplo", "isto é", "ou seja"])
    def _find_explicitness_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_insertion_handling(self, source_text, target_text):
        # Heuristic: parenthetical or inserted phrases removed or moved
        return "(" in source_text and "(" not in target_text
    def _find_insertion_handling_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_title_optimization(self, source_text, target_text):
        # Heuristic: title present in target but not in source
        return target_text.strip().endswith(":") or target_text.strip().istitle()
    def _find_title_optimization_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_selective_omission(self, source_text, target_text):
        # Heuristic: target much shorter than source
        return len(target_text) < len(source_text) * 0.7
    def _find_selective_omission_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_semantic_deviation(self, source_text, target_text):
        # Use optimized semantic similarity calculation
        similarity = self._calculate_semantic_similarity(source_text, target_text)
        return similarity < 0.5
    def _find_semantic_deviation_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_global_rewriting(self, source_text, target_text):
        # Heuristic: target is a full rewrite (low lexical overlap)
        src_words = set(self._tokenize_text(source_text))
        tgt_words = set(self._tokenize_text(target_text))
        overlap = len(src_words.intersection(tgt_words)) / max(len(src_words), 1)
        return overlap < 0.3
    def _find_global_rewriting_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_content_structuring(self, source_text, target_text):
        # Heuristic: target contains more paragraphs or connectives
        return "\n" in target_text or any(x in target_text.lower() for x in ["primeiro", "depois", "em seguida", "por fim"])
    def _find_content_structuring_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_referential_clarity(self, source_text, target_text):
        # Heuristic: pronouns replaced by nouns
        pronouns = ["ele", "ela", "eles", "elas", "isso", "isto", "aquele", "aquela"]
        src_pronouns = any(p in source_text.lower() for p in pronouns)
        tgt_pronouns = any(p in target_text.lower() for p in pronouns)
        return src_pronouns and not tgt_pronouns
    def _find_referential_clarity_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _has_voice_change(self, source_text, target_text):
        # Heuristic: passive/active voice change (simple check)
        return ("foi" in source_text and "foi" not in target_text) or ("foi" not in source_text and "foi" in target_text)
    def _find_voice_change_examples(self, source_text, target_text):
        return [{"original": source_text, "simplified": target_text}]

    def _create_strategy(self, sigla: str, impacto: str, confianca: float, exemplos: List[Dict[str, str]]) -> SimplificationStrategy:
        """Helper to create a SimplificationStrategy object"""
        strategy_info = STRATEGY_DESCRIPTIONS.get(sigla, {})
        # Ensure impacto is a Literal
        # Cast impacto to Literal type
        impacto_literal = impacto if impacto in ("baixo", "médio", "alto") else "médio"
        # Convert exemplos to StrategyExample objects
        exemplos_objs = []
        for ex in exemplos:
            if isinstance(ex, dict):
                exemplos_objs.append(
                    StrategyExample(
                        original=ex.get("original", ""),
                        simplified=ex.get("simplified", ex.get("fragmentado", ""))
                    )
                )
            elif "StrategyExample" in str(type(ex)):
                exemplos_objs.append(ex)
        return SimplificationStrategy(
            sigla=sigla,
            nome=strategy_info.get("nome", "Estratégia Desconhecida"),
            descricao=strategy_info.get("descricao", ""),
            tipo=strategy_info.get("tipo", SimplificationStrategyType.SEMANTIC),
            impacto=impacto_literal,
            confianca=float(confianca),
            exemplos=exemplos_objs
        )

    def _has_lexical_simplification(self, source_text, target_text):
        """SL+ (Adequação de Vocabulário) detection"""
        # Basic check: average word length reduction
        source_avg_len = float(np.mean([len(w) for w in self._tokenize_text(source_text)])) if source_text else 0.0
        target_avg_len = float(np.mean([len(w) for w in self._tokenize_text(target_text)])) if target_text else 0.0
        
        if target_avg_len > 0 and source_avg_len > target_avg_len * 1.05:
            return True
            
        # Check for simpler synonyms using frequency (placeholder)
        return False

    def _get_lexical_simplification_impact(self, source_text, target_text):
        """Calculate impact of lexical simplification"""
        source_avg_len = np.mean([len(w) for w in self._tokenize_text(source_text)]) if source_text else 0
        target_avg_len = np.mean([len(w) for w in self._tokenize_text(target_text)]) if target_text else 0
        
        if source_avg_len == 0:
            return 0.0
            
        reduction_ratio = (source_avg_len - target_avg_len) / source_avg_len
        return min(1.0, max(0.0, float(reduction_ratio) * 2.0))

    def _find_lexical_substitutions(self, source_text, target_text):
        """Find examples of lexical substitutions (for SL+)"""
        # This is a simplified placeholder
        return [{"original": "e.g., 'complexo'", "simplified": "'simples'"}]

    def _has_sentence_fragmentation(self, source_text, target_text):
        """RP+ (Fragmentação Sintática) detection"""
        source_sentences = self._split_into_sentences(source_text)
        target_sentences = self._split_into_sentences(target_text)
        
        if len(target_sentences) > len(source_sentences):
            if len(target_text) > len(source_text) * 0.6:
                return True
        
        return False

    def _get_sentence_fragmentation_impact(self, source_text, target_text):
        """Calculate impact of sentence fragmentation"""
        source_sentences = self._split_into_sentences(source_text)
        target_sentences = self._split_into_sentences(target_text)
        
        if not source_sentences:
            return 0.0
            
        increase_ratio = (len(target_sentences) - len(source_sentences)) / len(source_sentences)
        return min(1.0, max(0.0, increase_ratio * 0.7))

    def _find_sentence_splits(self, source_text, target_text):
        """Find examples of sentence splits (for RP+) - Optimized for performance"""
        try:
            source_sentences = self._split_into_sentences(source_text)
            target_sentences = self._split_into_sentences(target_text)
            
            if not source_sentences or not target_sentences:
                return []
            
            examples = []
            
            # Performance optimization: limit to first few sentences
            MAX_SENTENCES_TO_CHECK = 3
            
            for src_sent in source_sentences[:MAX_SENTENCES_TO_CHECK]:
                if len(src_sent.split()) < 15:
                    continue
                
                potential_fragments = []
                best_coverage = 0
                src_words = set(self._tokenize_text(src_sent))
                
                for tgt_sent in target_sentences:
                    tgt_words = set(self._tokenize_text(tgt_sent))
                    overlap = len(src_words.intersection(tgt_words))
                    
                    if overlap > 3 and len(tgt_sent.split()) < len(src_sent.split()) * 0.8:
                        potential_fragments.append(tgt_sent)
                        best_coverage += overlap
                
                if len(potential_fragments) > 1 and best_coverage > len(src_words) * 0.6:
                    examples.append({
                        "original": src_sent,
                        "fragmentado": " [...] ".join(potential_fragments[:3])
                    })
                    
                # Early stopping: max 1 example to avoid timeout
                if len(examples) >= 1:
                    break
            
            return examples
        
        except (ValueError, RuntimeError) as e:
            logging.warning(f"Error finding sentence splits: {e}")
            return []

    def _has_perspective_reinterpretation(self, source_text, target_text):
        """MOD+ (Reinterpretação Perspectiva) detection using BERTimbau"""
        perspective_shifts = self._find_perspective_shifts(source_text, target_text)
        return len(perspective_shifts) > 0

    def _find_perspective_shifts(self, source_text, target_text):
        """Find examples of perspective shifts (for MOD+) - Optimized for performance"""
        if not self.semantic_model:
            return []
            
        try:
            source_sentences = self._split_into_sentences(source_text)
            target_sentences = self._split_into_sentences(target_text)
            
            if not source_sentences or not target_sentences:
                return []
            
            # Performance optimization: limit sentence comparisons
            MAX_SENTENCES = 5  # Limit to first 5 sentences to avoid timeout
            source_sentences = source_sentences[:MAX_SENTENCES]
            target_sentences = target_sentences[:MAX_SENTENCES]
            
            perspective_shifts = []
            
            for src_sent in source_sentences:
                if len(src_sent.split()) < 5:
                    continue
                    
                best_match = None
                best_score = 0.0
                
                for tgt_sent in target_sentences:
                    if len(tgt_sent.split()) < 5:
                        continue
                        
                    # Use optimized semantic similarity calculation
                    sem_sim = self._calculate_semantic_similarity(src_sent, tgt_sent)
                    
                    src_words = set(self._tokenize_text(src_sent))
                    tgt_words = set(self._tokenize_text(tgt_sent))
                    lex_overlap = len(src_words.intersection(tgt_words)) / max(len(src_words.union(tgt_words)), 1)
                    
                    if sem_sim > 0.75 and lex_overlap < 0.5 and sem_sim > best_score:
                        best_score = sem_sim
                        best_match = (tgt_sent, sem_sim, lex_overlap)
                
                if best_match:
                    perspective_shifts.append({
                        "original": src_sent,
                        "simplified": best_match[0]
                    })
                    
                # Early stopping: max 2 examples to avoid timeout
                if len(perspective_shifts) >= 2:
                    break
            
            return perspective_shifts
            
        except (ValueError, RuntimeError) as e:
            logging.warning(f"Error finding perspective shifts: {e}")
            return []

    def _split_into_sentences(self, text):
        """Split text into sentences using spaCy if available, or simple heuristics"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]
        else:
            return re.split(r'(?<=[.!?])\s+', text)

    def _tokenize_text(self, text):
        """Tokenize text into words, removing punctuation and lowercasing"""
        if self.nlp:
            doc = self.nlp(text)
            return [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
        else:
            return re.findall(r'\b\w+\b', text.lower())

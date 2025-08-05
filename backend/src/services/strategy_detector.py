"""
Strategy Detection Implementation for NET-EST

This file contains example implementation of strategy detection based on
the "Tabela de Estratégias de Simplificação Textual" document.
"""

from typing import List, Dict, Optional
import re
from ..models.strategy_models import SimplificationStrategy, SimplificationStrategyType, STRATEGY_DESCRIPTIONS, StrategyExample
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer, util
import logging

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
    """Class for detecting simplification strategies in text pairs"""
    
    def __init__(self):
        # Use cached models for performance
        self.nlp, self.semantic_model = _initialize_models()
        
        # Special flags for OM+ and PRO+
        self.enable_om_detection = False  # Disabled by default as per documentation
        self.pro_tag_allowed = False  # PRO+ is for human annotation only
    
    def identify_strategies(self, source_text: str, target_text: str) -> List[SimplificationStrategy]:
        """Identify simplification strategies used in text transformation"""
        strategies = []
        if not source_text or not target_text:
            return strategies
        
        # Performance optimization: limit text size for analysis
        MAX_TEXT_LENGTH = 5000  # Limit to 5000 chars for performance
        if len(source_text) > MAX_TEXT_LENGTH:
            logging.info(f"📊 Large text detected ({len(source_text)} chars), using first {MAX_TEXT_LENGTH} chars for analysis")
            source_text = source_text[:MAX_TEXT_LENGTH]
        
        if len(target_text) > MAX_TEXT_LENGTH:
            logging.info(f"📊 Large target text detected ({len(target_text)} chars), using first {MAX_TEXT_LENGTH} chars for analysis")
            target_text = target_text[:MAX_TEXT_LENGTH]
        
        # Create docs once for efficiency
        source_doc = self.nlp(source_text) if self.nlp else None
        target_doc = self.nlp(target_text) if self.nlp else None

        # Quick heuristic checks first (no ML models needed)
        quick_strategies = self._detect_quick_strategies(source_text, target_text)
        strategies.extend(quick_strategies)
        
        # Only run expensive ML-based checks if we have fewer than 3 strategies
        if len(strategies) < 3 and self.semantic_model:
            ml_strategies = self._detect_ml_strategies(source_text, target_text)
            strategies.extend(ml_strategies)
        
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

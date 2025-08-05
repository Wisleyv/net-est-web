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
    
    # Try to load sentence transformer with timeout
    try:
        # Use a smaller, faster model that's more likely to be available
        # or disable ML features entirely for now
        logging.info("⚠️ SentenceTransformer disabled for performance - using heuristic detection only")
        _model_cache['semantic_model'] = None
        # _model_cache['semantic_model'] = SentenceTransformer("neuralmind/bert-base-portuguese-cased")
        # logging.info("✅ SentenceTransformer model loaded successfully")
    except Exception as e:
        logging.warning(f"⚠️ SentenceTransformer model not available: {e}")
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
        
        # SL+ (Adequação de Vocabulário) - Word complexity and length analysis
        if self._has_lexical_simplification(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="SL+",
                impacto="alto" if self._get_lexical_simplification_impact(source_text, target_text) > 0.7 else "médio",
                confianca=0.85,
                exemplos=self._find_lexical_substitutions(source_text, target_text)
            ))
        
        # RP+ (Fragmentação Sintática) - Sentence count and complexity
        if self._has_sentence_fragmentation(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="RP+",
                impacto="alto" if self._get_sentence_fragmentation_impact(source_text, target_text) > 0.6 else "médio",
                confianca=0.8,
                exemplos=self._find_sentence_splits(source_text, target_text)
            ))
        
        # EXP+ (Explicitação e Detalhamento) - Target longer with explanatory content
        if self._has_explicitation(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="EXP+",
                impacto="médio",
                confianca=0.75,
                exemplos=self._find_explicitation_examples(source_text, target_text)
            ))
        
        # DL+ (Reorganização Posicional) - Word order changes
        if self._has_positional_reorganization(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="DL+",
                impacto="médio",
                confianca=0.7,
                exemplos=self._find_word_order_changes(source_text, target_text)
            ))
        
        # IN+ (Manejo de Inserções) - Parentheses, commas, insertions
        if self._has_insertion_management(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="IN+",
                impacto="médio",
                confianca=0.75,
                exemplos=self._find_insertion_changes(source_text, target_text)
            ))
        
        # TA+ (Clareza Referencial) - Pronoun and reference changes
        if self._has_referential_clarity(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="TA+",
                impacto="médio",
                confianca=0.7,
                exemplos=self._find_referential_changes(source_text, target_text)
            ))
        
        # MV+ (Alteração da Voz Verbal) - Active/passive voice
        if self._has_voice_change(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="MV+",
                impacto="médio",
                confianca=0.75,
                exemplos=self._find_voice_changes(source_text, target_text)
            ))
        
        # RD+ (Estruturação de Conteúdo) - Paragraph and structure changes
        if self._has_content_restructuring(source_text, target_text):
            strategies.append(self._create_strategy(
                sigla="RD+",
                impacto="alto",
                confianca=0.8,
                exemplos=self._find_structure_changes(source_text, target_text)
            ))
        
        # RF+ (Reescrita Global) - Comprehensive rewriting
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
    def _has_meaning_change(self, source_text, target_text):
        # Heuristic: semantic similarity below threshold
        if self.semantic_model:
            src_emb = self.semantic_model.encode(source_text, convert_to_tensor=True)
            tgt_emb = self.semantic_model.encode(target_text, convert_to_tensor=True)
            sim = util.pytorch_cos_sim(src_emb, tgt_emb).item()
            return sim < 0.7
        return False
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
        # Heuristic: semantic similarity very low
        if self.semantic_model:
            src_emb = self.semantic_model.encode(source_text, convert_to_tensor=True)
            tgt_emb = self.semantic_model.encode(target_text, convert_to_tensor=True)
            sim = util.pytorch_cos_sim(src_emb, tgt_emb).item()
            return sim < 0.5
        return False
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
                        
                    src_emb = self.semantic_model.encode(src_sent, convert_to_tensor=True)
                    tgt_emb = self.semantic_model.encode(tgt_sent, convert_to_tensor=True)
                    sem_sim = util.pytorch_cos_sim(src_emb, tgt_emb).item()
                    
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

    # === NEW STRATEGY DETECTION METHODS ===
    
    def _has_explicitation(self, source_text: str, target_text: str) -> bool:
        """EXP+ - Detect explicitation by looking for expansion and clarification"""
        source_words = len(source_text.split())
        target_words = len(target_text.split())
        
        # Target should be significantly longer (expansion)
        if target_words <= source_words:
            return False
            
        expansion_ratio = target_words / source_words
        return expansion_ratio > 1.2  # 20% longer or more
    
    def _find_explicitation_examples(self, source_text: str, target_text: str) -> List[Dict]:
        """Find examples of explicitation"""
        examples = []
        
        # Simple heuristic: look for added explanatory phrases
        source_sents = self._split_into_sentences(source_text)
        target_sents = self._split_into_sentences(target_text)
        
        for i, (src, tgt) in enumerate(zip(source_sents, target_sents)):
            if len(tgt.split()) > len(src.split()) * 1.3:  # Significant expansion
                examples.append({
                    "original": src.strip(),
                    "explicitado": tgt.strip()
                })
                if len(examples) >= 2:  # Limit examples
                    break
        
        return examples

    def _has_positional_reorganization(self, source_text: str, target_text: str) -> bool:
        """DL+ - Detect word order changes"""
        source_words = self._tokenize_text(source_text)
        target_words = self._tokenize_text(target_text)
        
        # Check for significant word order differences
        source_set = set(source_words)
        target_set = set(target_words)
        
        # Must have significant vocabulary overlap but different order
        overlap = len(source_set.intersection(target_set))
        total_unique = len(source_set.union(target_set))
        
        if total_unique == 0:
            return False
            
        overlap_ratio = overlap / total_unique
        return overlap_ratio > 0.6  # Good vocabulary overlap suggests reordering
    
    def _find_word_order_changes(self, source_text: str, target_text: str) -> List[Dict]:
        """Find examples of positional reorganization"""
        return [{
            "original": "Estrutura original da frase",
            "reorganizado": "Estrutura reorganizada para maior clareza"
        }]
    
    def _has_insertion_management(self, source_text: str, target_text: str) -> bool:
        """IN+ - Detect management of insertions (parentheses, commas, etc.)"""
        # Count parentheses, commas, and other insertion markers
        source_insertions = source_text.count('(') + source_text.count(',') + source_text.count('—')
        target_insertions = target_text.count('(') + target_text.count(',') + target_text.count('—')
        
        # Significant reduction in insertion markers
        return source_insertions > target_insertions and source_insertions >= 2
    
    def _find_insertion_changes(self, source_text: str, target_text: str) -> List[Dict]:
        """Find examples of insertion management"""
        return [{
            "original": "Texto com inserções (explicações) e elementos intercalados",
            "simplificado": "Texto com estrutura mais fluida e direta"
        }]
    
    def _has_referential_clarity(self, source_text: str, target_text: str) -> bool:
        """TA+ - Detect pronoun and reference clarification"""
        # Count pronouns and potential ambiguous references
        pronouns = ['ele', 'ela', 'eles', 'elas', 'isso', 'isto', 'aquilo', 'esta', 'esta', 'esse', 'essa']
        
        source_pronouns = sum(source_text.lower().count(p) for p in pronouns)
        target_pronouns = sum(target_text.lower().count(p) for p in pronouns)
        
        # Reduction in pronouns suggests clarification
        return source_pronouns > target_pronouns and source_pronouns >= 2
    
    def _find_referential_changes(self, source_text: str, target_text: str) -> List[Dict]:
        """Find examples of referential clarity improvements"""
        return [{
            "original": "Ele disse que isso era importante",
            "clarificado": "O professor disse que o conceito era importante"
        }]
    
    def _has_voice_change(self, source_text: str, target_text: str) -> bool:
        """MV+ - Detect voice changes (passive to active or vice versa)"""
        # Look for passive voice markers
        passive_markers = ['foi', 'foram', 'é', 'são', 'ser', 'sendo', 'sido']
        
        source_passive = sum(source_text.lower().count(marker) for marker in passive_markers)
        target_passive = sum(target_text.lower().count(marker) for marker in passive_markers)
        
        # Significant change in passive voice usage
        return abs(source_passive - target_passive) >= 2
    
    def _find_voice_changes(self, source_text: str, target_text: str) -> List[Dict]:
        """Find examples of voice changes"""
        return [{
            "original": "O texto foi simplificado pelos pesquisadores",
            "alterado": "Os pesquisadores simplificaram o texto"
        }]
    
    def _has_content_restructuring(self, source_text: str, target_text: str) -> bool:
        """RD+ - Detect content and flow restructuring"""
        # Look for paragraph and structural changes
        source_paragraphs = source_text.count('\n\n') + source_text.count('\n')
        target_paragraphs = target_text.count('\n\n') + target_text.count('\n')
        
        # Also check for connector words that suggest restructuring
        connectors = ['portanto', 'assim', 'então', 'logo', 'por isso', 'além disso', 'também']
        source_connectors = sum(source_text.lower().count(conn) for conn in connectors)
        target_connectors = sum(target_text.lower().count(conn) for conn in connectors)
        
        # Changes in paragraph structure or connector usage
        return abs(source_paragraphs - target_paragraphs) >= 1 or abs(source_connectors - target_connectors) >= 1
    
    def _find_structure_changes(self, source_text: str, target_text: str) -> List[Dict]:
        """Find examples of content restructuring"""
        return [{
            "original": "Estrutura textual original com múltiplos parágrafos",
            "reestruturado": "Organização melhorada com fluxo mais claro"
        }]

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
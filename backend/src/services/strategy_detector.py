"""
Strategy Detection Implementation for NET-EST

This file contains comprehensive implementation of strategy detection based on
the "Tabela de Estratégias de Simplificação Textual" document.
"""

from typing import List, Dict, Optional, Literal
import re
import logging
try:
    from ..models.strategy_models import SimplificationStrategy, SimplificationStrategyType, STRATEGY_DESCRIPTIONS, StrategyExample
except ImportError:
    # Fallback for testing
    from models.strategy_models import SimplificationStrategy, SimplificationStrategyType, STRATEGY_DESCRIPTIONS, StrategyExample

try:
    import spacy
    from sentence_transformers import SentenceTransformer, util
    import numpy as np
except ImportError:
    spacy = None
    SentenceTransformer = None
    util = None
    np = None

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
        if spacy:
            _model_cache['nlp'] = spacy.load("pt_core_news_sm")
            logging.info("✅ spaCy Portuguese model loaded successfully")
        else:
            logging.warning("⚠️ spaCy not available")
            _model_cache['nlp'] = None
    except (OSError, ImportError) as e:
        logging.warning(f"⚠️ spaCy model not available: {e}")
        _model_cache['nlp'] = None
    
    # Load the lightweight multilingual model for semantic analysis
    try:
        if SentenceTransformer:
            _model_cache['semantic_model'] = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            logging.info("✅ Lightweight multilingual semantic model loaded successfully")
        else:
            logging.warning("⚠️ SentenceTransformer not available")
            _model_cache['semantic_model'] = None
    except Exception as e:
        logging.warning(f"⚠️ Semantic model not available: {e}")
        _model_cache['semantic_model'] = None
    
    _model_cache['initialized'] = True
    return _model_cache['nlp'], _model_cache['semantic_model']


class StrategyDetector:
    """Detects simplification strategies using hybrid approach: lightweight ML + heuristics"""
    
    def __init__(self):
        self.nlp, self.semantic_model = _initialize_models()
        logging.info("StrategyDetector initialized with hybrid detection (ML + heuristics)")
    
    def identify_strategies(
        self, 
        source_text: str, 
        target_text: str,
        enable_om_detection: bool = False,
        pro_tag_allowed: bool = False
    ) -> List[SimplificationStrategy]:
        """
        Identify simplification strategies using hybrid approach:
        Lightweight ML semantic analysis + intelligent heuristics
        """
        strategies = []
        
        # Apply text length limits for performance
        max_length = 50000  # 50k characters max
        if len(source_text) > max_length:
            source_text = source_text[:max_length]
        if len(target_text) > max_length:
            target_text = target_text[:max_length]
        
        # Calculate semantic similarity if model is available
        semantic_similarity = self._calculate_semantic_similarity(source_text, target_text)
        
        # Extract features for evidence-based classification
        features = self._extract_features(source_text, target_text, semantic_similarity)
        
        # Evidence-based strategy detection
        strategies.extend(self._detect_strategies_with_evidence(
            source_text, target_text, features, enable_om_detection, pro_tag_allowed
        ))
        
        return strategies
    
    def _calculate_semantic_similarity(self, source_text: str, target_text: str) -> float:
        """Calculate semantic similarity using lightweight multilingual model"""
        if not self.semantic_model:
            return 0.0
        
        try:
            # Encode both texts
            embeddings = self.semantic_model.encode([source_text, target_text])
            # Calculate cosine similarity
            if util:
                similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
            else:
                # Fallback cosine similarity calculation
                dot_product = np.dot(embeddings[0], embeddings[1]) if np else 0
                norm_a = np.linalg.norm(embeddings[0]) if np else 1
                norm_b = np.linalg.norm(embeddings[1]) if np else 1
                similarity = dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
            logging.debug(f"Semantic similarity calculated: {similarity:.3f}")
            return float(similarity)
        except Exception as e:
            logging.warning(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def _extract_features(self, source_text: str, target_text: str, semantic_similarity: float) -> Dict[str, float]:
        """
        Enhanced feature extraction for evidence-based classification
        Step 2: Advanced linguistic features for academic rigor
        """
        features = {}
        
        # Text length features
        source_len = len(source_text)
        target_len = len(target_text)
        features['length_ratio'] = target_len / source_len if source_len > 0 else 0
        features['compression_ratio'] = (source_len - target_len) / source_len if source_len > 0 else 0
        
        # Character-level complexity
        source_chars = len(source_text.replace(' ', ''))
        target_chars = len(target_text.replace(' ', ''))
        features['char_density_ratio'] = target_chars / source_chars if source_chars > 0 else 0
        
        # Word-level features
        source_words = source_text.lower().split()
        target_words = target_text.lower().split()
        
        if len(source_words) > 0 and len(target_words) > 0:
            # Enhanced lexical complexity analysis
            source_avg_word_len = sum(len(w) for w in source_words) / len(source_words)
            target_avg_word_len = sum(len(w) for w in target_words) / len(target_words)
            features['word_complexity_reduction'] = (source_avg_word_len - target_avg_word_len) / source_avg_word_len if source_avg_word_len > 0 else 0
            
            # Vocabulary diversity (Type-Token Ratio)
            source_unique = len(set(source_words))
            target_unique = len(set(target_words))
            features['source_ttr'] = source_unique / len(source_words)
            features['target_ttr'] = target_unique / len(target_words)
            features['ttr_change'] = features['target_ttr'] - features['source_ttr']
            
            # Advanced vocabulary overlap analysis
            source_set = set(source_words)
            target_set = set(target_words)
            intersection = source_set.intersection(target_set)
            union = source_set.union(target_set)
            
            features['vocabulary_overlap'] = len(intersection) / len(union) if union else 0
            features['vocabulary_retention'] = len(intersection) / len(source_set) if source_set else 0
            features['vocabulary_innovation'] = len(target_set - source_set) / len(target_set) if target_set else 0
            
            # Word frequency complexity (simple heuristic)
            # Longer words often correlate with lower frequency/higher complexity
            source_complex_words = sum(1 for w in source_words if len(w) > 6)
            target_complex_words = sum(1 for w in target_words if len(w) > 6)
            features['complex_word_reduction'] = (source_complex_words - target_complex_words) / len(source_words) if source_words else 0
            
        else:
            features.update({
                'word_complexity_reduction': 0, 'source_ttr': 0, 'target_ttr': 0, 'ttr_change': 0,
                'vocabulary_overlap': 0, 'vocabulary_retention': 0, 'vocabulary_innovation': 0,
                'complex_word_reduction': 0
            })
        
        # Enhanced sentence-level analysis
        source_sentences = re.split(r'[.!?]+', source_text)
        target_sentences = re.split(r'[.!?]+', target_text)
        source_sentences = [s.strip() for s in source_sentences if s.strip()]
        target_sentences = [s.strip() for s in target_sentences if s.strip()]
        
        features['sentence_count_ratio'] = len(target_sentences) / len(source_sentences) if len(source_sentences) > 0 else 0
        features['sentence_fragmentation'] = max(0, len(target_sentences) - len(source_sentences)) / len(source_sentences) if source_sentences else 0
        
        if len(source_sentences) > 0 and len(target_sentences) > 0:
            # Sentence complexity analysis
            source_sentence_lengths = [len(s.split()) for s in source_sentences]
            target_sentence_lengths = [len(s.split()) for s in target_sentences]
            
            source_avg_sent_len = sum(source_sentence_lengths) / len(source_sentences)
            target_avg_sent_len = sum(target_sentence_lengths) / len(target_sentences)
            features['sentence_simplification'] = (source_avg_sent_len - target_avg_sent_len) / source_avg_sent_len if source_avg_sent_len > 0 else 0
            
            # Sentence length variability (standard deviation proxy)
            if len(source_sentence_lengths) > 1:
                source_sent_var = sum((x - source_avg_sent_len) ** 2 for x in source_sentence_lengths) / len(source_sentence_lengths)
                features['source_sent_variability'] = source_sent_var ** 0.5
            else:
                features['source_sent_variability'] = 0
                
            if len(target_sentence_lengths) > 1:
                target_sent_var = sum((x - target_avg_sent_len) ** 2 for x in target_sentence_lengths) / len(target_sentence_lengths)
                features['target_sent_variability'] = target_sent_var ** 0.5
            else:
                features['target_sent_variability'] = 0
                
            features['variability_reduction'] = (features['source_sent_variability'] - features['target_sent_variability']) / features['source_sent_variability'] if features['source_sent_variability'] > 0 else 0
        else:
            features.update({
                'sentence_simplification': 0, 'source_sent_variability': 0, 
                'target_sent_variability': 0, 'variability_reduction': 0
            })
        
        # Punctuation and structural analysis
        source_punct = len(re.findall(r'[,;:\(\)\[\]\"\'—–-]', source_text))
        target_punct = len(re.findall(r'[,;:\(\)\[\]\"\'—–-]', target_text))
        features['punctuation_ratio'] = target_punct / source_punct if source_punct > 0 else 0
        features['punctuation_reduction'] = (source_punct - target_punct) / len(source_text.split()) if source_text.split() else 0
        
        # Conjunction and connective analysis (Portuguese specific)
        source_connectives = len(re.findall(r'\b(porque|portanto|contudo|entretanto|ademais|outrossim|todavia|não obstante)\b', source_text.lower()))
        target_connectives = len(re.findall(r'\b(porque|portanto|contudo|entretanto|ademais|outrossim|todavia|não obstante)\b', target_text.lower()))
        features['connective_reduction'] = (source_connectives - target_connectives) / len(source_words) if source_words else 0
        
        # Readability proxy features
        # Flesch-Kincaid proxy: average sentence length and average syllables per word
        features['readability_improvement'] = features['sentence_simplification'] + features['word_complexity_reduction']
        
        # Semantic coherence features
        features['semantic_similarity'] = semantic_similarity
        features['semantic_preservation'] = 1.0 if semantic_similarity > 0.8 else semantic_similarity
        features['semantic_drift'] = max(0, 0.5 - semantic_similarity) * 2  # How much meaning has changed
        
        # Text density and information packaging
        if source_words and target_words:
            features['information_density'] = (len(set(target_words)) / len(target_words)) / (len(set(source_words)) / len(source_words)) if source_words else 1
        else:
            features['information_density'] = 1
        
        return features
    
    def _detect_strategies_with_evidence(
        self, 
        source_text: str, 
        target_text: str, 
        features: Dict[str, float],
        enable_om_detection: bool, 
        pro_tag_allowed: bool
    ) -> List[SimplificationStrategy]:
        """
        Enhanced evidence-based strategy detection with stricter academic thresholds
        Step 2.5: Fixed overly permissive thresholds for better text differentiation
        """
        strategies = []
        
        # Stricter evidence thresholds for academic rigor and proper differentiation
        HIGH_CONFIDENCE_THRESHOLD = 0.85   # Raised from 0.82
        MEDIUM_CONFIDENCE_THRESHOLD = 0.72  # Raised from 0.65
        SEMANTIC_PRESERVATION_MIN = 0.65    # Raised from 0.6
        
        # Text complexity factor - longer texts need stronger evidence
        text_complexity_factor = min(1.2, 1.0 + (len(source_text.split()) / 1000) * 0.1)
        
        # SL+ (Adequação de Vocabulário) - Stricter lexical simplification detection
        lexical_evidence = (
            features['word_complexity_reduction'] * 0.4 +  
            features['complex_word_reduction'] * 0.3 +     
            features['vocabulary_innovation'] * 0.2 +      
            features['semantic_preservation'] * 0.1        
        )
        
        # Stricter thresholds for lexical simplification
        if (features['word_complexity_reduction'] > 0.18 * text_complexity_factor and  # Raised from 0.12
            features['complex_word_reduction'] > 0.08 * text_complexity_factor and     # Raised from 0.05
            features['semantic_similarity'] > SEMANTIC_PRESERVATION_MIN):
            confidence = min(0.92, lexical_evidence + features['semantic_similarity'] * 0.2)
            if confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("SL+", 
                    "alto" if confidence > HIGH_CONFIDENCE_THRESHOLD else "médio", confidence))
        
        # RP+ (Fragmentação Sintática) - Much stricter sentence fragmentation detection
        fragmentation_evidence = (
            features['sentence_fragmentation'] * 0.35 +    
            features['sentence_simplification'] * 0.25 +   
            features['variability_reduction'] * 0.2 +      
            features['semantic_preservation'] * 0.2        
        )
        
        # Much stricter thresholds for fragmentation
        if (features['sentence_count_ratio'] > 1.35 * text_complexity_factor and     # Raised from 1.15
            features['sentence_fragmentation'] > 0.25 * text_complexity_factor and  # Raised from 0.1
            features['sentence_simplification'] > 0.25 * text_complexity_factor and # Raised from 0.15
            features['semantic_similarity'] > SEMANTIC_PRESERVATION_MIN):
            confidence = min(0.90, fragmentation_evidence + features['semantic_similarity'] * 0.15)
            if confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("RP+", 
                    "alto" if confidence > HIGH_CONFIDENCE_THRESHOLD else "médio", confidence))
        
        # RF+ (Reescrita Global) - Much stricter global rewriting detection
        rewriting_evidence = (
            (1 - features['vocabulary_retention']) * 0.3 + 
            features['vocabulary_innovation'] * 0.25 +     
            features['readability_improvement'] * 0.2 +    
            features['semantic_preservation'] * 0.25       
        )
        
        # Much stricter thresholds for global rewriting
        if (features['vocabulary_overlap'] < 0.35 / text_complexity_factor and      # Lowered from 0.55 (more restrictive)
            features['vocabulary_innovation'] > 0.45 * text_complexity_factor and   # Raised from 0.3
            features['semantic_similarity'] > SEMANTIC_PRESERVATION_MIN and
            features['readability_improvement'] > 0.2 * text_complexity_factor):    # Raised from 0.1
            confidence = min(0.88, rewriting_evidence + features['semantic_similarity'] * 0.15)
            if confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("RF+", 
                    "alto" if confidence > HIGH_CONFIDENCE_THRESHOLD else "médio", confidence))
        
        # MOD+ (Reinterpretação Perspectiva) - Stricter perspective reinterpretation
        reinterpretation_evidence = (
            features['semantic_similarity'] * 0.4 +        
            (1 - features['vocabulary_overlap']) * 0.25 +  
            features['sentence_simplification'] * 0.2 +    
            features['information_density'] * 0.15         
        )
        
        # Stricter thresholds for perspective reinterpretation
        if (features['semantic_similarity'] > 0.78 and                              # Raised from 0.72
            features['vocabulary_overlap'] < 0.55 / text_complexity_factor and     # More restrictive
            features['sentence_simplification'] > 0.15 * text_complexity_factor and # Raised from 0.08
            features['ttr_change'] > -0.1):                                         # Less vocabulary loss allowed
            confidence = min(0.85, reinterpretation_evidence)
            if confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("MOD+", 
                    "alto" if confidence > HIGH_CONFIDENCE_THRESHOLD else "médio", confidence))
        
        # EXP+ (Explicitação) - Stricter explicitation detection
        explicitation_evidence = (
            features['length_ratio'] * 0.3 +               
            features['semantic_preservation'] * 0.3 +      
            features['vocabulary_innovation'] * 0.2 +      
            features['punctuation_ratio'] * 0.2            
        )
        
        # Stricter thresholds for explicitation
        if (features['length_ratio'] > 1.20 * text_complexity_factor and          # Raised from 1.12
            features['semantic_similarity'] > 0.82 and                            # Raised from 0.78
            features['vocabulary_innovation'] > 0.25 * text_complexity_factor):   # Raised from 0.15
            confidence = min(0.87, explicitation_evidence)
            if confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("EXP+", 
                    "alto" if confidence > HIGH_CONFIDENCE_THRESHOLD else "médio", confidence))
        
        # OM+ (Supressão) - Even stricter omission detection
        if enable_om_detection:
            omission_evidence = (
                features['compression_ratio'] * 0.4 +       
                features['semantic_preservation'] * 0.35 +  
                (1 - features['punctuation_ratio']) * 0.25  
            )
            
            # Much stricter thresholds for omission
            if (features['compression_ratio'] > 0.35 * text_complexity_factor and  # Raised from 0.25
                features['semantic_similarity'] > 0.80 and                        # Raised from 0.75
                features['sentence_simplification'] > 0.2 * text_complexity_factor): # Raised from 0.1
                confidence = min(0.85, omission_evidence)
                if confidence > HIGH_CONFIDENCE_THRESHOLD:  # Keep higher threshold for OM+
                    strategies.append(self._create_strategy("OM+", "alto", confidence))
        
        # DL+ (Reorganização) - Stricter reorganization detection
        reorganization_evidence = (
            features['vocabulary_overlap'] * 0.35 +        
            features['semantic_preservation'] * 0.3 +      
            features['sentence_simplification'] * 0.2 +    
            (1 - features['semantic_drift']) * 0.15        
        )
        
        # Stricter thresholds for reorganization
        if (features['vocabulary_overlap'] > 0.75 and                              # Raised from 0.65
            features['semantic_similarity'] > 0.82 and                             # Raised from 0.77
            features['sentence_simplification'] > 0.08 * text_complexity_factor and # Keep relatively low
            features['variability_reduction'] > 0.15):                             # Raised from 0.1
            confidence = min(0.82, reorganization_evidence)
            if confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("DL+", 
                    "alto" if confidence > HIGH_CONFIDENCE_THRESHOLD else "médio", confidence))
        
        # AS+ (Alteração de Sentido) - Stricter meaning change detection
        meaning_change_evidence = (
            features['semantic_drift'] * 0.4 +             
            (1 - features['vocabulary_retention']) * 0.3 + 
            features['vocabulary_innovation'] * 0.3        
        )
        
        # Stricter thresholds for meaning change
        if (features['semantic_similarity'] < 0.45 and                             # Lowered from 0.55 (more restrictive)
            features['vocabulary_overlap'] < 0.35 and                              # Lowered from 0.45
            features['semantic_drift'] > 0.3):                                     # Raised from 0.2
            confidence = min(0.75, meaning_change_evidence)
            if confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("AS+", 
                    "alto" if confidence > 0.72 else "médio", confidence))         # Raised threshold
        
        # Stricter heuristic strategies with enhanced validation
        
        # IN+ (Inserções) - Much stricter insertion detection
        if (self._has_insertions(source_text, target_text) and 
            features['semantic_similarity'] > 0.75 and                             # Raised from 0.6
            features['length_ratio'] > 1.15 * text_complexity_factor):             # Raised from 1.05
            insertion_confidence = min(0.75, features['length_ratio'] * 0.4 + features['semantic_similarity'] * 0.3)
            if insertion_confidence > 0.70:                                         # Raised from 0.55
                strategies.append(self._create_strategy("IN+", "médio", insertion_confidence))
        
        # TA+ (Clareza Referencial) - Stricter referential clarity
        if (self._has_referential_clarity(source_text, target_text) and 
            features['semantic_similarity'] > 0.78 and                             # Raised from 0.72
            features['vocabulary_innovation'] > 0.15 * text_complexity_factor):    # Added complexity factor
            clarity_confidence = min(0.78, features['semantic_similarity'] * 0.5 + features['vocabulary_innovation'] * 0.3)
            if clarity_confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("TA+", "médio", clarity_confidence))
        
        # MV+ (Voz Verbal) - Stricter voice change detection
        if (self._has_voice_change(source_text, target_text) and 
            features['semantic_similarity'] > 0.80 and                             # Raised from 0.75
            features['sentence_simplification'] > 0.08 * text_complexity_factor):  # Added complexity factor
            voice_confidence = min(0.80, features['semantic_similarity'] * 0.6 + features['sentence_simplification'] * 0.2)
            if voice_confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                strategies.append(self._create_strategy("MV+", "médio", voice_confidence))
        
        return strategies
    
    def _create_strategy(self, sigla: str, impacto: Literal["baixo", "médio", "alto"], confianca: float) -> SimplificationStrategy:
        """Create a strategy object with proper mapping"""
        strategy_info = STRATEGY_DESCRIPTIONS.get(sigla, {
            'nome': f'Estratégia {sigla}',
            'descricao': f'Estratégia de simplificação {sigla}',
            'tipo': SimplificationStrategyType.LEXICAL
        })
        
        return SimplificationStrategy(
            sigla=sigla,
            nome=strategy_info['nome'],
            descricao=strategy_info['descricao'],
            tipo=strategy_info['tipo'],
            impacto=impacto,
            confianca=confianca,
            exemplos=[]
        )
    
    # Strategy detection methods
    def _has_lexical_simplification(self, source: str, target: str) -> bool:
        """Detect lexical simplification (word substitutions)"""
        source_words = source.lower().split()
        target_words = target.lower().split()
        
        # Check for word length reduction
        if len(source_words) > 0 and len(target_words) > 0:
            source_avg_len = sum(len(w) for w in source_words) / len(source_words)
            target_avg_len = sum(len(w) for w in target_words) / len(target_words)
            return source_avg_len > target_avg_len + 0.5
        
        return False
    
    def _get_lexical_complexity_reduction(self, source: str, target: str) -> float:
        """Calculate lexical complexity reduction ratio"""
        source_words = source.lower().split()
        target_words = target.lower().split()
        
        if len(source_words) > 0 and len(target_words) > 0:
            source_avg_len = sum(len(w) for w in source_words) / len(source_words)
            target_avg_len = sum(len(w) for w in target_words) / len(target_words)
            return (source_avg_len - target_avg_len) / source_avg_len if source_avg_len > 0 else 0
        
        return 0
    
    def _has_sentence_fragmentation(self, source: str, target: str) -> bool:
        """Detect sentence fragmentation (long sentences split into shorter ones)"""
        source_sentences = re.split(r'[.!?]+', source)
        target_sentences = re.split(r'[.!?]+', target)
        
        source_sentences = [s.strip() for s in source_sentences if s.strip()]
        target_sentences = [s.strip() for s in target_sentences if s.strip()]
        
        if len(source_sentences) > 0 and len(target_sentences) > 0:
            source_avg_len = sum(len(s.split()) for s in source_sentences) / len(source_sentences)
            target_avg_len = sum(len(s.split()) for s in target_sentences) / len(target_sentences)
            
            # Check if target has more sentences with shorter average length
            return (len(target_sentences) > len(source_sentences) and 
                    target_avg_len < source_avg_len * 0.7)
        
        return False
    
    def _has_global_rewriting(self, source: str, target: str) -> bool:
        """Detect global rewriting (significant structural changes)"""
        # Calculate word overlap
        source_words = set(source.lower().split())
        target_words = set(target.lower().split())
        
        if len(source_words) > 0:
            overlap = len(source_words.intersection(target_words)) / len(source_words)
            return overlap < 0.5  # Less than 50% word overlap indicates global rewriting
        
        return False
    
    def _has_perspective_reinterpretation(self, source: str, target: str) -> bool:
        """Detect perspective reinterpretation"""
        # Look for changes in narrative perspective, tense, or viewpoint
        perspective_indicators = ['eu', 'você', 'ele', 'ela', 'nós', 'eles', 'elas']
        tense_indicators = ['foi', 'será', 'é', 'era', 'seria']
        
        source_lower = source.lower()
        target_lower = target.lower()
        
        source_perspectives = sum(1 for indicator in perspective_indicators if indicator in source_lower)
        target_perspectives = sum(1 for indicator in perspective_indicators if indicator in target_lower)
        
        return abs(source_perspectives - target_perspectives) >= 2
    
    def _has_explicitation(self, source: str, target: str) -> bool:
        """Detect explicitation (target is longer with added explanations)"""
        return len(target) > len(source) * 1.2
    
    def _has_suppression(self, source: str, target: str) -> bool:
        """Detect suppression/omission (significant content removal)"""
        return len(target) < len(source) * 0.6
    
    def _has_reorganization(self, source: str, target: str) -> bool:
        """Detect reorganization of content"""
        # Simple heuristic: look for similar words in different positions
        source_words = source.lower().split()
        target_words = target.lower().split()
        
        common_words = set(source_words).intersection(set(target_words))
        
        if len(common_words) >= 3:
            # Check if word order has changed significantly
            source_positions = {word: i for i, word in enumerate(source_words) if word in common_words}
            target_positions = {word: i for i, word in enumerate(target_words) if word in common_words}
            
            position_changes = 0
            for word in common_words:
                if word in source_positions and word in target_positions:
                    if abs(source_positions[word] - target_positions[word]) > 2:
                        position_changes += 1
            
            return position_changes >= 2
        
        return False
    
    def _has_insertions(self, source: str, target: str) -> bool:
        """Detect insertions (punctuation, parentheses, etc.)"""
        source_punct = re.findall(r'[()[\]{},;:]', source)
        target_punct = re.findall(r'[()[\]{},;:]', target)
        
        return len(target_punct) > len(source_punct)
    
    def _has_referential_clarity(self, source: str, target: str) -> bool:
        """Detect referential clarity improvements (pronoun replacements)"""
        pronouns = ['ele', 'ela', 'eles', 'elas', 'isto', 'isso', 'aquilo', 'este', 'esta', 'aquele', 'aquela']
        
        source_pronouns = sum(1 for p in pronouns if p in source.lower())
        target_pronouns = sum(1 for p in pronouns if p in target.lower())
        
        return source_pronouns > target_pronouns
    
    def _has_voice_change(self, source: str, target: str) -> bool:
        """Detect voice changes (passive to active or vice versa)"""
        passive_indicators = ['foi', 'foram', 'é', 'são', 'sendo', 'sido']
        
        source_passive = sum(1 for indicator in passive_indicators if indicator in source.lower())
        target_passive = sum(1 for indicator in passive_indicators if indicator in target.lower())
        
        return abs(source_passive - target_passive) >= 1
    
    def _has_title_modification(self, source: str, target: str) -> bool:
        """Detect title modifications"""
        # Look for title patterns (capitalized words at beginning)
        source_lines = source.split('\n')
        target_lines = target.split('\n')
        
        source_titles = sum(1 for line in source_lines if line.strip() and line.strip()[0].isupper())
        target_titles = sum(1 for line in target_lines if line.strip() and line.strip()[0].isupper())
        
        return source_titles != target_titles
    
    def _has_structuring(self, source: str, target: str) -> bool:
        """Detect structural changes (paragraphs, sections)"""
        source_paragraphs = len([p for p in source.split('\n\n') if p.strip()])
        target_paragraphs = len([p for p in target.split('\n\n') if p.strip()])
        
        return abs(source_paragraphs - target_paragraphs) >= 1
    
    def _has_meaning_change(self, source: str, target: str) -> bool:
        """Detect meaning changes"""
        # Simple heuristic: very different vocabulary suggests meaning change
        source_words = set(source.lower().split())
        target_words = set(target.lower().split())
        
        if len(source_words) > 0:
            overlap = len(source_words.intersection(target_words)) / len(source_words.union(target_words))
            return overlap < 0.3  # Very low overlap suggests meaning change
        
        return False
    
    def _has_pro_strategy(self, source: str, target: str) -> bool:
        """Detect PRO+ strategy (advanced/experimental)"""
        # Simple placeholder - PRO+ is for advanced strategies
        return False

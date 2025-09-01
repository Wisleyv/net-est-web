"""Feature Extraction Models for NET-EST System
Module 3 - Feature Extractor and Classifier Models
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TagType(str, Enum):
    """Available simplification strategy tags"""
    AS_PLUS = "AS+"  # Alteração de Sentido
    DL_PLUS = "DL+"  # Reorganização Posicional  
    EXP_PLUS = "EXP+"  # Explicitação e Detalhamento
    IN_PLUS = "IN+"  # Manejo de Inserções
    MOD_PLUS = "MOD+"  # Reinterpretação Perspectiva
    MT_PLUS = "MT+"  # Otimização de Títulos
    OM_PLUS = "OM+"  # Supressão Seletiva (manual activation only)
    PRO_PLUS = "PRO+"  # Desvio Semântico (manual insertion only, never generated)
    RF_PLUS = "RF+"  # Reescrita Global
    RD_PLUS = "RD+"  # Estruturação de Conteúdo e Fluxo
    RP_PLUS = "RP+"  # Fragmentação Sintática
    SL_PLUS = "SL+"  # Adequação de Vocabulário
    TA_PLUS = "TA+"  # Clareza Referencial
    MV_PLUS = "MV+"  # Alteração da Voz Verbal


class ConfidenceLevel(str, Enum):
    """Confidence levels for tag assignment"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TagConfiguration(BaseModel):
    """Configuration for individual tags"""
    active: bool = Field(description="Whether this tag is active for analysis")
    weight: float = Field(ge=0.0, le=2.0, description="Weight multiplier for this tag")
    manual_only: bool = Field(default=False, description="Tag can only be manually assigned")


class UserConfiguration(BaseModel):
    """User configuration for tag analysis"""
    
    # Default configuration based on requirements
    tag_config: Dict[TagType, TagConfiguration] = Field(
        default_factory=lambda: {
            # Active by default - transformation tags
            TagType.AS_PLUS: TagConfiguration(active=True, weight=1.0),
            TagType.DL_PLUS: TagConfiguration(active=True, weight=1.0),
            TagType.EXP_PLUS: TagConfiguration(active=True, weight=1.0),
            TagType.IN_PLUS: TagConfiguration(active=True, weight=1.0),
            TagType.MOD_PLUS: TagConfiguration(active=True, weight=1.2),  # Higher weight for semantic changes
            TagType.MT_PLUS: TagConfiguration(active=True, weight=1.0),
            TagType.RF_PLUS: TagConfiguration(active=True, weight=1.5),  # Higher weight for global rewriting
            TagType.RD_PLUS: TagConfiguration(active=True, weight=1.0),
            TagType.RP_PLUS: TagConfiguration(active=True, weight=1.0),
            TagType.SL_PLUS: TagConfiguration(active=True, weight=1.3),  # Higher weight for vocabulary changes
            TagType.TA_PLUS: TagConfiguration(active=True, weight=1.0),
            TagType.MV_PLUS: TagConfiguration(active=True, weight=1.0),
            
            # Inactive by default - special cases
            TagType.OM_PLUS: TagConfiguration(active=False, weight=1.0),  # Manual activation only
            TagType.PRO_PLUS: TagConfiguration(active=False, weight=1.0, manual_only=True),  # Never generated
        }
    )
    
    # Analysis thresholds
    similarity_threshold: float = Field(default=0.5, description="Threshold for semantic alignment")
    confidence_thresholds: Dict[ConfidenceLevel, float] = Field(
        default_factory=lambda: {
            ConfidenceLevel.HIGH: 0.8,
            ConfidenceLevel.MEDIUM: 0.6,
            ConfidenceLevel.LOW: 0.3
        }
    )
    
    # Simplification expectations
    expected_reduction_ratio: float = Field(default=0.65, description="Expected text reduction ratio (65%)")
    reduction_tolerance: float = Field(default=0.15, description="Tolerance for reduction ratio")


class DiscourseFeatures(BaseModel):
    """Extracted discourse-level features from aligned paragraphs"""
    
    # Text reduction metrics
    word_reduction_ratio: float = Field(description="Ratio of word count reduction")
    character_reduction_ratio: float = Field(description="Ratio of character count reduction")
    
    # Readability changes
    readability_change: float = Field(description="Change in readability score")
    complexity_reduction: float = Field(description="Reduction in text complexity")
    
    # Lexical analysis
    lexical_density_change: float = Field(description="Change in lexical density")
    vocabulary_complexity_change: float = Field(description="Change in vocabulary complexity")
    
    # Syntactic analysis
    sentence_length_change: float = Field(description="Change in average sentence length")
    syntactic_complexity_change: float = Field(description="Change in syntactic complexity")
    
    # Semantic analysis
    semantic_similarity: float = Field(description="Semantic similarity between paragraphs")
    information_preservation: float = Field(description="Estimated information preservation")


class TagEvidence(BaseModel):
    """Evidence for tag assignment"""
    
    feature_name: str = Field(description="Name of the feature providing evidence")
    evidence_value: float = Field(description="Numerical value of the evidence")
    threshold_met: bool = Field(description="Whether the evidence meets the threshold")
    contribution_score: float = Field(description="Contribution to final confidence")


class TagAnnotation(BaseModel):
    """Individual tag annotation"""
    
    id: str = Field(description="Unique annotation ID")
    tag: TagType = Field(description="Applied tag type")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score for this tag")
    confidence_level: ConfidenceLevel = Field(description="Categorical confidence level")
    
    # Paragraph references
    source_indices: List[int] = Field(description="Source paragraph indices")
    target_indices: List[int] = Field(description="Target paragraph indices")
    
    # Supporting evidence
    evidence: List[TagEvidence] = Field(description="Evidence supporting this tag")
    features: DiscourseFeatures = Field(description="Extracted features for this annotation")
    
    # Metadata
    manually_assigned: bool = Field(default=False, description="Whether manually assigned by user")
    validated: bool = Field(default=False, description="Whether validated by human expert")


class FeatureExtractionRequest(BaseModel):
    """Request for feature extraction and classification"""
    
    # Input from Module 2 (Semantic Alignment)
    alignment_data: Dict[str, Any] = Field(description="Results from semantic alignment")
    
    # User configuration
    user_config: UserConfiguration = Field(description="User configuration for analysis")
    
    # Analysis options
    extract_detailed_features: bool = Field(default=True, description="Extract detailed linguistic features")
    apply_heuristic_rules: bool = Field(default=True, description="Apply heuristic classification rules")


class FeatureExtractionResponse(BaseModel):
    """Response with extracted features and annotations"""
    
    success: bool = Field(description="Whether extraction was successful")
    annotated_data: List[TagAnnotation] = Field(description="List of tag annotations")
    
    # Analysis summary
    total_annotations: int = Field(description="Total number of annotations")
    confidence_distribution: Dict[ConfidenceLevel, int] = Field(description="Distribution of confidence levels")
    tag_distribution: Dict[TagType, int] = Field(description="Distribution of tag types")
    
    # Processing metrics
    processing_time: float = Field(description="Processing time in seconds")
    features_extracted: int = Field(description="Number of feature sets extracted")
    
    # Analysis insights
    average_confidence: float = Field(description="Average confidence across all annotations")
    reduction_ratio_achieved: float = Field(description="Actual reduction ratio achieved")
    reduction_ratio_expected: float = Field(description="Expected reduction ratio from config")
    
    # Warnings and recommendations
    warnings: List[str] = Field(default_factory=list, description="Analysis warnings")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    
    # Metadata
    user_config_used: UserConfiguration = Field(description="User configuration used for analysis")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Compatibility: accept and expose distributions with string keys for ease of JSON serialization
    def model_dump_compat(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict with enum keys converted to strings."""
        base = self.model_dump() if hasattr(self, 'model_dump') else self.dict()
        # Convert confidence_distribution keys
        conf = base.get('confidence_distribution') or {}
        base['confidence_distribution'] = {str(k): int(v) for k, v in conf.items()} if conf else {}
        tagd = base.get('tag_distribution') or {}
        base['tag_distribution'] = {str(k): int(v) for k, v in tagd.items()} if tagd else {}
        return base

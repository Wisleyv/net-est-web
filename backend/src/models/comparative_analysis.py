"""
Comparative Analysis Models

Includes experimental M4 fields:
 - include_visual_salience / salience_visual_mode (frontend hints only)
 - include_micro_spans / micro_span_mode (activates MicroSpanExtractor; hierarchy_version -> 1.2 when present)

Stability:
 - Experimental flags default to False; response shape remains backward compatible (no micro_spans keys when disabled).
 - Micro-span salience normalization is local per sentence (max=1.0) and may evolve; do not persist weights for long-term analytics yet.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Import feedback models for integration
try:
    from .feedback import FeedbackCollectionPrompt
except ImportError:
    FeedbackCollectionPrompt = None


class AnalysisOptions(BaseModel):
    """Options for comparative analysis"""
    include_lexical_analysis: bool = True
    include_syntactic_analysis: bool = True
    include_semantic_analysis: bool = True
    include_readability_metrics: bool = True
    include_strategy_identification: bool = True
    include_salience: bool = Field(
        True,
        description="If true and hierarchical_output enabled, compute salience weights (paragraph/sentence).",
    )
    # M4 flags (visual salience + micro-spans)
    include_visual_salience: bool = Field(
        False,
        description="Enable delivery of visual salience hints (gradient/bars) in hierarchical output.",
    )
    include_micro_spans: bool = Field(
        False,
        description="Enable experimental micro-span extraction (M4).",
    )
    salience_visual_mode: str | None = Field(
        None,
        description="Preferred visualization mode for salience: 'gradient' | 'bar' (frontend hint).",
    )
    micro_span_mode: str | None = Field(
        None,
        description="Micro-span extraction mode (e.g., 'ngram-basic').",
    )


class ComparativeAnalysisRequest(BaseModel):
    """Request model for comparative analysis"""
    source_text: str = Field(..., min_length=50, description="Original complex text")
    target_text: str = Field(..., min_length=20, description="Simplified text")
    analysis_options: AnalysisOptions = Field(default_factory=AnalysisOptions)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    hierarchical_output: bool = Field(
        False,
        description="If true, include hierarchical analysis structure (paragraph→sentence).",
    )
    salience_method: Optional[str] = Field(
        None,
        description="Override salience method (e.g., 'frequency','keybert','yake'); defaults to env or provider fallback.",
    )
    # Pass-through experimental visualization / micro-span overrides (optional; duplicate of nested for convenience)
    include_micro_spans: Optional[bool] = Field(
        default=None,
        description="Override analysis_options.include_micro_spans if provided.",
    )
    include_visual_salience: Optional[bool] = Field(
        default=None,
        description="Override analysis_options.include_visual_salience if provided.",
    )
    micro_span_mode: Optional[str] = Field(
        default=None,
        description="Override analysis_options.micro_span_mode if provided.",
    )
    salience_visual_mode: Optional[str] = Field(
        default=None,
        description="Override analysis_options.salience_visual_mode if provided.",
    )


class SimplificationStrategyType(str, Enum):
    """Types of simplification strategies"""
    LEXICAL = "lexical"
    SYNTACTIC = "syntactic"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"


class SimplificationStrategy(BaseModel):
    """Model for identified simplification strategy"""
    name: str
    type: SimplificationStrategyType
    description: str
    impact: str = Field(..., pattern="^(low|medium|high)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    examples: List[Dict[str, str]] = Field(default_factory=list)

    # Phase 1: stable identifier & metadata (additive)
    strategy_id: Optional[str] = Field(
        default=None,
        description="Stable unique ID for this strategy instance (UUIDv4 or content-hash)."
    )

    # Additional fields for frontend compatibility
    code: Optional[str] = Field(None, description="Strategy code (e.g., 'SL+', 'RP+')")
    color: Optional[str] = Field(None, description="Hex color code for UI highlighting")
    targetPosition: Optional[Dict[str, Any]] = Field(None, description="Legacy coarse position (sentence-level)")
    sourcePosition: Optional[Dict[str, Any]] = Field(None, description="Legacy coarse position (sentence-level)")

    # Phase 1: extended granular offsets (paragraph/sentence/char)
    target_offsets: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed target offsets: {paragraph, sentence, char_start, char_end}"
    )
    source_offsets: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed source offsets: {paragraph, sentence, char_start, char_end}"
    )


class ReadabilityMetric(BaseModel):
    """Individual readability metric"""
    label: str
    source: float
    target: float
    improvement: float
    description: str


class ReadabilityMetrics(BaseModel):
    """Collection of readability metrics"""
    flesch_reading_ease: ReadabilityMetric
    flesch_kincaid_grade: ReadabilityMetric
    automated_readability_index: ReadabilityMetric
    coleman_liau_index: ReadabilityMetric
    gunning_fog: ReadabilityMetric


class LexicalAnalysis(BaseModel):
    """Lexical analysis results"""
    source_unique_words: int
    target_unique_words: int
    source_complexity: float
    target_complexity: float
    vocabulary_overlap: float
    complexity_reduction: float
    substitutions: List[Dict[str, str]] = Field(default_factory=list)


class SyntacticAnalysis(BaseModel):
    """Syntactic analysis results"""
    source_avg_sentence_length: float
    target_avg_sentence_length: float
    source_avg_clause_length: float
    target_avg_clause_length: float
    sentence_simplification_ratio: float
    clause_reduction: float
    structural_changes: List[Dict[str, Any]] = Field(default_factory=list)


class SemanticAnalysis(BaseModel):
    """Semantic analysis results"""
    semantic_similarity: float
    meaning_preservation: float
    information_loss: float
    concept_simplification: List[Dict[str, str]] = Field(default_factory=list)


class ComparativeAnalysisResponse(BaseModel):
    """Response model for comparative analysis"""
    analysis_id: str
    timestamp: datetime
    
    # Input data
    source_text: str
    target_text: str
    source_length: int
    target_length: int
    compression_ratio: float
    
    # Overall assessment
    overall_score: int = Field(..., ge=0, le=100)
    overall_assessment: str
    
    # Detailed analyses
    lexical_analysis: Optional[LexicalAnalysis] = None
    syntactic_analysis: Optional[SyntacticAnalysis] = None
    semantic_analysis: Optional[SemanticAnalysis] = None
    readability_metrics: Optional[ReadabilityMetrics] = None
    
    # Identified strategies
    simplification_strategies: List[SimplificationStrategy] = Field(default_factory=list)
    strategies_count: int
    
    # Metrics summary
    semantic_preservation: float = Field(..., ge=0.0, le=100.0)
    readability_improvement: float
    
    # Highlighted differences for UI
    highlighted_differences: List[Dict[str, str]] = Field(default_factory=list)
    
    # Metadata
    processing_time: float
    model_version: str = "1.0.0"
    detection_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Runtime detection configuration & feature flags (additive)."
    )
    hierarchical_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Hierarchical analysis tree when requested (versioned).",
    )

    # M6: Feedback system integration
    feedback_prompt: Optional[Any] = Field(
        default=None,
        description="Feedback collection prompt when feedback system is enabled.",
    )


class AnalysisHistoryItem(BaseModel):
    """Item in analysis history"""
    analysis_id: str
    timestamp: datetime
    source_length: int
    target_length: int
    overall_score: int
    strategies_count: int
    semantic_preservation: float
    readability_improvement: float


class AnalysisExportRequest(BaseModel):
    """Request for exporting analysis"""
    analysis_id: str
    format: str = Field(..., pattern="^(pdf|csv|json)$")
    include_sections: List[str] = Field(default_factory=lambda: ["overview", "strategies", "metrics"])


class TextUploadResponse(BaseModel):
    """Response for text file upload"""
    content: str
    filename: str
    size: int
    file_type: str
    encoding: str = "utf-8"
    timestamp: datetime

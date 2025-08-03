"""
Comparative Analysis Models - Phase 2.B.5 Implementation
Pydantic models for comparative analysis functionality
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AnalysisOptions(BaseModel):
    """Options for comparative analysis"""
    include_lexical_analysis: bool = True
    include_syntactic_analysis: bool = True
    include_semantic_analysis: bool = True
    include_readability_metrics: bool = True
    include_strategy_identification: bool = True


class ComparativeAnalysisRequest(BaseModel):
    """Request model for comparative analysis"""
    source_text: str = Field(..., min_length=50, description="Original complex text")
    target_text: str = Field(..., min_length=20, description="Simplified text")
    analysis_options: AnalysisOptions = Field(default_factory=AnalysisOptions)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


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

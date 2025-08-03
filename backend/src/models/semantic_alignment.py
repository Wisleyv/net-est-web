"""Semantic Alignment Models for NET-EST System
Handles paragraph alignment using BERTimbau embeddings
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AlignmentMethod(str, Enum):
    """Methods for semantic alignment"""

    COSINE_SIMILARITY = "cosine_similarity"
    EUCLIDEAN_DISTANCE = "euclidean_distance"
    DOT_PRODUCT = "dot_product"


class AlignmentRequest(BaseModel):
    """Request model for semantic alignment"""

    source_paragraphs: list[str] = Field(..., description="Source text paragraphs")
    target_paragraphs: list[str] = Field(..., description="Target text paragraphs")
    similarity_threshold: float = Field(
        0.5, ge=0.0, le=1.0, description="Similarity threshold for alignment"
    )
    alignment_method: AlignmentMethod = Field(
        AlignmentMethod.COSINE_SIMILARITY, description="Alignment method to use"
    )
    max_alignments_per_source: int = Field(
        3, ge=1, le=5, description="Maximum alignments per source paragraph"
    )
    user_config: dict[str, Any] = Field(default_factory=dict, description="User configuration")


class AlignedPair(BaseModel):
    """Model for an aligned paragraph pair"""

    source_index: int = Field(..., description="Index of source paragraph")
    target_index: int = Field(..., description="Index of target paragraph")
    source_text: str = Field(..., description="Source paragraph text")
    target_text: str = Field(..., description="Target paragraph text")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    confidence: str = Field(..., description="Confidence level (high/medium/low)")
    alignment_method: str = Field(..., description="Method used for alignment")


class UnalignedParagraph(BaseModel):
    """Model for unaligned paragraphs"""

    index: int = Field(..., description="Paragraph index")
    text: str = Field(..., description="Paragraph text")
    reason: str = Field(..., description="Reason for no alignment")
    nearest_similarity: float | None = Field(None, description="Highest similarity found")


class AlignmentMatrix(BaseModel):
    """Model for similarity matrix"""

    source_count: int = Field(..., description="Number of source paragraphs")
    target_count: int = Field(..., description="Number of target paragraphs")
    matrix: list[list[float]] = Field(..., description="Similarity matrix")
    method: str = Field(..., description="Method used to compute similarity")


class AlignmentResult(BaseModel):
    """Result model for semantic alignment"""

    aligned_pairs: list[AlignedPair] = Field(
        ..., description="Successfully aligned paragraph pairs"
    )
    unaligned_source_indices: list[int] = Field(
        ..., description="Indices of unaligned source paragraphs"
    )
    unaligned_target_indices: list[int] = Field(
        ..., description="Indices of unaligned target paragraphs"
    )
    unaligned_source_details: list[UnalignedParagraph] = Field(
        ..., description="Details of unaligned source paragraphs"
    )
    unaligned_target_details: list[UnalignedParagraph] = Field(
        ..., description="Details of unaligned target paragraphs"
    )
    similarity_matrix: AlignmentMatrix = Field(..., description="Complete similarity matrix")
    alignment_stats: dict[str, Any] = Field(..., description="Alignment statistics")


class AlignmentResponse(BaseModel):
    """Response model for semantic alignment"""

    success: bool
    alignment_result: AlignmentResult | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    processing_metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingRequest(BaseModel):
    """Request for generating embeddings"""

    model_config = ConfigDict(protected_namespaces=())

    texts: list[str] = Field(..., description="Texts to generate embeddings for")
    model_name: str = Field(
        "neuralmind/bert-base-portuguese-cased", description="Model to use for embeddings"
    )
    normalize: bool = Field(True, description="Whether to normalize embeddings")


class EmbeddingResponse(BaseModel):
    """Response for embeddings"""

    model_config = ConfigDict(protected_namespaces=())

    embeddings: list[list[float]] = Field(..., description="Generated embeddings")
    model_used: str = Field(..., description="Model used for generation")
    embedding_dim: int = Field(..., description="Dimension of embeddings")
    processing_time: float = Field(..., description="Time taken to generate embeddings")


class AlignmentConfiguration(BaseModel):
    """Configuration for alignment process"""

    bertimbau_model: str = Field(
        "neuralmind/bert-base-portuguese-cased", description="BERTimbau model to use"
    )
    similarity_threshold: float = Field(0.5, description="Default similarity threshold")
    max_sequence_length: int = Field(512, description="Maximum sequence length for BERT")
    batch_size: int = Field(8, description="Batch size for processing")
    device: str = Field("cpu", description="Device to use (cpu/cuda)")
    cache_embeddings: bool = Field(True, description="Whether to cache embeddings")
    confidence_thresholds: dict[str, float] = Field(
        default_factory=lambda: {"high": 0.8, "medium": 0.6, "low": 0.3},
        description="Thresholds for confidence levels",
    )

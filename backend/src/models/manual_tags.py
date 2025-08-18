"""Manual Tag Models for Sentence-Level User Annotations
User-created tags that persist across sessions
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ManualTagType(str, Enum):
    """Available manual tag types (subset of feature extraction tags for manual use)"""
    AS_PLUS = "AS+"  # Alteração de Sentido
    DL_PLUS = "DL+"  # Reorganização Posicional  
    EXP_PLUS = "EXP+"  # Explicitação e Detalhamento
    IN_PLUS = "IN+"  # Manejo de Inserções
    MOD_PLUS = "MOD+"  # Reinterpretação Perspectiva
    MT_PLUS = "MT+"  # Otimização de Títulos
    OM_PLUS = "OM+"  # Supressão Seletiva
    PRO_PLUS = "PRO+"  # Desvio Semântico
    RF_PLUS = "RF+"  # Reescrita Global
    RD_PLUS = "RD+"  # Estruturação de Conteúdo e Fluxo
    RP_PLUS = "RP+"  # Fragmentação Sintática
    SL_PLUS = "SL+"  # Adequação de Vocabulário
    TA_PLUS = "TA+"  # Clareza Referencial
    MV_PLUS = "MV+"  # Alteração da Voz Verbal


class ManualTag(BaseModel):
    """Manual tag annotation for a sentence"""
    id: str = Field(description="Unique tag ID")
    tag_type: ManualTagType = Field(description="Tag type")
    sentence_index: int = Field(description="Index of the sentence in target text")
    sentence_text: str = Field(description="Text of the tagged sentence")
    analysis_id: str = Field(description="ID of the analysis session this tag belongs to")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Manual tags have 100% confidence")
    evidence: List[str] = Field(default_factory=lambda: ["Manually added by human validator"])
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user_notes: Optional[str] = Field(default=None, description="Optional user notes")


class CreateTagRequest(BaseModel):
    """Request to create a new manual tag"""
    tag_type: ManualTagType = Field(description="Tag type to add")
    sentence_index: int = Field(ge=0, description="Index of the sentence to tag")
    sentence_text: str = Field(min_length=1, description="Text of the sentence being tagged")
    analysis_id: str = Field(description="ID of the current analysis session")
    user_notes: Optional[str] = Field(default=None, description="Optional user notes")


class UpdateTagRequest(BaseModel):
    """Request to update an existing manual tag"""
    tag_type: Optional[ManualTagType] = Field(default=None, description="New tag type")
    user_notes: Optional[str] = Field(default=None, description="Updated user notes")


class TagResponse(BaseModel):
    """Response containing tag information"""
    success: bool = Field(default=True)
    tag: Optional[ManualTag] = Field(default=None)
    message: str = Field(default="Operation successful")


class TagListResponse(BaseModel):
    """Response containing list of tags"""
    success: bool = Field(default=True)
    tags: List[ManualTag] = Field(default_factory=list)
    total_count: int = Field(default=0)
    analysis_id: str = Field(description="Analysis ID these tags belong to")


class DeleteTagResponse(BaseModel):
    """Response for tag deletion"""
    success: bool = Field(default=True)
    message: str = Field(default="Tag deleted successfully")
    deleted_tag_id: Optional[str] = Field(default=None)
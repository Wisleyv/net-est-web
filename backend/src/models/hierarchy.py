"""Hierarchical Analysis Data Models (Milestone M2)
Defines hierarchical nodes for paragraph → sentence → (future) micro-span.
Backwards compatible: existing ComparativeAnalysisResponse unchanged unless
hierarchical_output flag triggers inclusion in extended response (to be wired in service layer).
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MicroSpanNode(BaseModel):
    span_id: str
    text: str
    start: int
    end: int
    salience: float | None = Field(None, ge=0.0, le=1.0)
    strategies: List[str] = Field(default_factory=list)


class SentenceNode(BaseModel):
    sentence_id: str
    index: int
    text: str
    salience: float | None = Field(None, ge=0.0, le=1.0)
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    alignment: Dict[str, Any] | None = None  # {target_indices, relation, similarity}
    micro_spans: List[MicroSpanNode] = Field(default_factory=list)
    strategies: List[str] = Field(default_factory=list)


class ParagraphNode(BaseModel):
    paragraph_id: str
    index: int
    role: str = Field(..., pattern="^(source|target)$")
    text: str
    salience: float | None = Field(None, ge=0.0, le=1.0)
    sentences: List[SentenceNode] = Field(default_factory=list)
    alignment: Dict[str, Any] | None = None  # {partner_index, similarity, confidence}
    strategies: List[str] = Field(default_factory=list)


class HierarchicalAnalysis(BaseModel):
    hierarchy_version: str = "1.1"
    source_paragraphs: List[ParagraphNode]
    target_paragraphs: List[ParagraphNode]
    metadata: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "ParagraphNode",
    "SentenceNode",
    "MicroSpanNode",
    "HierarchicalAnalysis",
]

# Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime, timezone
import uuid

AnnotationStatus = Literal['pending','accepted','rejected','modified','created']

class Offset(BaseModel):
    start: int
    end: int

class Annotation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_code: str
    source_offsets: Optional[List[Offset]] = None
    target_offsets: Optional[List[Offset]] = None
    confidence: Optional[float] = None
    origin: Literal['machine','human'] = 'machine'
    status: AnnotationStatus = 'pending'
    original_code: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None
    evidence: Optional[List[str]] = None
    comment: Optional[str] = None

class AnnotationAction(BaseModel):
    action: Literal['accept','reject','modify']
    session_id: str
    new_code: Optional[str] = None

class AnnotationResponse(BaseModel):
    annotation: Annotation

class AnnotationsList(BaseModel):
    annotations: List[Annotation]

class AuditEntry(BaseModel):
    annotation_id: str
    action: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    from_code: Optional[str] = None
    to_code: Optional[str] = None

class AnnotationCreate(BaseModel):
    strategy_code: str
    target_offsets: List[Offset]
    origin: Literal['human'] = 'human'
    status: Literal['created'] = 'created'
    comment: Optional[str] = None

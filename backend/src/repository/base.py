from __future__ import annotations
from typing import Protocol, List, Optional, Iterable
from abc import abstractmethod
from src.models.annotation import Annotation, AuditEntry

class AnnotationRepository(Protocol):
    """Abstract repository for annotations & audit log.
    Future backends (SQLite, etc.) must honor these contracts.
    All methods are synchronous for simplicity; async wrapper can be added later.
    """
    # Annotation CRUD / lifecycle
    @abstractmethod
    def load_session(self, session_id: str) -> None: ...
    @abstractmethod
    def persist_session(self, session_id: str) -> None: ...
    @abstractmethod
    def list_visible(self) -> List[Annotation]: ...
    @abstractmethod
    def get(self, annotation_id: str) -> Optional[Annotation]: ...
    @abstractmethod
    def accept(self, annotation_id: str, session_id: str) -> Annotation: ...
    @abstractmethod
    def reject(self, annotation_id: str, session_id: str) -> Annotation: ...
    @abstractmethod
    def modify(self, annotation_id: str, session_id: str, new_code: str) -> Annotation: ...
    @abstractmethod
    def create(self, session_id: str, strategy_code: str, target_offsets: List[dict], comment: Optional[str] = None) -> Annotation: ...

    # Audit
    @abstractmethod
    def list_audit(self, annotation_id: Optional[str] = None, actions: Optional[List[str]] = None, session_id: Optional[str] = None) -> List[AuditEntry]: ...
    @abstractmethod
    def export(self, include_statuses: Optional[List[str]] = None) -> List[Annotation]: ...

    # Filtered queries (Phase 4b support)
    @abstractmethod
    def query(self, statuses: Optional[List[str]] = None, strategy_codes: Optional[List[str]] = None, session_id: Optional[str] = None) -> List[Annotation]: ...

    # Future extension points (placeholder):
    # def search_audit(self, filters: dict) -> Iterable[AuditEntry]: ...

__all__ = ["AnnotationRepository"]

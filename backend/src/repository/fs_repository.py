from __future__ import annotations
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime, timezone
from src.models.annotation import Annotation, AuditEntry, Offset
from src.repository.base import AnnotationRepository
from src.core.config import settings
from src.repository.sqlite_repository import SQLiteAnnotationRepository
from src.services.explanation_generator import generate_explanation

DATA_DIR = Path(__file__).parent.parent / 'data' / 'annotations'
DATA_DIR.mkdir(parents=True, exist_ok=True)

class FSAnnotationRepository(AnnotationRepository):
    def __init__(self):
        # In-memory collections (per-process)
        self._annotations: Dict[str, Annotation] = {}
        self._audit: List[AuditEntry] = []
        self._current_session = None  # current active session id

    # Session persistence
    def load_session(self, session_id: str) -> None:
        path = DATA_DIR / f'{session_id}.json'
        # If already on this session and we have in-memory state, keep it.
        if self._current_session == session_id and (self._annotations or self._audit):
            return
        # Switch active session; reset in-memory state when session changes
        if self._current_session != session_id:
            self._annotations = {}
            self._audit = []
        self._current_session = session_id
        if path.exists():
            raw = json.loads(path.read_text(encoding='utf-8'))
            self._annotations = {a['id']: Annotation(**a) for a in raw.get('annotations', [])}
            self._audit = [AuditEntry(**e) for e in raw.get('audit', [])]
        # If no file exists we intentionally keep whatever is currently
        # in memory (tests may have pre-seeded data) to avoid losing
        # fixtures before first persistence.

    def persist_session(self, session_id: str) -> None:
        path = DATA_DIR / f'{session_id}.json'
        def convert(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, list):
                return [convert(x) for x in obj]
            if isinstance(obj, dict):
                return {k: convert(v) for k,v in obj.items()}
            return obj
        payload = {
            'annotations': convert([a.model_dump() for a in self._annotations.values()]),
            'audit': convert([e.model_dump() for e in self._audit])
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    # Queries
    def list_visible(self) -> List[Annotation]:
        return [a for a in self._annotations.values() if a.status != 'rejected']

    def get(self, annotation_id: str) -> Optional[Annotation]:
        return self._annotations.get(annotation_id)

    # Lifecycle operations
    def accept(self, annotation_id: str, session_id: str) -> Annotation:
        ann = self._annotations.get(annotation_id)
        if not ann:
            raise KeyError('annotation_not_found')
        if ann.status == 'modified':
            raise ValueError('cannot_accept_modified')
        from_status = ann.status
        ann.status = 'accepted'
        ann.validated = True
        ann.updated_at = datetime.now(timezone.utc)
        ann.updated_by = session_id
        if not ann.explanation:
            ann.explanation = generate_explanation(ann)
        self._audit.append(AuditEntry(annotation_id=ann.id, action='accept', session_id=session_id, from_status=from_status, to_status=ann.status, from_code=ann.strategy_code, to_code=ann.strategy_code))
        return ann

    def reject(self, annotation_id: str, session_id: str) -> Annotation:
        ann = self._annotations.get(annotation_id)
        if not ann:
            raise KeyError('annotation_not_found')
        from_status = ann.status
        ann.status = 'rejected'
        ann.validated = False
        ann.updated_at = datetime.now(timezone.utc)
        ann.updated_by = session_id
        self._audit.append(AuditEntry(annotation_id=ann.id, action='reject', session_id=session_id, from_status=from_status, to_status=ann.status, from_code=ann.strategy_code, to_code=ann.strategy_code))
        return ann

    def modify(self, annotation_id: str, session_id: str, new_code: str) -> Annotation:
        ann = self._annotations.get(annotation_id)
        if not ann:
            raise KeyError('annotation_not_found')
        if not new_code or not isinstance(new_code, str):
            raise ValueError('invalid_new_code')
        from_status = ann.status
        if ann.original_code is None:
            ann.original_code = ann.strategy_code
        ann.strategy_code = new_code
        ann.status = 'modified'
        ann.validated = False
        ann.updated_at = datetime.now(timezone.utc)
        ann.updated_by = session_id
        ann.explanation = generate_explanation(ann)
        self._audit.append(
            AuditEntry(
                annotation_id=ann.id,
                action='modify',
                session_id=session_id,
                from_status=from_status,
                to_status=ann.status,
                from_code=ann.original_code,
                to_code=ann.strategy_code,
            )
        )
        return ann

    def create(self, session_id: str, strategy_code: str, target_offsets: List[dict], comment: Optional[str] = None) -> Annotation:
        offsets = [Offset(**o) if not isinstance(o, Offset) else o for o in target_offsets]
        ann = Annotation(strategy_code=strategy_code, target_offsets=offsets, origin='human', status='created', comment=comment, manually_assigned=True, validated=False)
        ann.explanation = generate_explanation(ann)
        self._annotations[ann.id] = ann
        self._audit.append(AuditEntry(annotation_id=ann.id, action='create', session_id=session_id, from_status=None, to_status=ann.status, from_code=None, to_code=ann.strategy_code))
        return ann

    # External synchronization helper (used by dual-write when FS acts as mirror)
    def sync_from_action(self, ann: Annotation, action: str, session_id: str,
                         from_status: Optional[str], to_status: Optional[str],
                         from_code: Optional[str], to_code: Optional[str]) -> None:
        # Ensure session is active
        if self._current_session != session_id:
            self.load_session(session_id)
        # Upsert annotation snapshot
        self._annotations[ann.id] = ann
        # Append audit entry
        self._audit.append(AuditEntry(
            annotation_id=ann.id,
            action=action,
            session_id=session_id,
            from_status=from_status,
            to_status=to_status,
            from_code=from_code,
            to_code=to_code,
        ))

    # Audit / export
    def list_audit(self, annotation_id: Optional[str] = None, actions: Optional[List[str]] = None, session_id: Optional[str] = None) -> List[AuditEntry]:
        if session_id and session_id != self._current_session:
            self.load_session(session_id)
        logs = self._audit
        if annotation_id is not None:
            logs = [e for e in logs if e.annotation_id == annotation_id]
        if actions:
            s = set(actions)
            logs = [e for e in logs if e.action in s]
        return list(logs)

    def export(self, include_statuses: Optional[List[str]] = None) -> List[Annotation]:
        allowed = include_statuses or ['accepted','modified','created']
        return [a for a in self._annotations.values() if a.status in allowed]

    # Filtered query
    def query(self, statuses: Optional[List[str]] = None, strategy_codes: Optional[List[str]] = None, session_id: Optional[str] = None) -> List[Annotation]:
        if session_id and session_id != self._current_session:
            self.load_session(session_id)
        anns = list(self._annotations.values())
        if statuses:
            s = set(statuses)
            anns = [a for a in anns if a.status in s]
        if strategy_codes:
            c = set(strategy_codes)
            anns = [a for a in anns if a.strategy_code in c]
        return anns

class DualWriteRepository(AnnotationRepository):
    """Shadow-writes to SQLite while keeping FS as the source of truth.

    Reads are always served from FS. Writes go to FS and mirrored to SQLite.
    This is feature-flag controlled via settings.ENABLE_DUAL_WRITE.
    """

    def __init__(self, fs_repo: FSAnnotationRepository, sqlite_repo: SQLiteAnnotationRepository):
        self.fs = fs_repo
        self.db = sqlite_repo

    # Session
    def load_session(self, session_id: str) -> None:
        self.fs.load_session(session_id)
        # keep sqlite session in sync for queries/exports if used directly
        self.db.load_session(session_id)

    def persist_session(self, session_id: str) -> None:
        self.fs.persist_session(session_id)
        # sqlite is already durable; nothing required

    # Queries use FS only
    def list_visible(self):
        return self.fs.list_visible()

    def get(self, annotation_id: str):
        return self.fs.get(annotation_id)

    # Mutations mirror to DB via sync_from_action helper
    def accept(self, annotation_id: str, session_id: str):
        before = self.fs.get(annotation_id)
        ann = self.fs.accept(annotation_id, session_id)
        self.db.sync_from_action(ann, 'accept', session_id, getattr(before, 'status', None), ann.status, ann.strategy_code, ann.strategy_code)
        return ann

    def reject(self, annotation_id: str, session_id: str):
        before = self.fs.get(annotation_id)
        ann = self.fs.reject(annotation_id, session_id)
        self.db.sync_from_action(ann, 'reject', session_id, getattr(before, 'status', None), ann.status, ann.strategy_code, ann.strategy_code)
        return ann

    def modify(self, annotation_id: str, session_id: str, new_code: str):
        before = self.fs.get(annotation_id)
        ann = self.fs.modify(annotation_id, session_id, new_code)
        self.db.sync_from_action(ann, 'modify', session_id, getattr(before, 'status', None), ann.status, getattr(before, 'original_code', None) or getattr(before, 'strategy_code', None), ann.strategy_code)
        return ann

    def create(self, session_id: str, strategy_code: str, target_offsets: List[dict], comment: Optional[str] = None):
        ann = self.fs.create(session_id, strategy_code, target_offsets, comment)
        self.db.sync_from_action(ann, 'create', session_id, None, ann.status, None, ann.strategy_code)
        return ann

    # Audit / export via FS
    def list_audit(self, annotation_id: Optional[str] = None, actions: Optional[List[str]] = None, session_id: Optional[str] = None):
        return self.fs.list_audit(annotation_id, actions=actions, session_id=session_id)

    def export(self, include_statuses: Optional[List[str]] = None):
        return self.fs.export(include_statuses)

    def query(self, statuses: Optional[List[str]] = None, strategy_codes: Optional[List[str]] = None, session_id: Optional[str] = None):
        return self.fs.query(statuses, strategy_codes, session_id)


class DualWriteSQLitePrimary(AnnotationRepository):
    """SQLite as primary; mirror writes to FS for safety. Reads use SQLite.
    Used when PERSISTENCE_BACKEND=sqlite and ENABLE_DUAL_WRITE=true.
    """

    def __init__(self, sqlite_repo: SQLiteAnnotationRepository, fs_repo: FSAnnotationRepository):
        self.db = sqlite_repo
        self.fs = fs_repo

    def load_session(self, session_id: str) -> None:
        self.db.load_session(session_id)
        self.fs.load_session(session_id)

    def persist_session(self, session_id: str) -> None:
        # DB is durable; persist FS mirror for completeness
        self.fs.persist_session(session_id)

    # Reads from DB
    def list_visible(self):
        return self.db.list_visible()

    def get(self, annotation_id: str):
        return self.db.get(annotation_id)

    # Writes to DB and mirror to FS via sync
    def accept(self, annotation_id: str, session_id: str):
        before = self.db.get(annotation_id)
        ann = self.db.accept(annotation_id, session_id)
        self.fs.sync_from_action(ann, 'accept', session_id, getattr(before, 'status', None), ann.status, ann.strategy_code, ann.strategy_code)
        self.fs.persist_session(session_id)
        return ann

    def reject(self, annotation_id: str, session_id: str):
        before = self.db.get(annotation_id)
        ann = self.db.reject(annotation_id, session_id)
        self.fs.sync_from_action(ann, 'reject', session_id, getattr(before, 'status', None), ann.status, ann.strategy_code, ann.strategy_code)
        self.fs.persist_session(session_id)
        return ann

    def modify(self, annotation_id: str, session_id: str, new_code: str):
        before = self.db.get(annotation_id)
        ann = self.db.modify(annotation_id, session_id, new_code)
        self.fs.sync_from_action(ann, 'modify', session_id, getattr(before, 'status', None), ann.status, getattr(before, 'original_code', None) or getattr(before, 'strategy_code', None), ann.strategy_code)
        self.fs.persist_session(session_id)
        return ann

    def create(self, session_id: str, strategy_code: str, target_offsets: List[dict], comment: Optional[str] = None):
        ann = self.db.create(session_id, strategy_code, target_offsets, comment)
        self.fs.sync_from_action(ann, 'create', session_id, None, ann.status, None, ann.strategy_code)
        self.fs.persist_session(session_id)
        return ann

    def list_audit(self, annotation_id: Optional[str] = None, actions: Optional[List[str]] = None, session_id: Optional[str] = None):
        return self.db.list_audit(annotation_id, actions=actions, session_id=session_id)

    def export(self, include_statuses: Optional[List[str]] = None):
        return self.db.export(include_statuses)

    def query(self, statuses: Optional[List[str]] = None, strategy_codes: Optional[List[str]] = None, session_id: Optional[str] = None):
        return self.db.query(statuses, strategy_codes, session_id)


class FallbackRepository(AnnotationRepository):
    """Wrap a primary repo with a fallback for resilience. On failure, use fallback.
    Intended for SQLite primary with FS fallback in read paths; will also write to
    fallback if primary write fails.
    """
    def __init__(self, primary: AnnotationRepository, fallback: AnnotationRepository):
        self.primary = primary
        self.fallback = fallback

    def _try(self, fn_primary, fn_fallback, *args, **kwargs):
        try:
            return fn_primary(*args, **kwargs)
        except Exception:
            return fn_fallback(*args, **kwargs)

    def load_session(self, session_id: str) -> None:
        # Load both to keep caches coherent
        try:
            self.primary.load_session(session_id)
        finally:
            try:
                self.fallback.load_session(session_id)
            except Exception:
                pass

    def persist_session(self, session_id: str) -> None:
        try:
            self.primary.persist_session(session_id)
        finally:
            try:
                self.fallback.persist_session(session_id)
            except Exception:
                pass

    # Reads
    def list_visible(self):
        return self._try(self.primary.list_visible, self.fallback.list_visible)

    def get(self, annotation_id: str):
        return self._try(self.primary.get, self.fallback.get, annotation_id)

    def list_audit(self, annotation_id: Optional[str] = None, actions: Optional[List[str]] = None, session_id: Optional[str] = None):
        return self._try(self.primary.list_audit, self.fallback.list_audit, annotation_id, actions, session_id)

    def export(self, include_statuses: Optional[List[str]] = None):
        return self._try(self.primary.export, self.fallback.export, include_statuses)

    def query(self, statuses: Optional[List[str]] = None, strategy_codes: Optional[List[str]] = None, session_id: Optional[str] = None):
        return self._try(self.primary.query, self.fallback.query, statuses, strategy_codes, session_id)

    # Writes
    def accept(self, annotation_id: str, session_id: str):
        try:
            return self.primary.accept(annotation_id, session_id)
        except Exception:
            return self.fallback.accept(annotation_id, session_id)

    def reject(self, annotation_id: str, session_id: str):
        try:
            return self.primary.reject(annotation_id, session_id)
        except Exception:
            return self.fallback.reject(annotation_id, session_id)

    def modify(self, annotation_id: str, session_id: str, new_code: str):
        try:
            return self.primary.modify(annotation_id, session_id, new_code)
        except Exception:
            return self.fallback.modify(annotation_id, session_id, new_code)

    def create(self, session_id: str, strategy_code: str, target_offsets: List[dict], comment: Optional[str] = None):
        try:
            return self.primary.create(session_id, strategy_code, target_offsets, comment)
        except Exception:
            return self.fallback.create(session_id, strategy_code, target_offsets, comment)


# Factory: choose repo based on env settings
_REPO: AnnotationRepository | None = None

def reset_repository() -> None:
    """Reset the process-wide repository singleton (for tests).

    Allows tests to switch persistence modes by clearing the cached instance.
    """
    global _REPO
    _REPO = None

def get_repository() -> AnnotationRepository:
    """Return process-wide singleton repository based on settings.
    Defaults to FS. If PERSISTENCE_BACKEND=sqlite, return SQLite repo.
    If ENABLE_DUAL_WRITE=true, return DualWrite with FS primary and DB shadow.
    """
    global _REPO
    if _REPO is not None:
        return _REPO

    backend = (settings.PERSISTENCE_BACKEND or 'fs').lower()
    if backend == 'sqlite':
        db_path = settings.SQLITE_DB_PATH
        sqlite_repo = SQLiteAnnotationRepository(db_path)
        if settings.ENABLE_DUAL_WRITE:
            fs_repo = FSAnnotationRepository()
            primary = DualWriteSQLitePrimary(sqlite_repo, fs_repo)
        else:
            primary = sqlite_repo
        if settings.ENABLE_FS_FALLBACK:
            # Reuse fs_repo if created
            fs_repo = fs_repo if 'fs_repo' in locals() else FSAnnotationRepository()
            _REPO = FallbackRepository(primary, fs_repo)
        else:
            _REPO = primary
        return _REPO

    # default FS
    fs_repo = FSAnnotationRepository()
    if settings.ENABLE_DUAL_WRITE:
        db_repo = SQLiteAnnotationRepository(settings.SQLITE_DB_PATH)
        _REPO = DualWriteRepository(fs_repo, db_repo)
    else:
        _REPO = fs_repo
    return _REPO

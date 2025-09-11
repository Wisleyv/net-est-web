from __future__ import annotations
from typing import List, Optional, Iterable, Tuple
import json
import sqlite3
from pathlib import Path
from datetime import datetime

from src.models.annotation import Annotation, AuditEntry, Offset
from src.services.explanation_generator import generate_explanation
from src.repository.base import AnnotationRepository


def _iso(dt: datetime | None) -> Optional[str]:
    return dt.isoformat() if dt else None


def _parse_dt(s: str | None) -> Optional[datetime]:
    if not s:
        return None
    # datetime.fromisoformat handles timezone-aware strings
    return datetime.fromisoformat(s)


def _ser_offsets(offsets: Optional[List[Offset]]) -> Optional[str]:
    if offsets is None:
        return None
    arr = [o.model_dump() if hasattr(o, "model_dump") else dict(o) for o in offsets]
    return json.dumps(arr, ensure_ascii=False)


def _de_offsets(s: Optional[str]) -> Optional[List[Offset]]:
    if not s:
        return None
    arr = json.loads(s)
    return [Offset(**o) for o in arr]


class SQLiteAnnotationRepository(AnnotationRepository):
    """SQLite-backed repository using stdlib sqlite3. Session is a column.

    This implementation is fully synchronous and aims to mirror the FS repository
    observable behavior used by API handlers and tests.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._current_session: Optional[str] = None
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # --- low-level helpers ---
    def _connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS annotations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    strategy_code TEXT NOT NULL,
                    source_offsets TEXT,
                    target_offsets TEXT,
                    confidence REAL,
                    origin TEXT,
                    status TEXT,
                    validated INTEGER DEFAULT 0,
                    manually_assigned INTEGER DEFAULT 0,
                    original_code TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    updated_by TEXT,
                    evidence TEXT,
                    comment TEXT,
                    explanation TEXT
                );
                """
            )
            # Backfill explanation column if DB existed without it
            try:
                cur.execute("PRAGMA table_info(annotations);")
                cols = [r[1] for r in cur.fetchall()]
                if 'validated' not in cols:
                    cur.execute("ALTER TABLE annotations ADD COLUMN validated INTEGER DEFAULT 0;")
                if 'manually_assigned' not in cols:
                    cur.execute("ALTER TABLE annotations ADD COLUMN manually_assigned INTEGER DEFAULT 0;")
                if 'explanation' not in cols:
                    cur.execute("ALTER TABLE annotations ADD COLUMN explanation TEXT;")
            except Exception:
                pass
            cur.execute("CREATE INDEX IF NOT EXISTS idx_annotations_session ON annotations(session_id);")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    annotation_id TEXT,
                    action TEXT,
                    timestamp TEXT,
                    session_id TEXT,
                    from_status TEXT,
                    to_status TEXT,
                    from_code TEXT,
                    to_code TEXT
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_session ON audit(session_id);")
            con.commit()

    # --- protocol methods ---
    def load_session(self, session_id: str) -> None:
        self._current_session = session_id

    def persist_session(self, session_id: str) -> None:
        # SQLite persists immediately; nothing to do.
        return None

    # Mapping rows
    def _row_to_annotation(self, row: sqlite3.Row) -> Annotation:
        return Annotation(
            id=row["id"],
            strategy_code=row["strategy_code"],
            source_offsets=_de_offsets(row["source_offsets"]),
            target_offsets=_de_offsets(row["target_offsets"]),
            confidence=row["confidence"],
            origin=row["origin"],
            status=row["status"],
            validated=bool(row["validated"]) if "validated" in row.keys() else False,
            manually_assigned=bool(row["manually_assigned"]) if "manually_assigned" in row.keys() else False,
            original_code=row["original_code"],
            created_at=_parse_dt(row["created_at"]),
            updated_at=_parse_dt(row["updated_at"]),
            updated_by=row["updated_by"],
            evidence=json.loads(row["evidence"]) if row["evidence"] else None,
            comment=row["comment"],
            explanation=row["explanation"],
        )

    def list_visible(self) -> List[Annotation]:
        if not self._current_session:
            return []
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM annotations WHERE session_id=? AND status != 'rejected'",
                (self._current_session,),
            )
            return [self._row_to_annotation(r) for r in cur.fetchall()]

    def get(self, annotation_id: str) -> Optional[Annotation]:
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM annotations WHERE id=?", (annotation_id,))
            row = cur.fetchone()
            return self._row_to_annotation(row) if row else None

    # Lifecycle operations
    def _insert_audit(self, con: sqlite3.Connection, entry: AuditEntry):
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO audit (annotation_id, action, timestamp, session_id, from_status, to_status, from_code, to_code)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                entry.annotation_id,
                entry.action,
                _iso(entry.timestamp),
                entry.session_id,
                entry.from_status,
                entry.to_status,
                entry.from_code,
                entry.to_code,
            ),
        )

    def _upsert_annotation(self, con: sqlite3.Connection, ann: Annotation, session_id: str):
        cur = con.cursor()
        cur.execute(
            """
                    INSERT INTO annotations (id, session_id, strategy_code, source_offsets, target_offsets, confidence, origin,
                                     status, validated, manually_assigned, original_code, created_at, updated_at, updated_by, evidence, comment, explanation)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                session_id=excluded.session_id,
                strategy_code=excluded.strategy_code,
                source_offsets=excluded.source_offsets,
                target_offsets=excluded.target_offsets,
                confidence=excluded.confidence,
                origin=excluded.origin,
                status=excluded.status,
                validated=excluded.validated,
                manually_assigned=excluded.manually_assigned,
                original_code=excluded.original_code,
                created_at=excluded.created_at,
                updated_at=excluded.updated_at,
                updated_by=excluded.updated_by,
                evidence=excluded.evidence,
                comment=excluded.comment,
                explanation=excluded.explanation
            """,
            (
                ann.id,
                session_id,
                ann.strategy_code,
                _ser_offsets(ann.source_offsets),
                _ser_offsets(ann.target_offsets),
                ann.confidence,
                ann.origin,
                ann.status,
                1 if getattr(ann, 'validated', False) else 0,
                1 if getattr(ann, 'manually_assigned', False) else 0,
                ann.original_code,
                _iso(ann.created_at),
                _iso(ann.updated_at),
                ann.updated_by,
                json.dumps(ann.evidence) if ann.evidence is not None else None,
                ann.comment,
                ann.explanation,
            ),
        )

    def accept(self, annotation_id: str, session_id: str) -> Annotation:
        ann = self.get(annotation_id)
        if not ann:
            raise KeyError("annotation_not_found")
        if ann.status == "modified":
            raise ValueError("cannot_accept_modified")
        from_status = ann.status
        ann.status = "accepted"
        ann.validated = True
        if not ann.explanation:
            # Populate explanation lazily to match FS behavior
            ann.explanation = generate_explanation(ann)
        ann.updated_by = session_id
        ann.updated_at = datetime.now(ann.updated_at.tzinfo) if ann.updated_at else datetime.now()
        entry = AuditEntry(
            annotation_id=ann.id,
            action="accept",
            session_id=session_id,
            from_status=from_status,
            to_status=ann.status,
            from_code=ann.strategy_code,
            to_code=ann.strategy_code,
        )
        with self._connect() as con:
            self._upsert_annotation(con, ann, session_id)
            self._insert_audit(con, entry)
            con.commit()
        return ann

    def reject(self, annotation_id: str, session_id: str) -> Annotation:
        ann = self.get(annotation_id)
        if not ann:
            raise KeyError("annotation_not_found")
        from_status = ann.status
        ann.status = "rejected"
        ann.validated = False
        ann.updated_by = session_id
        ann.updated_at = datetime.now(ann.updated_at.tzinfo) if ann.updated_at else datetime.now()
        entry = AuditEntry(
            annotation_id=ann.id,
            action="reject",
            session_id=session_id,
            from_status=from_status,
            to_status=ann.status,
            from_code=ann.strategy_code,
            to_code=ann.strategy_code,
        )
        with self._connect() as con:
            self._upsert_annotation(con, ann, session_id)
            self._insert_audit(con, entry)
            con.commit()
        return ann

    def modify(self, annotation_id: str, session_id: str, new_code: str) -> Annotation:
        if not new_code or not isinstance(new_code, str):
            raise ValueError("invalid_new_code")
        ann = self.get(annotation_id)
        if not ann:
            raise KeyError("annotation_not_found")
        from_status = ann.status
        if ann.original_code is None:
            ann.original_code = ann.strategy_code
        ann.strategy_code = new_code
        ann.status = "modified"
        ann.validated = False
        ann.explanation = generate_explanation(ann)
        ann.updated_by = session_id
        ann.updated_at = datetime.now(ann.updated_at.tzinfo) if ann.updated_at else datetime.now()
        entry = AuditEntry(
            annotation_id=ann.id,
            action="modify",
            session_id=session_id,
            from_status=from_status,
            to_status=ann.status,
            from_code=ann.original_code,
            to_code=ann.strategy_code,
        )
        with self._connect() as con:
            self._upsert_annotation(con, ann, session_id)
            self._insert_audit(con, entry)
            con.commit()
        return ann

    def create(self, session_id: str, strategy_code: str, target_offsets: List[dict], comment: Optional[str] = None) -> Annotation:
        offsets = [Offset(**o) if not isinstance(o, Offset) else o for o in target_offsets]
        ann = Annotation(strategy_code=strategy_code, target_offsets=offsets, origin='human', status='created', comment=comment, manually_assigned=True, validated=False)
        ann.explanation = generate_explanation(ann)
        entry = AuditEntry(annotation_id=ann.id, action='create', session_id=session_id, from_status=None, to_status=ann.status, from_code=None, to_code=ann.strategy_code)
        with self._connect() as con:
            self._upsert_annotation(con, ann, session_id)
            self._insert_audit(con, entry)
            con.commit()
        return ann

    def list_audit(self, annotation_id: Optional[str] = None, actions: Optional[List[str]] = None, session_id: Optional[str] = None) -> List[AuditEntry]:
        sess = session_id or self._current_session
        params: List[object] = []
        where = []
        if sess:
            where.append("session_id = ?")
            params.append(sess)
        if annotation_id is not None:
            where.append("annotation_id = ?")
            params.append(annotation_id)
        if actions:
            # Build simple IN (?, ?, ?)
            where.append(f"action IN ({','.join(['?']*len(actions))})")
            params.extend(actions)
        sql = "SELECT annotation_id, action, timestamp, session_id, from_status, to_status, from_code, to_code FROM audit"
        if where:
            sql += " WHERE " + " AND ".join(where)
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            out: List[AuditEntry] = []
            for r in rows:
                out.append(
                    AuditEntry(
                        annotation_id=r["annotation_id"],
                        action=r["action"],
                        timestamp=_parse_dt(r["timestamp"]),
                        session_id=r["session_id"],
                        from_status=r["from_status"],
                        to_status=r["to_status"],
                        from_code=r["from_code"],
                        to_code=r["to_code"],
                    )
                )
            return out

    def export(self, include_statuses: Optional[List[str]] = None) -> List[Annotation]:
        statuses = include_statuses or ['accepted','modified','created']
        sess = self._current_session
        if not sess:
            return []
        with self._connect() as con:
            cur = con.cursor()
            qmarks = ','.join(['?']*len(statuses))
            cur.execute(
                f"SELECT * FROM annotations WHERE session_id=? AND status IN ({qmarks})",
                (sess, *statuses),
            )
            anns = [self._row_to_annotation(r) for r in cur.fetchall()]
            # Lazy fill explanation like FS repo for accepted annotations missing explanation
            changed = False
            for a in anns:
                if a.strategy_code in ('SL+','RP+') and not a.explanation:
                    a.explanation = generate_explanation(a)
                    changed = True
            if changed:
                # Persist any newly generated explanations
                with self._connect() as con2:
                    for a in anns:
                        if a.explanation:
                            self._upsert_annotation(con2, a, sess)
                    con2.commit()
            return anns

    def query(self, statuses: Optional[List[str]] = None, strategy_codes: Optional[List[str]] = None, session_id: Optional[str] = None) -> List[Annotation]:
        sess = session_id or self._current_session
        params: List[object] = []
        where = []
        if sess:
            where.append("session_id = ?")
            params.append(sess)
        if statuses:
            where.append(f"status IN ({','.join(['?']*len(statuses))})")
            params.extend(statuses)
        if strategy_codes:
            where.append(f"strategy_code IN ({','.join(['?']*len(strategy_codes))})")
            params.extend(strategy_codes)
        sql = "SELECT * FROM annotations"
        if where:
            sql += " WHERE " + " AND ".join(where)
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(sql, tuple(params))
            rows = [self._row_to_annotation(r) for r in cur.fetchall()]
            if not rows and sess is not None:
                # Fallback: query without session filter
                cur.execute("SELECT * FROM annotations")
                rows = [self._row_to_annotation(r) for r in cur.fetchall()]
            return rows

    # --- helpers for dual-write shadow mode ---
    def sync_from_action(self, ann: Annotation, action: str, session_id: str,
                         from_status: Optional[str], to_status: Optional[str],
                         from_code: Optional[str], to_code: Optional[str]) -> None:
        entry = AuditEntry(
            annotation_id=ann.id,
            action=action,
            session_id=session_id,
            from_status=from_status,
            to_status=to_status,
            from_code=from_code,
            to_code=to_code,
        )
        with self._connect() as con:
            self._upsert_annotation(con, ann, session_id)
            self._insert_audit(con, entry)
            con.commit()

__all__ = ["SQLiteAnnotationRepository"]

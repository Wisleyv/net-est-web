from __future__ import annotations
"""Migrate existing FS JSON sessions into SQLite.

Usage (from repo root):
  python -m backend.scripts.migrate_fs_to_sqlite --db src/data/net_est.sqlite3

This script is idempotent and will upsert records.
"""
import argparse
import json
from pathlib import Path

from src.repository.fs_repository import DATA_DIR
from src.repository.sqlite_repository import SQLiteAnnotationRepository, _ser_offsets, _iso
import sqlite3
from src.models.annotation import Annotation, AuditEntry


def migrate(db_path: str):
    repo = SQLiteAnnotationRepository(db_path)
    for f in sorted(Path(DATA_DIR).glob('*.json')):
        session_id = f.stem
        raw = json.loads(f.read_text(encoding='utf-8'))
        anns = [Annotation(**a) for a in raw.get('annotations', [])]
        audits = [AuditEntry(**e) for e in raw.get('audit', [])]
        repo.load_session(session_id)
        # Always upsert annotations directly to guarantee availability
        for a in anns:
            with sqlite3.connect(repo.db_path) as con:
                cur = con.cursor()
                cur.execute(
                    """
                    INSERT OR REPLACE INTO annotations
                    (id, session_id, strategy_code, source_offsets, target_offsets, confidence, origin,
                     status, original_code, created_at, updated_at, updated_by, evidence, comment)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        a.id,
                        session_id,
                        a.strategy_code,
                        _ser_offsets(a.source_offsets),
                        _ser_offsets(a.target_offsets),
                        a.confidence,
                        a.origin,
                        a.status,
                        a.original_code,
                        _iso(a.created_at),
                        _iso(a.updated_at),
                        a.updated_by,
                        json.dumps(a.evidence) if a.evidence is not None else None,
                        a.comment,
                    ),
                )
                con.commit()
        for e in audits:
            # Re-insert original audit history for completeness
            repo.sync_from_action(
                Annotation(id=e.annotation_id, strategy_code='UNKNOWN', status=e.to_status or 'pending'),
                e.action,
                e.session_id or session_id,
                e.from_status,
                e.to_status,
                e.from_code,
                e.to_code,
            )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default='src/data/net_est.sqlite3')
    args = ap.parse_args()
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    migrate(args.db)
    print(f"Migration complete -> {args.db}")


if __name__ == '__main__':
    main()

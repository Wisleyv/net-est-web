from __future__ import annotations
import sys
import json
import csv
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from src.repository.fs_repository import get_repository
from src.models.annotation import Annotation, AuditEntry

def _iso(dt: datetime | None) -> Optional[str]:
    if dt is None:
        return None
    s = dt.astimezone().isoformat()
    # Normalize Z for UTC
    if s.endswith('+00:00'):
        s = s[:-6] + 'Z'
    return s

def _annotation_row(session_id: str, a: Annotation) -> dict:
    return {
        'id': a.id,
        'session_id': session_id,
        'strategy_code': a.strategy_code,
        'original_code': a.original_code,
        'status': a.status,
        'decision': a.status,
        'origin': a.origin,
        'confidence': a.confidence,
        'source_offsets': json.dumps([o.model_dump() for o in (a.source_offsets or [])], ensure_ascii=False) if a.source_offsets else None,
        'target_offsets': json.dumps([o.model_dump() for o in (a.target_offsets or [])], ensure_ascii=False) if a.target_offsets else None,
        'created_at': _iso(a.created_at),
        'updated_at': _iso(a.updated_at),
        'updated_by': a.updated_by,
        'evidence': json.dumps(a.evidence, ensure_ascii=False) if a.evidence else None,
        'comment': a.comment,
    # New in Phase 4f: include human-readable explanation/rationale when available
    'explanation': a.explanation,
        'validated': getattr(a, 'validated', False),
        'manually_assigned': getattr(a, 'manually_assigned', False),
    }

def export_annotations(session_id: str, fmt: str = 'jsonl', include_statuses: Optional[List[str]] = None, out_dir: str | Path = 'export', scope: str = 'both') -> Path:
    repo = get_repository()
    repo.load_session(session_id)
    if scope == 'gold':
        base = repo.export(include_statuses or ['accepted','created'])
        anns = [a for a in base if getattr(a, 'validated', False)]
    elif scope == 'raw':
        anns = repo.export(include_statuses or ['pending','modified'])
    else:
        anns = repo.export(include_statuses)
    # stable order
    anns.sort(key=lambda x: (x.created_at, x.id))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if fmt == 'jsonl':
        out_path = out_dir / f'{session_id}.annotations.jsonl'
        with out_path.open('w', encoding='utf-8') as f:
            for a in anns:
                row = _annotation_row(session_id, a)
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
        return out_path
    elif fmt == 'csv':
        out_path = out_dir / f'{session_id}.annotations.csv'
        rows = [_annotation_row(session_id, a) for a in anns]
        fieldnames = list(rows[0].keys()) if rows else [
            'id','session_id','strategy_code','original_code','status','decision','origin','confidence',
            'source_offsets','target_offsets','created_at','updated_at','updated_by','evidence','comment','explanation','validated','manually_assigned'
        ]
        with out_path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return out_path
    else:
        raise ValueError('unsupported_format')

def _audit_row(e: AuditEntry) -> dict:
    return {
        'annotation_id': e.annotation_id,
        'session_id': e.session_id,
        'action': e.action,
        'timestamp': _iso(e.timestamp),
        'from_status': e.from_status,
        'to_status': e.to_status,
        'from_code': e.from_code,
        'to_code': e.to_code,
    }

def export_audit(session_id: str, fmt: str = 'jsonl', out_dir: str | Path = 'export') -> Path:
    repo = get_repository()
    repo.load_session(session_id)
    events = repo.list_audit(session_id=session_id)
    # stable order by timestamp then annotation_id
    events.sort(key=lambda x: (x.timestamp, x.annotation_id))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if fmt == 'jsonl':
        out_path = out_dir / f'{session_id}.audit.jsonl'
        with out_path.open('w', encoding='utf-8') as f:
            for e in events:
                f.write(json.dumps(_audit_row(e), ensure_ascii=False) + '\n')
        return out_path
    elif fmt == 'csv':
        out_path = out_dir / f'{session_id}.audit.csv'
        rows = [_audit_row(e) for e in events]
        fieldnames = list(rows[0].keys()) if rows else ['annotation_id','session_id','action','timestamp','from_status','to_status','from_code','to_code']
        with out_path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return out_path
    else:
        raise ValueError('unsupported_format')

def main(argv: List[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description='NET-EST Export Tool')
    p.add_argument('--session', required=True, help='Session ID to export')
    p.add_argument('--type', choices=['annotations','audit'], default='annotations')
    p.add_argument('--format', choices=['jsonl','csv'], default='jsonl')
    p.add_argument('--out', default='export')
    p.add_argument('--scope', choices=['gold','raw','both'], default='both')
    p.add_argument('--statuses', nargs='*', default=None)
    args = p.parse_args(argv)
    if args.type == 'annotations':
        path = export_annotations(args.session, fmt=args.format, include_statuses=args.statuses, out_dir=args.out, scope=args.scope)
    else:
        path = export_audit(args.session, fmt=args.format, out_dir=args.out)
    print(str(path))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

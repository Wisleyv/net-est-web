from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import List, Optional

from src.repository.fs_repository import get_repository
from src.models.annotation import Offset


def _load_jsonl(path: Path) -> List[dict]:
    with path.open('r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def _load_csv(path: Path) -> List[dict]:
    with path.open('r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def import_annotations(session_id: str, path: str | Path, fmt: Optional[str] = None) -> int:
    repo = get_repository()
    repo.load_session(session_id)
    p = Path(path)
    fmt = fmt or ('jsonl' if p.suffix == '.jsonl' else 'csv')
    records = _load_jsonl(p) if fmt == 'jsonl' else _load_csv(p)
    count = 0
    for rec in records:
        code = rec.get('strategy_code') or rec.get('original_code')
        target = rec.get('target_offsets')
        if isinstance(target, str):
            try:
                target = json.loads(target)
            except Exception:
                target = []
        offsets = [o if isinstance(o, dict) else Offset(**o).model_dump() for o in (target or [])]
        ann = repo.create(session_id, code, offsets, rec.get('comment'))
        # Note: status transitions (accept/modify) can be applied here if needed; kept minimal for round-trip parity smoke.
        count += 1
    repo.persist_session(session_id)
    return count


def main(argv: List[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description='NET-EST Import Tool (round-trip)')
    p.add_argument('--session', required=True)
    p.add_argument('--file', required=True)
    p.add_argument('--format', choices=['jsonl','csv'], default=None)
    args = p.parse_args(argv)
    n = import_annotations(args.session, args.file, fmt=args.format)
    print(n)
    return 0


if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))

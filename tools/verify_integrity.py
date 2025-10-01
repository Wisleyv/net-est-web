"""Minimal repository integrity verification script.

Purpose:
  - Assert presence and Git tracking of critical infra files.
  - Validate JSON syntax of .vscode/tasks.json.
  - Exit non-zero if any invariant is violated.

Extend later with hashing, baseline diffs, or CI integration.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

CRITICAL_FILES = [
    Path('.vscode/tasks.json'),
    Path('docs_dev/development_guidelines.md'),
]

def is_tracked(path: Path) -> bool:
    try:
        # --error-unmatch returns non-zero if not tracked
        subprocess.run(['git', 'ls-files', '--error-unmatch', str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def validate_tasks_json(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            errors.append('tasks.json root must be an object')
        else:
            if 'version' not in data:
                errors.append('tasks.json missing version field')
            if 'tasks' not in data or not isinstance(data['tasks'], list):
                errors.append('tasks.json missing tasks array')
    except json.JSONDecodeError as e:
        errors.append(f'JSON decode error: {e}')
    except FileNotFoundError:
        errors.append('tasks.json file missing at validation phase')
    return errors


def main() -> int:
    problems: list[str] = []

    for f in CRITICAL_FILES:
        if not f.exists():
            problems.append(f'MISSING: {f}')
        else:
            if not is_tracked(f):
                problems.append(f'UNTRACKED: {f} (expected to be version-controlled)')

    tasks_path = Path('.vscode/tasks.json')
    if tasks_path.exists():
        problems.extend(validate_tasks_json(tasks_path))

    if problems:
        print('INTEGRITY CHECK FAILED:')
        for p in problems:
            print(f' - {p}')
        return 1
    print('INTEGRITY CHECK PASSED: critical files present, tracked, and structurally valid.')
    return 0

if __name__ == '__main__':
    sys.exit(main())

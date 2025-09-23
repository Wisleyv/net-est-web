# Next Session Plan

Date: 2025-09-18

## Session Summary
- Stabilization focus: we halted the environment to avoid further regressions.
- Backend state:
  - Legacy venv at `backend/venv` is unhealthy (Python 3.13.3, pip shim missing, pyvenv.cfg errors). Avoid using it.
  - Confirmed pinned interpreter requirement: use Python 3.12.7 at `C:\Python312\python.exe`.
  - Did not modify backend code; removed a temporary seeding script to prevent regressions: `backend/tmp_seed_repo.py`.
- Processes & ports:
  - Stopped lingering Python/Node processes (none left after targeted termination).
  - No evidence of servers listening on 8000/5173/3000 after cleanup.
- Caches:
  - Cleaned `__pycache__` across the workspace using the existing task.

## Artifacts Added
- VS Code tasks in `.vscode/tasks.json`:
  - "Stop Servers (safe)": stops python/node processes cleanly.
  - "Setup Py312 Venv (pinned)": creates/updates `backend/.venv_py312` using `C:\Python312\python.exe` and installs backend requirements.

## What Worked
- Process cleanup and cache cleanup tasks completed successfully.
- Added safe, minimal tasks to streamline future sessions while respecting the Python 3.12.7 constraint.

## Known Issues / Avoid
- Do not use `backend/venv` (points to Python 3.13.3 and is unstable in this setup).
- Avoid netstat/findstr dependent checks in tasks; the provided safe stop task doesn’t rely on them.

## Recommended Next Steps
1. Initialize the pinned venv (once):
   - Run the VS Code task: "Setup Py312 Venv (pinned)".
2. Sanity check backend imports in the pinned venv:
   - Optionally run backend unit tests via a 3.12 venv (can be added as a task if desired).
3. Start the backend using the 3.12 venv (future task suggestion):
   - Add/run a task that calls `${workspaceFolder}/backend/.venv_py312/Scripts/python.exe start_server.py`.
4. Re-test HITL UI flows with the backend up, focusing on:
   - Tag editing persistence and export (JSONL/CSV) using backend `src/tools/export.py`.
   - PDF export once backend is stable.
5. If exports are still empty:
   - Validate session file presence under `backend/src/data/annotations/<session>.json`.
   - Use `src/tools/export.py --session <id> --type annotations|audit` while backend is stopped (FS repo).

## Rollback/Recovery
- If any instability occurs, use the "Stop Servers (safe)" task to kill processes and return to a clean slate.

## Notes
- All changes were minimal and reversible. No code paths were altered beyond removing a temporary script and adding tasks.
- The environment is left halted and ready for a clean start in the next session.

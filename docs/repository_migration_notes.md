# Repository Migration Notes (Phase 4c)

This document explains how to enable and operate the Persistence Abstraction with Dual-Write (FS primary, SQLite shadow).

## Overview

The system keeps FS JSON (per-session files under `backend/src/data/annotations/`) as the source of truth. When feature flag `ENABLE_DUAL_WRITE=true` is set, all writes are mirrored to a SQLite database for observability and future cutover. Reads continue to use FS only, ensuring backward compatibility.

Environment flags (in `.env` or env vars):
- PERSISTENCE_BACKEND=fs|sqlite (default: fs)
- ENABLE_DUAL_WRITE=true|false (default: false)
- SQLITE_DB_PATH=src/data/net_est.sqlite3 (path to SQLite file)

Modes:
- FS (default): FS only, no DB touched
- SQLite: Use SQLite as the main repository (advanced; not default)
- FS + Dual-write: FS reads/writes; writes mirrored to SQLite
 - SQLite + Dual-write: SQLite reads/writes; writes mirrored to FS
 - SQLite + FS Fallback: SQLite primário; retorna ao FS automaticamente se houver falha

## Migration

To import existing FS sessions into SQLite:

Optional commands (Windows PowerShell):
```
# Run from repo root
${env:PYTHONPATH} = "backend"; python backend/scripts/migrate_fs_to_sqlite.py --db backend/src/data/net_est.sqlite3
```

The script upserts all annotations and appends audit entries. It is idempotent.

## Rollback

- Disable dual-write: set `ENABLE_DUAL_WRITE=false` and restart the backend. FS remains the source of truth.
- Force FS-only: ensure `PERSISTENCE_BACKEND=fs`.
 - If running SQLite primary with dual-write, FS contém espelho atualizado—rollback seguro.

No data loss occurs in FS since DB is shadow-only in dual-write mode.

## Known risks

- Divergence: If SQLite is manually modified, it may diverge. Use the migration script again to re-sync from FS.
- Timestamps/timezones: Values are stored as ISO strings in SQLite. Ensure consistent timezone handling.
- Performance: Dual-write adds overhead during write operations.

## Phase 4d specifics

- To run SQLite as primary safely:
	- Set `PERSISTENCE_BACKEND=sqlite`.
	- Consider `ENABLE_FS_FALLBACK=true` to allow automatic fallback.
	- For rollback-friendly operations, also set `ENABLE_DUAL_WRITE=true` (espelha em FS).
- Diagnostics endpoint: `GET /api/v1/system/persistence`.

## Testing strategy

See `backend/tests/test_sqlite_repository.py` for:
- Basic SQLite CRUD
- Dual-write consistency check
- Export parity (FS vs SQLite)
- Migration from existing FS JSON sessions

## Environment Setup

On systems where the default VS Code shell is PowerShell 7 (pwsh), tasks that call `powershell` may fail. Update task definitions to use `pwsh` instead of `powershell` to ensure compatibility. Alternatively, run commands directly in a pwsh terminal.

Status:
- `NET-est-optimized.code-workspace` tasks now use `pwsh` consistently for backend and frontend (Run Backend Tests, Start Backend Server, Run Frontend Tests, Start Frontend Server).
- If you still see any task invoking `powershell`, update it to:
	- `"command": "pwsh"`
	- Include `-NoLogo -NoProfile -Command` or `-File` as needed.
	- Prefer fully-qualified paths like `backend/venv/Scripts/python.exe`.

Examples:
- Replace task command `powershell -ExecutionPolicy Bypass -Command ...` with `pwsh -NoLogo -NoProfile -Command ...`.
- For backend tasks that call the venv Python, prefer fully qualified paths like `backend/venv/Scripts/python.exe` to avoid activation issues.

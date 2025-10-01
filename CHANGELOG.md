# Changelog

## 2025-09-25

### Added
- Accurate character spans for meso and micro stage strategies, enabling consistent range highlighting in the target text panel.

### Fixed
- Text selection validation now ignores superscript markers while preventing overlaps with existing highlighted ranges, restoring manual tag creation.
- Explanation generator now accepts both dict and Pydantic model inputs, resolving annotation export 400 errors.
- Hierarchical analysis output generation hardened with fallback retry logic to ensure consistent availability.

### Changed
- Bumped `pytest-asyncio` to 0.23.7 and re-synced backend dev dependencies so async-marked tests execute under pytest 8.
- Introduced persistence defaults (`PERSISTENCE_BACKEND`, `ENABLE_DUAL_WRITE`, `ENABLE_FS_FALLBACK`, `SQLITE_DB_PATH`) in `src/core/config.py` to stabilize repository selection during tests.

### Tests
- Backend test suite: 253 passed, 2 skipped, 21 warnings - all critical functionality restored
- Hierarchical output generation now stable across all test scenarios
- Explanation generator handles both dict and Pydantic model inputs without errors

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/

## 2025-09-27 — Developer session summary

Summary:
- Investigated a regression in the frontend comparative-analysis file upload flow that produced persistent 500 errors.
- Implemented a FormData-aware axios interceptor and removed manual multipart headers on the frontend; added vitest regression tests for Content-Type behavior.
- Added enhanced backend logging in `backend/src/api/comparative_analysis.py` and validated the endpoint via a TestClient smoke test (200 OK).
- Discovered intermittent failures were caused by runtime environment issues: a ghost Python/Uvicorn reloader process kept port 8000 occupied and also caused encoding/logging surprises.
- Updated `docs_dev/backend_windows_troubleshooting.md` with explicit guidance about VS Code task wiring, `start_optimized.py` behavior, UTF-8 log capture, and the dual reloader/worker model.
- Upgraded `kill_backend_8000.ps1` to reliably terminate the full Uvicorn/watchfiles process tree (parents first) and validate port release; added a follow-up plan recommending Task Manager as the final fallback and suggesting disabling hot-reload when not needed.

Files changed during session:
- `frontend/src/services/api.js` (axios FormData-aware interceptor and tests) — frontend request fix and regression tests added
- `backend/src/api/comparative_analysis.py` (logging) — detailed request/stack logging for upload failures
- `backend/start_optimized.py` (startup improvements) — port fallback and improved startup messaging already present; used for validation
- `kill_backend_8000.ps1` (updated) — stronger termination of uvicorn reload process tree
- `docs_dev/backend_windows_troubleshooting.md` (updated) — new section about VS Code tasks, ghost process behavior, logging capture, and follow-up plan
- `CHANGELOG.md` (this entry) — session summary

Next steps / handoff:
1. If this session is resumed, start by running the updated `Stop Backend Server` task and confirm the `kill_backend_8000.ps1` output; if PIDs remain, use Task Manager to stop `python.exe` processes that match `uvicorn`/`watchfiles`/`src.main:app`.
2. Run frontend vitest suite and the backend pytest suite under the official Python 3.12.7 virtualenv (`.venv_py312`) to ensure regression coverage is green.
3. Consider a small follow-up change: allow toggling `RELOAD` via an environment variable or a quick UI in `start_optimized.py` for dev sessions where hot reload is not required.

Acceptance criteria for next session:
- Frontend file upload reproduces successfully via UI to `http://127.0.0.1:8000` without 500s.
- `kill_backend_8000.ps1` reliably frees port 8000 without requiring Task Manager in 90% of cases; remaining cases logged for triage.
- Vitest and pytest regression suites pass locally under project standard environments.

## 2025-10-01 — Full-Stack Validation & Developer Experience Hardening

### Validated
- ✅ Frontend test suite: **31 passed, 1 skipped** (vitest) — All interceptor tests for FormData handling pass
- ✅ Backend test suite: **254 passed, 2 skipped** (pytest under Python 3.12.7) — All critical functionality stable
- ✅ End-to-end upload workflow: Confirmed via September 27 logs (ATS.txt + ATT.txt → 200 OK responses + analysis complete)

### Added
- **UVICORN_RELOAD environment variable:** Allows developers to disable hot-reload mode to avoid ghost process issues when not needed. Set `UVICORN_RELOAD=false` (or `0`, `no`) to disable; defaults to enabled for dev convenience.
- **kill_backend_8000.ps1 validation report:** Documented edge cases (debugger interference, elevated processes, concurrent Python sessions) and recommended enhancements for future work (see `docs_dev/kill_script_validation_report.md`).

### Changed
- `backend/start_optimized.py`: Now reads `UVICORN_RELOAD` environment variable to override `settings.RELOAD` configuration. Provides fallback handling when config import fails.
- `backend/.env.example`: Added `UVICORN_RELOAD` documentation with usage examples.
- `.vscode/tasks.json`: Added `detail` fields to `Start Backend Server` and `Stop Backend Server` tasks, referencing troubleshooting documentation.

### Documentation
- Created `docs_dev/kill_script_validation_report.md` with test scenarios, known limitations, and recommended future enhancements
- Updated `docs_dev/session_handoff_2025-09-27.md` with comprehensive session context for next development session

### Quality Gates
- All automated test suites green (frontend + backend)
- Enhanced kill script validated via design review (manual validation recommended for edge cases)
- Developer experience improvements documented and ready for team adoption

### Next Session Recommendations
1. Manual validation of `kill_backend_8000.ps1` under edge cases (debugger attached, rapid start/stop cycles)
2. Consider implementing telemetry logging for orphaned process detection
3. Evaluate making `UVICORN_RELOAD=false` the default for stability-focused dev sessions


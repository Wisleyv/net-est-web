## Phase 4b: Frontend Audit Search UI

Feature flag: `enableAuditSearch` (default: false)

Scope:
- Audit Search Panel with filters: statuses, strategy code, audit actions.
- Calls backend `/api/v1/annotations/search` and `/api/v1/annotations/audit` with filters.
- Accessible UI: labels, aria attributes, keyboard navigation (Enter to expand rows).
- UX: reset filters, loading indicator, no results message.
- Tests: store search behavior and panel rendering.

Endpoints:
- GET `/api/v1/annotations/search?session_id=...&statuses=...&strategy_codes=...`
- GET `/api/v1/annotations/audit?session_id=...&actions=...&annotation_id=...`

Future:
- Extend filters with date ranges and user, plus pagination.

## Phase 4c: Persistence Abstraction with Dual-Write (FS primary, DB shadow)

Feature flags (backend .env):
- PERSISTENCE_BACKEND=fs|sqlite (default: fs)
- ENABLE_DUAL_WRITE=true|false (default: false)
- SQLITE_DB_PATH=src/data/net_est.sqlite3

Scope:
- Add `SQLiteAnnotationRepository` and `DualWriteRepository`.
- Update repository factory to honor env flags (default FS-only).
- Migration script `backend/scripts/migrate_fs_to_sqlite.py` to prefill DB from FS JSON.

Compatibility:
- API continues working without DB.
- Dual-write mirrors writes to DB; reads remain FS.

Testing:
- Unit tests cover SQLite CRUD, dual-write consistency, export parity, and migration.

Risks/rollback:
- Disable dual-write by setting `ENABLE_DUAL_WRITE=false`.
- Force FS-only with `PERSISTENCE_BACKEND=fs`.

## Phase 4d: SQLite as Primary with FS Fallback — COMPLETED

- Env:
	- `PERSISTENCE_BACKEND=sqlite`
	- Optional: `ENABLE_DUAL_WRITE=true` (mirror to FS) and `ENABLE_FS_FALLBACK=true`
- Added endpoint: `GET /api/v1/system/persistence`
- Tests ensure primary reads from DB, fallback safety, and export parity.

## NEXT STEPS (Phase 4)

- 4e: Export schema alignment for ML/gold datasets (consistent fields, schema version, CSV/JSONL equivalence)
- 4f: Accessibility hardening + E2E tests (keyboard focus traps, ARIA labels, high contrast)
- Optional refinements: global export toolbar, toast confirmations for actions, timeline pagination

### Phase 4e — Export Schema Alignment & Tooling
- Align FS and SQLite export schemas; provide deterministic export for analytics. — COMPLETED
- Export CLI implemented: `python -m src.tools.export --format {jsonl,csv}` with filters. — COMPLETED
- Schema documented in `docs/EXPORT_SCHEMA.md`. — COMPLETED
- Round-trip import tool and tests — COMPLETED
- Audit export (audit.jsonl/csv) — COMPLETED

Linkage & guardrails:
- Persistence modes: validate against both `PERSISTENCE_BACKEND=fs|sqlite` and dual-write/fallback combos.
- Feature flags: ensure exports integrate with `enableAuditSearch` datasets to avoid regressions.

### Phase 4f — Accessibility, E2E, and Observability
- Frontend accessibility sweep (WCAG) and keyboard navigation for audit search UI.
- Add E2E tests (Playwright) for annotation flow and audit filtering.
- Add lightweight request/trace logging and timing in backend (structlog fields).
- Error budget metrics in diagnostics endpoint.

Status (2025-09-10):
- Base E2E (stubbed backend) passing.
- Accessibility audit test added (axe-core) for main analysis page; no serious/critical violations yet.
- Real-backend integration spec scaffolded behind `REAL_BACKEND` env flag.
- Next: extend a11y coverage to strategy tab + audit search UI; implement keyboard focus outline enhancements.
 - In Progress: Core HITL actions (accept/modify/reject) UI wiring and explanation field generation for RP+/SL+.

Linkage & guardrails:
- Respect frontend feature flags (e.g., `enableAuditSearch`) in E2E paths.
- Exercise both persistence modes in E2E matrix.

## Repository Abstraction & Migration Notes

Phase 4 introduced a persistence abstraction (`AnnotationRepository`). The initial concrete implementation is filesystem JSON (`FSAnnotationRepository`). This mirrors the previous `AnnotationStore` behavior while enabling a future switch to SQLite (or another backend) with minimal API surface change.

### Current State
* API endpoints now call `get_repository()` instead of accessing the legacy `store`.
* A process-wide singleton repository instance is used so existing tests (which mutate internal dicts) continue to work without broad refactors.
* The legacy `src/services/annotation_store.py` now simply maps `store = get_repository()` as a compatibility shim.
* Session persistence writes `<session_id>.json` under `src/data/annotations/` (unchanged format).

### Design Principles
1. Non-regression: Existing tests and data files remain valid.
2. Incremental migration: Keep the legacy symbol `store` until all tests transition to repository-oriented setup/fixtures.
3. Pure Pydantic models in JSON (no backend-specific serialization) to simplify future DB ingestion.
4. Explicit lifecycle methods: `accept`, `reject`, `modify`, `create` each emit an `AuditEntry` (contract to preserve across backends).

### Future: SQLite Backend Plan (Outline)
| Concern | Approach |
|---------|----------|
| Schema | Tables: `annotations`, `audit_log`; optional `sessions` meta table. |
| Transactions | Wrap each lifecycle operation in a transaction (BEGIN IMMEDIATE). |
| Concurrency | Use WAL mode; repository instance could become per-request with connection pooling. |
| Migration | One-off script to read existing JSON session files and bulk insert. |
| Search/Filters | Add indexed columns on `(status, strategy_code, updated_at)` for timeline and analytics queries. |

### Contract to Preserve
* `list_visible()` must exclude `rejected`.
* `modify()` must set `original_code` on first change and forbid `accept` of a `modified` annotation (mirrors existing business rule).
* `export()` defaults to statuses: accepted / modified / created.
* `audit` order is append-only chronological (DB: ORDER BY autoincrement id or timestamp).

### Migration Steps (Planned)
1. Introduce `SQLAnnotationRepository` implementing the same interface.
2. Add environment variable `PERSISTENCE_BACKEND=sqlite` and selection logic in `get_repository()`.
3. Provide migration CLI: `python -m scripts.migrate_json_to_sqlite --src src/data/annotations --db data/annotations.db`.
4. Dual-write (optional short window): Wrap FS + SQL writes to validate parity before cutover.
5. Remove dual-write & legacy `store` shim after test suite updated.

Note: Env-based backend selection is intentionally deferred until SQLite work begins. The current factory always returns the FS implementation.

### Risks & Mitigations
* Risk: Test flakes due to singleton state. Mitigation: tests explicitly clear `_annotations` / `_audit` (current pattern) or future fixture to reinstantiate repository.
* Risk: Large JSON sessions in memory. Mitigation: for DB backend, lazy page results for timeline endpoints.

### Cleanup Targets (Post-SQLite)
* Remove `annotation_store.py`.
* Replace direct attribute peeks (`_annotations`) with accessor or test fixtures.
* Add richer query methods (filter by date/status) to repository interface.

---
Status: FS abstraction integrated; tests passing for repository + API adaptation.

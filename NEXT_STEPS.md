# HITL Gap Analysis – Status Note (2025-09-11)

Done (Phase 4e)
- Gold annotation persistence (FS and SQLite), with validated/manually_assigned flags
- CRUD actions: accept, modify (with original_code tracking), reject (hidden/deleted per design)
- Export pipeline: scoped exports (gold/raw/both) with ML-ready fields via API and CLI
- E2E stabilization: explicit data attributes for markers; network stubs for deterministic tests
- Safety guard: test-only feedback flag enabled only in dev/test builds

Pending / Next (defer to planning)
- Bulk operations for annotations (multi-select accept/reject)
- Advanced rationale generation and richer explanation UI
- Additional audit reporting and export filters
- Performance tuning for large sessions and pagination in UI timelines

References
- See ONBOARDING.md (Troubleshooting) for integration E2E environment notes
- See EXPORT_SCHEMA.md for ML export field definitions and examples# NEXT STEPS

Phase 4e/4f planning snapshot for quick pickup next session.

## Phase 4e — Export Schema Alignment & Tooling
- Align FS and SQLite export schemas; provide deterministic export for analytics.
- Add export CLI: `python -m src.tools.export --format {jsonl,csv}` with filters.
- Round-trip test: export -> import parity across backends.
- Document export contracts and versioning.

## Phase 4f — Accessibility, E2E, and Observability
- Frontend accessibility sweep (WCAG) and keyboard navigation for audit search UI.
- Add E2E tests (Playwright) for annotation flow and audit filtering.
- Add lightweight request/trace logging and timing in backend (structlog fields).
- Error budget metrics in diagnostics endpoint.

## Refinements (Optional, Low-risk)
- Remove legacy `annotation_store` alias after tests port fully to repositories.
- Feature-flag defaults guardrails: warn if dual-write+fallback are both off.
- CI: jobs for backend pytest matrix (Py 3.12/3.13) + frontend vitest.
- Script: `scripts/check_persistence_health.py` to ping `/system/persistence`.
- Docs: add architecture diagrams for repository factory and mode matrix.

## Notes
- Phase 4d milestone tagged as `phase4d-milestone`.
- See `docs/repository_migration_notes.md` and `docs/HITL_PHASE4_PLAN.md` for details.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/

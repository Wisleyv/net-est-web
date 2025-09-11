### Phase 4e: Gold Annotations & ML Export

- Accepting an annotation marks it as `validated=true` (gold).
- Human-created annotations are `manually_assigned=true`.
- API export supports scopes: `gold`, `raw`, `both`.
- CLI export adds `--scope` to match API.

Quick try:
1) Create and accept an annotation via API or UI.
2) Export gold-only: POST `/api/v1/annotations/export?session_id=S1&format=jsonl&scope=gold`.
3) CLI: `python -m src.tools.export --session S1 --type annotations --scope gold`.

# Onboarding

## Local Dev Quickstart (pwsh)
- Backend venv: backend/venv
- Run tests:
  - Optional
    & "backend/venv/Scripts/python.exe" -m pytest -q
- Frontend tests:
  - Optional
    npm test --silent --prefix frontend

## Notes
- Tasks updated to use `pwsh` for compatibility.
- See `docs/repository_migration_notes.md` for environment setup.

## Export Tools
- CLI export (JSONL):
  - python -m src.tools.export --session SESSION_ID --format jsonl --out export
- CLI export (CSV):
  - python -m src.tools.export --session SESSION_ID --format csv --out export
- Import (round-trip validation):
  - python -m src.tools.import_tool --session NEW_SESSION --file export/SESSION_ID.annotations.jsonl --format jsonl
- Schema & details: see `docs/EXPORT_SCHEMA.md`.
 - Explanation field now included in both JSONL and CSV exports as column `explanation` (Phase 4f). Only populated for strategy codes with templates (currently RP+, SL+).

## E2E Tests (Playwright)
- Install browsers (first run):
  - npx playwright install
- Run E2E suite with config:
  - npx playwright test --config=playwright.config.ts --reporter=list
- If a run appears frozen:
  - Ensure pwsh is used, not legacy powershell.
  - Close residual Vite or backend servers on 5173/8000.
  - Use the provided config which starts uvicorn with --no-reload for stability.

### Accessibility Audit (axe-core)
- Run only accessibility tests:
  - npx playwright test --grep @a11y
- Add new pages to audit by creating a spec using AxeBuilder from '@axe-core/playwright'.
- Failing test indicates serious/critical WCAG 2.0 A/AA violations.

### Real Backend Integration Variant
- Default fast tests stub the backend for determinism.
- Run real-backend test (may be slower):
  - REAL_BACKEND=true npx playwright test --grep @integration
- Skip integration test (default) by omitting the env var.

## HITL Annotation API (Phase 4f additions)
- Create manual annotation:
  POST /api/v1/annotations?session_id=SESSION
  { "strategy_code": "SL+", "target_offsets": [{"start":0,"end":12}], "comment":"ajuste manual" }

- Update annotation status (accept/reject/modify):
  PATCH /api/v1/annotations/{id}?session_id=SESSION
  { "action": "accept", "session_id": "SESSION" }
  { "action": "modify", "session_id": "SESSION", "new_code": "RP+" }

- Explanation field:
  Returned as `explanation` when available (currently RP+/SL+ heuristic templates).

## Feedback UI Feature Flag
- The interactive Accept/Modify/Reject controls are gated by `enableFeedbackActions` (frontend store/config). Disabled controls render read-only view.
 - Playwright spec `feedbackFeatureFlag.spec.js` covers toggle behavior.
 - Test-only feature flag: You can enable feedback actions in E2E by setting `window.__ENABLE_FEEDBACK_FLAG__`.
  - Safety: This hook is honored only in development/test builds (gated via `import.meta.env.DEV` / `MODE==='test'`).
  - Never exposed in production builds.

### Running the integration E2E test against a live backend

The `@integration` Playwright spec (`tests/e2e/integrationAnalysis.spec.js`) runs against a real backend to validate the full stack:

1) Start the backend locally (FastAPI):
  - Use the project venv python and run the server (or use the provided script/VS Code task if available).
2) Start the frontend (Vite dev server) with the API base pointing to the backend.
3) Run the integration test with the REAL_BACKEND flag so the spec skips network stubs:

```powershell
cd frontend
$env:REAL_BACKEND = 'true'
npm run test:integration
```

Notes:
- The Playwright config spins up servers automatically for most specs; the integration spec expects a reachable backend at `http://127.0.0.1:8000`.
- If port or host differ, update `playwright.config.ts` or set `VITE_API_BASE_URL` accordingly.

### Troubleshooting

- Integration E2E timeouts: The `@integration` test requires a healthy, responsive backend running with `STRATEGY_DETECTION_MODE=performance`. If it times out waiting for results, first verify the backend is up and serving, then re-run once the analysis completes. Occasional timeouts can occur on slower environments and are an accepted known issue.

## Test Suites Summary
- Backend: & "backend/venv/Scripts/python.exe" -m pytest -q
- Frontend unit: npm test --silent --prefix frontend
- E2E: npx playwright test --config=playwright.config.ts
- Targeted backend export explanation test: pytest -q backend/tests/test_annotations_export_explanation.py

## Recent Changes (Phase 4f snapshot)
- Added explanation field to export (jsonl/csv).
- Added backend tests validating explanation presence across fs/sqlite.
- Added unit interaction tests for FeedbackCollection (accept/reject callbacks).
- Added Playwright tests for feedback feature flag and annotation panel interactions.

## Repository Isolation Fixture (Backend)
To guarantee clean state in backend tests, use the `isolated_repo` Pytest fixture (defined in `backend/tests/conftest.py`). It:
- Redirects `DATA_DIR` to a temporary directory
- Resets the singleton repository
- Clears in-memory annotations and audit lists

Example:
```
def test_create_annotation(isolated_repo):
  isolated_repo.load_session('s1')
  isolated_repo.create('s1', 'SL+', [{'start':0,'end':4}], comment=None)
  assert len(isolated_repo.query(session_id='s1')) == 1
```
Prefer this over manual file deletions for new tests to reduce flakiness.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/

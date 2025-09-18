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

### UI Flow: Create and Adjust Annotations (HITL)
- Create: In "Texto Simplificado", select a span with the mouse. A menu appears; pick a strategy to create a manual annotation.
- Adjust span: Open a strategy in the side panel, click "Ajustar intervalo", then select the new span in "Texto Simplificado". The annotation offsets are updated.
- Accept/Reject/Modify: Use the buttons in the Strategy Detail Panel. Modify lets you change the strategy code.

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

## Start Backend and Frontend (Dev)

Use these steps to run both services locally and ensure they talk to each other.

1) Kill anything listening on ports 8000/5173 (optional cleanup):

```powershell
# Backend on 8000, Frontend on 5173
$ports = 8000,5173
foreach ($p in $ports) { Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } }
```

2) Start the backend (FastAPI + Uvicorn):

```powershell
cd backend
# Ensure venv and deps (first run only):
#  c:\Python313\python.exe -m venv venv
#  .\venv\Scripts\pip.exe install -r requirements.txt
$env:STRATEGY_DETECTION_MODE = 'performance'
.\venv\Scripts\python.exe .\start_server.py
# Server will listen on http://127.0.0.1:8000
```

3) Start the frontend (Vite dev server):

```powershell
cd ../frontend
# First run only:
# npm ci
$env:VITE_API_BASE_URL = 'http://127.0.0.1:8000'
npm run dev
# App will be at http://localhost:5173
```

4) Verify connectivity:

```powershell
# Health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health | Select-Object -ExpandProperty Content
# Ports
foreach ($p in 8000,5173) { $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue; if ($c) { "Port $p LISTENING" } else { "Port $p not listening" } }
```

Front-end uses `VITE_API_BASE_URL` (see `src/services/config.js`). In dev, setting the env variable before `npm run dev` is sufficient. Alternatively, edit `.env.development`.

### Troubleshooting Frontend-Backend Communication

- Frontend loads but actions are read-only: ensure feature flag `enableFeedbackActions` is enabled in dev. For E2E or manual QA, you can temporarily set in dev tools console:
  `window.__ENABLE_FEEDBACK_FLAG__ = true; location.reload();` (only honored in dev/test builds).
- 404/Network errors on API calls: confirm `VITE_API_BASE_URL` points to the running backend (default `http://127.0.0.1:8000`).
- Backend healthy but requests fail CORS: backend runs with FastAPI/uvicorn defaults configured for local dev; if custom host/port is used, review CORS settings in backend config.
- Timeouts on long analyses: set `STRATEGY_DETECTION_MODE=performance` and retry. Large models may load on first request.
- After history rewrite or branch updates: stop dev servers, `git pull`, and restart both services.

 - 405 Method Not Allowed on /api/v1/comparative-analysis/: This endpoint is POST-only in the backend (`@router.post("/")`). Ensure the frontend sends POST to `/api/v1/comparative-analysis/` with JSON `{ source_text, target_text, analysis_options }`. If you see a GET, clear Vite cache (`node_modules/.vite`, `dist`), restart `npm run dev`, and hard refresh (Ctrl+Shift+R). The canonical client helpers are:
   - `comparativeAnalysisAPI.analyze(data)` -> POST `/api/v1/comparative-analysis/`
   - `ComparativeAnalysisService.performComparativeAnalysis(analysisData)` -> POST `/api/v1/comparative-analysis/`
   Validate in DevTools Network that the method is POST and payload has the fields above.

 - Feature flag not taking effect: In dev, `.env.development` sets `VITE_ENABLE_FEEDBACK=true`. On app load, the app sets `window.__ENABLE_FEEDBACK_FLAG__ = true` and `useAppStore().config.enableFeedbackActions = true` (dev/test only). Check the console logs for `[NET-EST][dev] ENABLE_FEEDBACK diagnostics` and `[NET-EST][dev] Feedback actions enabled:`. If missing, ensure you restarted Vite after env changes.

#### Debugging interactive controls not showing (frontend rendering)
- Inspect store: In DevTools console run `useAppStore.getState().config.enableFeedbackActions` (or `window.NET_EST.getStore().config.enableFeedbackActions`). It should be `true`.
- Force-enable from console (dev only): `window.NET_EST.enableFeedback()` or `window.__ENABLE_FEEDBACK_FLAG__ = true; location.reload()`.
- Check component mounts: Open Console and look for `[NET-EST] FeedbackCollection mounted` and `[NET-EST] StrategyDetailPanel render` logs. If absent, the detail panel is not being opened.
- Open the Strategy Detail Panel: Click a superscript marker (¹²…) in the target text. The panel renders `FeedbackCollection` only when a strategy is active.
- Verify data: Ensure `analysisResult.simplification_strategies` exists and markers render. If not, hard reload and confirm POST to `/api/v1/comparative-analysis/` returns strategies.
- Clear Vite cache if stale UI persists: stop dev server, delete `frontend/node_modules/.vite` and `frontend/dist`, then `npm ci` and `npm run dev`.

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

## Condensed Next-session Onboarding (copy-paste)

Purpose: Minimal, copy-paste commands to start both backend and frontend on Windows (PowerShell). Use these as the first steps in the next chat to bring the workspace to an active state.

1) Start the backend (recommended: use VS Code task "Start Backend Server")

PowerShell (activate venv and run supervised start):

```powershell
# from repository root (C:\net)
cd C:\net\backend
# activate venv
.\venv\Scripts\Activate.ps1
# supervised start (recommended via VS Code task) or run the launcher
python.exe start_server.py
```

Alternative (run uvicorn directly):

```powershell
cd C:\net\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

Verify backend health (quick check):

```powershell
# from repo root
.\backend\venv\Scripts\python.exe -c "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=5).read().decode())"
```

2) Start the frontend (Vite/React)

PowerShell (from repo root):

```powershell
cd C:\net\frontend
# install deps (once)
npm install
# start dev server
npm run dev
```

Quick frontend smoke test (open the app):
- Visit: http://localhost:5173
- If using the frontend test harness, run the provided tests that exercise HITL flows.

Notes / Recommendations:
- Prefer using the provided VS Code tasks for supervised starts (Start Backend Server, Start Frontend Dev Server). They set the correct working directory and use the repository virtualenv.
- If the backend fails to start, check `backend/uvicorn_launch.log` and the venv packages: `c:\net\backend\venv\Scripts\pip.exe list`.
- Use the health endpoint first (`/health`) before running integration flows.

Contact: This workspace was stabilized by the previous maintenance run; if you need me to start the servers now, say "Please start backend and frontend" in the next chat and I will.


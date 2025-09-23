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

**Environment & Shell Configuration:**
- VS Code is configured for PowerShell 7 (`pwsh.exe`) in `.vscode/settings.json`
- All tasks in `.vscode/tasks.json` use deterministic shell invocation
- Backend uses Python 3.12 venv: `backend/.venv_py312`
- No manual PATH configuration needed

**Quick Start Tasks (via VS Code):**
1. **Setup Backend**: Ctrl+Shift+P → "Tasks: Run Task" → "Install Backend Dependencies"
2. **Start Backend**: Ctrl+Shift+P → "Tasks: Run Task" → "Start Backend Server"
3. **Setup Frontend**: Ctrl+Shift+P → "Tasks: Run Task" → "Install Frontend Dependencies"
4. **Start Frontend**: Ctrl+Shift+P → "Tasks: Run Task" → "Start Frontend Server"

### spaCy PT model (strongly recommended)

For best accuracy in feature extraction and strategy detection, install the Portuguese spaCy model. Use the provided task:

- VS Code → Tasks: Run Task → "Install spaCy PT model (recommended)"

Verification (optional):

```powershell
# From repo root
& "backend/.venv_py312/Scripts/python.exe" -c "import spacy; spacy.load('pt_core_news_sm'); print('spaCy PT model OK')"
```

Without the model, the backend still runs but falls back to lighter heuristics with reduced accuracy on linguistic features.

**Manual Commands (if needed):**
- Backend venv: backend/.venv_py312
- Run tests:
  - Optional: `& "backend/.venv_py312/Scripts/python.exe" -m pytest -q`
- Frontend tests:
  - Optional: `npm test --silent --prefix frontend`

## 🚨 CRITICAL: tasks.json Authority Protocol

**For All Developers & AI Coding Agents:**

The `.vscode/tasks.json` file is the **AUTHORITATIVE** source for all system loading and service management operations in this workspace. This protocol must be followed strictly to prevent port conflicts, environment issues, and development disruptions.

### **Absolute Requirements:**

1. **NEVER** start services manually outside of tasks.json
2. **NEVER** create new ports without updating tasks.json first
3. **NEVER** use alternative startup strategies as "workarounds"
4. **ALWAYS** fix tasks.json if it doesn't work for a new scenario
5. **ALWAYS** use standard ports defined in tasks.json:
   - **Backend**: Port 8000 only
   - **Frontend**: Port 5173 (with fallback to 5174 if authorized in CORS)
   - **Test servers**: As defined in tasks.json

### **Standard Ports (Authorized in CORS):**
```
Backend:    http://127.0.0.1:8000
Frontend:   http://localhost:5173
Fallback:   http://localhost:5174
Dev APIs:   http://localhost:3000 (if needed)
```

### **If Tasks Don't Work:**
1. **Fix tasks.json FIRST** - Never create workarounds
2. Update environment configurations if needed
3. Test the fix through tasks.json
4. Document the fix in this file

### **Enforcement:**
- Vite configured with `strictPort: true` to prevent unauthorized ports
- CORS configured only for authorized origins
- Port management scripts integrated with tasks.json
- Any deviation from this protocol causes immediate system failures

### **Rationale:**
This protocol prevents the hour-long debugging sessions caused by:
- Port conflicts between unauthorized services
- CORS policy violations from undocumented origins  
- Environment inconsistencies from manual startup procedures
- Resource waste from "trial and error" approaches

**Reference Documentation:**
- Port management: `docs_dev/port_management_final_status.md`
- Task configuration: `docs_dev/tasks_json_fix_analysis.md`
- Incident reports: `docs_dev/incident_reports/`

## Troubleshooting

**Shell/Environment Issues:**


## Troubleshooting

**PowerShell Version:** This project requires PowerShell Core (`pwsh`). If you see Windows PowerShell (`powershell.exe`) being invoked, check your user-level VS Code settings to ensure they are not overriding the workspace settings. All project scripts are configured to use `pwsh`.
- Backend runs on port 8000, frontend on 5173
- Use `Environment Status Check` task to verify running services
- Inspect/Kill port 8000 processes:
  - Inspect: `pwsh -File scripts/capture_8000_procs.ps1`
  - Kill: `taskkill /PID <PID> /F`

**spaCy model missing:** If you see errors like "Can't find model 'pt_core_news_sm'" in backend logs, run the VS Code task "Install spaCy PT model (recommended)" and restart the backend task.

## Notes
- Tasks updated to use `pwsh` for compatibility with providers
- All configuration enforces PowerShell 7 usage
- See `docs/repository_migration_notes.md` for environment setup
- See `docs_dev/tasks_json_fix_analysis.md` for shell configuration details

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

### **Recommended: Use VS Code Tasks (Fastest Method)**

The project includes a consolidated `tasks.json` configuration that resolves all common startup issues. This is the preferred method:

**One-Command Startup:**
1. Press `Ctrl+Shift+P` → "Tasks: Run Build Task" → Enter
2. Or run "Start Full Development Environment" task

This automatically:
- Stops any conflicting servers
- Sets up Python 3.12 virtual environment (`.venv_py312`)
- Installs backend dependencies
- Starts backend server (port 8000)
- Installs frontend dependencies  
- Starts frontend server (port 5173)

**Individual Tasks Available:**
- `Stop All Servers` - Safely terminate backend/frontend
- `Start Backend Server` - Backend only with dependencies
- `Start Frontend Server` - Frontend only with dependencies
- `Environment Status Check` - Verify setup and ports

### **Manual Startup (Alternative Method)**

Use these steps if you prefer manual control or need to troubleshoot:

1) Kill anything listening on ports 8000/5173 (optional cleanup):

```powershell
# Backend on 8000, Frontend on 5173
$ports = 8000,5173
foreach ($p in $ports) { Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } }
```

2) Setup Python 3.12 environment (first run only):

```powershell
# Use pinned Python 3.12 to avoid instability issues
C:\Python312\python.exe -m venv C:\net\backend\.venv_py312
C:\net\backend\.venv_py312\Scripts\python.exe -m pip install -r C:\net\backend\requirements.txt
```

3) Start the backend (FastAPI + Uvicorn):

```powershell
cd C:\net\backend
# Use Python 3.12 venv for stability
$env:STRATEGY_DETECTION_MODE = 'performance'
.\.venv_py312\Scripts\python.exe .\start_server.py
# Server will listen on http://127.0.0.1:8000
```

4) Start the frontend (Vite dev server):

```powershell
cd C:\net\frontend
# First run only: npm install
$env:VITE_API_BASE_URL = 'http://127.0.0.1:8000'
npm run dev
# App will be at http://localhost:5173
```

5) Verify connectivity:

```powershell
# Health check both services
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
Invoke-WebRequest -UseBasicParsing http://localhost:5173/
# Port status
foreach ($p in 8000,5173) { $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue; if ($c) { "Port $p LISTENING" } else { "Port $p not listening" } }
```

Front-end uses `VITE_API_BASE_URL` (see `src/services/config.js`). In dev, setting the env variable before `npm run dev` is sufficient. Alternatively, edit `.env.development`.

### **tasks.json Fix Documentation**

**Problem**: The original `tasks.json` had structural issues causing frequent startup failures:
1. **Invalid JSON structure** - Multiple separate JSON objects instead of single valid file
2. **Duplicate task labels** - Same task names with different implementations
3. **Mixed Python environments** - Tasks referenced both Python 3.13 (unstable) and 3.12 (stable)  
4. **Working directory issues** - npm commands failed due to incorrect `cwd` settings
5. **Missing unified startup** - No single task to start everything cleanly

**Solution**: Consolidated `tasks.json` with:
- Single valid JSON structure with all tasks properly organized
- Consistent Python 3.12 usage throughout (`.venv_py312`)
- Proper working directories for all frontend/backend operations
- Clear task dependencies ensuring setup happens before startup
- Compound "Start Full Development Environment" task for one-click startup

**Backup Location**: Original tasks.json saved as `tasks.json.backup`

**Key Benefits**:
- ✅ Eliminates "Task not found" errors
- ✅ Consistent Python 3.12 environment prevents instability
- ✅ Reliable one-command startup via build task
- ✅ Proper npm working directory handling
- ✅ Dedicated terminal panels for backend/frontend

If you encounter startup issues, always try the VS Code tasks first before manual troubleshooting.

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

## New: Port detection utilities (Phase 1)

We added a lightweight, read-only port inspection module in `scripts/port-management.ps1`.

Usage examples (PowerShell):

```powershell
# Check which process is listening on port 8000 and get details in JSON
pwsh -NoProfile -File scripts/port-management.ps1 -Function Get-PortProcess -Port 8000

# Test whether a port appears available (returns True/False)
pwsh -NoProfile -File scripts/port-management.ps1 -Function Test-PortAvailable -Port 8000

# Run the integrated test script (Phase 1 checks)
pwsh -NoProfile -File scripts/test_port_management.ps1
```

Notes:
- Phase 1 is detection-only. No process termination functions are implemented yet.
- Logs are written to `scripts/logs/port-management.log` for audit.
- Keep `scripts/inspect_pid.ps1` for comparison testing if needed.

Contact: This workspace was stabilized by the previous maintenance run; if you need me to start the servers now, say "Please start backend and frontend" in the next chat and I will.


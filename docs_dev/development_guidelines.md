<!-- RESTORED FILE: Source commit eb8d3c1e5 | Restoration UTC 2025-09-24T00:00:00Z (placeholder) -->

### **AI Agent Development Guidelines**

Please adhere to the following principles for all tasks:

- **Cleanliness:** Make minimal, targeted changes. Remove debug logs and comments before finalizing. Follow existing code patterns and style.
- **Documentation:** Update relevant documentation (e.g., `ONBOARDING.md`, `CHANGELOG.md`) concurrently with code changes. Explain the "why" for non-trivial logic in comments.
- **Organization:** Reuse existing patterns and utilities. Ensure new code integrates seamlessly with the current architecture (e.g., repository abstraction, state management).
- **Communication:** Provide a concise summary upon completion, including what was changed, test results, and any specific verification steps.
- **Production-Readiness:** Prioritize stability and user experience. Implement robust error handling and ensure all changes are covered by tests to prevent regressions.
- **Regression-Free Approach Check-List:**
  - Scope is atomic – change is small, targeted, and clearly described.
  - Intent documented – before/after behavior explained in plain language.
  - Tests updated/added – unit + regression tests cover the new/changed behavior.
  - Full test suite passes – no failing unit, integration, or E2E tests.
  - Static analysis clean – no lint/type/security errors introduced.
  - Performance checked – no measurable slowdown vs. baseline.
  - Backwards compatibility – APIs, data contracts, and existing workflows remain stable.
  - Monitoring considered – error logging/metrics updated if relevant.
  - Human review required – at least one reviewer confirms no regressions.
  - Rollback ready – release/tag point identified for fast revert if needed.

### **🚨 MANDATORY: tasks.json Authority Protocol**

**CRITICAL DIRECTIVE FOR ALL DEVELOPERS & AI AGENTS:**

The `.vscode/tasks.json` file is the **SINGLE SOURCE OF TRUTH** for all system loading, service management, and development environment operations. Violation of this protocol results in immediate system failures and extended debugging sessions.

**ABSOLUTE PROHIBITIONS:**
- ❌ Starting services outside of tasks.json (manual terminal commands, scripts, etc.)
- ❌ Opening new ports without updating tasks.json and CORS configuration first
- ❌ Using "workaround" strategies when tasks.json doesn't work
- ❌ Creating alternative startup procedures or "temporary fixes"
- ❌ Ignoring port conflicts by incrementing to unauthorized ports

**MANDATORY REQUIREMENTS:**
- ✅ ALL system loading MUST use tasks.json exclusively
- ✅ If tasks.json fails, fix tasks.json FIRST, then retry
- ✅ Use only authorized ports: Backend (8000), Frontend (5173), Fallback (5174)
- ✅ Update CORS configuration when adding new authorized ports
- ✅ Document any changes to port management in this file

**ENFORCEMENT MECHANISMS:**
- `vite.config.js`: `strictPort: true` prevents unauthorized ports
- `backend/.env`: CORS only allows authorized origins
- Port management scripts: Detect and prevent conflicts
- Task dependencies: Ensure proper startup sequence

**RATIONALE:**
This protocol exists because violations cause:
- 1+ hour debugging sessions from port conflicts
- CORS policy violations blocking frontend-backend communication
- Environment inconsistencies causing unpredictable failures
- Resource waste from repeated "trial and error" cycles

**For AI Agents:** Never propose alternative strategies. If tasks.json doesn't solve the problem, your first and only response should be to fix tasks.json, not work around it.

### **VS Code Environment & Shell Configuration**

**Shell Standardization:**
- All PowerShell tasks must use `type: "process"` with explicit `pwsh.exe` command
- Avoid ambiguous shell invocation; use deterministic process execution
- Provider compatibility requires consistent shell detection

**Task Configuration:**
- Backend tasks use Python 3.12 venv: `backend/.venv_py312/Scripts/python.exe`
- Frontend tasks use `npm.cmd` on Windows for reliable execution
- All tasks specify explicit working directories with `"cwd"` option
- Background tasks (servers) use dedicated terminal panels

**Environment Detection:**
- VS Code settings enforce PowerShell 7 (`pwsh.exe`) for all terminals
- Automation shell profile set to `pwsh.exe` to avoid legacy PowerShell
- PowerShell extension configured for consistent behavior

**Troubleshooting:**
- If tasks fail, verify PowerShell 7 installation and PATH availability
- Check for port conflicts (8000 for backend, 5173 for frontend)
- Use `Environment Status Check` task to diagnose common issues
- Review `docs_dev/tasks_json_fix_analysis.md` for detailed configuration rationale

### **Regression-Free Approach (Condensed)**
Take all reasonable measures to prevent introducing regressions. When in doubt, stop and request clarification before proceeding.

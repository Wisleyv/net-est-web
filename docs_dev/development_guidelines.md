### **AI Agent Development Guidelines**

Please adhere to the following principles for all tasks:

- **Cleanliness:** Make minimal, targeted changes. Remove debug logs and comments before finalizing. Follow existing code patterns and style.

- **Documentation:** Update relevant documentation (e.g., `ONBOARDING.md`, `CHANGELOG.md`) concurrently with code changes. Explain the "why" for non-trivial logic in comments.

- **Organization:** Reuse existing patterns and utilities. Ensure new code integrates seamlessly with the current architecture (e.g., repository abstraction, state management).

- **Communication:** Provide a concise summary upon completion, including what was changed, test results, and any specific verification steps.

- **Production-Readiness:** Prioritize stability and user experience. Implement robust error handling and ensure all changes are covered by tests to prevent regressions.

### **VS Code Environment & Shell Configuration**

**Shell Standardization:**
- All PowerShell tasks must use `type: "process"` with explicit `pwsh.exe` command
- Avoid ambiguous shell invocation; use deterministic process execution
- Provider compatibility (e.g., code-supernova) requires consistent shell detection

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
- Review `docs_dev/tasks_json_fix_analysis.md` for detailed configuration rationalet Development Guidelines**

Please adhere to the following principles for all tasks:

- **Cleanliness:** Make minimal, targeted changes. Remove debug logs and comments before finalizing. Follow existing code patterns and style.

- **Documentation:** Update relevant documentation (e.g., `ONBOARDING.md`, `CHANGELOG.md`) concurrently with code changes. Explain the "why" for non-trivial logic in comments.

- **Organization:** Reuse existing patterns and utilities. Ensure new code integrates seamlessly with the current architecture (e.g., repository abstraction, state management).

- **Communication:** Provide a concise summary upon completion, including what was changed, test results, and any specific verification steps.

- **Production-Readiness:** Prioritize stability and user experience. Implement robust error handling and ensure all changes are covered by tests to prevent regressions.

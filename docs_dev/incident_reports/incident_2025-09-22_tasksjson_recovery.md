# Incident: Corrupted `.vscode/tasks.json` caused terminal command injection

Date: 2025-09-22

Summary
- A corrupted `.vscode/tasks.json` (multiple top-level JSON objects concatenated) caused VS Code to pass non-PowerShell JSON text to the integrated PowerShell terminal. This produced parsing errors and froze terminals.

Actions taken
1. Listed active `pwsh` processes and confirmed frozen terminals.
2. Terminated all `pwsh` processes to regain terminal control (authorized).
3. Restored `.vscode/tasks.json` from `tasks.json.backup` by extracting the main tasks block and replacing the corrupted file.
4. Created this incident report under `docs_dev/incident_reports/`.

Validation
- Restored `tasks.json` validated with JSON parse (Python `json.tool`).
- Verified no lingering `pwsh` processes remained after cleanup.

Root cause
- Multiple edits and concatenations left `tasks.json` containing several top-level JSON objects. VS Code's tasks subsystem attempted to interpret the malformed file and sent its contents to the PowerShell terminal, which attempted to execute it.

Prevention / Recommendations
- Always keep `tasks.json` under git control and avoid manual concatenations.
- Use wrapper scripts (`-File`) instead of `-Command` inline one-liners when possible.
- Add a CI/lint step to validate `.vscode/tasks.json` with `jq` or Python `json.tool` before merges.
- Add PSScriptAnalyzer checks and pre-commit hooks to prevent task-related regressions.

Follow-ups (require explicit approval before implementation)
- Add automatic validation in CI to reject malformed `tasks.json`.
- Replace remaining inline `-Command` one-liners with wrapper scripts.
- Add a pre-commit hook to validate `.vscode/tasks.json` on commit.

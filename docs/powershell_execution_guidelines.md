## PowerShell execution guidelines for tasks

Short, actionable rules to avoid parsing and quoting problems when invoking PowerShell from VS Code tasks.

- Prefer `-File` and small wrapper scripts over `-Command` one-liners. Wrapper scripts are easier to quote, test, and lint.
- Use explicit exit codes (non-zero on failure) in wrapper scripts so task runners can detect failures.
- Avoid embedding ${workspaceFolder} directly inside quoted `-Command` strings; pass it via parameters or rely on `cwd`.
- Use `-NoProfile -ExecutionPolicy Bypass -File` consistently when calling pwsh from tasks.
- Run PSScriptAnalyzer on wrapper scripts and fix high-severity warnings before adding them to tasks.
- When you need to run inline small commands, prefer using a separate script file created for that command and keep the script under version control.

Example (safe):

pwsh.exe -NoProfile -ExecutionPolicy Bypass -File ${workspaceFolder}/scripts/setup_python_env_wrapper.ps1

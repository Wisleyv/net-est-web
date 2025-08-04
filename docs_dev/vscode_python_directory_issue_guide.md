# VS Code Python Directory Jumping Issue: Root Cause Analysis & Solution Guide

## Context
This guide addresses a recurring issue where Python scripts executed in VS Code terminals (especially with virtual environments) attempt to run from the wrong directory (e.g., project root instead of intended backend/frontend subfolder). This leads to errors such as "can't open file" or missing modules, even when the shell prompt shows the correct working directory.

## Problem Summary
- VS Code terminal shows correct working directory (e.g., `c:\net\backend`)
- Python commands (e.g., `python start_optimized.py`) fail, reporting file not found in the root (e.g., `c:\net\start_optimized.py`)
- Activating virtual environments and using full paths does not resolve the issue
- Installing dependencies does not fix the directory confusion

## Root Cause - CONFIRMED ANALYSIS

**Primary Root Cause:** VS Code workspace settings + Python interpreter path resolution issue.

**Investigation Results:**
1. ✅ VS Code settings fixed: `"terminal.integrated.cwd": "${workspaceFolder}"`
2. ✅ Terminal opens in correct directory (`C:\net`)
3. ✅ Navigation to backend works (`cd backend`)
4. ✅ Virtual environment activation works (`.\venv\Scripts\Activate.ps1`)
5. ❌ **CRITICAL ISSUE IDENTIFIED:** Python command execution still resolves from wrong directory

**The Real Issue:** Even when the shell is in `C:\net\backend` and shows `(venv)`, when Python executes `python start_optimized.py`, it tries to find the file at `C:\net\start_optimized.py` instead of `C:\net\backend\start_optimized.py`.

This indicates a fundamental disconnect between:
- **Shell working directory:** `C:\net\backend` ✅ Correct
- **Python's script resolution context:** `C:\net` ❌ Wrong

**Root Cause Confirmed:** This is a Python interpreter path resolution issue within VS Code's integrated terminal, not a script content issue.

**Secondary Factors:**
- The issue is not missing dependencies, but a mismatch between the shell's working directory and the context Python uses to resolve script paths.
- VS Code's integrated terminal or task runner may launch commands with an unexpected working directory, especially when using background tasks, custom launch configurations, or certain extensions.
- This can be triggered by:
  - Terminal not being properly reset after previous commands
  - VS Code tasks or launch.json configurations specifying the wrong `cwd`
  - Using full paths in commands, which can override the intended working directory
  - Virtual environment activation scripts that do not update the shell's context

## Step-by-Step Solution

### DEFINITIVE FIX: Update VS Code Settings

1. **Fix the root cause** - Open `.vscode/settings.json` and change:
   ```json
   {
     "terminal.integrated.cwd": "${workspaceFolder}",
     "terminal.integrated.defaultProfile.windows": "PowerShell",
     "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
     "python.terminal.activateEnvironment": false
   }
   ```

2. **Add proper backend task** - In `.vscode/tasks.json`, ensure you have:
   ```json
   {
     "label": "Start Backend Server",
     "type": "shell",
     "command": "python",
     "args": ["start_optimized.py"],
     "options": {
       "cwd": "${workspaceFolder}/backend"
     }
   }
   ```

### 1. Verify VS Code Terminal Working Directory
- In the integrated terminal, run:
  ```powershell
  Get-Location
  ```
- Confirm it matches the intended folder (e.g., `c:\net\backend`).

### 2. Check Python's Perceived Working Directory
- Run:
  ```powershell
  python -c "import os; print(os.getcwd())"
  ```
- Output should match the shell's working directory.

### 3. Avoid Full Paths in Python Commands
- Always use relative paths when running scripts:
  ```powershell
  python start_optimized.py
  ```
- Avoid:
  ```powershell
  python c:\net\backend\start_optimized.py
  ```
- Full paths can cause Python to resolve from the root, not the intended folder.

### 4. Activate Virtual Environment Correctly
- For PowerShell:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- Confirm `(venv)` appears in the prompt.

### 5. Use VS Code Terminal Directly (Not Background Tasks)
- Run commands interactively in the terminal, not as background tasks or via custom launch configurations, unless you have verified the `cwd` setting.
- If using tasks, ensure the `cwd` property is set to the correct folder in `tasks.json`.

### 6. Check VS Code Task/Launch Configurations
- Open `.vscode/tasks.json` and `.vscode/launch.json` (if present).
- Ensure all tasks and launch configurations specify the correct `cwd` (e.g., `c:\net\backend`).

### 7. Reset Terminal Between Runs
- If you encounter directory confusion, close and reopen the terminal to reset its context.
- Alternatively, use the `Clear` or `Kill Terminal` command in VS Code.

### EMERGENCY WORKAROUND: Use VS Code Tasks

If the terminal continues to have directory issues despite the settings fix, use VS Code's task system:

1. **Use Ctrl+Shift+P** and search for "Tasks: Run Task"
2. **Select "Start Backend Server"** from the task list
3. This ensures the correct `cwd` is used regardless of terminal issues

### ALTERNATIVE: Manual Directory Reset

If working directly in terminal:

1. **Always verify location first:**
   ```powershell
   Get-Location  # Should show C:\net\backend
   ```

2. **If in wrong directory, navigate correctly:**
   ```powershell
   Set-Location C:\net\backend  # Absolute path navigation
   ```

3. **Then run your Python command:**
   ```powershell
   python start_optimized.py
   ```

### 8. Document the Solution
- Save this guide in your `docs_dev` folder for future reference.

---

## Quick Troubleshooting Checklist
- [ ] Shell and Python working directories match
- [ ] Virtual environment is activated in the correct folder
- [ ] Python commands use relative paths
- [ ] VS Code tasks/launch configs have correct `cwd`
- [ ] Terminal is reset between runs

---

## Reference
This guide was created in response to recurring issues in the NET-EST project, where backend scripts failed due to directory confusion. Following these steps will help prevent and resolve similar problems in VS Code Python projects.

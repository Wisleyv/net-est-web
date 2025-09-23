# Scripts Directory Structure

This document describes the organized structure of PowerShell scripts in the NET-EST project.

## Directory Organization

### `scripts/backend/`
Backend-specific scripts for Python operations:
- `start-server.ps1` - Start FastAPI backend server
- `run-tests.ps1` - Run backend tests from workspace root
- `run-tests-quick.ps1` - Run backend tests from backend directory

### `scripts/setup/`
Environment setup and configuration scripts:
- `setup-backend-environment.ps1` - Main backend environment setup
- `setup-py312-venv.ps1` - Python 3.12 virtual environment setup
- `setup-python-312.ps1` - Python 3.12 specific setup
- `setup-python-env-wrapper.ps1` - Python environment wrapper
- `recreate-venv-and-install.ps1` - Recreate virtual environment

### `scripts/process/`
Server and process management scripts:
- `start-*` - Server startup scripts
- `stop-*` - Server shutdown scripts
- `restart-*` - Server restart scripts
- `safe-shutdown-complete.ps1` - Complete system shutdown

### `scripts/utilities/`
General utility and maintenance scripts:
- `check-env-status.ps1` - Main environment status checker
- `clean-*` - Cache and cleanup scripts
- `disk-usage-*` - Disk space analysis
- `backup-*` - Backup utilities
- `archive-*` - Archive utilities

### `scripts/debug/`
Debugging and diagnostic scripts:
- `performance-monitor.ps1` - System performance monitoring
- `inspect-*` - Process inspection utilities
- `debug-*` - Debug utilities
- `capture-*` - Process capture utilities

### `scripts/port-management/`
Port management and conflict resolution:
- `release-ports.ps1` - Release NET-EST project ports
- `manage-ports*.ps1` - Port management utilities
- `test-port-management.ps1` - Port management testing

## Naming Conventions

All scripts follow a consistent **verb-noun** naming pattern with hyphens:
- `start-server.ps1` (not `start_server.ps1`)
- `check-env-status.ps1` (not `env_status_fixed.ps1`)
- `clean-cache-files.ps1` (not `clean_cache.ps1`)

## Integration with tasks.json

All scripts are referenced in `.vscode/tasks.json` using relative paths:
```json
{
    "command": "scripts/backend/start-server.ps1",
    "options": {
        "cwd": "${workspaceFolder}"
    }
}
```

## Workspace Detection

Scripts automatically detect the workspace folder using:
1. `$env:WORKSPACEFOLDER` environment variable (set by VS Code)
2. Auto-detection from script location (relative to scripts directory)

## Maintenance

When adding new scripts:
1. Place in appropriate subdirectory
2. Follow verb-noun naming convention with hyphens
3. Update tasks.json if the script should be available as a task
4. Document any new functionality in this file
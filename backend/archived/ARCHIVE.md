# Archived files

These files were moved out of the importable paths to reduce accidental imports, runtime noise, and test flakiness.
They are preserved in this folder and the repository history. To restore any file:

  git checkout <branch> -- path/to/file
  git mv backend/archived/<file> <original/path>
  git commit -m "restore: <file>"

Common candidates (review before running the archival script):
- debug_*.py (dev/debugging helpers)
- *.py.bak (backup copies)
- strategy_detector_backup*.py (legacy variations)
- vscode_backup_* (workspace backups)

Rationale
- Non-destructive: files are moved with git so history is preserved.
- Prevents accidental imports from debug code.
- Keeps the repo tidy while preserving content for future reference.

Restore procedure
1. git mv backend/archived/<file> <original/path>
2. git commit -m "restore: <file>"
3. Run tests to confirm behavior.

Notes
- Review the archive list and the archival script patterns before executing.
- If any archived file is required at runtime, restore it and refactor imports instead of deleting.

---
/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/

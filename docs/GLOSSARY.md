# Glossary

This glossary explains acronyms and shorthand used in the HITL project to make onboarding easier for new contributors.

---

## Core Concepts

- **HITL** → **Human-in-the-Loop**  
  A system design where humans validate, refine, or override machine-generated outputs to ensure quality and correctness.

- **CRUD** → **Create, Read, Update, Delete**  
  The four basic operations for data handling. In this project, it refers to annotation management: creating, reviewing, modifying, and deleting annotations.

- **FS** → **File System**  
  A storage backend where data is written as files (e.g., JSONL/CSV). FS is the default persistence option in earlier phases.

- **SQLite**  
  A lightweight relational database used as an alternative persistence backend, supporting migrations and audit queries.

- **CLI** → **Command-Line Interface**  
  A text-based interface for running commands, such as export tools, without the graphical frontend.

- **E2E** → **End-to-End**  
  Testing that verifies the full workflow of the system — frontend to backend to persistence — to ensure integrated behavior.

---

## Development & Tooling

- **VCS** → **Version Control System**  
  Here, Git is the version control system managing source code history and collaboration.

- **PAT** → **Personal Access Token**  
  A GitHub authentication token granting push/pull access in place of a password.

- **CI** → **Continuous Integration**  
  Automated pipelines that run tests and checks (e.g., GitHub Actions) whenever code is pushed, to prevent regressions.

- **Venv** → **Virtual Environment**  
  A Python environment isolated from the global installation, ensuring reproducible dependencies.

- **pwsh** → **PowerShell (Core)**  
  A cross-platform shell used for automation and scripting. In this project, some VS Code tasks reference PowerShell.

---

## Documentation & Exports

- **JSONL** → **JSON Lines**  
  A text format where each line is a valid JSON object, useful for streaming and ML dataset exports.

- **CSV** → **Comma-Separated Values**  
  A tabular text format for representing data in spreadsheets or ML pipelines.

---

## Testing & Quality

- **Vitest**  
  A unit testing framework for modern JavaScript/TypeScript projects (frontend).

- **Playwright**  
  A framework for running browser-based E2E tests.

- **Accessibility (a11y)**  
  Practices ensuring the system is usable by people with disabilities, including screen reader and keyboard-only users.

---

## Project-Specific

- **Audit Log**  
  A record of all actions (create, update, delete, accept/reject) taken on annotations, ensuring transparency and reproducibility.

- **Feature Flags**  
  Configurable switches to enable/disable features in development or production without changing the core codebase.

- **Dual-Write**  
  Writing data simultaneously to two persistence backends (FS and SQLite) to ensure consistency during migrations.

- **Diagnostics Endpoint**  
  A backend API endpoint that exposes system health and debug information.

---

✨ Tip: If you encounter an unfamiliar acronym not listed here, please add it so the glossary stays up to date!

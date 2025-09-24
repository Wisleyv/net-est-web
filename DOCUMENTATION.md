# NET-EST Documentation Hub

This document serves as the central hub for all NET-EST project documentation. It provides an overview of the project and links to specialized documentation files for different aspects of the system.

## Project Overview

NET-EST is a linguistic analysis system developed by the Núcleo de Estudos de Tradução (UFRJ) in partnership with Politécnico de Leiria. The system analyzes intralingual translation, focusing on text simplification strategies.

## Current Status (as of August 5, 2025)

- **Foundation Layer**: ✅ Complete
- **Text Input Module**: ✅ Complete
- **Semantic Alignment**: 🚧 In Progress (80%)
- **Feature Extraction**: 🚧 In Progress (60%)
- **UI Integration**: 🚧 In Progress (70%)
- **Analytics Module**: 🔄 Planned

## Documentation Structure

### Core Documentation

- [**README.md**](./README.md): Quick start guide and essential information
- [**ARCHITECTURE.md**](./ARCHITECTURE.md): System architecture and design decisions
- [**DEVELOPMENT.md**](./DEVELOPMENT.md): Development workflow and guidelines

### Component-Specific Documentation

- **Backend**: [Backend Documentation](./backend/README.md)
- **Frontend**: [Frontend Documentation](./frontend/README.md)

### Specialized Documentation

- [**API Documentation**](./docs/api/endpoints.md): Detailed API reference
- [**Simplification Strategies**](./docs/Tabela%20Simplificação%20Textual.md): Linguistic strategies identified by the system

### Development Resources

- [**Development Resources**](./DEVELOPMENT_RESOURCES.md): Consolidated development guides and troubleshooting
- [**Project Structure**](./docs_dev/project_structure.md): Detailed breakdown of repository organization

## Documentation By Audience

### For New Developers

1. Start with the [README.md](./README.md) for a project overview
2. Review the [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system design
3. Set up your development environment using [DEVELOPMENT.md](./DEVELOPMENT.md)
4. Refer to component-specific documentation as needed

### For Linguistic Researchers

1. Start with the [README.md](./README.md) for a project overview
2. Review the [Simplification Strategies](./docs/Tabela%20Simplificação%20Textual.md) documentation
3. Understand the [Feature Extraction](./docs/api/endpoints.md#feature-extraction) process

### For Project Maintainers

1. Maintain familiarity with all documentation
2. Regularly update status information in this document
3. Ensure documentation remains synchronized with code changes

## Incident Log (2025-09-24 Minimal Entry)

On 2025-09-24 a loss of the critical `.vscode/tasks.json` and `docs_dev/development_guidelines.md` was detected during P0 UI debugging.

Root Cause:
- Blanket `.vscode/` ignore rule in `.gitignore` prevented version control of the authoritative orchestration file.

Immediate Remediation:
1. Restored both files from historical commit `eb8d3c1e5`.
2. Adjusted `.gitignore` to track only `tasks.json` via explicit negation rule.
3. Embedded provenance metadata in a `_provenance` block inside `tasks.json` (keeps valid JSON for tooling).
4. Added `tools/verify_integrity.py` for minimal presence + structure validation.

Deferred (Post-P0):
- Expanded audit log & hash ledger
- CI gating / CODEOWNERS protections
- Baseline diff automation & drift report

See `docs_dev/development_guidelines.md` (Authority Protocol) for operational directives.

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/

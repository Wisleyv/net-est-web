# Changelog

## 2025-09-25

### Added
- Accurate character spans for meso and micro stage strategies, enabling consistent range highlighting in the target text panel.

### Fixed
- Text selection validation now ignores superscript markers while preventing overlaps with existing highlighted ranges, restoring manual tag creation.
- Explanation generator now accepts both dict and Pydantic model inputs, resolving annotation export 400 errors.
- Hierarchical analysis output generation hardened with fallback retry logic to ensure consistent availability.

### Changed
- Bumped `pytest-asyncio` to 0.23.7 and re-synced backend dev dependencies so async-marked tests execute under pytest 8.
- Introduced persistence defaults (`PERSISTENCE_BACKEND`, `ENABLE_DUAL_WRITE`, `ENABLE_FS_FALLBACK`, `SQLITE_DB_PATH`) in `src/core/config.py` to stabilize repository selection during tests.

### Tests
- Backend test suite: 253 passed, 2 skipped, 21 warnings - all critical functionality restored
- Hierarchical output generation now stable across all test scenarios
- Explanation generator handles both dict and Pydantic model inputs without errors

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/

"""Legacy compatibility layer.

Historically the codebase used a global `store` instance (AnnotationStore).
Tests and some modules still import `store` directly and access internal
attributes for seeding (e.g. `store._annotations`). During Phase 4 we
introduced the repository abstraction. To avoid a large, risky refactor
of all tests at once, we map the legacy `store` symbol to the process-wide
FSAnnotationRepository instance. This preserves behavior while allowing
new code paths to rely on the abstraction.

Future: remove this file after tests migrate to repository factory.
"""
from src.repository.fs_repository import get_repository

store = get_repository()


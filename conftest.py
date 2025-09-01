"""
Repository-level pytest configuration helpers.

This file ensures the `backend/src` directory is on sys.path during test
collection and execution so legacy tests that import `services.*` or
use package-relative imports resolve correctly when pytest is run from the
repo root.
"""
import os
import sys

ROOT = os.path.dirname(__file__)
BACKEND_SRC = os.path.join(ROOT, "backend", "src")

if os.path.isdir(BACKEND_SRC) and BACKEND_SRC not in sys.path:
    # Prepend so local package resolution takes precedence over installed packages
    sys.path.insert(0, BACKEND_SRC)

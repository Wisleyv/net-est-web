"""Top-level test configuration and compatibility shims.

This file auto-marks coroutine test functions with pytest.mark.asyncio so that
tests declared as `async def` in demonstration scripts (e.g., test_confidence_*.py)
are executed under the asyncio plugin during CI and local runs.

This is a small, safe shim to avoid editing demonstration test files directly.
"""
import inspect
import os
import pytest

# When running tests we often want to avoid loading large ML models (torch/spaCy)
# which can cause memory/OS-level issues in CI or constrained environments.
# Set an env var here so services can skip heavy model initialization during tests.
os.environ.setdefault("NET_EST_DISABLE_MODELS", "1")


def pytest_collection_modifyitems(config, items):
    """Auto-apply asyncio marker to coroutine test functions.

    Some demo/test scripts declare `async def` tests without explicit markers.
    When pytest-asyncio is installed this shim ensures those tests are executed
    by adding the `pytest.mark.asyncio` marker at collection time.
    """
    for item in items:
        try:
            fn = getattr(item, "obj", None)
            if inspect.iscoroutinefunction(fn):
                item.add_marker(pytest.mark.asyncio)
        except Exception:
            # Be conservative: do not fail collection if something goes wrong here.
            continue
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

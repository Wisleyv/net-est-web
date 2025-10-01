import os
import json
import importlib
from pathlib import Path

# Ensure models are disabled for fast tests
os.environ.setdefault("NET_EST_DISABLE_MODELS", "1")

# Force reload in case prior tests imported modules before we changed YAML
import core.feature_flags as ff_module  # type: ignore
importlib.reload(ff_module)
from core.feature_flags import feature_flags  # type: ignore

# Import the feature switches layer
import core.feature_switches as fs  # type: ignore
importlib.reload(fs)
from core.feature_switches import FEATURE_HIERARCHICAL_OUTPUT, FEATURE_MANUAL_TAGGING  # type: ignore

def test_hierarchical_flag_default_disabled():
    # Direct YAML path assertion
    assert feature_flags.is_enabled("experimental.hierarchical_output") is False
    assert FEATURE_HIERARCHICAL_OUTPUT is False

def test_manual_tagging_flag_default_disabled():
    assert feature_flags.is_enabled("experimental.manual_tagging") is False
    assert FEATURE_MANUAL_TAGGING is False


def test_feature_flags_yaml_contains_expected_keys():
    # Validate structure presence; do not assume other flags' values
    flags = feature_flags.flags
    assert "experimental" in flags
    experimental = flags["experimental"]
    assert "hierarchical_output" in experimental
    assert "manual_tagging" in experimental

# Optional future expansion: if API endpoint is wired in tests, we could hit it with TestClient.
# Avoid adding FastAPI dependency here unless already present in test harness.

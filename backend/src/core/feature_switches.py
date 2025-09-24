"""Centralized feature switch accessors.

Provides stable, typed-like constants for feature gates so calling code does not
scatter raw string keys. This layer allows future enrichment (e.g., telemetry,
rollout strategies) without changing import sites.
"""
from __future__ import annotations

from .feature_flags import feature_flags

# Public constant-style accessors. Evaluated at import time for simplicity.
# If hot-reload semantics are later required, we can convert to functions.

FEATURE_HIERARCHICAL_OUTPUT: bool = feature_flags.is_enabled("experimental.hierarchical_output")
FEATURE_MANUAL_TAGGING: bool = feature_flags.is_enabled("experimental.manual_tagging")

__all__ = [
    "FEATURE_HIERARCHICAL_OUTPUT",
    "FEATURE_MANUAL_TAGGING",
]

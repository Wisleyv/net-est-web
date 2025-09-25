"""Explanation generator utilities for annotations and strategies."""

from typing import Any, Dict, Mapping, Optional

from pydantic import BaseModel


def _to_mapping(data: Any) -> Mapping[str, Any]:
    """Return a read-only mapping for diverse annotation/context inputs."""

    if isinstance(data, Mapping):
        return data

    if isinstance(data, BaseModel):
        return data.model_dump()

    if hasattr(data, "model_dump"):
        try:
            return data.model_dump()  # type: ignore[call-arg]
        except Exception:
            pass

    if hasattr(data, "dict"):
        try:
            return data.dict()  # type: ignore[call-arg]
        except Exception:
            pass

    if hasattr(data, "__dict__"):
        return dict(getattr(data, "__dict__"))  # type: ignore[arg-type]

    return {}


def generate_explanation(
    annotation: Any,
    context: Optional[Any] = None,
) -> str:
    """Generate a human-readable explanation for an annotation input.

    Accepts either dictionaries, Pydantic models, or lightweight objects that
    expose `model_dump`, `dict`, or `__dict__` so repository callers can pass
    domain models directly without conversion.
    """

    annotation_data = _to_mapping(annotation)
    context_data = _to_mapping(context) if context is not None else {}

    strategy_code = annotation_data.get("strategy_code", "UNKNOWN")
    confidence = annotation_data.get("confidence", 0.0) or 0.0

    base_explanation = f"Estratégia {strategy_code} detectada"

    try:
        confidence_value = float(confidence)
    except (TypeError, ValueError):
        confidence_value = 0.0

    if confidence_value > 0:
        confidence_pct = int(confidence_value * 100)
        base_explanation += f" com {confidence_pct}% de confiança"

    evidence = context_data.get("evidence")
    if evidence:
        try:
            first_evidence = evidence[0]
        except (TypeError, IndexError):
            first_evidence = None
        if first_evidence:
            base_explanation += f". Evidência: {first_evidence}"

    return base_explanation
"""Optional dependency gates with stable installation guidance."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType


def require_optional(import_name: str, extra: str, feature: str) -> ModuleType:
    try:
        return import_module(import_name)
    except ImportError as exc:
        raise ImportError(
            f"{feature} requires the optional dependency {import_name!r}. "
            f"Install it with: pip install 'universal-output-hub[{extra}]'"
        ) from exc

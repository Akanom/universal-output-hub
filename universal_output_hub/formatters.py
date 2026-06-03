"""Formatting utilities for Universal Output Hub."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import pandas as pd

DEFAULT_STAR_LEVELS: dict[str, float] = {"***": 0.01, "**": 0.05, "*": 0.10}


def is_missing(value: Any) -> bool:
    """Return True for None, NaN, pandas NA, and non-finite floats."""
    if value is None:
        return True
    try:
        if bool(pd.isna(value)):
            return True
    except Exception:
        pass
    try:
        value_float = float(value)
        return math.isnan(value_float) or math.isinf(value_float)
    except Exception:
        return False


def as_float(value: Any) -> float | None:
    """Convert a value to finite float where possible."""
    if is_missing(value):
        return None
    try:
        output = float(value)
    except Exception:
        return None
    if math.isnan(output) or math.isinf(output):
        return None
    return output


def format_number(value: Any, decimals: int = 3) -> str:
    """Format a numeric value for publication tables."""
    value_float = as_float(value)
    if value_float is None:
        return ""
    return f"{value_float:.{decimals}f}"


def significance_stars(
    pvalue: Any,
    star_levels: Mapping[str, float] | None = None,
) -> str:
    """Return significance stars for a p-value.

    Defaults follow common econometric table conventions:
    *** for p <= 0.01, ** for p <= 0.05, and * for p <= 0.10.
    Custom levels may be supplied as {"†": 0.15, "*": 0.10, ...}.
    """
    pvalue_float = as_float(pvalue)
    if pvalue_float is None:
        return ""
    levels = dict(star_levels or DEFAULT_STAR_LEVELS)
    for mark, threshold in sorted(levels.items(), key=lambda item: item[1]):
        threshold_float = as_float(threshold)
        if threshold_float is not None and pvalue_float <= threshold_float:
            return mark
    return ""


def format_significance_note(
    star_levels: Mapping[str, float] | None = None,
    *,
    comparator: str = "≤",
) -> str:
    """Build a compact publication-table note for significance stars."""
    levels = dict(star_levels or DEFAULT_STAR_LEVELS)
    parts: list[str] = []
    for mark, threshold in sorted(levels.items(), key=lambda item: item[1], reverse=True):
        threshold_float = as_float(threshold)
        if threshold_float is None:
            continue
        parts.append(f"{mark} p{comparator}{threshold_float:g}")
    return ", ".join(parts)


def safe_filename(name: str, *, suffix: str | None = None) -> str:
    """Create a filesystem-safe filename from an arbitrary output name."""
    import re

    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(name).strip()).strip("_")
    if not cleaned:
        cleaned = "output"
    if suffix:
        suffix = suffix if suffix.startswith(".") else f".{suffix}"
        if not cleaned.lower().endswith(suffix.lower()):
            cleaned += suffix
    return cleaned


def normalise_label(value: Any) -> str:
    """Normalise a human-facing label."""
    import re

    return re.sub(r"\s+", " ", str(value).strip())

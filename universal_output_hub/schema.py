from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NormalizedCoefficient:
    """One normalized coefficient row."""

    name: str
    estimate: float | None = None
    std_error: float | None = None
    statistic: float | None = None
    p_value: float | None = None
    conf_low: float | None = None
    conf_high: float | None = None


@dataclass(frozen=True)
class NormalizedResult:
    """Estimator-agnostic representation of a model result."""

    name: str
    estimator: str | None = None
    backend: str | None = None
    covariance_type: str | None = None
    nobs: int | None = None
    n_groups: int | None = None
    n_instruments: int | None = None
    coefficients: list[NormalizedCoefficient] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


def significance_stars(p_value: float | None) -> str:
    """Return conventional significance stars."""

    if p_value is None:
        return ""

    try:
        p = float(p_value)
    except (TypeError, ValueError):
        return ""

    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""

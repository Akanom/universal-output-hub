from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

from universal_output_hub.schema import NormalizedCoefficient, NormalizedResult


def _safe_get(obj: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if isinstance(obj, Mapping) and name in obj:
            return obj[name]
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def _as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _series_from_any(value: Any) -> pd.Series:
    if value is None:
        return pd.Series(dtype="float64")
    if isinstance(value, pd.Series):
        return value
    if isinstance(value, Mapping):
        return pd.Series(value)
    if isinstance(value, pd.DataFrame) and value.shape[1] == 1:
        return value.iloc[:, 0]
    return pd.Series(value)


def _extract_params(result: Any) -> pd.Series:
    return _series_from_any(
        _safe_get(result, "params", "coefficients", "coef", "beta", default=None)
    )


def _extract_std_errors(result: Any) -> pd.Series:
    return _series_from_any(
        _safe_get(
            result,
            "std_errors",
            "standard_errors",
            "stderr",
            "std_err",
            "bse",
            "se",
            default=None,
        )
    )


def _extract_p_values(result: Any) -> pd.Series:
    return _series_from_any(
        _safe_get(result, "p_values", "pvalues", "pvals", "p_value", default=None)
    )


def _extract_statistics(result: Any) -> pd.Series:
    return _series_from_any(
        _safe_get(
            result,
            "z_values",
            "z",
            "t_values",
            "tvalues",
            "t_stats",
            "statistics",
            default=None,
        )
    )


def _extract_conf_int(result: Any) -> tuple[pd.Series, pd.Series]:
    conf = _safe_get(result, "conf_int", "confidence_intervals", default=None)

    if callable(conf):
        try:
            conf = conf()
        except TypeError:
            conf = None

    if isinstance(conf, pd.DataFrame) and conf.shape[1] >= 2:
        return conf.iloc[:, 0], conf.iloc[:, 1]

    return pd.Series(dtype="float64"), pd.Series(dtype="float64")


def _extract_coefficients(result: Any) -> list[NormalizedCoefficient]:
    params = _extract_params(result)
    std_errors = _extract_std_errors(result)
    p_values = _extract_p_values(result)
    statistics = _extract_statistics(result)
    conf_low, conf_high = _extract_conf_int(result)

    coefficients: list[NormalizedCoefficient] = []

    for name in list(params.index):
        coefficients.append(
            NormalizedCoefficient(
                name=str(name),
                estimate=_as_float(params.get(name)),
                std_error=_as_float(std_errors.get(name)),
                statistic=_as_float(statistics.get(name)),
                p_value=_as_float(p_values.get(name)),
                conf_low=_as_float(conf_low.get(name)),
                conf_high=_as_float(conf_high.get(name)),
            )
        )

    return coefficients


def _extract_diagnostics(result: Any) -> dict[str, Any]:
    names = {
        "hansen_p": ("hansen_p",),
        "sargan_p": ("sargan_p",),
        "ar1": ("ar1",),
        "ar1_p": ("ar1_p",),
        "ar2": ("ar2",),
        "ar2_p": ("ar2_p",),
        "j_stat": ("j_stat", "j"),
        "n_instruments": ("n_instruments", "instrument_count"),
        "n_groups": ("n_groups", "groups"),
        "nobs": ("nobs", "n_obs"),
    }

    diagnostics: dict[str, Any] = {}

    for public_name, aliases in names.items():
        value = _safe_get(result, *aliases, default=None)
        if value is not None:
            diagnostics[public_name] = value

    extra = _safe_get(result, "diagnostics", default=None)
    if isinstance(extra, Mapping):
        diagnostics.update(dict(extra))

    return diagnostics


def normalize_result(
    result: Any,
    *,
    name: str | None = None,
    estimator: str | None = None,
    backend: str | None = None,
) -> NormalizedResult:
    """Normalize a result object into the Universal Output Hub schema."""

    result_name = (
        name
        or _safe_get(result, "name", "model_name", "spec_name", default=None)
        or "model"
    )

    inferred_estimator = estimator or _safe_get(
        result,
        "estimator",
        "estimator_type",
        "model_type",
        default=None,
    )

    inferred_backend = backend or _safe_get(
        result,
        "backend",
        "backend_name",
        default=None,
    )

    covariance_type = _safe_get(
        result,
        "covariance_type",
        "cov_type",
        "vcov_type",
        default=None,
    )

    metadata = _safe_get(result, "metadata", default=None)
    if not isinstance(metadata, Mapping):
        metadata = {}

    return NormalizedResult(
        name=str(result_name),
        estimator=str(inferred_estimator) if inferred_estimator is not None else None,
        backend=str(inferred_backend) if inferred_backend is not None else None,
        covariance_type=str(covariance_type) if covariance_type is not None else None,
        nobs=_as_int(_safe_get(result, "nobs", "n_obs", default=None)),
        n_groups=_as_int(_safe_get(result, "n_groups", "groups", default=None)),
        n_instruments=_as_int(
            _safe_get(result, "n_instruments", "instrument_count", default=None)
        ),
        coefficients=_extract_coefficients(result),
        diagnostics=_extract_diagnostics(result),
        metadata=dict(metadata),
    )

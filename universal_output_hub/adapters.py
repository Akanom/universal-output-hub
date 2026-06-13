"""Model adapters for Universal Output Hub.

The philosophy is deliberately practical: accept outputs from Python model objects,
plain dictionaries, and coefficient tables exported from Stata/R/SPSS/EViews/etc.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from .formatters import normalise_label


@dataclass(slots=True)
class RegressionModel:
    """Canonical representation of one fitted model/result."""

    name: str
    params: pd.Series
    std_errors: pd.Series = field(default_factory=lambda: pd.Series(dtype="float64"))
    pvalues: pd.Series = field(default_factory=lambda: pd.Series(dtype="float64"))
    depvar: str | None = None
    statistics: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"

    @property
    def terms(self) -> list[str]:
        return [str(x) for x in self.params.index.tolist()]

    def coefficient(self, term: str) -> Any:
        return self.params.get(term, None)

    def standard_error(self, term: str) -> Any:
        return self.std_errors.get(term, None)

    def pvalue(self, term: str) -> Any:
        return self.pvalues.get(term, None)

    def stat(self, key: str) -> Any:
        if key in self.statistics:
            return self.statistics[key]
        return self.diagnostics.get(key, None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "depvar": self.depvar,
            "source": self.source,
            "params": _json_safe(self.params),
            "std_errors": _json_safe(self.std_errors),
            "pvalues": _json_safe(self.pvalues),
            "statistics": _json_safe(self.statistics),
            "diagnostics": _json_safe(self.diagnostics),
            "metadata": _json_safe(self.metadata),
        }


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, pd.Series):
        return {str(k): _json_safe(v) for k, v in value.to_dict().items()}
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    try:
        return float(value)
    except Exception:
        return str(value)


def _call_if_possible(value: Any) -> Any:
    if callable(value):
        try:
            return value()
        except TypeError:
            return value
        except Exception:
            return value
    return value


def _first_attr(obj: Any, names: Sequence[str], default: Any = None) -> Any:
    for name in names:
        if hasattr(obj, name):
            try:
                return _call_if_possible(getattr(obj, name))
            except Exception:
                continue
    return default


def _series(value: Any, *, name: str) -> pd.Series:
    if value is None:
        return pd.Series(dtype="float64", name=name)
    if isinstance(value, pd.Series):
        out = value.copy()
        out.name = name
        out.index = out.index.map(str)
        return out
    if isinstance(value, Mapping):
        return pd.Series(dict(value), name=name)
    try:
        out = pd.Series(value, name=name)
        if isinstance(out.index, pd.RangeIndex):
            out.index = [f"x{i}" for i in range(len(out))]
        out.index = out.index.map(str)
        return out
    except Exception:
        return pd.Series(dtype="float64", name=name)


# ------------------------------------------------------------------
# Embedded regression-table statistic extraction
# ------------------------------------------------------------------

_STAT_ALIASES = {
    "n": "N",
    "obs": "N",
    "nobs": "N",
    "observations": "N",
    "numberofobservations": "N",
    "r2": "R2",
    "rsquared": "R2",
    "rsquare": "R2",
    "adjr2": "Adj. R2",
    "adjustedr2": "Adj. R2",
    "adjustedrsquared": "Adj. R2",
    "withinr2": "Within R2",
    "overallr2": "Overall R2",
    "aic": "AIC",
    "bic": "BIC",
    "loglikelihood": "Log Likelihood",
    "fstatistic": "F statistic",
    "fpvalue": "F p-value",
    "entityfe": "Entity FE",
    "countryfe": "Entity FE",
    "individualfe": "Entity FE",
    "firmfe": "Entity FE",
    "unitfe": "Entity FE",
    "timefe": "Time FE",
    "yearfe": "Time FE",
    "periodfe": "Time FE",
    "fixedeffects": "Fixed effects",
    "clusteredse": "Clustered SE",
}

_DIAGNOSTIC_ALIASES = {
    "ar1p": "AR(1) p",
    "ar1pvalue": "AR(1) p",
    "ar1testp": "AR(1) p",
    "ar2p": "AR(2) p",
    "ar2pvalue": "AR(2) p",
    "ar2testp": "AR(2) p",
    "hansenp": "Hansen p",
    "hansenjp": "Hansen p",
    "hansenjtestp": "Hansen p",
    "hansenpvalue": "Hansen p",
    "hansenjtestpvalue": "Hansen p",
    "sarganp": "Sargan p",
    "sarganpvalue": "Sargan p",
    "sargantestp": "Sargan p",
    "diffhansenp": "Diff-Hansen p",
    "differenceinhansenp": "Diff-Hansen p",
    "differenceinhansenpvalue": "Diff-Hansen p",
    "instruments": "Instruments",
    "numberofinstruments": "Instruments",
    "ninstruments": "Instruments",
    "numinstruments": "Instruments",
}


def _compact_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _first_non_missing(row: pd.Series, columns: Sequence[str | None]) -> Any:
    for column in columns:
        if column and column in row.index:
            value = row[column]
            try:
                if pd.notna(value):
                    return value
            except Exception:
                return value
    return None


def _row_has_no_estimation_values(
    row: pd.Series,
    *,
    coef_col: str,
    se_col: str | None,
    pvalue_col: str | None,
) -> bool:
    non_stat_cols = [se_col, pvalue_col]
    for column in non_stat_cols:
        if column and column in row.index:
            try:
                if pd.notna(row[column]) and str(row[column]).strip() != "":
                    return False
            except Exception:
                return False
    return True


def _extract_embedded_table_stats(
    table: pd.DataFrame,
    *,
    term_col: str,
    coef_col: str,
    se_col: str | None,
    pvalue_col: str | None,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    """Extract N/R2/Hansen/AR/Sargan/etc. rows from imported coefficient tables.

    This supports Stata/R/MATLAB/SPSS/EViews-style exports where diagnostics
    are included as rows below the coefficient rows.
    """
    stats: dict[str, Any] = {}
    diagnostics: dict[str, Any] = {}
    keep_rows: list[bool] = []

    value_columns = [coef_col, "value", "stat", "statistic", "estimate"]

    for _, row in table.iterrows():
        term = str(row[term_col])
        key = _compact_key(term)

        stat_name = _STAT_ALIASES.get(key)
        diagnostic_name = _DIAGNOSTIC_ALIASES.get(key)

        if (stat_name or diagnostic_name) and _row_has_no_estimation_values(
            row,
            coef_col=coef_col,
            se_col=se_col,
            pvalue_col=pvalue_col,
        ):
            value = _first_non_missing(row, value_columns)
            if diagnostic_name:
                diagnostics[diagnostic_name] = value
            elif stat_name:
                stats[stat_name] = value
            keep_rows.append(False)
        else:
            keep_rows.append(True)

    return table.loc[keep_rows].copy(), stats, diagnostics


def from_coefficient_table(
    table: pd.DataFrame,
    *,
    name: str,
    term_col: str = "term",
    coef_col: str = "coef",
    se_col: str | None = "se",
    pvalue_col: str | None = "pvalue",
    depvar: str | None = None,
    statistics: Mapping[str, Any] | None = None,
    diagnostics: Mapping[str, Any] | None = None,
    source: str = "coefficient-table",
) -> RegressionModel:
    """Build a model from a coefficient table exported by any software.

    Expected minimum columns are term and coefficient. Standard errors and
    p-values are optional.

    Diagnostic/statistic rows such as N, Hansen p, AR(2) p, Sargan p,
    Instruments, Entity FE, and Time FE are automatically extracted when they
    appear as rows in the imported table.
    """
    if term_col not in table.columns:
        raise ValueError(f"term_col='{term_col}' was not found in the coefficient table.")
    if coef_col not in table.columns:
        raise ValueError(f"coef_col='{coef_col}' was not found in the coefficient table.")

    cleaned, embedded_stats, embedded_diagnostics = _extract_embedded_table_stats(
        table,
        term_col=term_col,
        coef_col=coef_col,
        se_col=se_col,
        pvalue_col=pvalue_col,
    )

    final_stats = dict(embedded_stats)
    final_stats.update(dict(statistics or {}))

    final_diagnostics = dict(embedded_diagnostics)
    final_diagnostics.update(dict(diagnostics or {}))

    indexed = cleaned.copy()
    indexed[term_col] = indexed[term_col].map(str)
    indexed = indexed.set_index(term_col)

    return RegressionModel(
        name=normalise_label(name),
        depvar=depvar,
        params=_series(indexed[coef_col], name="coef"),
        std_errors=(
            _series(indexed[se_col], name="se") if se_col and se_col in indexed.columns else pd.Series(dtype="float64")
        ),
        pvalues=(
            _series(indexed[pvalue_col], name="pvalue")
            if pvalue_col and pvalue_col in indexed.columns
            else pd.Series(dtype="float64")
        ),
        statistics=final_stats,
        diagnostics=final_diagnostics,
        metadata={"term_col": term_col, "coef_col": coef_col, "se_col": se_col, "pvalue_col": pvalue_col},
        source=source,
    )


def _from_mapping(
    result: Mapping[str, Any],
    *,
    name: str | None = None,
    diagnostics: Mapping[str, Any] | None = None,
) -> RegressionModel:
    model_name = normalise_label(name or result.get("name") or "Model")
    params = result.get("params") or result.get("coef") or result.get("coefs") or result.get("coefficients")
    se = result.get("std_errors") or result.get("standard_errors") or result.get("bse") or result.get("se")
    pvalues = result.get("pvalues") or result.get("p_values") or result.get("pvalue")

    stats = dict(result.get("statistics") or result.get("stats") or {})
    diags = dict(result.get("diagnostics") or {})
    if diagnostics:
        diags.update(dict(diagnostics))

    # Convenience: allow common stats at top level.
    for key in ["N", "nobs", "R2", "Adj. R2", "AIC", "BIC"]:
        if key in result and key not in stats:
            stats["N" if key == "nobs" else key] = result[key]
    for key in ["AR(1) p", "AR(2) p", "Hansen p", "Sargan p", "Diff-Hansen p", "Instruments"]:
        if key in result and key not in diags:
            diags[key] = result[key]

    return RegressionModel(
        name=model_name,
        depvar=result.get("depvar") or result.get("dependent"),
        params=_series(params, name="coef"),
        std_errors=_series(se, name="se"),
        pvalues=_series(pvalues, name="pvalue"),
        statistics=stats,
        diagnostics=diags,
        metadata=dict(result.get("metadata") or {}),
        source=str(result.get("source") or "mapping"),
    )


def _from_statsmodels(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    model = getattr(result, "model", None)
    depvar = _first_attr(model, ["endog_names"], None) if model is not None else None
    stats: dict[str, Any] = {}
    for attr, label in [
        ("nobs", "N"),
        ("rsquared", "R2"),
        ("rsquared_adj", "Adj. R2"),
        ("aic", "AIC"),
        ("bic", "BIC"),
        ("llf", "Log Likelihood"),
        ("f_pvalue", "F p-value"),
    ]:
        if hasattr(result, attr):
            try:
                stats[label] = getattr(result, attr)
            except Exception:
                pass
    return RegressionModel(
        name=name,
        depvar=str(depvar) if depvar is not None else None,
        params=_series(getattr(result, "params", None), name="coef"),
        std_errors=_series(getattr(result, "bse", None), name="se"),
        pvalues=_series(getattr(result, "pvalues", None), name="pvalue"),
        statistics=stats,
        diagnostics=dict(diagnostics or {}),
        metadata={"class": result.__class__.__name__, "module": result.__class__.__module__},
        source="statsmodels",
    )


def _from_linearmodels(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    stats: dict[str, Any] = {}
    for attr, label in [
        ("nobs", "N"),
        ("rsquared", "R2"),
        ("rsquared_within", "Within R2"),
        ("rsquared_between", "Between R2"),
        ("rsquared_overall", "Overall R2"),
        ("loglik", "Log Likelihood"),
    ]:
        if hasattr(result, attr):
            try:
                stats[label] = getattr(result, attr)
            except Exception:
                pass
    f_stat = getattr(result, "f_statistic", None)
    if f_stat is not None:
        stats["F statistic"] = getattr(f_stat, "stat", None)
        stats["F p-value"] = getattr(f_stat, "pval", None)

    depvar = None
    model = getattr(result, "model", None)
    if model is not None:
        depvar = _first_attr(model, ["dependent", "endog_names"], None)
        if hasattr(depvar, "vars"):
            try:
                depvar = ", ".join(map(str, depvar.vars))
            except Exception:
                depvar = str(depvar)

    return RegressionModel(
        name=name,
        depvar=str(depvar) if depvar is not None else None,
        params=_series(getattr(result, "params", None), name="coef"),
        std_errors=_series(_first_attr(result, ["std_errors", "bse", "std_err"], None), name="se"),
        pvalues=_series(getattr(result, "pvalues", None), name="pvalue"),
        statistics=stats,
        diagnostics=dict(diagnostics or {}),
        metadata={"class": result.__class__.__name__, "module": result.__class__.__module__},
        source="linearmodels",
    )


def _from_pyfixest_like(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    params = _first_attr(result, ["coef", "coefs", "params", "coefficients"], None)
    se = _first_attr(result, ["se", "std_errors", "bse"], None)
    pvalues = _first_attr(result, ["pvalue", "pvalues", "p_value", "p_values"], None)

    tidy = _first_attr(result, ["tidy", "coeftable", "coef_table"], None)
    if isinstance(tidy, pd.DataFrame) and params is None:
        lower = {str(col).lower(): col for col in tidy.columns}
        term_col = lower.get("term") or lower.get("variable")
        coef_col = lower.get("estimate") or lower.get("coef") or lower.get("coefficient")
        se_col = lower.get("std.error") or lower.get("std_error") or lower.get("se")
        p_col = lower.get("p.value") or lower.get("pvalue") or lower.get("p_value")
        if term_col and coef_col:
            return from_coefficient_table(
                tidy,
                name=name,
                term_col=term_col,
                coef_col=coef_col,
                se_col=se_col,
                pvalue_col=p_col,
                diagnostics=diagnostics,
                source="pyfixest-like",
            )

    stats: dict[str, Any] = {}
    for attr, label in [("nobs", "N"), ("r2", "R2"), ("r2_adj", "Adj. R2"), ("rmse", "RMSE")]:
        value = _first_attr(result, [attr], None)
        if value is not None:
            stats[label] = value

    return RegressionModel(
        name=name,
        depvar=str(_first_attr(result, ["depvar", "dependent", "yname"], None) or "") or None,
        params=_series(params, name="coef"),
        std_errors=_series(se, name="se"),
        pvalues=_series(pvalues, name="pvalue"),
        statistics=stats,
        diagnostics=dict(diagnostics or {}),
        metadata={"class": result.__class__.__name__, "module": result.__class__.__module__},
        source="pyfixest-like",
    )


def _from_generic_object(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    stats: dict[str, Any] = {}

    stat_attrs = [
        ("nobs", "N"),
        ("n_obs", "N"),
        ("n_groups", "Groups"),
        ("groups", "Groups"),
        ("n_instruments", "Instruments"),
        ("instrument_count", "Instruments"),
        ("rsquared", "R2"),
        ("r2", "R2"),
        ("aic", "AIC"),
        ("bic", "BIC"),
        ("hansen_p", "Hansen p"),
        ("sargan_p", "Sargan p"),
        ("diff_hansen_p", "Diff-Hansen p"),
        ("ar1_p", "AR(1) p"),
        ("ar2_p", "AR(2) p"),
        ("ar1", "AR(1)"),
        ("ar2", "AR(2)"),
        ("backend", "Backend"),
        ("covariance_type", "Covariance type"),
        ("cov_type", "Covariance type"),
    ]

    for attr, label in stat_attrs:
        value = _first_attr(result, [attr], None)
        if value is not None:
            stats[label] = value

    def _yes_no(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            lowered = cleaned.lower()
            if lowered in {"true", "yes", "y", "1", "enabled", "present"}:
                return "Yes"
            if lowered in {"false", "no", "n", "0", "disabled", "absent", "none"}:
                return "No"
            return "Yes" if cleaned else "No"
        if isinstance(value, Mapping):
            return "Yes" if len(value) > 0 else "No"
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return "Yes" if len(value) > 0 else "No"
        try:
            return "Yes" if bool(value) else "No"
        except Exception:
            return "Yes"

    entity_fe = _first_attr(
        result,
        [
            "entity_effects",
            "has_entity_effects",
            "entity_fe",
            "individual_effects",
            "has_individual_effects",
        ],
        None,
    )
    time_fe = _first_attr(
        result,
        [
            "time_effects",
            "has_time_effects",
            "time_fe",
            "period_effects",
            "has_period_effects",
        ],
        None,
    )
    fixed_effects = _first_attr(
        result,
        [
            "fixed_effects",
            "has_fixed_effects",
            "absorbed_effects",
            "effects",
            "fe",
        ],
        None,
    )
    clustered = _first_attr(
        result,
        [
            "clustered",
            "clustered_se",
            "cluster_entity",
            "cluster_time",
            "clusters",
        ],
        None,
    )

    if _yes_no(entity_fe) is not None:
        stats.setdefault("Entity FE", _yes_no(entity_fe))
    if _yes_no(time_fe) is not None:
        stats.setdefault("Time FE", _yes_no(time_fe))
    if _yes_no(fixed_effects) is not None:
        stats.setdefault("Fixed effects", _yes_no(fixed_effects))
    if _yes_no(clustered) is not None:
        stats.setdefault("Clustered SE", _yes_no(clustered))

    return RegressionModel(
        name=name,
        depvar=str(_first_attr(result, ["depvar", "dependent", "yname"], None) or "") or None,
        params=_series(_first_attr(result, ["params", "coef", "coefs", "coefficients"], None), name="coef"),
        std_errors=_series(_first_attr(result, ["bse", "std_errors", "standard_errors", "se"], None), name="se"),
        pvalues=_series(_first_attr(result, ["pvalues", "p_values", "pvalue"], None), name="pvalue"),
        statistics=stats,
        diagnostics=dict(diagnostics or {}),
        metadata={"class": result.__class__.__name__, "module": result.__class__.__module__},
        source="generic-object",
    )


def normalise_model(
    result: Any,
    *,
    name: str | None = None,
    diagnostics: Mapping[str, Any] | None = None,
    adapter: str = "auto",
) -> RegressionModel:
    """Convert many result types into a canonical RegressionModel."""
    if isinstance(result, RegressionModel):
        if name:
            result.name = normalise_label(name)
        if diagnostics:
            result.diagnostics.update(dict(diagnostics))
        return result

    if isinstance(result, Mapping):
        return _from_mapping(result, name=name, diagnostics=diagnostics)

    adapter = adapter.lower().strip()
    model_name = normalise_label(name or getattr(result, "name", None) or result.__class__.__name__)
    module = result.__class__.__module__.lower()
    class_name = result.__class__.__name__.lower()

    if adapter == "statsmodels" or (adapter == "auto" and "statsmodels" in module):
        return _from_statsmodels(result, name=model_name, diagnostics=diagnostics)
    if adapter == "linearmodels" or (adapter == "auto" and "linearmodels" in module):
        return _from_linearmodels(result, name=model_name, diagnostics=diagnostics)
    if adapter in {"pyfixest", "pyfixest-like"} or (
        adapter == "auto" and ("pyfixest" in module or "fixest" in class_name)
    ):
        return _from_pyfixest_like(result, name=model_name, diagnostics=diagnostics)
    return _from_generic_object(result, name=model_name, diagnostics=diagnostics)

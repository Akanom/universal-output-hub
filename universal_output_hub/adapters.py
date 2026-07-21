"""Model adapters for Universal Output Hub.

The philosophy is deliberately practical: accept outputs from Python model objects,
plain dictionaries, and coefficient tables exported from Stata/R/SPSS/EViews/etc.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
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


AdapterPredicate = Callable[[Any], bool]
AdapterConverter = Callable[[Any, str, Mapping[str, Any] | None], RegressionModel]
_CUSTOM_ADAPTERS: dict[str, tuple[AdapterPredicate, AdapterConverter]] = {}


def register_model_adapter(
    name: str,
    predicate: AdapterPredicate,
    converter: AdapterConverter,
    *,
    replace: bool = False,
) -> None:
    """Register a custom result adapter used by :func:`normalise_model`.

    The converter receives ``(result, model_name, diagnostics)`` and must
    return a :class:`RegressionModel`. Registration is process-local and does
    not import or execute third-party plugins automatically.
    """
    key = str(name).strip().lower()
    if not key or key in {"auto", "generic", "generic-object"}:
        raise ValueError("Adapter name must be non-empty and cannot be a reserved adapter name.")
    if not callable(predicate) or not callable(converter):
        raise TypeError("predicate and converter must be callable.")
    if key in _CUSTOM_ADAPTERS and not replace:
        raise ValueError(f"Adapter '{key}' is already registered. Pass replace=True to replace it.")
    _CUSTOM_ADAPTERS[key] = (predicate, converter)


def unregister_model_adapter(name: str) -> None:
    """Remove a previously registered custom adapter."""
    key = str(name).strip().lower()
    if key not in _CUSTOM_ADAPTERS:
        raise KeyError(f"Adapter '{key}' is not registered.")
    del _CUSTOM_ADAPTERS[key]


def registered_model_adapters() -> tuple[str, ...]:
    """Return registered custom adapter names in matching order."""
    return tuple(_CUSTOM_ADAPTERS)


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


def _first_mapping_value(mapping: Mapping[str, Any], names: Sequence[str], default: Any = None) -> Any:
    """Return the first present, non-None mapping value without truth testing it."""
    for name in names:
        if name in mapping and mapping[name] is not None:
            return mapping[name]
    return default


def _flatten_frame(value: pd.DataFrame, *, name: str) -> pd.Series:
    """Flatten equation/model columns into stable ``column: term`` labels."""
    labels: list[str] = []
    values: list[Any] = []
    for column in value.columns:
        for term in value.index:
            labels.append(f"{column}: {term}")
            values.append(value.loc[term, column])
    return pd.Series(values, index=labels, name=name)


def _series(value: Any, *, name: str) -> pd.Series:
    if value is None:
        return pd.Series(dtype="float64", name=name)
    if isinstance(value, pd.Series):
        out = value.copy()
        out.name = name
        out.index = out.index.map(str)
        return out
    if isinstance(value, pd.DataFrame):
        return _flatten_frame(value, name=name)
    if isinstance(value, Mapping):
        return pd.Series(dict(value), name=name)
    try:
        array = np.asarray(value)
        if array.ndim > 1:
            labels = ["x[" + ",".join(map(str, index)) + "]" for index in np.ndindex(array.shape)]
            return pd.Series(array.ravel(), index=labels, name=name)
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
    params = _first_mapping_value(result, ["params", "params_", "coef", "coef_", "coefs", "coefficients"])
    se = _first_mapping_value(
        result,
        ["std_errors", "standard_errors", "standard_errors_", "bse", "se", "std_err", "stderr"],
    )
    pvalues = _first_mapping_value(result, ["pvalues", "p_values", "pvalue", "p_value", "pval"])

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


def _from_limiteddepkit(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    """Normalize limiteddepkit's shared fitted-result contract.

    The adapter is intentionally duck typed so Universal Output Hub does not
    require limiteddepkit as a runtime dependency. ``all_params`` is preferred
    over ``params`` because multi-equation and ordinal models use it to expose
    thresholds, ancillary parameters, and equation-prefixed coefficients in
    covariance order.
    """
    params = _first_attr(result, ["all_params", "params"], None)
    if params is None and hasattr(result, "params_outcome") and hasattr(result, "params_selection"):
        outcome = _series(result.params_outcome, name="coef")
        selection = _series(result.params_selection, name="coef")
        outcome.index = [f"outcome:{term}" for term in outcome.index]
        selection.index = [f"selection:{term}" for term in selection.index]
        ancillary = pd.Series(
            {
                "log_sigma": _first_attr(result, ["log_sigma"], None),
                "atanh_rho": _first_attr(result, ["atanh_rho"], None),
            },
            dtype="float64",
        )
        params = pd.concat([outcome, selection, ancillary]).rename("coef")

    stats: dict[str, Any] = {}
    for attr, label in [
        ("nobs", "N"),
        ("nobs_total", "N"),
        ("nobs_observed", "Observed N"),
        ("n_entities", "Groups"),
        ("n_clusters", "Clusters"),
        ("n_events", "Events"),
        ("n_choice_sets", "Choice sets"),
        ("n_alts", "Alternatives"),
        ("aic", "AIC"),
        ("bic", "BIC"),
        ("loglike", "Log Likelihood"),
        ("composite_loglike", "Log Likelihood"),
        ("converged", "Converged"),
        ("inference_valid", "Inference valid"),
    ]:
        value = _first_attr(result, [attr], None)
        if value is not None:
            stats.setdefault(label, value)

    categories = _first_attr(result, ["categories"], None)
    if categories is not None:
        try:
            stats["Categories"] = len(categories)
        except TypeError:
            pass

    metadata: dict[str, Any] = {
        "class": result.__class__.__name__,
        "module": result.__class__.__module__,
        "estimator": result.__class__.__name__.removesuffix("Result"),
    }
    for attr in ["backend", "covariance_type", "link", "quantile", "inference_valid"]:
        value = _first_attr(result, [attr], None)
        if value is not None:
            metadata[attr] = value
    if categories is not None:
        try:
            metadata["categories"] = [str(category) for category in categories]
        except TypeError:
            pass

    extracted_diagnostics = dict(diagnostics or {})
    for attr, label in [
        ("score_norm", "Score norm"),
        ("scaled_score_norm", "Scaled score norm"),
        ("scaled_kkt_residual", "Scaled KKT residual"),
        ("information_rank", "Information rank"),
    ]:
        value = _first_attr(result, [attr], None)
        if value is not None:
            extracted_diagnostics.setdefault(label, value)

    return RegressionModel(
        name=name,
        depvar=str(_first_attr(result, ["depvar", "dependent", "yname"], None) or "") or None,
        params=_series(params, name="coef"),
        std_errors=_series(_first_attr(result, ["standard_errors", "bse", "se"], None), name="se"),
        pvalues=_series(_first_attr(result, ["pvalues", "p_values", "pvalue"], None), name="pvalue"),
        statistics=stats,
        diagnostics=extracted_diagnostics,
        metadata=metadata,
        source="limiteddepkit",
    )


def _normalised_columns(table: pd.DataFrame) -> dict[str, Any]:
    return {_compact_key(column): column for column in table.columns}


def _from_summary_table(
    table: pd.DataFrame,
    *,
    name: str,
    source: str,
    diagnostics: Mapping[str, Any] | None = None,
    depvar: str | None = None,
    statistics: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> RegressionModel:
    """Normalize common tidy/summary-table column conventions."""
    columns = _normalised_columns(table)
    coef_col = next(
        (columns[key] for key in ["coef", "coefficient", "estimate", "mean"] if key in columns),
        None,
    )
    if coef_col is None:
        raise ValueError(f"{source} summary table has no coefficient/estimate column.")
    se_col = next(
        (columns[key] for key in ["secoef", "stderr", "standarderror", "stddev", "sd", "se"] if key in columns),
        None,
    )
    p_col = next(
        (columns[key] for key in ["p", "pvalue", "pval", "probt", "prt", "prz"] if key in columns),
        None,
    )
    return RegressionModel(
        name=name,
        depvar=depvar,
        params=_series(table[coef_col], name="coef"),
        std_errors=_series(table[se_col], name="se") if se_col is not None else pd.Series(dtype="float64"),
        pvalues=_series(table[p_col], name="pvalue") if p_col is not None else pd.Series(dtype="float64"),
        statistics=dict(statistics or {}),
        diagnostics=dict(diagnostics or {}),
        metadata=dict(metadata or {}),
        source=source,
    )


def _from_lifelines(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    summary = _first_attr(result, ["summary"], None)
    if not isinstance(summary, pd.DataFrame):
        raise TypeError("lifelines result must expose a pandas summary table.")
    stats: dict[str, Any] = {}
    for attr, label in [
        ("_n_examples", "N"),
        ("AIC_", "AIC"),
        ("AIC_partial_", "AIC"),
        ("log_likelihood_", "Log Likelihood"),
    ]:
        value = _first_attr(result, [attr], None)
        if value is not None:
            stats.setdefault(label, value)
    return _from_summary_table(
        summary,
        name=name,
        source="lifelines",
        diagnostics=diagnostics,
        statistics=stats,
        metadata={"class": result.__class__.__name__, "module": result.__class__.__module__},
    )


def _from_arch(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    stats: dict[str, Any] = {}
    for attr, label in [
        ("nobs", "N"),
        ("aic", "AIC"),
        ("bic", "BIC"),
        ("loglikelihood", "Log Likelihood"),
    ]:
        value = _first_attr(result, [attr], None)
        if value is not None:
            stats[label] = value
    return RegressionModel(
        name=name,
        params=_series(_first_attr(result, ["params"], None), name="coef"),
        std_errors=_series(_first_attr(result, ["std_err", "std_errors"], None), name="se"),
        pvalues=_series(_first_attr(result, ["pvalues"], None), name="pvalue"),
        statistics=stats,
        diagnostics=dict(diagnostics or {}),
        metadata={"class": result.__class__.__name__, "module": result.__class__.__module__},
        source="arch",
    )


def _from_doubleml(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    params = _first_attr(result, ["coef"], None)
    se = _first_attr(result, ["se"], None)
    pvalues = _first_attr(result, ["pval", "pvalues"], None)
    treatment_names = _first_attr(result, ["treatment_names", "d_cols"], None)
    if treatment_names is not None and not isinstance(params, (pd.Series, pd.DataFrame, Mapping)):
        names = [str(item) for item in treatment_names]
        values = np.asarray(params).reshape(-1)
        if len(names) == len(values):
            params = pd.Series(values, index=names)
            se = pd.Series(np.asarray(se).reshape(-1), index=names) if se is not None else None
            pvalues = pd.Series(np.asarray(pvalues).reshape(-1), index=names) if pvalues is not None else None
    stats = {"N": value} if (value := _first_attr(result, ["n_obs", "nobs"], None)) is not None else {}
    return RegressionModel(
        name=name,
        params=_series(params, name="coef"),
        std_errors=_series(se, name="se"),
        pvalues=_series(pvalues, name="pvalue"),
        statistics=stats,
        diagnostics=dict(diagnostics or {}),
        metadata={"class": result.__class__.__name__, "module": result.__class__.__module__},
        source="doubleml",
    )


def _coefficient_names(result: Any, count: int) -> list[str]:
    names = _first_attr(result, ["feature_names_in_", "feature_names", "coef_names"], None)
    if names is not None:
        flattened = [str(item) for item in np.asarray(names).reshape(-1)]
        if len(flattened) == count:
            return flattened
    return [f"x{i}" for i in range(count)]


def _from_sklearn_like(
    result: Any,
    *,
    name: str,
    diagnostics: Mapping[str, Any] | None = None,
    source: str = "sklearn",
) -> RegressionModel:
    coefficients = _first_attr(result, ["coef_", "coef"], None)
    if coefficients is None:
        raise TypeError(
            f"{source} estimator does not expose coefficients. "
            "Export predictions or metrics with add_table(...) instead."
        )
    array = np.asarray(coefficients)
    feature_count = array.shape[-1] if array.ndim else 1
    features = _coefficient_names(result, feature_count)
    classes = _first_attr(result, ["classes_"], None)
    if array.ndim <= 1:
        params = pd.Series(array.reshape(-1), index=features)
    else:
        equation_names = (
            [str(value) for value in classes] if classes is not None and len(classes) == array.shape[0] else None
        )
        equation_names = equation_names or [f"equation_{idx}" for idx in range(array.shape[0])]
        params = _flatten_frame(pd.DataFrame(array, index=equation_names, columns=features).T, name="coef")
    intercept = _first_attr(result, ["intercept_", "intercept"], None)
    if intercept is not None:
        intercept_values = np.asarray(intercept).reshape(-1)
        if len(intercept_values) == 1:
            params = pd.concat([pd.Series({"Intercept": intercept_values[0]}), params])
        elif array.ndim > 1 and len(intercept_values) == array.shape[0]:
            labels = [f"{equation}: Intercept" for equation in equation_names]
            params = pd.concat([pd.Series(intercept_values, index=labels), params])
    metadata = {
        "class": result.__class__.__name__,
        "module": result.__class__.__module__,
        "inference_available": False,
        "warning": "Estimator exposes coefficients but not inferential standard errors or p-values.",
    }
    return RegressionModel(
        name=name,
        params=_series(params, name="coef"),
        statistics={},
        diagnostics=dict(diagnostics or {}),
        metadata=metadata,
        source=source,
    )


def _from_arviz(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    try:
        import arviz as az
    except ImportError as exc:
        raise ImportError("ArviZ is required to normalize Bayesian InferenceData results.") from exc
    summary = az.summary(result, kind="stats")
    if not isinstance(summary, pd.DataFrame) or "mean" not in summary.columns:
        raise ValueError("ArviZ summary did not contain posterior means.")
    credible_columns = [column for column in summary.columns if str(column).startswith("hdi_")]
    metadata: dict[str, Any] = {
        "class": result.__class__.__name__,
        "module": result.__class__.__module__,
        "inference": "posterior",
        "pvalues_available": False,
    }
    if credible_columns:
        metadata["credible_intervals"] = summary[credible_columns].to_dict(orient="index")
    return _from_summary_table(
        summary,
        name=name,
        source="arviz",
        diagnostics=diagnostics,
        metadata=metadata,
    )


def _from_econml(result: Any, *, name: str, diagnostics: Mapping[str, Any] | None = None) -> RegressionModel:
    coefficients = _first_attr(result, ["coef_"], None)
    if coefficients is None:
        raise TypeError(
            "EconML estimator does not expose a finite-dimensional coef_. "
            "Export effect estimates and intervals with add_table(...) instead."
        )
    inference = _first_attr(result, ["coef__inference"], None)
    se = _first_attr(inference, ["stderr", "stderr_"], None) if inference is not None else None
    pvalues = _first_attr(inference, ["pvalue", "pvalues"], None) if inference is not None else None
    params = _series(coefficients, name="coef")
    metadata = {
        "class": result.__class__.__name__,
        "module": result.__class__.__module__,
        "inference_available": inference is not None,
    }
    return RegressionModel(
        name=name,
        params=params,
        std_errors=_series(se, name="se"),
        pvalues=_series(pvalues, name="pvalue"),
        diagnostics=dict(diagnostics or {}),
        metadata=metadata,
        source="econml",
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

    params = _first_attr(result, ["params", "params_", "coef", "coef_", "coefs", "coefficients"], None)
    se = _first_attr(
        result,
        ["bse", "std_errors", "standard_errors", "standard_errors_", "se", "std_err", "stderr"],
        None,
    )
    pvalues = _first_attr(result, ["pvalues", "p_values", "pvalue", "p_value", "pval"], None)
    summary = _first_attr(result, ["summary_frame", "tidy", "summary"], None)
    if params is None and isinstance(summary, pd.DataFrame):
        try:
            return _from_summary_table(
                summary,
                name=name,
                source="generic-summary",
                diagnostics=diagnostics,
                statistics=stats,
                metadata={"class": result.__class__.__name__, "module": result.__class__.__module__},
            )
        except ValueError:
            pass

    return RegressionModel(
        name=name,
        depvar=str(_first_attr(result, ["depvar", "dependent", "yname"], None) or "") or None,
        params=_series(params, name="coef"),
        std_errors=_series(se, name="se"),
        pvalues=_series(pvalues, name="pvalue"),
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

    if adapter in _CUSTOM_ADAPTERS:
        return _CUSTOM_ADAPTERS[adapter][1](result, model_name, diagnostics)
    if adapter == "auto":
        for _, (predicate, converter) in _CUSTOM_ADAPTERS.items():
            try:
                matches = bool(predicate(result))
            except Exception:
                matches = False
            if matches:
                return converter(result, model_name, diagnostics)

    if adapter == "statsmodels" or (adapter == "auto" and "statsmodels" in module):
        return _from_statsmodels(result, name=model_name, diagnostics=diagnostics)
    if adapter == "linearmodels" or (adapter == "auto" and "linearmodels" in module):
        return _from_linearmodels(result, name=model_name, diagnostics=diagnostics)
    if adapter in {"pyfixest", "pyfixest-like"} or (
        adapter == "auto" and ("pyfixest" in module or "fixest" in class_name)
    ):
        return _from_pyfixest_like(result, name=model_name, diagnostics=diagnostics)
    if adapter == "limiteddepkit" or (adapter == "auto" and module.startswith("limiteddepkit")):
        return _from_limiteddepkit(result, name=model_name, diagnostics=diagnostics)
    if adapter == "lifelines" or (adapter == "auto" and module.startswith("lifelines")):
        return _from_lifelines(result, name=model_name, diagnostics=diagnostics)
    if adapter == "arch" or (adapter == "auto" and module.startswith("arch")):
        return _from_arch(result, name=model_name, diagnostics=diagnostics)
    if adapter == "doubleml" or (adapter == "auto" and module.startswith("doubleml")):
        return _from_doubleml(result, name=model_name, diagnostics=diagnostics)
    if adapter in {"arviz", "bayesian"} or (
        adapter == "auto" and (module.startswith("arviz") or class_name == "inferencedata")
    ):
        return _from_arviz(result, name=model_name, diagnostics=diagnostics)
    if adapter == "econml" or (adapter == "auto" and module.startswith("econml")):
        return _from_econml(result, name=model_name, diagnostics=diagnostics)
    if adapter in {"sklearn", "scikit-learn"} or (adapter == "auto" and module.startswith("sklearn")):
        return _from_sklearn_like(result, name=model_name, diagnostics=diagnostics)
    if adapter not in {"auto", "generic", "generic-object"}:
        valid = [
            "auto",
            "arch",
            "arviz",
            "doubleml",
            "econml",
            "generic",
            "lifelines",
            "limiteddepkit",
            "linearmodels",
            "pyfixest",
            "sklearn",
            "statsmodels",
            *_CUSTOM_ADAPTERS,
        ]
        raise ValueError(f"Unknown adapter '{adapter}'. Valid adapters: {', '.join(dict.fromkeys(valid))}.")
    return _from_generic_object(result, name=model_name, diagnostics=diagnostics)

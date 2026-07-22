from __future__ import annotations

import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from universal_output_hub import (
    RegressionModel,
    normalise_model,
    register_model_adapter,
    registered_model_adapters,
    unregister_model_adapter,
)


def test_mapping_accepts_pandas_series_without_truth_value_error() -> None:
    model = normalise_model(
        {
            "name": "Series model",
            "params": pd.Series({"x": 1.0}),
            "std_errors": pd.Series({"x": 0.2}),
            "pvalues": pd.Series({"x": 0.01}),
        }
    )
    assert model.coefficient("x") == 1.0
    assert model.standard_error("x") == 0.2


def test_matrix_parameters_are_flattened_and_aligned_by_equation() -> None:
    result_type = type("MultinomialResults", (), {"__module__": "statsmodels.discrete.discrete_model"})
    result = result_type()
    result.params = pd.DataFrame({"choice_b": [1.0, 2.0], "choice_c": [3.0, 4.0]}, index=["const", "x"])
    result.bse = pd.DataFrame({"choice_b": [0.1, 0.2], "choice_c": [0.3, 0.4]}, index=["const", "x"])
    result.pvalues = pd.DataFrame({"choice_b": [0.01, 0.02], "choice_c": [0.03, 0.04]}, index=["const", "x"])
    result.nobs = 100
    result.model = SimpleNamespace(endog_names="choice")

    model = normalise_model(result)

    assert model.terms == ["choice_b: const", "choice_b: x", "choice_c: const", "choice_c: x"]
    assert model.standard_error("choice_c: x") == 0.4
    assert model.pvalue("choice_b: const") == 0.01


def test_custom_adapter_registry_supports_explicit_and_auto_matching() -> None:
    result = SimpleNamespace(value=2.5)

    def converter(value: object, name: str, diagnostics: object) -> RegressionModel:
        return RegressionModel(name=name, params=pd.Series({"custom": value.value}), source="custom")  # type: ignore[attr-defined]

    register_model_adapter("example", lambda value: hasattr(value, "value"), converter)
    try:
        assert "example" in registered_model_adapters()
        assert normalise_model(result, name="Auto").source == "custom"
        assert normalise_model(result, name="Explicit", adapter="example").coefficient("custom") == 2.5
        with pytest.raises(ValueError, match="already registered"):
            register_model_adapter("example", lambda value: True, converter)
    finally:
        unregister_model_adapter("example")


def test_generic_aliases_cover_underscore_and_short_inference_names() -> None:
    result = SimpleNamespace(
        params_=pd.Series({"x": 0.75}),
        standard_errors_=pd.Series({"x": 0.25}),
        pval=pd.Series({"x": 0.03}),
        n_obs=80,
    )
    model = normalise_model(result)
    assert model.coefficient("x") == 0.75
    assert model.standard_error("x") == 0.25
    assert model.pvalue("x") == 0.03
    assert model.statistics["N"] == 80


def test_lifelines_summary_contract() -> None:
    result_type = type("CoxPHFitter", (), {"__module__": "lifelines.fitters.coxph_fitter"})
    result = result_type()
    result.summary = pd.DataFrame(
        {"coef": [0.4], "se(coef)": [0.1], "p": [0.002]},
        index=pd.Index(["age"], name="covariate"),
    )
    result._n_examples = 120
    result.log_likelihood_ = -50.0
    model = normalise_model(result)
    assert model.source == "lifelines"
    assert model.coefficient("age") == 0.4
    assert model.standard_error("age") == 0.1
    assert model.statistics["N"] == 120


def test_arch_and_doubleml_contracts() -> None:
    arch_type = type("ARCHModelResult", (), {"__module__": "arch.univariate.base"})
    arch_result = arch_type()
    arch_result.params = pd.Series({"omega": 0.2})
    arch_result.std_err = pd.Series({"omega": 0.05})
    arch_result.pvalues = pd.Series({"omega": 0.01})
    arch_result.nobs = 500
    arch_result.loglikelihood = -100.0
    assert normalise_model(arch_result).source == "arch"

    doubleml_type = type("DoubleMLPLR", (), {"__module__": "doubleml.plm.plr"})
    doubleml_result = doubleml_type()
    doubleml_result.coef = np.array([0.6, -0.2])
    doubleml_result.se = np.array([0.1, 0.08])
    doubleml_result.pval = np.array([0.001, 0.02])
    doubleml_result.treatment_names = ["treatment_a", "treatment_b"]
    model = normalise_model(doubleml_result)
    assert model.source == "doubleml"
    assert model.terms == ["treatment_a", "treatment_b"]
    assert model.pvalue("treatment_b") == 0.02


def test_econml_contract_preserves_available_inference() -> None:
    inference = SimpleNamespace(stderr=np.array([0.1, 0.2]), pvalue=lambda: np.array([0.01, 0.04]))
    result_type = type("LinearDML", (), {"__module__": "econml.dml.dml"})
    result = result_type()
    result.coef_ = np.array([0.5, -0.3])
    result.coef__inference = lambda: inference
    model = normalise_model(result)
    assert model.source == "econml"
    assert model.standard_error("x0") == 0.1
    assert model.pvalue("x1") == 0.04


def test_arviz_contract_uses_posterior_sd_without_fabricating_pvalues(monkeypatch: pytest.MonkeyPatch) -> None:
    summary = pd.DataFrame(
        {"mean": [0.5], "sd": [0.1], "hdi_3%": [0.3], "hdi_97%": [0.7]},
        index=["beta[0]"],
    )
    monkeypatch.setitem(sys.modules, "arviz", SimpleNamespace(summary=lambda result, kind: summary))
    result_type = type("InferenceData", (), {"__module__": "arviz.data.inference_data"})
    model = normalise_model(result_type())
    assert model.source == "arviz"
    assert model.coefficient("beta[0]") == 0.5
    assert model.standard_error("beta[0]") == 0.1
    assert model.pvalues.empty
    assert model.metadata["pvalues_available"] is False


def test_sklearn_real_linear_and_multiclass_models() -> None:
    sklearn = pytest.importorskip("sklearn")
    assert sklearn is not None
    from sklearn.linear_model import LinearRegression, LogisticRegression

    X = pd.DataFrame({"x1": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0], "x2": [1.0, 0.0, 1.0, 0.0, 1.0, 0.0]})
    linear = LinearRegression().fit(X, np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]))
    linear_model = normalise_model(linear)
    assert linear_model.source == "sklearn"
    assert linear_model.terms == ["Intercept", "x1", "x2"]
    assert linear_model.std_errors.empty
    assert linear_model.metadata["inference_available"] is False

    y = np.array([0, 1, 2, 0, 1, 2])
    logistic = LogisticRegression(max_iter=500).fit(X, y)
    logistic_model = normalise_model(logistic)
    assert {"0: x1", "1: x1", "2: x1"} <= set(logistic_model.terms)


def test_sklearn_prediction_only_model_has_actionable_error() -> None:
    pytest.importorskip("sklearn")
    from sklearn.cluster import KMeans

    fitted = KMeans(n_clusters=2, random_state=1, n_init=2).fit([[0.0], [1.0], [10.0], [11.0]])
    with pytest.raises(TypeError, match=r"add_table\(\.\.\.\)"):
        normalise_model(fitted)


def test_unknown_explicit_adapter_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown adapter"):
        normalise_model(SimpleNamespace(params=[1.0]), adapter="does-not-exist")


def test_real_statsmodels_ols_contract() -> None:
    sm = pytest.importorskip("statsmodels.api")
    X = pd.DataFrame({"const": 1.0, "x": np.arange(20, dtype=float)})
    result = sm.OLS(1.0 + 2.0 * X["x"], X).fit()
    model = normalise_model(result)
    assert model.source == "statsmodels"
    assert model.terms == ["const", "x"]
    assert model.statistics["N"] == 20
    assert model.coefficient("x") == pytest.approx(2.0)


def test_real_linearmodels_panel_contract() -> None:
    panel = pytest.importorskip("linearmodels.panel")
    index = pd.MultiIndex.from_product([range(6), range(4)], names=["entity", "time"])
    x = np.linspace(-1.0, 1.0, len(index))
    data = pd.DataFrame({"y": 1.5 * x + np.repeat(np.arange(6), 4), "x": x}, index=index)
    result = panel.PanelOLS(data.y, data[["x"]], entity_effects=True).fit()
    model = normalise_model(result)
    assert model.source == "linearmodels"
    assert model.terms == ["x"]
    assert model.statistics["N"] == len(index)
    assert model.statistics["Within R2"] == pytest.approx(result.rsquared_within)


def test_real_pyfixest_contract_when_installed() -> None:
    pf = pytest.importorskip("pyfixest")
    data = pd.DataFrame({"y": np.arange(20, dtype=float), "x": np.arange(20, dtype=float)})
    result = pf.feols("y ~ x", data=data)
    model = normalise_model(result)
    assert model.source == "pyfixest-like"
    assert "x" in model.terms
    assert model.coefficient("x") == pytest.approx(1.0)

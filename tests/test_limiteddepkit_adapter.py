from __future__ import annotations

import pandas as pd

from universal_output_hub import OutputHub, normalise_model


class FakeLimitedDepkitResult:
    __module__ = "limiteddepkit.zero_inflated_poisson"

    def __init__(self) -> None:
        self.params = pd.Series({"raw": 99.0})
        self.all_params = pd.Series({"inflation: const": -1.0, "count: x": 0.5})
        self.standard_errors = pd.Series({"inflation: const": 0.2, "count: x": 0.1})
        self.pvalues = pd.Series({"inflation: const": 0.001, "count: x": 0.02})
        self.nobs = 250
        self.n_clusters = 25
        self.loglike = -120.5
        self.aic = 247.0
        self.bic = 254.0
        self.converged = True
        self.inference_valid = True
        self.backend = "native-mle"
        self.covariance_type = "clustered"
        self.score_norm = 1e-8


class FakeSampleSelectionResult:
    __module__ = "limiteddepkit.sample_selection"

    def __init__(self) -> None:
        self.params_outcome = pd.Series({"const": 1.0, "x": 0.5})
        self.params_selection = pd.Series({"const": -0.5, "z": 0.25})
        self.log_sigma = 0.1
        self.atanh_rho = -0.2
        labels = ["outcome:const", "outcome:x", "selection:const", "selection:z", "log_sigma", "atanh_rho"]
        self.standard_errors = pd.Series(0.1, index=labels)
        self.pvalues = pd.Series(0.01, index=labels)
        self.nobs_total = 300
        self.nobs_observed = 225
        self.loglike = -200.0
        self.converged = True
        self.inference_valid = True


def test_limiteddepkit_auto_adapter_uses_complete_parameter_vector() -> None:
    result = FakeLimitedDepkitResult()
    model = normalise_model(result, name="ZIP")

    assert model.source == "limiteddepkit"
    assert list(model.params.index) == ["inflation: const", "count: x"]
    assert model.statistics["N"] == 250
    assert model.statistics["Clusters"] == 25
    assert model.statistics["Converged"] is True
    assert model.metadata["backend"] == "native-mle"
    assert model.metadata["covariance_type"] == "clustered"
    assert model.diagnostics["Score norm"] == 1e-8


def test_limiteddepkit_adapter_renders_shared_statistics() -> None:
    hub = OutputHub("limiteddepkit compatibility")
    hub.add_model(FakeLimitedDepkitResult(), name="ZIP")

    table = hub.regression_table()

    assert table.loc["inflation: const", "ZIP"] == "-1.000***"
    assert table.loc["count: x", "ZIP"] == "0.500**"
    assert table.loc["N", "ZIP"] == "250"
    assert table.loc["Clusters", "ZIP"] == "25"
    assert table.loc["Converged", "ZIP"] == "Yes"


def test_limiteddepkit_sample_selection_equations_are_combined() -> None:
    model = normalise_model(FakeSampleSelectionResult(), name="Selection")

    assert list(model.params.index) == [
        "outcome:const",
        "outcome:x",
        "selection:const",
        "selection:z",
        "log_sigma",
        "atanh_rho",
    ]
    assert model.statistics["N"] == 300
    assert model.statistics["Observed N"] == 225
    assert model.standard_error("selection:z") == 0.1

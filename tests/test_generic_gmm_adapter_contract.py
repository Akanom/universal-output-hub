from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from universal_output_hub.adapters import normalise_model


@dataclass
class GenericGMMResult:
    name: str
    params: pd.Series
    std_errors: pd.Series
    p_values: pd.Series
    nobs: int
    n_groups: int
    n_instruments: int
    hansen_p: float
    sargan_p: float
    diff_hansen_p: float
    ar1: float
    ar1_p: float
    ar2: float
    ar2_p: float
    backend: str
    covariance_type: str


def test_generic_gmm_like_object_is_normalised_with_diagnostics() -> None:
    result = GenericGMMResult(
        name="Generic GMM",
        params=pd.Series({"L1.y": 0.62, "x": 1.84}),
        std_errors=pd.Series({"L1.y": 0.07, "x": 0.62}),
        p_values=pd.Series({"L1.y": 0.001, "x": 0.003}),
        nobs=1248,
        n_groups=96,
        n_instruments=8,
        hansen_p=0.160,
        sargan_p=0.088,
        diff_hansen_p=0.120,
        ar1=-1.748,
        ar1_p=0.081,
        ar2=-0.167,
        ar2_p=0.868,
        backend="generic-gmm",
        covariance_type="robust-two-step",
    )

    model = normalise_model(result)

    assert model.name == "Generic GMM"
    assert model.coefficient("L1.y") == 0.62
    assert model.standard_error("x") == 0.62
    assert model.pvalue("x") == 0.003

    assert model.stat("N") == 1248
    assert model.stat("Groups") == 96
    assert model.stat("Instruments") == 8
    assert model.stat("Hansen p") == 0.160
    assert model.stat("Sargan p") == 0.088
    assert model.stat("Diff-Hansen p") == 0.120
    assert model.stat("AR(1)") == -1.748
    assert model.stat("AR(1) p") == 0.081
    assert model.stat("AR(2)") == -0.167
    assert model.stat("AR(2) p") == 0.868
    assert model.stat("Backend") == "generic-gmm"
    assert model.stat("Covariance type") == "robust-two-step"


def test_dictionary_gmm_result_keeps_statistics_and_diagnostics() -> None:
    result = {
        "name": "Dictionary GMM",
        "params": {"L1.y": 0.62, "x": 1.84},
        "std_errors": {"L1.y": 0.07, "x": 0.62},
        "pvalues": {"L1.y": 0.001, "x": 0.003},
        "statistics": {
            "N": 1248,
            "Groups": 96,
            "Instruments": 8,
            "Backend": "dictionary",
            "Covariance type": "robust-two-step",
        },
        "diagnostics": {
            "Hansen p": 0.160,
            "Sargan p": 0.088,
            "AR(1) p": 0.081,
            "AR(2) p": 0.868,
        },
    }

    model = normalise_model(result)

    assert model.name == "Dictionary GMM"
    assert model.coefficient("x") == 1.84
    assert model.standard_error("x") == 0.62
    assert model.pvalue("x") == 0.003

    assert model.stat("N") == 1248
    assert model.stat("Groups") == 96
    assert model.stat("Instruments") == 8
    assert model.stat("Backend") == "dictionary"
    assert model.stat("Covariance type") == "robust-two-step"
    assert model.stat("Hansen p") == 0.160
    assert model.stat("Sargan p") == 0.088
    assert model.stat("AR(1) p") == 0.081
    assert model.stat("AR(2) p") == 0.868

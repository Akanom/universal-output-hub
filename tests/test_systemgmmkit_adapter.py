from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from universal_output_hub import OutputHub


@dataclass
class FakeSystemGMMResult:
    name: str
    params: pd.Series
    std_errors: pd.Series
    p_values: pd.Series
    nobs: int
    n_groups: int
    n_instruments: int
    backend: str
    covariance_type: str
    hansen_p: float
    ar1: float
    ar1_p: float
    ar2: float
    ar2_p: float


def _as_text(output: object) -> str:
    if isinstance(output, str):
        return output
    if hasattr(output, "to_string"):
        return output.to_string()
    return str(output)


def test_systemgmmkit_like_result_is_exported_with_gmm_diagnostics() -> None:
    result = FakeSystemGMMResult(
        name="Native System GMM",
        params=pd.Series({"L1.y": 0.617740, "x": 1.841295, "w": -0.402523}),
        std_errors=pd.Series({"L1.y": 0.065489, "x": 0.619813, "w": 0.038887}),
        p_values=pd.Series({"L1.y": 0.0000, "x": 0.0030, "w": 0.0000}),
        nobs=1248,
        n_groups=96,
        n_instruments=8,
        backend="native",
        covariance_type="robust-clustered-two-step-windmeijer",
        hansen_p=0.15998,
        ar1=-1.7479,
        ar1_p=0.0805,
        ar2=-0.1667,
        ar2_p=0.8676,
    )

    hub = OutputHub("systemgmmkit compatibility")
    hub.add_model(result)

    output = hub.regression_table()
    output_text = _as_text(output)

    assert "Native System GMM" in output_text
    assert "L1.y" in output_text
    assert "x" in output_text
    assert "w" in output_text
    assert "0.618" in output_text
    assert "1.841" in output_text
    assert "-0.403" in output_text
    assert "1248" in output_text

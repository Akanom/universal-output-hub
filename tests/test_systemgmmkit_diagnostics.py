from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from universal_output_hub import OutputHub


@dataclass
class FakeSystemGMMDiagnosticResult:
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
    sargan_p: float
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


def test_systemgmmkit_gmm_diagnostics_are_exported() -> None:
    result = FakeSystemGMMDiagnosticResult(
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
        sargan_p=0.08792,
        ar1=-1.7479,
        ar1_p=0.0805,
        ar2=-0.1667,
        ar2_p=0.8676,
    )

    hub = OutputHub("systemgmmkit diagnostics")
    hub.add_model(result)

    output_text = _as_text(hub.regression_table())

    assert "Native System GMM" in output_text
    assert "1248" in output_text
    assert "96" in output_text
    assert "8" in output_text
    assert "0.160" in output_text or "0.15998" in output_text
    assert "0.088" in output_text or "0.08792" in output_text
    assert "0.081" in output_text or "0.0805" in output_text
    assert "0.868" in output_text or "0.8676" in output_text
    assert "robust-clustered-two-step-windmeijer" in output_text

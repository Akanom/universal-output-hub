from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from universal_output_hub import OutputHub


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
    ar1_p: float
    ar2_p: float
    backend: str
    covariance_type: str


result = GenericGMMResult(
    name="Generic Dynamic Panel GMM",
    params=pd.Series({"L1.y": 0.618, "x": 1.841, "w": -0.403}),
    std_errors=pd.Series({"L1.y": 0.065, "x": 0.620, "w": 0.039}),
    p_values=pd.Series({"L1.y": 0.000, "x": 0.003, "w": 0.000}),
    nobs=1248,
    n_groups=96,
    n_instruments=8,
    hansen_p=0.160,
    sargan_p=0.088,
    ar1_p=0.081,
    ar2_p=0.868,
    backend="generic-gmm",
    covariance_type="robust-two-step",
)

hub = OutputHub("Generic GMM output example")
hub.add_model(result)

print(hub.regression_table())

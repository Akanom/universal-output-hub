from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from universal_output_hub import outreg


@dataclass
class ExampleResult:
    name: str
    params: pd.Series
    std_errors: pd.Series
    p_values: pd.Series
    nobs: int
    r2: float


model_1 = ExampleResult(
    name="OLS",
    params=pd.Series({"x": 1.500, "w": -0.400}),
    std_errors=pd.Series({"x": 0.200, "w": 0.100}),
    p_values=pd.Series({"x": 0.010, "w": 0.040}),
    nobs=100,
    r2=0.250,
)

model_2 = ExampleResult(
    name="Fixed Effects",
    params=pd.Series({"x": 1.800, "w": -0.350}),
    std_errors=pd.Series({"x": 0.250, "w": 0.120}),
    p_values=pd.Series({"x": 0.005, "w": 0.060}),
    nobs=100,
    r2=0.310,
)

outreg(
    [model_1, model_2],
    using="outputs/outreg_example.md",
    model_names=["OLS", "FE"],
    stats=["N", "R2"],
    notes=["Standard errors in parentheses."],
    replace=True,
)

print("Wrote outputs/outreg_example.md")



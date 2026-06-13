from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from universal_output_hub import OutputHub
from universal_output_hub.adapters import normalise_model


@dataclass
class FakeFixedEffectsResult:
    name: str
    params: pd.Series
    std_errors: pd.Series
    p_values: pd.Series
    nobs: int
    r2: float
    entity_effects: bool
    time_effects: bool
    fixed_effects: list[str]
    clustered: bool
    covariance_type: str


def _result() -> FakeFixedEffectsResult:
    return FakeFixedEffectsResult(
        name="Two-way FE",
        params=pd.Series({"x": 1.5, "w": -0.4}),
        std_errors=pd.Series({"x": 0.2, "w": 0.1}),
        p_values=pd.Series({"x": 0.01, "w": 0.04}),
        nobs=100,
        r2=0.25,
        entity_effects=True,
        time_effects=True,
        fixed_effects=["entity", "time"],
        clustered=True,
        covariance_type="clustered",
    )


def test_fixed_effects_metadata_is_detected_from_generic_object() -> None:
    model = normalise_model(_result())

    assert model.stat("Entity FE") == "Yes"
    assert model.stat("Time FE") == "Yes"
    assert model.stat("Fixed effects") == "Yes"
    assert model.stat("Clustered SE") == "Yes"
    assert model.stat("Covariance type") == "clustered"


def test_fixed_effects_rows_are_shown_in_regression_table() -> None:
    hub = OutputHub("Fixed effects report")
    hub.add_model(_result())

    table_text = hub.regression_table().to_string()

    assert "Entity FE" in table_text
    assert "Time FE" in table_text
    assert "Fixed effects" in table_text
    assert "Clustered SE" in table_text
    assert "Covariance type" in table_text
    assert "Yes" in table_text
    assert "clustered" in table_text


def test_economics_template_orders_common_econometric_diagnostics() -> None:
    hub = OutputHub("Economics table")
    hub.add_model(_result())

    table_text = hub.regression_table(template="economics").to_string()

    assert "N" in table_text
    assert "R2" in table_text
    assert "Entity FE" in table_text
    assert "Time FE" in table_text
    assert "Clustered SE" in table_text
    assert "Covariance type" in table_text


def test_unknown_table_template_raises_value_error() -> None:
    hub = OutputHub("Bad template")
    hub.add_model(_result())

    import pytest

    with pytest.raises(ValueError, match="Unknown table template"):
        hub.regression_table(template="not-a-template")

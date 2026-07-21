from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pytest

from universal_output_hub import outreg


@dataclass
class FakeRegressionResult:
    name: str
    params: pd.Series
    std_errors: pd.Series
    p_values: pd.Series
    nobs: int
    r2: float


def _model(name: str, coef: float) -> FakeRegressionResult:
    return FakeRegressionResult(
        name=name,
        params=pd.Series({"x": coef, "w": -0.4}),
        std_errors=pd.Series({"x": 0.2, "w": 0.1}),
        p_values=pd.Series({"x": 0.01, "w": 0.04}),
        nobs=100,
        r2=0.25,
    )


def test_outreg_exports_single_model_markdown(tmp_path: Path) -> None:
    output = tmp_path / "results.md"

    returned = outreg(_model("OLS", 1.5), using=output, replace=True)

    assert returned == output
    assert output.exists()

    text = output.read_text(encoding="utf-8")
    assert "OLS" in text
    assert "x" in text
    assert "1.500" in text
    assert "N" in text
    assert "100" in text


def test_outreg_exports_multiple_models_csv_with_names(tmp_path: Path) -> None:
    output = tmp_path / "results.csv"

    outreg(
        [_model("Model A", 1.5), _model("Model B", 2.0)],
        using=output,
        model_names=["FE", "IV"],
        stats=["N", "R2"],
        replace=True,
    )

    text = output.read_text(encoding="utf-8")
    assert "FE" in text
    assert "IV" in text
    assert "1.500" in text
    assert "2.000" in text
    assert "R2" in text


def test_outreg_prevents_overwrite_without_replace(tmp_path: Path) -> None:
    output = tmp_path / "results.txt"
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        outreg(_model("OLS", 1.5), using=output)


def test_outreg_validates_model_names_length(tmp_path: Path) -> None:
    output = tmp_path / "results.txt"

    with pytest.raises(ValueError, match="model_names"):
        outreg(
            [_model("A", 1.0), _model("B", 2.0)],
            using=output,
            model_names=["Only one name"],
            replace=True,
        )


def test_outreg_rejects_append_for_now(tmp_path: Path) -> None:
    output = tmp_path / "results.txt"

    with pytest.raises(NotImplementedError, match="append"):
        outreg(_model("OLS", 1.5), using=output, append=True)

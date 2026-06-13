from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from universal_output_hub import outreg


@dataclass
class FakeTemplateResult:
    name: str
    params: pd.Series
    std_errors: pd.Series
    p_values: pd.Series
    nobs: int
    r2: float
    entity_effects: bool
    time_effects: bool
    clustered: bool
    covariance_type: str


def test_outreg_accepts_journal_template(tmp_path: Path) -> None:
    result = FakeTemplateResult(
        name="FE",
        params=pd.Series({"x": 1.5}),
        std_errors=pd.Series({"x": 0.2}),
        p_values=pd.Series({"x": 0.01}),
        nobs=100,
        r2=0.25,
        entity_effects=True,
        time_effects=True,
        clustered=True,
        covariance_type="clustered",
    )

    output = tmp_path / "journal_table.md"

    outreg(
        result,
        using=output,
        template="journal",
        replace=True,
    )

    text = output.read_text(encoding="utf-8")

    assert "x" in text
    assert "1.500" in text
    assert "Entity FE" in text
    assert "Time FE" in text
    assert "Clustered SE" in text
    assert "Yes" in text

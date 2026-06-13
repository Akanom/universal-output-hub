from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from universal_output_hub.normalizer import normalize_result
from universal_output_hub.schema import NormalizedResult


DEFAULT_STAR_LEVELS: tuple[tuple[float, str], ...] = (
    (0.01, "***"),
    (0.05, "**"),
    (0.10, "*"),
)


def _normalize_star_levels(
    star_levels: (
        dict[Any, Any]
        | list[tuple[Any, Any]]
        | tuple[tuple[Any, Any], ...]
        | None
    ),
) -> list[tuple[float, str]]:
    if star_levels is None:
        return list(DEFAULT_STAR_LEVELS)

    items = star_levels.items() if isinstance(star_levels, dict) else star_levels

    normalized: list[tuple[float, str]] = []
    for left, right in items:
        try:
            threshold = float(left)
            star = str(right)
        except (TypeError, ValueError):
            star = str(left)
            threshold = float(right)

        normalized.append((threshold, star))

    return sorted(normalized, key=lambda item: item[0])


def _stars(
    p_value: float | None,
    *,
    show_stars: bool,
    star_levels: (
        dict[Any, Any]
        | list[tuple[Any, Any]]
        | tuple[tuple[Any, Any], ...]
        | None
    ),
) -> str:
    if not show_stars or p_value is None:
        return ""

    try:
        p = float(p_value)
    except (TypeError, ValueError):
        return ""

    for threshold, star in _normalize_star_levels(star_levels):
        if p < threshold:
            return star

    return ""


class OutputTable:
    """Build publication-oriented tables from normalized results."""

    def __init__(
        self,
        results: list[NormalizedResult],
        *,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
        notes: list[str] | None = None,
        show_stars: bool = True,
        star_levels: dict[Any, Any] | list[tuple[Any, Any]] | None = None,
        se_in_parentheses: bool = True,
        variable_labels: dict[str, str] | None = None,
    ) -> None:
        self.results = results
        self.title = title
        self.metadata = metadata or {}
        self.notes = notes or []
        self.show_stars = show_stars
        self.star_levels = star_levels
        self.se_in_parentheses = se_in_parentheses
        self.variable_labels = variable_labels or {}

    @classmethod
    def from_results(
        cls,
        results: list[Any],
        *,
        model_names: list[str] | None = None,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
        notes: list[str] | None = None,
        show_stars: bool = True,
        star_levels: dict[Any, Any] | list[tuple[Any, Any]] | None = None,
        se_in_parentheses: bool = True,
        variable_labels: dict[str, str] | None = None,
    ) -> OutputTable:
        normalized: list[NormalizedResult] = []

        for i, result in enumerate(results):
            name = model_names[i] if model_names and i < len(model_names) else None
            normalized.append(normalize_result(result, name=name))

        return cls(
            normalized,
            title=title,
            metadata=metadata,
            notes=notes,
            show_stars=show_stars,
            star_levels=star_levels,
            se_in_parentheses=se_in_parentheses,
            variable_labels=variable_labels,
        )

    def _label(self, variable: str) -> str:
        return self.variable_labels.get(variable, variable)

    def coefficient_frame(self) -> pd.DataFrame:
        all_vars: list[str] = []

        for result in self.results:
            for coef in result.coefficients:
                if coef.name not in all_vars:
                    all_vars.append(coef.name)

        rows: list[dict[str, str]] = []

        for var in all_vars:
            coef_row: dict[str, str] = {"variable": self._label(var)}
            se_row: dict[str, str] = {"variable": ""}

            for result in self.results:
                match = next((c for c in result.coefficients if c.name == var), None)

                if match is None or match.estimate is None:
                    coef_row[result.name] = ""
                    se_row[result.name] = ""
                    continue

                star = _stars(
                    match.p_value,
                    show_stars=self.show_stars,
                    star_levels=self.star_levels,
                )
                coef_row[result.name] = f"{match.estimate:.4f}{star}"

                if match.std_error is None:
                    se_row[result.name] = ""
                elif self.se_in_parentheses:
                    se_row[result.name] = f"({match.std_error:.4f})"
                else:
                    se_row[result.name] = f"{match.std_error:.4f}"

            rows.append(coef_row)
            rows.append(se_row)

        return pd.DataFrame(rows)

    def diagnostics_frame(self) -> pd.DataFrame:
        ordered = [
            "N",
            "nobs",
            "n_groups",
            "Instruments",
            "n_instruments",
            "Hansen p",
            "hansen_p",
            "Sargan p",
            "sargan_p",
            "Diff-Hansen p",
            "diff_hansen_p",
            "AR(1)",
            "ar1",
            "AR(1) p",
            "ar1_p",
            "AR(2)",
            "ar2",
            "AR(2) p",
            "ar2_p",
            "j_stat",
            "Entity FE",
            "Time FE",
        ]

        seen: set[str] = set()
        keys: list[str] = []

        for key in ordered:
            for result in self.results:
                if key in result.diagnostics and key not in seen:
                    keys.append(key)
                    seen.add(key)

        for result in self.results:
            for key in result.diagnostics:
                if key not in seen:
                    keys.append(key)
                    seen.add(key)

        rows: list[dict[str, object]] = []

        for key in keys:
            row: dict[str, object] = {"diagnostic": key}
            has_value = False

            for result in self.results:
                value = result.diagnostics.get(key, None)

                if value is not None:
                    has_value = True
                    row[result.name] = value
                else:
                    row[result.name] = ""

            if has_value:
                rows.append(row)

        for row_name, attr in [
            ("estimator", "estimator"),
            ("backend", "backend"),
            ("covariance_type", "covariance_type"),
        ]:
            row = {"diagnostic": row_name}
            has_value = False

            for result in self.results:
                value = getattr(result, attr, None)
                if value is not None:
                    has_value = True
                    row[result.name] = value
                else:
                    row[result.name] = ""

            if has_value:
                rows.append(row)

        return pd.DataFrame(rows)

    def metadata_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            [{"field": key, "value": value} for key, value in self.metadata.items()]
        )

    def to_markdown(self) -> str:
        coef = self.coefficient_frame()
        diagnostics = self.diagnostics_frame()
        metadata = self.metadata_frame()

        parts: list[str] = []

        if self.title:
            parts.extend([f"# {self.title}", ""])

        if not metadata.empty:
            parts.extend(["## Metadata", "", metadata.to_markdown(index=False), ""])

        parts.extend(["## Coefficients", "", coef.to_markdown(index=False)])

        if not diagnostics.empty:
            parts.extend(["", "## Diagnostics", "", diagnostics.to_markdown(index=False)])

        if self.notes:
            parts.extend(["", "## Notes", ""])
            parts.extend([f"- {note}" for note in self.notes])

        return "\n".join(parts) + "\n"

    def to_csv(self, path: str | Path) -> None:
        coef = self.coefficient_frame()
        diagnostics = self.diagnostics_frame()

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if diagnostics.empty:
            coef.to_csv(output_path, index=False)
            return

        combined = pd.concat(
            [
                coef,
                pd.DataFrame([{}]),
                diagnostics.rename(columns={"diagnostic": "variable"}),
            ],
            ignore_index=True,
        )
        combined.to_csv(output_path, index=False)

    def to_csv_string(self) -> str:
        return self.coefficient_frame().to_csv(index=False)

    def to_latex(self) -> str:
        return self.coefficient_frame().to_latex(index=False, escape=True)

    def to_html(self) -> str:
        parts: list[str] = []

        if self.title:
            parts.append(f"<h1>{self.title}</h1>")

        if self.metadata:
            parts.append("<h2>Metadata</h2>")
            parts.append(self.metadata_frame().to_html(index=False))

        parts.append("<h2>Coefficients</h2>")
        parts.append(self.coefficient_frame().to_html(index=False))

        diagnostics = self.diagnostics_frame()
        if not diagnostics.empty:
            parts.append("<h2>Diagnostics</h2>")
            parts.append(diagnostics.to_html(index=False))

        if self.notes:
            parts.append("<h2>Notes</h2>")
            parts.append("<ul>")
            parts.extend(f"<li>{note}</li>" for note in self.notes)
            parts.append("</ul>")

        return "\n".join(parts) + "\n"

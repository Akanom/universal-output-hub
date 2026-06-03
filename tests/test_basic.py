from pathlib import Path

import pandas as pd

from universal_output_hub import OutputHub


def test_dictionary_model_and_exports(tmp_path: Path) -> None:
    hub = OutputHub("Test")
    hub.add_model(
        {
            "name": "M1",
            "params": {"x": 1.0, "z": -2.0},
            "std_errors": {"x": 0.1, "z": 0.2},
            "pvalues": {"x": 0.01, "z": 0.20},
            "statistics": {"N": 100},
            "diagnostics": {"Hansen p": 0.50},
        }
    )
    table = hub.regression_table()
    assert "M1" in table.columns
    assert "x" in table.index
    assert table.loc["x", "M1"] == "1.000***"
    assert table.loc["z", "M1"] == "-2.000"
    assert "N" in table.index
    assert "Significance" in table.index
    bundle = hub.export_bundle(tmp_path)
    assert bundle["manifest"].exists()
    assert bundle["html_report"].exists()


def test_external_coefficient_table() -> None:
    hub = OutputHub("External")
    df = pd.DataFrame({"term": ["x"], "coef": [1.2], "se": [0.3], "pvalue": [0.04]})
    hub.add_model_table(df, name="External Model")
    out = hub.regression_table()
    assert out.loc["x", "External Model"] == "1.200**"


def test_custom_star_levels_and_no_stars() -> None:
    hub = OutputHub("Stars")
    hub.add_model({"name": "M", "params": {"x": 1.0}, "std_errors": {"x": 0.1}, "pvalues": {"x": 0.04}})

    custom = hub.regression_table(star_levels={"***": 0.001, "**": 0.01, "*": 0.05})
    assert custom.loc["x", "M"] == "1.000*"

    plain = hub.regression_table(stars=False)
    assert plain.loc["x", "M"] == "1.000"
    assert "Significance" not in plain.index


def test_native_docx_pdf_report_exports(tmp_path: Path) -> None:
    hub = OutputHub("Model Output Report", metadata={"project": "test"})
    hub.add_model(
        {
            "name": "M1",
            "params": {"x": 1.0},
            "std_errors": {"x": 0.1},
            "pvalues": {"x": 0.01},
            "statistics": {"N": 100},
        }
    )
    hub.add_table("Summary table", pd.DataFrame({"metric": ["N"], "value": [100]}))
    hub.add_note("Generated during automated testing.")

    docx_path = hub.export_report(tmp_path / "output_report.docx")
    pdf_path = hub.export_report(tmp_path / "output_report.pdf")

    assert docx_path.exists()
    assert pdf_path.exists()

    bundle = hub.export_bundle(tmp_path / "bundle")

    assert (tmp_path / "bundle" / "reports" / "output_report.docx").exists()
    assert (tmp_path / "bundle" / "reports" / "output_report.pdf").exists()
    assert "reports" in bundle


def test_comprehensive_output_exports(tmp_path: Path) -> None:
    hub = OutputHub("Model Output Report", metadata={"project": "test"})
    hub.add_model(
        {
            "name": "M1",
            "params": {"x": 1.0},
            "std_errors": {"x": 0.1},
            "pvalues": {"x": 0.01},
            "statistics": {"N": 100},
            "diagnostics": {"Hansen p": 0.50},
        }
    )
    hub.add_table("Summary table", pd.DataFrame({"metric": ["N"], "value": [100]}))
    hub.add_note("Generated during automated testing.")
    assert hub.export_report(tmp_path / "output_report.docx").exists()
    assert hub.export_report(tmp_path / "output_report.pdf").exists()
    assert hub.export_report(tmp_path / "output_report.tex").exists()
    assert hub.export_excel_workbook(tmp_path / "output_workbook.xlsx").exists()
    assert hub.export_regression_table(tmp_path / "regression_table.pdf").exists()
    assert hub.export_regression_table(tmp_path / "regression_table.tex").exists()
    assert hub.export_regression_table(tmp_path / "regression_table.xlsx").exists()
    table_paths = hub.export_tables(tmp_path / "tables", formats=("xlsx", "tex", "pdf"))
    assert len(table_paths) == 3
    assert all(path.exists() for path in table_paths)
    bundle = hub.export_bundle(tmp_path / "bundle")
    assert (tmp_path / "bundle" / "reports" / "output_report.docx").exists()
    assert (tmp_path / "bundle" / "reports" / "output_report.pdf").exists()
    assert (tmp_path / "bundle" / "reports" / "output_report.tex").exists()
    assert (tmp_path / "bundle" / "workbooks" / "output_workbook.xlsx").exists()
    assert (tmp_path / "bundle" / "regression_tables" / "regression_table.pdf").exists()
    assert "reports" in bundle
    assert "workbook" in bundle

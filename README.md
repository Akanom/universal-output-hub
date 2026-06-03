# Universal Output Hub

`universal-output-hub` is a lightweight Python reporting layer for collecting model results, statistical tables, diagnostics, notes, and graphs into one reproducible output bundle.

It is designed as a broader Python alternative to Stata-style reporting tools such as `outreg2`, `esttab`, and `asdoc`, but with a wider scope: not only regression tables, but also ordinary tables, figures, metadata, diagnostics, and complete report exports.

## Purpose

Statistical work often produces output from many places:

- Python models from `statsmodels`, `linearmodels`, `pyfixest`, or custom estimators;
- external statistical software such as Stata, R, SPSS, EViews, SAS, Excel, or CSV exports;
- regression tables, descriptive statistics, robustness checks, diagnostics, and plots;
- final outputs needed in Excel, LaTeX, HTML, Word, PDF, Markdown, CSV, or JSON.

The goal is simple:

> Run your models anywhere. Collect your outputs once. Export them everywhere.

## Core capabilities

| Capability | Status |
|---|---:|
| Add Python model results | Yes |
| Add custom model dictionaries | Yes |
| Add coefficient tables from external software | Yes |
| Add ordinary pandas tables | Yes |
| Add CSV, Excel, Stata `.dta`, TSV, and Parquet tables | Yes |
| Add graph/image files | Yes |
| Save matplotlib-style figures | Yes |
| Build publication-style regression tables | Yes |
| Add configurable significance stars | Yes |
| Store diagnostics and model statistics | Yes |
| Export CSV | Yes |
| Export Excel `.xlsx` | Yes |
| Export HTML | Yes |
| Export Markdown | Yes |
| Export LaTeX `.tex` tables and reports | Yes |
| Export JSON | Yes |
| Export Word `.docx` reports | Yes |
| Export PDF tables and reports | Yes |
| Export combined Excel workbook | Yes |
| Create reproducible output bundles | Yes |

## Installation

Install from GitHub:

```bash
python -m pip install git+https://github.com/Akanom/universal-output-hub.git
```

Development installation:

```bash
python -m pip install -e ".[dev,examples]"
pytest -q
```

Windows PowerShell:

```powershell
cd "C:\Users\omoko\OneDrive\Python packages\universal-output-hub"

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,examples]"
pytest -q
```

## Basic example

```python
from universal_output_hub import OutputHub

hub = OutputHub(
    "Model Output Report",
    metadata={
        "project": "Panel-data model comparison",
        "software": "Python / Stata / R compatible",
    },
)

hub.add_model(
    {
        "name": "System GMM",
        "depvar": "growth_rate",
        "params": {
            "L.growth_rate": 0.31,
            "lPA": 0.08,
            "s_techshare": 0.16,
            "s_tech_frag_polity": -0.022,
        },
        "std_errors": {
            "L.growth_rate": 0.12,
            "lPA": 0.03,
            "s_techshare": 0.07,
            "s_tech_frag_polity": 0.012,
        },
        "pvalues": {
            "L.growth_rate": 0.011,
            "lPA": 0.007,
            "s_techshare": 0.041,
            "s_tech_frag_polity": 0.078,
        },
        "statistics": {"N": 946},
        "diagnostics": {
            "AR(1) p": 0.085,
            "AR(2) p": 0.316,
            "Hansen p": 0.190,
            "Sargan p": 0.098,
            "Instruments": 42,
        },
    }
)

hub.add_note("Standard errors are reported in parentheses.")
hub.export_bundle("outputs/model_output")
```

## Output bundle structure

```text
outputs/model_output/
├── index.html
├── manifest.json
├── regression_tables/
│   ├── regression_table.csv
│   ├── regression_table.xlsx
│   ├── regression_table.html
│   ├── regression_table.md
│   ├── regression_table.tex
│   ├── regression_table.pdf
│   └── regression_table.json
├── tables/
├── figures/
├── workbooks/
│   └── output_workbook.xlsx
└── reports/
    ├── output_report.docx
    ├── output_report.pdf
    └── output_report.tex
```

The default output filenames are generic: `output_report.docx`, `output_report.pdf`, `output_report.tex`, and `output_workbook.xlsx`.

The package does not assume that the project is a thesis, dissertation, paper, business report, or internal analysis.

## Regression tables

```python
hub.export_regression_table("outputs/regression_table.xlsx")
hub.export_regression_table("outputs/regression_table.tex")
hub.export_regression_table("outputs/regression_table.pdf")
hub.export_regression_table("outputs/regression_table.html")
hub.export_regression_table("outputs/regression_table.md")
hub.export_regression_table("outputs/regression_table.csv")
hub.export_regression_table("outputs/regression_table.json")
```

Stars are enabled by default:

```text
*** p≤0.01
**  p≤0.05
*   p≤0.10
```

Disable stars:

```python
hub.export_regression_table("outputs/regression_table.tex", stars=False)
```

Use custom thresholds:

```python
hub.export_regression_table(
    "outputs/regression_table.tex",
    star_levels={"***": 0.001, "**": 0.01, "*": 0.05},
)
```

## External model outputs

Export coefficient tables from Stata, R, SPSS, EViews, SAS, Excel, or another tool using:

| term | coef | se | pvalue |
|---|---:|---:|---:|
| lPA | 0.080 | 0.022 | 0.001 |
| s_techshare | 0.161 | 0.071 | 0.024 |

Then import:

```python
hub.add_model_file(
    "stata_fe_results.csv",
    name="Stata FE",
    term_col="term",
    coef_col="coef",
    se_col="se",
    pvalue_col="pvalue",
    statistics={"N": 885, "Within R2": 0.21},
    diagnostics={"Clustered SE": "country"},
    source="Stata export",
)
```

Supported model/table file formats:

```text
.csv
.tsv
.txt
.xlsx
.xls
.dta
.parquet
.pq
```

## Python models

```python
import statsmodels.api as sm
from universal_output_hub import OutputHub

hub = OutputHub("Python Model Output")

fit = sm.OLS(y, X).fit()
hub.add_model(fit, name="OLS", adapter="statsmodels")

hub.export_bundle("outputs/python_models")
```

## Ordinary tables

```python
hub.add_table("Descriptive statistics", df.describe())
hub.add_table("Correlation matrix", df.corr())
hub.add_table("Robustness summary", robustness_df)

hub.export_tables(
    "outputs/tables",
    formats=("csv", "xlsx", "html", "md", "tex", "pdf", "json"),
)
```

## Figures and graphs

Add an existing graph file:

```python
hub.add_figure(
    "Marginal effects plot",
    path="figures/marginal_effects.png",
    caption="Estimated marginal effects across institutional quality.",
)
```

Save a matplotlib figure directly:

```python
hub.add_figure(
    "Model comparison",
    fig=fig,
    output_dir="outputs/figures",
    filename="model_comparison.png",
)
```

## Complete reports

```python
hub.export_report("outputs/output_report.docx")
hub.export_report("outputs/output_report.pdf")
hub.export_report("outputs/output_report.tex")
hub.export_excel_workbook("outputs/output_workbook.xlsx")
```

With a bundle:

```python
hub.export_bundle(
    "outputs/model_output",
    report_filename="output_report",
    workbook_filename="output_workbook",
)
```

Use custom generic names:

```python
hub.export_bundle(
    "outputs/project_run_001",
    report_filename="model_output_report",
    workbook_filename="model_output_workbook",
)
```

## Recommended workflow

```python
from universal_output_hub import OutputHub

hub = OutputHub("Model Output Report")

hub.add_model(model_1, name="OLS")
hub.add_model(model_2, name="Fixed Effects")
hub.add_model(model_3, name="System GMM")

hub.add_table("Descriptive statistics", descriptives)
hub.add_table("Robustness checks", robustness)

hub.add_figure("Coefficient plot", path="figures/coefplot.png")

hub.export_bundle("outputs/run_001")
```

## Design philosophy

1. Model-agnostic.
2. Research-friendly.
3. Format-flexible.
4. Reproducible.
5. Simple API.

## Project status

Current release: `0.2.0`

This is an early-stage package. The public API is usable, but some internals may still change as the package matures.

## License

MIT License.

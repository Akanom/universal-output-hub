# Universal Output Hub

`universal-output-hub` is a lightweight Python reporting layer for collecting model results, regression tables, statistical tables, diagnostics, notes, and graphs into one reproducible output bundle.

It is designed as a broader Python alternative to Stata-style reporting tools such as `outreg2`, `esttab`, and `asdoc`, but with a wider scope: not only regression tables, but also ordinary tables, figures, metadata, diagnostics, table notes, and complete report exports.

The core idea is simple:

> Run your models anywhere. Collect your outputs once. Export them everywhere.

---

## Purpose

Statistical and applied research workflows often produce outputs from many sources:

* Python models from `statsmodels`, `linearmodels`, `pyfixest`, or custom estimators;
* external statistical software such as Stata, R, MATLAB, SPSS, EViews, SAS, Excel, or CSV exports;
* regression tables, descriptive statistics, robustness checks, diagnostics, and plots;
* final outputs needed in Excel, LaTeX, HTML, Word, PDF, Markdown, CSV, or JSON.

`universal-output-hub` provides one consistent interface for collecting those outputs and exporting them into publication-ready and review-friendly formats.

---

## Core capabilities

| Capability                                            | Status |
| ----------------------------------------------------- | -----: |
| Add Python model results                              |    Yes |
| Add custom model dictionaries                         |    Yes |
| Add coefficient tables from external software         |    Yes |
| Add ordinary pandas tables                            |    Yes |
| Add CSV, Excel, Stata `.dta`, TSV, and Parquet tables |    Yes |
| Add graph/image files                                 |    Yes |
| Save matplotlib-style figures                         |    Yes |
| Build publication-style regression tables             |    Yes |
| Put models side-by-side in columns                    |    Yes |
| Show coefficient estimates                            |    Yes |
| Show standard errors below coefficients               |    Yes |
| Add configurable significance stars                   |    Yes |
| Add table notes below model tables                    |    Yes |
| Store diagnostics and model statistics                |    Yes |
| Export CSV                                            |    Yes |
| Export Excel `.xlsx`                                  |    Yes |
| Export HTML                                           |    Yes |
| Export Markdown                                       |    Yes |
| Export LaTeX `.tex` tables and reports                |    Yes |
| Export JSON                                           |    Yes |
| Export Word `.docx` reports                           |    Yes |
| Export PDF tables and reports                         |    Yes |
| Export combined Excel workbook                        |    Yes |
| Create reproducible output bundles                    |    Yes |

---

## Outreg-style reporting

`universal-output-hub` supports `outreg2`-style model reporting in Python.

That means it can:

| Question                                                                              |                                            Answer |
| ------------------------------------------------------------------------------------- | ------------------------------------------------: |
| Export regression/model results like `outreg2`?                                       |                                      Yes, broadly |
| Put models side-by-side in columns?                                                   |                                               Yes |
| Show coefficient estimates?                                                           |                                               Yes |
| Show standard errors below coefficients?                                              |                                               Yes |
| Add significance stars?                                                               |                                               Yes |
| Customize star thresholds?                                                            |                                               Yes |
| Include diagnostics/statistics like N, R², Hansen p, Sargan p, AR tests, instruments? |                                               Yes |
| Add notes under the table?                                                            |                                               Yes |
| Export to Excel?                                                                      |                                               Yes |
| Export to LaTeX?                                                                      |                                               Yes |
| Export to PDF?                                                                        |                                               Yes |
| Export to Word/DOCX?                                                                  |                                               Yes |
| Export to HTML, Markdown, CSV, JSON?                                                  |                                               Yes |
| Accept `statsmodels` results?                                                         |                                               Yes |
| Accept custom model dictionaries?                                                     |                                               Yes |
| Accept Stata/R/MATLAB/SPSS/EViews outputs?                                            | Yes, if exported as structured coefficient tables |

This package is **not** a full clone of Stata’s `outreg2`. It provides `outreg2`-style reporting for Python and external coefficient-table workflows.

---

## Current limitations and roadmap

| Capability                                                            |  Status |
| --------------------------------------------------------------------- | ------: |
| Native MATLAB `.mat` model-object parser                              | Planned |
| Native Stata `.ster` parser                                           | Planned |
| Native R `.rds` model-object parser                                   | Planned |
| Exact Stata `outreg2` command compatibility                           | Planned |
| Full `esttab`-level formatting grammar                                | Planned |
| Multi-equation models with separate panels                            | Planned |
| Automatic fixed-effect yes/no row detection from native model objects | Planned |
| Journal templates                                                     | Planned |

External software compatibility currently works through structured coefficient tables with at least a term column and a coefficient column. Standard errors, p-values, statistics, diagnostics, and notes can also be supplied.

---

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

---

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
        "statistics": {
            "N": 946,
            "Instruments": 42,
        },
        "diagnostics": {
            "AR(1) p": 0.085,
            "AR(2) p": 0.316,
            "Hansen p": 0.190,
            "Sargan p": 0.098,
            "Diff-Hansen p": 0.089,
        },
    }
)

hub.add_table_note("Standard errors are reported in parentheses.")
hub.add_table_note("Hansen, Sargan, and AR tests are reported as p-values.")

hub.export_bundle("outputs/model_output")
```

---

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

The default output filenames are generic:

```text
output_report.docx
output_report.pdf
output_report.tex
output_workbook.xlsx
```

The package does not assume that the project is a thesis, dissertation, academic paper, business report, or internal analysis.

---

## Regression tables

Export regression/model tables to multiple formats:

```python
hub.export_regression_table("outputs/regression_table.xlsx")
hub.export_regression_table("outputs/regression_table.tex")
hub.export_regression_table("outputs/regression_table.pdf")
hub.export_regression_table("outputs/regression_table.html")
hub.export_regression_table("outputs/regression_table.md")
hub.export_regression_table("outputs/regression_table.csv")
hub.export_regression_table("outputs/regression_table.json")
```

A typical table includes:

```text
                         System GMM
L.growth_rate             0.310**
                          (0.120)

lPA                       0.080***
                          (0.030)

N                         946
Instruments               42
AR(1) p                   0.085
AR(2) p                   0.316
Hansen p                  0.190
Sargan p                  0.098
Diff-Hansen p             0.089

Significance              *** p≤0.01, ** p≤0.05, * p≤0.10
Notes                     Standard errors are reported in parentheses.
                          Hansen, Sargan, and AR tests are reported as p-values.
```

---

## Significance stars

Stars are enabled by default:

```text
*** p≤0.01
**  p≤0.05
*   p≤0.10
```

Disable stars:

```python
hub.export_regression_table(
    "outputs/regression_table.tex",
    stars=False,
)
```

Use custom thresholds:

```python
hub.export_regression_table(
    "outputs/regression_table.tex",
    star_levels={"***": 0.001, "**": 0.01, "*": 0.05},
)
```

---

## Table notes

Use table notes for `outreg2`-style notes under regression/model tables:

```python
hub.add_table_note("Standard errors in parentheses.")
hub.add_table_note("Country and year fixed effects included.")
hub.add_table_note("Hansen, Sargan, and AR tests are reported as p-values.")
```

Table notes are included in:

* regression/model tables;
* Excel exports;
* LaTeX exports;
* PDF exports;
* DOCX reports;
* PDF reports;
* LaTeX reports;
* manifest files.

You can also pass notes directly when building a regression table:

```python
table = hub.regression_table(
    table_notes=[
        "Standard errors in parentheses.",
        "Country and year fixed effects included.",
    ]
)
```

---

## Diagnostics and model statistics

Diagnostics and statistics can be supplied directly:

```python
hub.add_model(
    {
        "name": "System GMM",
        "params": {"L.y": 0.42, "x": 0.11},
        "std_errors": {"L.y": 0.10, "x": 0.04},
        "pvalues": {"L.y": 0.001, "x": 0.030},
        "statistics": {
            "N": 946,
            "Instruments": 42,
        },
        "diagnostics": {
            "AR(1) p": 0.085,
            "AR(2) p": 0.316,
            "Hansen p": 0.190,
            "Sargan p": 0.098,
            "Diff-Hansen p": 0.089,
        },
    }
)
```

Supported diagnostic/statistic rows include, among others:

```text
N
R2
Adj. R2
Within R2
Overall R2
AIC
BIC
Log Likelihood
F statistic
F p-value
AR(1) p
AR(2) p
Hansen p
Sargan p
Diff-Hansen p
Instruments
Entity FE
Time FE
Fixed effects
Clustered SE
```

The package exports diagnostics. It does not compute Hansen, Sargan, AR tests, or other estimator-specific tests by itself unless a backend or model object supplies them.

---

## External model outputs

External statistical software can be used by exporting coefficient tables into a structured format.

Minimum structure:

| term        |  coef |    se | pvalue |
| ----------- | ----: | ----: | -----: |
| lPA         | 0.080 | 0.022 |  0.001 |
| s_techshare | 0.161 | 0.071 |  0.024 |

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

---

## Embedded diagnostics from imported regression tables

Some tools export diagnostics as rows below the coefficients. For example:

```csv
term,coef,se,pvalue
L.y,0.42,0.10,0.001
x,0.11,0.04,0.030
N,946,,
Instruments,42,,
AR(1) p,0.085,,
AR(2) p,0.316,,
Hansen p,0.190,,
Sargan p,0.098,,
Diff-Hansen p,0.089,,
Entity FE,Yes,,
Time FE,Yes,,
```

The package can treat these as table statistics/diagnostics rather than coefficients when the embedded-diagnostics extractor is enabled in the adapter layer.

This is useful for Stata/R/MATLAB/SPSS/EViews-style result exports.

---

## Python models

```python
import statsmodels.api as sm
from universal_output_hub import OutputHub

hub = OutputHub("Python Model Output")

fit = sm.OLS(y, X).fit()
hub.add_model(fit, name="OLS", adapter="statsmodels")

hub.export_bundle("outputs/python_models")
```

The package extracts common model information such as coefficients, standard errors, p-values, N, R², AIC, BIC, log likelihood, and related statistics when available.

---

## Custom model dictionaries

Custom estimators can be passed directly:

```python
hub.add_model(
    {
        "name": "Custom Estimator",
        "depvar": "y",
        "params": {
            "x1": 1.25,
            "x2": -0.40,
        },
        "std_errors": {
            "x1": 0.20,
            "x2": 0.15,
        },
        "pvalues": {
            "x1": 0.004,
            "x2": 0.080,
        },
        "statistics": {
            "N": 100,
            "R2": 0.45,
        },
        "diagnostics": {
            "Hansen p": 0.31,
            "AR(2) p": 0.42,
        },
    }
)
```

This is the recommended interface for custom econometric packages, including dynamic-panel GMM workflows.

---

## Ordinary tables

Add descriptive statistics, robustness checks, correlations, or any pandas-compatible table:

```python
hub.add_table("Descriptive statistics", df.describe())
hub.add_table("Correlation matrix", df.corr())
hub.add_table("Robustness summary", robustness_df)

hub.export_tables(
    "outputs/tables",
    formats=("csv", "xlsx", "html", "md", "tex", "pdf", "json"),
)
```

---

## Figures and graphs

Add an existing graph file:

```python
hub.add_figure(
    "Marginal effects plot",
    path="figures/marginal_effects.png",
    caption="Estimated marginal effects across institutional quality.",
)
```

Save a matplotlib-style figure directly:

```python
hub.add_figure(
    "Model comparison",
    fig=fig,
    output_dir="outputs/figures",
    filename="model_comparison.png",
)
```

Figures are copied into reproducible output bundles and included in full reports where supported.

---

## Complete reports

Export full reports:

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

---

## Recommended workflow

```python
from universal_output_hub import OutputHub

hub = OutputHub("Model Output Report")

hub.add_model(model_1, name="OLS")
hub.add_model(model_2, name="Fixed Effects")
hub.add_model(model_3, name="System GMM")

hub.add_table_note("Standard errors in parentheses.")
hub.add_table_note("Country and year fixed effects included.")

hub.add_table("Descriptive statistics", descriptives)
hub.add_table("Robustness checks", robustness)

hub.add_figure("Coefficient plot", path="figures/coefplot.png")

hub.export_bundle("outputs/run_001")
```

---

## Design philosophy

1. **Model-agnostic**: accept Python models, custom dictionaries, and structured external coefficient tables.
2. **Research-friendly**: support regression tables, diagnostics, notes, tables, figures, and reproducible bundles.
3. **Format-flexible**: export to Excel, LaTeX, PDF, Word, HTML, Markdown, CSV, and JSON.
4. **Transparent**: avoid pretending to be a native parser for every statistical software object.
5. **Simple API**: collect outputs once and export them everywhere.

---

## Project status

Current release: `0.2.0`

This is an early-stage package. The public API is usable, but some internals may still change as the package matures.

---

## License

MIT License.

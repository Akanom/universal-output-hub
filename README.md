# Universal Output Hub

[![PyPI version](https://img.shields.io/pypi/v/universal-output-hub.svg)](https://pypi.org/project/universal-output-hub/)
[![Python versions](https://img.shields.io/pypi/pyversions/universal-output-hub.svg)](https://pypi.org/project/universal-output-hub/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/Akanom/universal-output-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/Akanom/universal-output-hub/actions/workflows/ci.yml)
[![Publish](https://github.com/Akanom/universal-output-hub/actions/workflows/publish.yml/badge.svg)](https://github.com/Akanom/universal-output-hub/actions/workflows/publish.yml)
[![Downloads](https://static.pepy.tech/badge/universal-output-hub/month)](https://pepy.tech/project/universal-output-hub)
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

`universal-output-hub` supports `outreg2`-style model reporting in Python through both the object-oriented `OutputHub` workflow and a one-line `outreg()` convenience API.

```python
from universal_output_hub import outreg

outreg(
    [model_1, model_2],
    using="results.docx",
    model_names=["OLS", "Fixed Effects"],
    template="economics",
    stats=["N", "R2", "Entity FE", "Time FE", "Clustered SE"],
    notes=["Standard errors in parentheses."],
    replace=True,
)
```

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
| Detect fixed-effect and clustered-SE rows from compatible model objects?              |                                               Yes |
| Add notes under the table?                                                            |                                               Yes |
| Use journal-style table presets?                                                      |                                               Yes |
| Export to Excel?                                                                      |                                               Yes |
| Export to LaTeX?                                                                      |                                               Yes |
| Export to PDF?                                                                        |                                               Yes |
| Export to Word/DOCX?                                                                  |                                               Yes |
| Export to HTML, Markdown, CSV, JSON?                                                  |                                               Yes |
| Accept `statsmodels` results?                                                         |                                               Yes |
| Accept `linearmodels` and `pyfixest`-like results?                                    |                                               Yes |
| Accept custom model dictionaries?                                                     |                                               Yes |
| Accept Stata/R/MATLAB/SPSS/EViews outputs?                                            | Yes, if exported as structured coefficient tables |

This package is **not** a full clone of Stata's `outreg2`. It provides `outreg2`-style reporting for Python and external coefficient-table workflows.

## Current limitations and roadmap

| Capability                                     |  Status |
| ---------------------------------------------- | ------: |
| Multi-equation models with separate panels     | Planned |
| Native MATLAB `.mat` model-object parser       | Planned |
| Native Stata `.ster` parser                    | Planned |
| Native R `.rds` model-object parser            | Planned |
| Exact Stata `outreg2` command compatibility    | Planned |
| Full `esttab`-level formatting grammar         | Planned |
| Advanced journal-specific submission templates | Planned |

External software compatibility currently works through structured coefficient tables with at least a term column and a coefficient column. Standard errors, p-values, statistics, diagnostics, and notes can also be supplied.

Automatic fixed-effect and clustered-standard-error row detection is supported for compatible native model objects that expose recognisable metadata. Lightweight table templates are available through the `template=` argument.

## Supported input types

`universal-output-hub` is designed as a generic output layer, not as a reporting layer for one estimator or one package only.

It accepts and normalises common statistical and econometric result formats, including:

* dictionaries with `params`, `std_errors`, `pvalues`, `statistics`, and `diagnostics`;
* external coefficient tables from pandas DataFrames and supported table files;
* `statsmodels`-like result objects;
* `linearmodels`-like result objects;
* `pyfixest`-like result objects;
* generic Python result objects exposing coefficient, standard-error, p-value, statistics, metadata, or diagnostics attributes;
* dynamic-panel and GMM-style result objects exposing diagnostics such as observations, group count, instrument count, Hansen/Sargan tests, AR tests, backend, and covariance type;
* compatible fixed-effects model objects exposing entity effects, time effects, fixed effects, clustered standard errors, or covariance-type metadata.
* `limiteddepkit` fitted results through automatic module detection or
  `adapter="limiteddepkit"`, including binary, ordinal, fixed-effects and
  dynamic ordinal, count, duration, censoring, multinomial, sequential,
  conditional-choice, small-sample, and sample-selection families. Complete
  multi-equation and ancillary parameter vectors are retained.

Compatibility with `systemgmmkit`-style dynamic-panel results is treated as one high-priority compatibility case within this broader adapter contract.

## Dynamic-panel and GMM reporting compatibility

`universal-output-hub` is designed to report dynamic-panel and GMM-style model outputs supplied by compatible estimators. This includes result objects or dictionaries exposing coefficients, standard errors, p-values, model statistics, diagnostics, metadata, and covariance information.

For `systemgmmkit`-style workflows, the reporting layer is intended to support outputs from:

* Difference GMM;
* System GMM;
* FOD Difference GMM;
* one-step and two-step estimators;
* Windmeijer-corrected and robust covariance labels where supplied by the estimator;
* diagnostics such as observations, groups, instruments, Hansen/Sargan tests, AR tests, backend, transformation, and covariance type.

`universal-output-hub` does not estimate GMM models and does not independently validate econometric diagnostics. It collects, normalises, formats, and exports results supplied by the estimator or by structured external result files.

This keeps `systemgmmkit` as one important compatibility case while preserving the broader goal of supporting generic econometric and statistical result objects from Python and external software.

## Table templates

The package includes lightweight publication-style presets through the `template=` argument.

```python
hub.regression_table(template="economics")

outreg(
    models,
    using="table.md",
    template="journal",
    replace=True,
)
```

Currently supported templates include:

| Template    | Purpose                                                              |
| ----------- | -------------------------------------------------------------------- |
| `economics` | Econometrics-oriented table with common FE, GMM, and diagnostic rows |
| `journal`   | Compact publication-style table preset                               |
| `stata`     | Stata/outreg-style ordering for common regression statistics         |

Templates are intentionally lightweight. They control common statistics ordering, significance-star conventions, and table-note defaults. They are not full journal-specific submission templates.

## Public API and module layout

The recommended public API is imported from the package root:

```python
from universal_output_hub import OutputHub, outreg
```

Users should not import from internal implementation modules unless they are extending the package.

The maintained internal layout for this release is:

```text
universal_output_hub/
├── __init__.py
├── adapters.py
├── core.py
├── formatters.py
└── reports.py
```

For this release, the maintained implementation is organised through `core.py`, `adapters.py`, `formatters.py`, and `reports.py`. Users should import from the package root unless they are extending internal package functionality.

## Installation

Install from PyPI:

```bash
python -m pip install universal-output-hub
```

The core install supports pandas/NumPy workflows and text-based exports. Install
only the file-format backends you need:

```bash
python -m pip install "universal-output-hub[excel]"     # .xlsx
python -m pip install "universal-output-hub[parquet]"   # Parquet
python -m pip install "universal-output-hub[documents]" # Word .docx
python -m pip install "universal-output-hub[pdf]"       # PDF
python -m pip install "universal-output-hub[reports]"   # Excel, Word, and PDF
python -m pip install "universal-output-hub[all]"       # every maintained backend
```

Install from GitHub:

```bash
python -m pip install git+https://github.com/Akanom/universal-output-hub.git
```

Development installation:

```bash
python -m pip install -e ".[dev,examples,integration]"
pytest -q
```

Windows PowerShell:

```powershell
cd "<UNIVERSAL_OUTPUT_HUB_REPO>"

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,examples,integration]"
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

In rich table formats (Excel, HTML, LaTeX, PDF, and DOCX), significance and
custom note rows span the full table width. This keeps long notes from forcing
one model column to become disproportionately wide. Plain-text formats such as
CSV, JSON, Markdown, and TXT retain the rectangular DataFrame representation
because those formats do not support merged cells.

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

### Python statistical-package compatibility

The automatic adapter recognises these result families. Optional packages are
not runtime dependencies; install only the packages used by your analysis.

| Package or result family | Integration | Inference handling |
| ------------------------ | ----------- | ------------------ |
| `statsmodels` | Native result adapter, including DataFrame-valued multi-equation parameters | Coefficients, standard errors, p-values, and common fit statistics |
| `linearmodels` | Native panel/IV-style result adapter | Coefficients, standard errors, p-values, panel R² measures, and F statistics |
| `pyfixest` | Native duck-typed adapter and tidy-table fallback | Coefficients, standard errors, p-values, and available fit statistics |
| `limiteddepkit` | Native shared-result adapter | Complete parameter vector, inference, fit statistics, and diagnostics |
| `lifelines` | Summary-table adapter | Coefficients, standard errors, p-values, N, AIC, and log likelihood |
| `arch` | Native result adapter | Parameters, standard errors, p-values, and common fit statistics |
| `DoubleML` | Treatment-effect result adapter | Treatment coefficients, standard errors, and p-values |
| `EconML` | Finite-dimensional coefficient adapter | Inference is included only when the estimator exposes `coef__inference()` |
| ArviZ / PyMC / Bambi `InferenceData` | ArviZ posterior-summary adapter | Posterior means and SDs; credible intervals are metadata; p-values are not fabricated |
| scikit-learn linear models | Coefficient adapter, including multiclass matrices | Coefficients and intercepts only; scikit-learn does not provide inferential SEs/p-values |
| Custom estimators | Mapping, generic object, summary-table, or registered adapter | Exactly the inference fields supplied by the estimator |

Prediction-only estimators, distribution objects, and effect functions without a
finite coefficient vector should be exported as ordinary tables with
`hub.add_table(...)`. Universal Output Hub reports estimator output; it does not
derive missing uncertainty estimates or convert predictive models into
inferential models.

Install the packages exercised by the CI integration matrix with:

```bash
python -m pip install -e ".[integration]"
```

The integration extra currently installs `statsmodels`, `linearmodels`,
`pyfixest`, and `scikit-learn`. Contract tests cover the other optional result
families without making those large ecosystems mandatory dependencies.

### Registering a custom model adapter

Use the process-local registry when a package does not expose one of the common
result contracts:

```python
import pandas as pd

from universal_output_hub import RegressionModel, register_model_adapter


def convert(result, name, diagnostics):
    return RegressionModel(
        name=name,
        params=pd.Series(result.estimates, name="coef"),
        diagnostics=dict(diagnostics or {}),
        source="my-package",
    )


register_model_adapter(
    "my-package",
    predicate=lambda result: result.__class__.__module__.startswith("my_package"),
    converter=convert,
)
```

Pass `adapter="my-package"` for explicit selection, or leave `adapter="auto"`
to use the predicate. Registration never imports third-party plugins
automatically, so applications retain control over code execution and adapter
precedence. Use `unregister_model_adapter("my-package")` to remove it.

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

Current stable release: [available from PyPI](https://pypi.org/project/universal-output-hub/).

This is an early-stage package. The public API is usable, but some internals may still change as the package matures.

---

## License

MIT License.






# Universal Output Hub

`universal-output-hub` is a lightweight Python reporting layer that collects **models, tables, diagnostics, notes, and graphs** into one reproducible output bundle.

It is designed as a broader Python alternative to Stata-style reporting tools such as `outreg2`: not only regression tables, but the full research-output layer around a project.

## What it does

- combines outputs from multiple model backends;
- accepts coefficient tables exported from Stata, R, SPSS, EViews, Excel, CSV, Stata `.dta`, or Parquet;
- stores System GMM diagnostics such as AR(1), AR(2), Hansen, Sargan, difference-in-Hansen, and instrument count;
- exports regression tables to CSV, Excel, HTML, Markdown, LaTeX, and JSON;
- adds publication-style significance stars by default: `*** p≤0.01`, `** p≤0.05`, `* p≤0.10`;
- collects ordinary tables such as descriptives, correlations, balance tables, robustness checks, and summary statistics;
- collects graph files or saves matplotlib figures;
- generates a reproducible output folder with `manifest.json` and `index.html`.

## Installation

### Local editable installation

```bash
cd universal-output-hub
python -m pip install -e .
```

### Development installation

```bash
python -m pip install -e ".[dev,examples]"
pytest -q
```

### Windows PowerShell setup

```powershell
cd universal-output-hub
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev,examples]"
pytest -q
```

### Install from GitHub after pushing

```bash
python -m pip install git+https://github.com/Akanom/universal-output-hub.git
```

## Basic use

```python
from universal_output_hub import OutputHub

hub = OutputHub("Aid-growth thesis results")

hub.add_model({
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
    "diagnostics": {"AR(2) p": 0.316, "Hansen p": 0.190, "Instruments": 42},
})

hub.export_bundle("outputs/thesis_results")
```

## Add models from external statistical software

Export a coefficient table from Stata/R/SPSS/EViews/Excel using columns like:

| term | coef | se | pvalue |
|---|---:|---:|---:|
| lPA | 0.080 | 0.022 | 0.001 |
| s_techshare | 0.161 | 0.071 | 0.024 |

Then import it:

```python
hub.add_model_file(
    "stata_fe_results.csv",
    name="Stata FE",
    term_col="term",
    coef_col="coef",
    se_col="se",
    pvalue_col="pvalue",
    statistics={"N": 885, "Within R2": 0.21},
    source="Stata export",
)
```

## Add Python models

```python
import statsmodels.api as sm

fit = sm.OLS(y, X).fit()
hub.add_model(fit, name="OLS", adapter="statsmodels")
```

The adapter also supports `linearmodels` and pyfixest-like objects where their APIs expose standard coefficient, standard-error, and p-value methods.

## Add ordinary tables

```python
hub.add_table("Descriptive statistics", df.describe())
hub.add_table("Correlation matrix", df.corr())
```

## Add graphs

```python
hub.add_figure("Marginal effects", fig=fig, output_dir="outputs/raw_figures")

# or register an existing file
hub.add_figure("Robustness plot", path="robustness.png")
```

## Export one regression table only

```python
hub.export_regression_table(
    "outputs/regression_table.tex",
    labels={
        "lPA": "ln(PDA)",
        "s_techshare": "Technical aid share",
        "s_tech_frag_polity": "Tech share × fragmentation × polity",
    },
    order=["L.growth_rate", "lPA", "s_techshare", "s_tech_frag_polity"],
    stats_order=["N", "AR(2) p", "Hansen p", "Instruments"],
    stars=True,
)
```

## Significance stars

Stars are enabled by default in regression tables. The default convention is:

```text
*** p≤0.01, ** p≤0.05, * p≤0.10
```

Custom thresholds:

```python
hub.export_regression_table(
    "outputs/regression_table.md",
    stars=True,
    star_levels={"***": 0.001, "**": 0.01, "*": 0.05},
    star_note="*** p≤0.001, ** p≤0.01, * p≤0.05",
)
```

No stars:

```python
hub.export_regression_table("outputs/no_stars.tex", stars=False)
```

## GitHub push

Create an empty repository on GitHub, then run:

```bash
git init
git add .
git commit -m "Initial release: universal output hub"
git branch -M main
git remote add origin https://github.com/Akanom/universal-output-hub.git
git push -u origin main
```

With GitHub CLI:

```bash
gh repo create Akanom/universal-output-hub --public --source=. --remote=origin --push
```

Or use the included helper scripts after creating an empty GitHub repository:

```powershell
.\scripts\push_to_github.ps1 Akanom/universal-output-hub
```

```bash
./scripts/push_to_github.sh Akanom/universal-output-hub
```

See [`INSTALLATION.md`](INSTALLATION.md) for the full setup path.

## Intended role inside `systemgmmkit`

Recommended folder placement:

```text
systemgmmkit/
  reporting/
    output_hub.py
```

Recommended package-level API:

```python
from systemgmmkit.reporting import OutputHub
```

The estimator should only estimate. The hub should report. That separation keeps the architecture clean.

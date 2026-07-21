# Dependency Review

Review date: 2026-07-21

Owner: Maintainer

Reassessment: every dependency change and at least quarterly

## Runtime dependencies

| Package | Purpose | Decision |
|---|---|---|
| NumPy | Model-adapter and numeric normalization support | Mandatory; `>=1.24,<3` |
| pandas | Tables, formatting, and exports | Mandatory; `>=2,<4` |

Matplotlib, OpenPyXL, PyArrow, python-docx, ReportLab, Statsmodels,
linearmodels, PyFixest, and scikit-learn were removed from the mandatory graph.
They remain bounded optional extras with feature-local imports and actionable
installation errors. Jinja2 and tabulate were removed because package code did
not use them directly and Markdown/HTML rendering has internal fallbacks.

An OSV-backed audit of the latest resolvable pre-change runtime graph found no
known vulnerabilities on 2026-07-21. CI now audits the reduced core graph and
hash-pinned test/export graph on every change.

## Expected capabilities

The core import performs no network or shell access. Figure handling accepts a
Matplotlib-like `savefig()` protocol without importing Matplotlib. File access
is explicitly requested by export APIs; document/PDF engines are not imported
until those formats are selected.

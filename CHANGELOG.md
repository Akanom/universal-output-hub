# Changelog

## Unreleased

- Replaced the hard-coded README release number with the canonical PyPI link.
- Upgraded `actions/checkout` to v7 and `actions/setup-python` to v6 for
  Node.js 24-compatible GitHub Actions execution.

## 0.2.3 - 2026-07-19

- Made significance and custom note rows span the full table width in Excel,
  HTML, LaTeX, PDF, and DOCX regression-table exports.
- Added automatic `limiteddepkit` result detection, complete-parameter export,
  shared fit statistics, diagnostics, metadata, and sample-selection equation
  normalization.

## 0.2.0

- Added native DOCX report export.
- Added native PDF report export.
- Added generic `export_report(...)` API.
- Added `reports/` output folder to `export_bundle(...)`.
- Added generic default report filename: `output_report`.
- Rewrote README to reflect the broader output-hub scope.

## 0.1.2

- Added GitHub-ready project files: `.gitignore`, `LICENSE`, `INSTALLATION.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `Makefile`, and GitHub Actions test workflow.
- Added clearer installation and repository-push instructions.
- Kept publication-style significance stars enabled by default.

## 0.1.1

- Added configurable significance stars for regression tables.
- Added automatic significance-note row.
- Added tests for default stars, custom stars, and no-star export.

## 0.1.0

- Initial package implementation.
- Added model, table, diagnostic, note, and figure collection.
- Added export bundle support for CSV, Excel, HTML, Markdown, LaTeX, JSON, manifest, and HTML report.

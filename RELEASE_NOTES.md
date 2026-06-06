# universal-output-hub v0.2.0

universal-output-hub is a lightweight Python reporting layer for collecting model results, regression tables, statistical tables, diagnostics, notes, and graphs into reproducible output bundles.

## Highlights

- Collect Python model results, custom model dictionaries, tables, diagnostics, notes, and figures.
- Export research outputs to CSV, Excel, HTML, Markdown, LaTeX, JSON, Word, and PDF.
- Support outreg2-style reporting workflows for Python and external statistical outputs.
- Provide reproducible output bundles with manifest files and report exports.
- Add public citation metadata through CITATION.cff.
- Add CI workflow for linting, tests, and package builds.
- Add PyPI publishing workflow scaffold through GitHub Releases.

## Validation position

- This is an alpha-stage research-output package.
- Users should validate exported tables against their own empirical workflow before publication.
- The package does not compute estimator-specific tests unless supplied by a model object, backend, or user-provided diagnostics.

## Development installation

Run:

python -m pip install -e ".[dev,examples]"
python -m pytest -q

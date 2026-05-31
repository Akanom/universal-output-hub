# Contributing

The package is intentionally small and practical. Contributions should preserve four principles:

1. Estimators estimate; the hub reports.
2. Adapters convert external model objects into one canonical result object.
3. Exporters must be deterministic and reproducible.
4. Research outputs should remain inspectable in plain formats: CSV, Markdown, LaTeX, HTML, JSON, and Excel.

## Development workflow

```bash
python -m pip install -e ".[dev,examples]"
pytest -q
ruff check .
```

## Adding a new model adapter

Add extraction logic in `universal_output_hub/adapters.py` and return a `RegressionModel` with:

- `params`
- `std_errors`
- `pvalues`
- `statistics`
- `diagnostics`
- `metadata`

Add tests in `tests/` before changing exporter behavior.

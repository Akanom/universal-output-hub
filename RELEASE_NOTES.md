# universal-output-hub v0.2.4

Security-focused patch release with a smaller core install and reproducible
dependency and distribution verification.

## Changes

- Keep the core runtime limited to pandas and NumPy.
- Provide `excel`, `parquet`, `documents`, `pdf`, `reports`, and `all` extras.
- Report the exact installation extra when an optional backend is missing.
- Bound dependencies and provide hash-verified requirement sets.
- Audit dependencies, inspect wheel/sdist contents, generate an SBOM, pin CI
  actions by commit, attest provenance, and publish through trusted PyPI OIDC.

## Installation

python -m pip install universal-output-hub==0.2.4

# Install every maintained file-format backend
python -m pip install "universal-output-hub[all]==0.2.4"

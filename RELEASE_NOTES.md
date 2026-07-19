# universal-output-hub v0.2.3

Patch release improving cross-package model compatibility and publication-table formatting.

## Changes

- Add automatic support for inferential `limiteddepkit` fitted results, including
  complete multi-equation and ancillary parameter vectors.
- Normalize `SampleSelectionResult` outcome, selection, scale, and correlation
  parameters into one aligned regression-table model.
- Export shared `limiteddepkit` fit statistics, diagnostics, and metadata.
- Merge significance and custom-note rows across the full table width in Excel,
  HTML, LaTeX, PDF, and DOCX outputs.
- Keep CSV, JSON, Markdown, and TXT output rectangular for format compatibility.

## Installation

python -m pip install universal-output-hub==0.2.3

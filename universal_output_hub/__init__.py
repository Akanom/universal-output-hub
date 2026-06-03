"""Universal Output Hub.

A small reporting layer for collecting models, tables, diagnostics, and graphs
from Python and external statistical software into one reproducible output bundle.
"""

from .adapters import RegressionModel, from_coefficient_table, normalise_model
from .core import FigureArtifact, OutputHub, TableArtifact
from .reports import attach_output_methods, attach_report_methods

__all__ = [
    "FigureArtifact",
    "OutputHub",
    "RegressionModel",
    "TableArtifact",
    "from_coefficient_table",
    "normalise_model",
    "attach_output_methods",
    "attach_report_methods",
]

attach_report_methods(OutputHub)

attach_output_methods(OutputHub)

__version__ = "0.2.0"

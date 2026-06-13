"""Universal Output Hub.

Generic statistical and econometric output/reporting utilities.
"""

from .adapters import RegressionModel, from_coefficient_table, normalise_model
from .core import FigureArtifact, OutputHub, TableArtifact, outreg
from .reports import attach_output_methods, attach_report_methods

attach_output_methods(OutputHub)
attach_report_methods(OutputHub)

__all__ = [
    "FigureArtifact",
    "OutputHub",
    "RegressionModel",
    "TableArtifact",
    "attach_output_methods",
    "attach_report_methods",
    "from_coefficient_table",
    "normalise_model",
    "outreg",
]



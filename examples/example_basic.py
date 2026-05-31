from pathlib import Path

import pandas as pd

from universal_output_hub import OutputHub


out = Path("example_outputs")
hub = OutputHub("Example research-output bundle", metadata={"project": "systemgmmkit"})

# 1. Custom System GMM-style result from a dictionary.
hub.add_model(
    {
        "name": "System GMM",
        "depvar": "growth_rate",
        "params": {
            "L.growth_rate": 0.312,
            "lPA": 0.081,
            "s_techshare": 0.162,
            "frag_index_orth": -0.044,
            "polity2": 0.003,
            "s_tech_frag_polity": -0.022,
        },
        "std_errors": {
            "L.growth_rate": 0.118,
            "lPA": 0.027,
            "s_techshare": 0.070,
            "frag_index_orth": 0.020,
            "polity2": 0.002,
            "s_tech_frag_polity": 0.012,
        },
        "pvalues": {
            "L.growth_rate": 0.009,
            "lPA": 0.003,
            "s_techshare": 0.021,
            "frag_index_orth": 0.029,
            "polity2": 0.160,
            "s_tech_frag_polity": 0.078,
        },
        "statistics": {"N": 946},
        "diagnostics": {"AR(1) p": 0.085, "AR(2) p": 0.316, "Hansen p": 0.190, "Instruments": 42},
    }
)

# 2. External table that could have come from Stata/R/SPSS/EViews.
external = pd.DataFrame(
    {
        "term": ["lPA", "s_techshare", "frag_index_orth", "polity2", "s_tech_frag_polity"],
        "coef": [0.080, 0.161, -0.038, 0.004, 0.008],
        "se": [0.020, 0.071, 0.018, 0.002, 0.003],
        "pvalue": [0.000, 0.024, 0.035, 0.120, 0.012],
    }
)
hub.add_model_table(
    external,
    name="Stata FE export",
    depvar="growth_rate",
    statistics={"N": 885, "Within R2": 0.214},
    source="Stata CSV export",
)

# 3. Ordinary table.
hub.add_table("Descriptive statistics", external.describe(), caption="Demonstration table.")

# 4. Export everything.
hub.export_bundle(
    out,
    regression_kwargs={
        "order": ["L.growth_rate", "lPA", "s_techshare", "frag_index_orth", "polity2", "s_tech_frag_polity"],
        "labels": {
            "L.growth_rate": "Lagged growth",
            "lPA": "ln(PDA)",
            "s_techshare": "Technical aid share",
            "frag_index_orth": "Donor concentration / fragmentation",
            "polity2": "Institutional quality",
            "s_tech_frag_polity": "Tech share × fragmentation × polity",
        },
        "stats_order": ["N", "Within R2", "AR(1) p", "AR(2) p", "Hansen p", "Instruments"],
    },
)

print(f"Wrote bundle to: {out.resolve()}")

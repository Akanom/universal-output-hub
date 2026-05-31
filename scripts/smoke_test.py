"""Smoke test for Universal Output Hub."""

from pathlib import Path

from universal_output_hub import OutputHub


def main() -> None:
    hub = OutputHub("Smoke Test")
    hub.add_model(
        {
            "name": "M1",
            "depvar": "growth_rate",
            "params": {"x": 1.0, "z": -0.25},
            "std_errors": {"x": 0.20, "z": 0.10},
            "pvalues": {"x": 0.004, "z": 0.089},
            "statistics": {"N": 100},
            "diagnostics": {"Hansen p": 0.42, "AR(2) p": 0.31, "Instruments": 12},
        }
    )
    out = Path("outputs/smoke_test")
    bundle = hub.export_bundle(out)
    print(f"Wrote bundle to: {bundle['root'].resolve()}")


if __name__ == "__main__":
    main()

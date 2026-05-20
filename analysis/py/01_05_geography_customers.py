#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.9",
#   "pandas>=2.2",
# ]
# ///
"""Generate the customers-by-country chart from the exported CSV.

Reads ``analysis/exports/CSVs/01_05_geography_customers.csv`` and writes
``analysis/exports/Charts/01_05_geography_customers.png``.

Run with:
    uv run --script analysis/py/01_05_geography_customers.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_05_geography_customers.csv"
CHART_DIR = REPO_ROOT / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"


def whole_number_axis(value: float, _position: int) -> str:
    """Format axis labels as whole numbers with thousands separators."""
    return f"{value:,.0f}"


def main() -> None:
    """Build and save a horizontal bar chart of customers by country."""
    customers = pd.read_csv(CSV_PATH)
    customers = customers.sort_values("number_of_customers", ascending=True)

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        customers["country"],
        customers["number_of_customers"],
        color="#0f766e",
    )

    ax.bar_label(
        bars,
        labels=[f"{value:,.0f}" for value in customers["number_of_customers"]],
        padding=4,
        fontsize=10,
    )
    ax.set_title("Customers by Country", fontsize=18, fontweight="bold", pad=18)
    ax.set_xlabel("Number of Customers", fontsize=12)
    ax.set_ylabel("Country", fontsize=12)
    ax.xaxis.set_major_formatter(FuncFormatter(whole_number_axis))
    ax.grid(axis="x", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, customers["number_of_customers"].max() * 1.12)
    fig.tight_layout()

    fig.savefig(CHART_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart to {CHART_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.9",
#   "pandas>=2.2",
# ]
# ///
"""Generate the geography revenue chart from the exported CSV.

Reads ``analysis/exports/CSVs/01_04_geography_revenue.csv`` and writes
``analysis/exports/Charts/01_04_geography_revenue.png``.

Run with:
    uv run --script analysis/py/01_04_geography_revenue.py
"""

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_04_geography_revenue.csv"
CHART_DIR = REPO_ROOT / "analysis" / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"
TOP_N = 20


def currency_axis(value: float, _position: int) -> str:
    """Format axis labels as compact whole-dollar amounts."""
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def geography_label(row: pd.Series) -> str:
    """Build a readable geography label for a city-level row."""
    label = f"{row['city']}, {row['region']}, {row['country']}"
    return textwrap.fill(label, width=28)


def main() -> None:
    """Build and save a horizontal bar chart of top geography revenue."""
    geography = pd.read_csv(CSV_PATH)
    geography = geography.sort_values("total_revenue", ascending=False).head(TOP_N)
    geography = geography.iloc[::-1].copy()
    geography["label"] = geography.apply(geography_label, axis=1)

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 9))
    bars = ax.barh(
        geography["label"],
        geography["total_revenue"],
        color="#2563eb",
        alpha=0.9,
    )

    for bar, revenue in zip(bars, geography["total_revenue"], strict=True):
        ax.annotate(
            f"${revenue:,.0f}",
            xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color="#111827",
        )

    ax.set_title(
        f"Top {TOP_N} Geographies by Revenue",
        fontsize=18,
        fontweight="bold",
        pad=18,
    )
    ax.set_xlabel("Total Revenue", fontsize=12)
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(FuncFormatter(currency_axis))
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    fig.savefig(CHART_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart to {CHART_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

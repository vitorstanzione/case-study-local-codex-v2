#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.9",
#   "pandas>=2.2",
# ]
# ///
"""Generate the best-sellers chart from the exported CSV.

Reads ``analysis/exports/CSVs/01_07_best_sellers.csv`` and writes
``analysis/exports/Charts/01_07_best_sellers.png``.

Run with:
    uv run --script analysis/py/01_07_best_sellers.py
"""

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_07_best_sellers.csv"
CHART_DIR = REPO_ROOT / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"
TOP_N = 15


def whole_number_axis(value: float, _position: int) -> str:
    """Format axis labels as whole numbers with thousands separators."""
    return f"{value:,.0f}"


def currency(value: float) -> str:
    """Format values as whole-dollar currency labels."""
    return f"${value:,.0f}"


def product_label(product_name: str) -> str:
    """Wrap long product names for legible horizontal-axis labels."""
    return textwrap.fill(product_name, width=24)


def main() -> None:
    """Build and save a bar chart of top-selling products by units sold."""
    best_sellers = pd.read_csv(CSV_PATH)
    best_sellers = best_sellers.sort_values("total_units_sold", ascending=False).head(TOP_N)
    best_sellers = best_sellers.iloc[::-1].copy()
    best_sellers["label"] = best_sellers["product_name"].map(product_label)

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(
        best_sellers["label"],
        best_sellers["total_units_sold"],
        color="#7c3aed",
        alpha=0.9,
    )

    for bar, units, revenue in zip(
        bars,
        best_sellers["total_units_sold"],
        best_sellers["total_revenue"],
        strict=True,
    ):
        ax.annotate(
            f"{units:,.0f} units • {currency(revenue)}",
            xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color="#111827",
        )

    ax.set_title(
        f"Top {TOP_N} Best-Selling Products by Units Sold",
        fontsize=18,
        fontweight="bold",
        pad=18,
    )
    ax.set_xlabel("Units Sold", fontsize=12)
    ax.set_ylabel("Product", fontsize=12)
    ax.xaxis.set_major_formatter(FuncFormatter(whole_number_axis))
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, best_sellers["total_units_sold"].max() * 1.25)
    fig.tight_layout()

    fig.savefig(CHART_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart to {CHART_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

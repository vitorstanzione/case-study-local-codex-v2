#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.9",
#   "pandas>=2.2",
# ]
# ///
"""Generate the revenue-over-time chart from the exported CSV.

Reads ``analysis/exports/CSVs/01_01_revenue_over_time.csv`` and writes
``analysis/exports/Charts/01_01_revenue_over_time.png``.
Run with:
    uv run --script analysis/py/01_01_revenue_over_time.py
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_01_revenue_over_time.csv"
CHART_DIR = REPO_ROOT / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"


def currency_axis(value: float, _position: int) -> str:
    """Format y-axis labels as compact whole-dollar amounts."""
    return f"${value:,.0f}"


def main() -> None:
    """Build and save a monthly revenue line chart."""
    revenue = pd.read_csv(CSV_PATH, parse_dates=["revenue_month"])
    revenue = revenue.sort_values("revenue_month")

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(
        revenue["revenue_month"],
        revenue["revenue"],
        color="#2563eb",
        linewidth=2.5,
        marker="o",
        markersize=5,
    )
    ax.fill_between(
        revenue["revenue_month"],
        revenue["revenue"],
        alpha=0.12,
        color="#2563eb",
    )

    ax.set_title("Monthly Revenue Over Time", fontsize=18, fontweight="bold", pad=18)
    ax.set_xlabel("Revenue Month", fontsize=12)
    ax.set_ylabel("Revenue", fontsize=12)
    ax.yaxis.set_major_formatter(FuncFormatter(currency_axis))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.autofmt_xdate(rotation=35, ha="right")
    fig.tight_layout()

    fig.savefig(CHART_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart to {CHART_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

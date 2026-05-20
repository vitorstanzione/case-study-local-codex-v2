# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.8",
#   "pandas>=2.2",
# ]
# ///
"""Generate the order value over time chart from the exported CSV.

Run with:
    uv run --script analysis/py/01_03_order_value_over_time.py
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_03_order_value_over_time.csv"
CHART_DIR = REPO_ROOT / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"


def currency_axis(value: float, _position: int) -> str:
    """Format axis labels as whole-dollar amounts."""
    return f"${value:,.0f}"


def main() -> None:
    """Read the order value export and save a time-series chart."""
    orders = pd.read_csv(CSV_PATH, parse_dates=["order_month"])
    orders = orders.sort_values("order_month")

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(
        orders["order_month"],
        orders["average_order_value"],
        color="#2563eb",
        linewidth=2.8,
        marker="o",
        markersize=5,
    )
    ax.fill_between(
        orders["order_month"],
        orders["average_order_value"],
        orders["average_order_value"].min() - 1,
        color="#2563eb",
        alpha=0.10,
    )

    highest = orders.loc[orders["average_order_value"].idxmax()]
    lowest = orders.loc[orders["average_order_value"].idxmin()]
    for label, point, y_offset in (
        ("Peak", highest, 12),
        ("Low", lowest, -22),
    ):
        ax.annotate(
            f"{label}: ${point['average_order_value']:.2f}",
            xy=(point["order_month"], point["average_order_value"]),
            xytext=(0, y_offset),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color="#111827",
            bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#d1d5db", "alpha": 0.95},
            arrowprops={"arrowstyle": "->", "color": "#6b7280", "lw": 1},
        )

    ax.set_title("Average Order Value Over Time", fontsize=18, weight="bold", pad=16)
    ax.set_xlabel("Order Month", fontsize=11)
    ax.set_ylabel("Average Order Value", fontsize=11)
    ax.yaxis.set_major_formatter(currency_axis)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.margins(x=0.02)
    ax.grid(axis="y", color="#e5e7eb")
    ax.grid(axis="x", visible=False)

    caption = (
        f"Source: {CSV_PATH.relative_to(REPO_ROOT)} | "
        f"{orders['order_month'].min():%b %Y}–{orders['order_month'].max():%b %Y}"
    )
    fig.text(0.01, 0.01, caption, fontsize=9, color="#6b7280")

    fig.autofmt_xdate(rotation=35, ha="right")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(CHART_PATH, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved chart to {CHART_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

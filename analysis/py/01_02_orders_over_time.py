# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.8",
# ]
# ///
"""Generate the orders-over-time chart from the exported CSV.

Run with:
    uv run --script analysis/py/01_02_orders_over_time.py
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_02_orders_over_time.csv"
CHART_DIR = REPO_ROOT / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"


def read_orders_over_time(csv_path: Path) -> tuple[list[datetime], list[int], list[int]]:
    """Read monthly order and customer counts from the exported CSV."""
    months: list[datetime] = []
    total_orders: list[int] = []
    unique_customers: list[int] = []

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            months.append(datetime.strptime(row["order_month"], "%Y-%m-%d"))
            total_orders.append(int(row["total_orders"]))
            unique_customers.append(int(row["unique_customers"]))

    return months, total_orders, unique_customers


def build_chart(csv_path: Path = CSV_PATH, chart_path: Path = CHART_PATH) -> Path:
    """Build and save a monthly orders and unique customers chart."""
    months, total_orders, unique_customers = read_orders_over_time(csv_path)

    chart_path.parent.mkdir(parents=True, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(
        months,
        total_orders,
        color="#1f77b4",
        marker="o",
        linewidth=2.5,
        label="Total orders",
    )
    ax.plot(
        months,
        unique_customers,
        color="#ff7f0e",
        marker="o",
        linewidth=2.5,
        label="Unique customers",
    )

    latest_month = months[-1]
    latest_orders = total_orders[-1]
    latest_customers = unique_customers[-1]
    ax.annotate(
        f"Latest: {latest_orders:,} orders\n{latest_customers:,} customers",
        xy=(latest_month, latest_orders),
        xytext=(-120, -50),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#444444"},
        bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": "#cccccc"},
    )

    ax.set_title("Orders and Unique Customers Over Time", fontsize=16, fontweight="bold")
    ax.set_xlabel("Order month")
    ax.set_ylabel("Count")
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.legend(frameon=True)
    ax.margins(x=0.02)
    fig.autofmt_xdate(rotation=45, ha="right")
    fig.tight_layout()

    fig.savefig(chart_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return chart_path


if __name__ == "__main__":
    output_path = build_chart()
    print(f"Saved chart to {output_path}")

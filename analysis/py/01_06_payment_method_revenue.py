#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.9",
#   "pandas>=2.2",
# ]
# ///
"""Generate the payment-method revenue chart from the exported CSV.

Reads ``analysis/exports/CSVs/01_06_payment_method_revenue.csv`` and writes
``analysis/exports/Charts/01_06_payment_method_revenue.png``.

Run with:
    uv run --script analysis/py/01_06_payment_method_revenue.py 
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_06_payment_method_revenue.csv"
CHART_DIR = REPO_ROOT / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"

PAYMENT_METHOD_LABELS = {
    "bank_transfer": "Bank Transfer",
    "coupon": "Coupon",
    "credit_card": "Credit Card",
    "gift_card": "Gift Card",
}
PAYMENT_METHOD_COLORS = {
    "credit_card": "#2563eb",
    "bank_transfer": "#16a34a",
    "gift_card": "#f59e0b",
    "coupon": "#dc2626",
}


def currency_axis(value: float, _position: int) -> str:
    """Format y-axis labels as compact dollar amounts."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def main() -> None:
    """Build and save a monthly payment-method revenue stacked area chart."""
    revenue = pd.read_csv(CSV_PATH, parse_dates=["order_month"])
    revenue = revenue.sort_values(["order_month", "payment_method"])

    monthly_revenue = revenue.pivot_table(
        index="order_month",
        columns="payment_method",
        values="revenue",
        aggfunc="sum",
        fill_value=0,
    )

    method_order = [
        "credit_card",
        "bank_transfer",
        "gift_card",
        "coupon",
    ]
    monthly_revenue = monthly_revenue.reindex(columns=method_order)

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.stackplot(
        monthly_revenue.index,
        [monthly_revenue[method] for method in method_order],
        labels=[PAYMENT_METHOD_LABELS[method] for method in method_order],
        colors=[PAYMENT_METHOD_COLORS[method] for method in method_order],
        alpha=0.85,
    )

    total_revenue = monthly_revenue.sum(axis=1)
    ax.plot(
        monthly_revenue.index,
        total_revenue,
        color="#111827",
        linewidth=2.25,
        label="Total Revenue",
    )

    ax.set_title("Monthly Revenue by Payment Method", fontsize=18, fontweight="bold", pad=18)
    ax.set_xlabel("Order Month", fontsize=12)
    ax.set_ylabel("Revenue", fontsize=12)
    ax.yaxis.set_major_formatter(FuncFormatter(currency_axis))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", frameon=False, ncols=2)
    fig.autofmt_xdate(rotation=35, ha="right")
    fig.tight_layout()

    fig.savefig(CHART_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart to {CHART_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

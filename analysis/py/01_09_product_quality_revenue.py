#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.9",
#   "pandas>=2.2",
# ]
# ///
"""Generate the product quality and revenue chart from the exported CSV.

Reads ``analysis/exports/CSVs/01_09_product_quality_revenue.csv`` and writes
``analysis/exports/Charts/01_09_product_quality_revenue.png``.

Run with:
    uv run --script analysis/py/01_09_product_quality_revenue.py
"""

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_09_product_quality_revenue.csv"
CHART_DIR = REPO_ROOT / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"

FLAG_COLORS = {
    "high revenue / high support rate": "#dc2626",
    "high revenue": "#2563eb",
    "monitor": "#6b7280",
}
FLAG_LABELS = {
    "high revenue / high support rate": "High revenue + high support rate",
    "high revenue": "High revenue",
    "monitor": "Monitor",
}


def product_label(product_name: str) -> str:
    """Wrap product labels so annotations fit near each bubble."""
    return textwrap.fill(product_name.replace("Jaffle ", ""), width=16)


def main() -> None:
    """Build and save a quality-vs-support bubble chart sized by revenue."""
    products = pd.read_csv(CSV_PATH)
    products = products.sort_values("item_revenue", ascending=False).copy()
    products["bubble_size"] = products["item_revenue"] / products["item_revenue"].max() * 1_900 + 150

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 8))

    for flag, group in products.groupby("product_action_flag", sort=False):
        ax.scatter(
            group["support_ticket_rate_per_order"],
            group["avg_rating"],
            s=group["bubble_size"],
            color=FLAG_COLORS.get(flag, "#6b7280"),
            alpha=0.72,
            edgecolor="white",
            linewidth=1.4,
            label=FLAG_LABELS.get(flag, flag.title()),
        )

    for rank, row in enumerate(products.itertuples(index=False), start=1):
        should_label = rank <= 5 or row.support_ticket_rate_per_order >= 10.5
        if not should_label:
            continue

        ax.annotate(
            product_label(row.product_name),
            xy=(row.support_ticket_rate_per_order, row.avg_rating),
            xytext=(9, 6 if rank % 2 else -15),
            textcoords="offset points",
            fontsize=9,
            color="#111827",
            arrowprops={"arrowstyle": "-", "color": "#9ca3af", "lw": 0.8},
        )

    median_support_rate = products["support_ticket_rate_per_order"].median()
    median_rating = products["avg_rating"].median()
    ax.axvline(median_support_rate, color="#9ca3af", linestyle="--", linewidth=1)
    ax.axhline(median_rating, color="#9ca3af", linestyle="--", linewidth=1)
    ax.text(
        median_support_rate + 0.03,
        products["avg_rating"].min() - 0.002,
        f"Median support rate: {median_support_rate:.1f}%",
        fontsize=9,
        color="#4b5563",
        va="bottom",
    )
    ax.text(
        products["support_ticket_rate_per_order"].min() - 0.04,
        median_rating + 0.001,
        f"Median rating: {median_rating:.2f}",
        fontsize=9,
        color="#4b5563",
        va="bottom",
    )

    revenue_handles = [
        ax.scatter([], [], s=size, color="#9ca3af", alpha=0.45, edgecolor="white", linewidth=1.0)
        for size in (450, 1_100, 2_050)
    ]
    revenue_labels = ["$50K revenue", "$125K revenue", "$205K revenue"]
    flag_legend = ax.legend(loc="upper right", frameon=False, title="Action Flag")
    ax.add_artist(flag_legend)
    ax.legend(
        revenue_handles,
        revenue_labels,
        loc="lower left",
        frameon=False,
        title="Bubble Size",
        scatterpoints=1,
        labelspacing=1.2,
    )

    ax.set_title(
        "Product Quality vs. Revenue Risk",
        fontsize=18,
        fontweight="bold",
        pad=18,
    )
    ax.set_xlabel("Support Tickets per 100 Product Orders", fontsize=12)
    ax.set_ylabel("Average Product Rating", fontsize=12)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _position: f"{value:.1f}%"))
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    caption = "Bubble size represents item revenue; dashed lines mark dataset medians."
    fig.text(0.125, 0.02, caption, ha="left", fontsize=10, color="#4b5563")
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    fig.savefig(CHART_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart to {CHART_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

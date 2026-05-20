#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.9",
#   "pandas>=2.2",
# ]
# ///
"""Generate the abandoned-cart recovery chart from the exported CSV.

Reads ``analysis/exports/CSVs/01_08_abandoned_cart_recovery.csv`` and writes
``analysis/exports/Charts/01_08_abandoned_cart_recovery.png``.

Run with:
    uv run --script analysis/py/01_08_abandoned_cart_recovery.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter


REPO_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = REPO_ROOT / "analysis" / "exports" / "CSVs" / "01_08_abandoned_cart_recovery.csv"
CHART_DIR = REPO_ROOT / "visualizations"
CHART_PATH = CHART_DIR / f"{CSV_PATH.stem}.png"
VALUE_BAND_ORDER = ["<$50", "$50-$99", "$100-$199", "$200-$499"]


def currency_axis(value: float, _position: int) -> str:
    """Format axis labels as compact dollar amounts."""
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def percent_label(value: float) -> str:
    """Format recovery-rate labels for bar annotations."""
    return f"{value:.1f}%"


def main() -> None:
    """Build and save an abandoned-cart recovery summary chart."""
    carts = pd.read_csv(CSV_PATH)

    source_summary = (
        carts.groupby("traffic_source", as_index=False)
        .agg(
            abandoned_cart_value=("abandoned_cart_value", "sum"),
            recovered_value_proxy=("recovered_value_proxy", "sum"),
            unrecovered_value_opportunity=("unrecovered_value_opportunity", "sum"),
            abandoned_carts=("abandoned_carts", "sum"),
            recovered_carts=("recovered_carts", "sum"),
        )
        .assign(
            recovery_rate=lambda frame: frame["recovered_carts"]
            / frame["abandoned_carts"]
            * 100
        )
        .sort_values("unrecovered_value_opportunity", ascending=True)
    )

    recovery_heatmap = carts.pivot_table(
        index="traffic_source",
        columns="cart_value_band",
        values="cart_recovery_rate",
        aggfunc="mean",
    ).reindex(index=source_summary["traffic_source"], columns=VALUE_BAND_ORDER)

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(13, 10), layout="constrained")
    grid = fig.add_gridspec(2, 1, height_ratios=[2.1, 1.25], hspace=0.18)

    ax_bar = fig.add_subplot(grid[0])
    bars_unrecovered = ax_bar.barh(
        source_summary["traffic_source"],
        source_summary["unrecovered_value_opportunity"],
        color="#dc2626",
        alpha=0.82,
        label="Unrecovered value opportunity",
    )
    ax_bar.barh(
        source_summary["traffic_source"],
        source_summary["recovered_value_proxy"],
        left=source_summary["unrecovered_value_opportunity"],
        color="#16a34a",
        alpha=0.9,
        label="Recovered value proxy",
    )

    for bar, total_value, recovery_rate in zip(
        bars_unrecovered,
        source_summary["abandoned_cart_value"],
        source_summary["recovery_rate"],
        strict=True,
    ):
        ax_bar.annotate(
            f"{currency_axis(total_value, 0)} total · {percent_label(recovery_rate)} recovered",
            xy=(total_value, bar.get_y() + bar.get_height() / 2),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=9.5,
            color="#111827",
        )

    ax_bar.set_title(
        "Abandoned Cart Recovery by Traffic Source",
        fontsize=18,
        fontweight="bold",
        pad=18,
    )
    ax_bar.set_xlabel("Abandoned Cart Value", fontsize=12)
    ax_bar.set_ylabel("Traffic Source", fontsize=12)
    ax_bar.xaxis.set_major_formatter(FuncFormatter(currency_axis))
    ax_bar.grid(axis="x", alpha=0.25)
    ax_bar.set_axisbelow(True)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.legend(loc="lower right", frameon=False)
    ax_bar.set_xlim(0, source_summary["abandoned_cart_value"].max() * 1.22)

    ax_heatmap = fig.add_subplot(grid[1])
    cmap = LinearSegmentedColormap.from_list(
        "recovery_rate",
        ["#fee2e2", "#fef3c7", "#bbf7d0"],
    )
    image = ax_heatmap.imshow(recovery_heatmap, cmap=cmap, aspect="auto")

    ax_heatmap.set_title(
        "Cart Recovery Rate by Value Band",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )
    ax_heatmap.set_xticks(range(len(recovery_heatmap.columns)))
    ax_heatmap.set_xticklabels(recovery_heatmap.columns)
    ax_heatmap.set_yticks(range(len(recovery_heatmap.index)))
    ax_heatmap.set_yticklabels(recovery_heatmap.index)
    ax_heatmap.set_xlabel("Cart Value Band", fontsize=12)
    ax_heatmap.set_ylabel("Traffic Source", fontsize=12)

    for row_index, traffic_source in enumerate(recovery_heatmap.index):
        for column_index, value_band in enumerate(recovery_heatmap.columns):
            value = recovery_heatmap.loc[traffic_source, value_band]
            if pd.notna(value):
                ax_heatmap.text(
                    column_index,
                    row_index,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=10,
                    color="#111827",
                )

    colorbar = fig.colorbar(image, ax=ax_heatmap, fraction=0.035, pad=0.02)
    colorbar.ax.set_ylabel("Recovery Rate", rotation=270, labelpad=16)
    colorbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _pos: f"{value:.0f}%"))

    fig.savefig(CHART_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved chart to {CHART_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

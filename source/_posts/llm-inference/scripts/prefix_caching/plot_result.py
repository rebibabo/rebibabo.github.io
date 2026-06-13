"""
Plot Prefix Length Experiment Results

Usage:
    python prefix_length_plot.py
"""

from pathlib import Path
import json

RESULTS_DIR = Path("/root/autodl-tmp/results/prefix_length_exp")


def plot_results():
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    # ---------- Style ----------
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

    on_path = RESULTS_DIR / "results_cache_on.json"
    off_path = RESULTS_DIR / "results_cache_off.json"

    if not on_path.exists() or not off_path.exists():
        print("Result files not found.")
        return

    with open(on_path, encoding="utf-8") as f:
        on_data = json.load(f)

    with open(off_path, encoding="utf-8") as f:
        off_data = json.load(f)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    x_on = [r["actual_prompt_tokens"] for r in on_data]
    y_on = [r["avg_ttft_ms"] for r in on_data]

    x_off = [r["actual_prompt_tokens"] for r in off_data]
    y_off = [r["avg_ttft_ms"] for r in off_data]

    y_save = [off - on for off, on in zip(y_off, y_on)]
    pct_save = [100 * s / o for s, o in zip(y_save, y_off)]

    # equally spaced positions
    pos = np.arange(len(x_off))

    # ------------------------------------------------------------------
    # Linear Fit
    # ------------------------------------------------------------------

    coeff_off = np.polyfit(x_off, y_off, 1)
    coeff_on = np.polyfit(x_on, y_on, 1)

    x_fit = np.linspace(min(x_off), max(x_off), 200)

    y_fit_off = np.polyval(coeff_off, x_fit)
    y_fit_on = np.polyval(coeff_on, x_fit)

    # ------------------------------------------------------------------
    # Figure
    # ------------------------------------------------------------------

    fig, (ax1, ax2) = plt.subplots(
        1,
        2,
        figsize=(10, 5),
        gridspec_kw={"width_ratios": [2.2, 1.2]},
    )

    # ==============================================================
    # Left: TTFT vs Prefix Length
    # ==============================================================

    ax1.plot(
        x_off,
        y_off,
        marker="o",
        linewidth=2,
        label="Prefix Cache OFF",
    )

    ax1.plot(
        x_on,
        y_on,
        marker="s",
        linewidth=2,
        label="Prefix Cache ON",
    )

    ax1.plot(
        x_fit,
        y_fit_off,
        "--",
        linewidth=1.5,
        alpha=0.7,
        label=f"OFF Fit ({coeff_off[0]*1000:.1f} ms / 1k tok)",
    )

    ax1.plot(
        x_fit,
        y_fit_on,
        "--",
        linewidth=1.5,
        alpha=0.7,
        label=f"ON Fit ({coeff_on[0]*1000:.1f} ms / 1k tok)",
    )

    for x, y in zip(x_off, y_off):
        ax1.text(
            x,
            y + 20,
            f"{y:.0f}",
            ha="center",
            fontsize=8,
        )

    ax1.set_xlabel("Prompt Tokens")
    ax1.set_ylabel("TTFT (ms)")
    ax1.set_title("(a) TTFT vs Prefix Length")

    ax1.grid(True, alpha=0.3)

    
    ax1.legend(
        frameon=False,
        fontsize=8,
        loc="upper left",
    )

    # ==============================================================
    # Right: Reduction %
    # ==============================================================

    bars = ax2.bar(
        pos,
        pct_save,
        width=0.45,
    )

    for p, v in zip(pos, pct_save):
        ax2.text(
            p,
            v + 1,
            f"{v:.1f}%",
            ha="center",
            fontsize=8,
        )

    ax2.set_xticks(pos)
    ax2.set_xticklabels([str(x) for x in x_off])

    ax2.set_ylim(0, max(pct_save) * 1.15)

    ax2.set_xlabel("Prompt Tokens")
    ax2.set_ylabel("Reduction (%)")
    ax2.set_title("(b) TTFT Reduction")

    ax2.grid(True, axis="y", alpha=0.3)

    # ------------------------------------------------------------------
    # Global Title
    # ------------------------------------------------------------------

    fig.suptitle(
        "Impact of Prefix Length on TTFT",
        fontsize=14,
        y=1.02,
    )

    plt.tight_layout()

    out = RESULTS_DIR / "prefix_length_summary.png"

    plt.savefig(
        out,
        dpi=300,
        bbox_inches="tight",
    )

    print(f"\nSaved: {out}")

    # ------------------------------------------------------------------
    # Console Summary
    # ------------------------------------------------------------------

    print("\n=== Summary ===")
    print(
        f"{'Tokens':>8} {'OFF(ms)':>10} {'ON(ms)':>10} "
        f"{'Saved(ms)':>10} {'Reduction':>10}"
    )

    for t, off, on, saved, pct in zip(
        x_off,
        y_off,
        y_on,
        y_save,
        pct_save,
    ):
        print(
            f"{t:>8} "
            f"{off:>10.1f} "
            f"{on:>10.1f} "
            f"{saved:>10.1f} "
            f"{pct:>9.1f}%"
        )

    print("\nLinear Fit:")
    print(
        f"OFF: +{coeff_off[0]*1000:.1f} ms per 1k tokens"
    )
    print(
        f" ON: +{coeff_on[0]*1000:.1f} ms per 1k tokens"
    )


if __name__ == "__main__":
    plot_results()
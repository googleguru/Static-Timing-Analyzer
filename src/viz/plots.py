"""
All timing visualization plots.
Rules: white background, tight layout, no overlapping elements,
legends outside data, high-resolution PNG output.
"""
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from typing import List, Optional

log = logging.getLogger(__name__)

STYLE = {
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "lines.linewidth": 2.0,
}

METHOD_COLORS = {
    "baseline":     "#4472C4",
    "random_search":"#ED7D31",
    "choa":         "#70AD47",
    "choa_memory":  "#9E2A2B",
}

METHOD_LABELS = {
    "baseline":      "OpenSTA Baseline",
    "random_search": "Random Search",
    "choa":          "OpenSTA + ChOA",
    "choa_memory":   "OpenSTA + ChOA + Memory",
}


def _apply_style():
    plt.rcParams.update(STYLE)


def _save(fig, path: Path, dpi: int = 150) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(path), dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    log.info("Saved figure: %s", path)


class TimingPlotter:
    def __init__(self, output_dir: str = "outputs/figures"):
        self.out = Path(output_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        _apply_style()

    # ------------------------------------------------------------------
    def convergence_plot(self, results: List[dict], benchmark: str = None) -> Path:
        """Convergence curves for ChOA and ChOA+memory runs."""
        _apply_style()
        fig, ax = plt.subplots(figsize=(8, 4))

        plotted = False
        for r in results:
            if "convergence" not in r:
                continue
            if benchmark and r["benchmark"] != benchmark:
                continue
            method = r["method"]
            color  = METHOD_COLORS.get(method, "gray")
            label  = METHOD_LABELS.get(method, method)
            curve  = r["convergence"]
            ax.plot(range(1, len(curve) + 1), curve, color=color, label=label)
            plotted = True

        if not plotted:
            ax.text(0.5, 0.5, "No convergence data", ha="center", va="center", transform=ax.transAxes)

        ax.set_xlabel("Iteration")
        ax.set_ylabel("Best Composite Score")
        title = f"ChOA Convergence — {benchmark}" if benchmark else "ChOA Convergence"
        ax.set_title(title)
        ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.0), framealpha=0.8)
        fig.tight_layout()

        fname = f"convergence_{benchmark or 'all'}.png"
        path = self.out / fname
        _save(fig, path)
        return path

    # ------------------------------------------------------------------
    def wns_comparison(self, df: pd.DataFrame) -> Path:
        """Grouped bar chart of WNS per benchmark, one bar per method."""
        _apply_style()
        benchmarks = df["benchmark"].unique()
        methods    = [m for m in METHOD_COLORS if m in df["method"].unique()]
        n_bm = len(benchmarks)
        n_m  = len(methods)
        bar_w = 0.8 / n_m
        x = np.arange(n_bm)

        fig, ax = plt.subplots(figsize=(max(8, n_bm * 1.5), 5))

        for i, method in enumerate(methods):
            sub = df[df["method"] == method]
            vals = [sub[sub["benchmark"] == bm]["wns"].values[0] if bm in sub["benchmark"].values else 0.0
                    for bm in benchmarks]
            offset = (i - n_m / 2 + 0.5) * bar_w
            bars = ax.bar(x + offset, vals, width=bar_w * 0.9,
                          color=METHOD_COLORS[method],
                          label=METHOD_LABELS.get(method, method),
                          edgecolor="white", linewidth=0.5)

        ax.set_xticks(x)
        ax.set_xticklabels(benchmarks, rotation=30, ha="right")
        ax.set_ylabel("WNS (ns)  [higher is better]")
        ax.set_title("Worst Negative Slack Comparison")
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.0), framealpha=0.8)
        fig.tight_layout()

        path = self.out / "wns_comparison.png"
        _save(fig, path)
        return path

    # ------------------------------------------------------------------
    def tns_comparison(self, df: pd.DataFrame) -> Path:
        """Grouped bar chart of TNS per benchmark."""
        _apply_style()
        benchmarks = df["benchmark"].unique()
        methods    = [m for m in METHOD_COLORS if m in df["method"].unique()]
        n_bm = len(benchmarks)
        n_m  = len(methods)
        bar_w = 0.8 / n_m
        x = np.arange(n_bm)

        fig, ax = plt.subplots(figsize=(max(8, n_bm * 1.5), 5))

        for i, method in enumerate(methods):
            sub = df[df["method"] == method]
            vals = [sub[sub["benchmark"] == bm]["tns"].values[0] if bm in sub["benchmark"].values else 0.0
                    for bm in benchmarks]
            offset = (i - n_m / 2 + 0.5) * bar_w
            ax.bar(x + offset, vals, width=bar_w * 0.9,
                   color=METHOD_COLORS[method],
                   label=METHOD_LABELS.get(method, method),
                   edgecolor="white", linewidth=0.5)

        ax.set_xticks(x)
        ax.set_xticklabels(benchmarks, rotation=30, ha="right")
        ax.set_ylabel("TNS (ns)  [closer to 0 is better]")
        ax.set_title("Total Negative Slack Comparison")
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.0), framealpha=0.8)
        fig.tight_layout()

        path = self.out / "tns_comparison.png"
        _save(fig, path)
        return path

    # ------------------------------------------------------------------
    def violation_histogram(self, df: pd.DataFrame) -> Path:
        """Violation count per benchmark, stacked by method."""
        _apply_style()
        methods    = [m for m in METHOD_COLORS if m in df["method"].unique()]
        benchmarks = df["benchmark"].unique()
        n_bm = len(benchmarks)
        n_m  = len(methods)
        bar_w = 0.8 / n_m
        x = np.arange(n_bm)

        fig, ax = plt.subplots(figsize=(max(8, n_bm * 1.5), 5))

        for i, method in enumerate(methods):
            sub = df[df["method"] == method]
            vals = [int(sub[sub["benchmark"] == bm]["violations"].values[0]) if bm in sub["benchmark"].values else 0
                    for bm in benchmarks]
            offset = (i - n_m / 2 + 0.5) * bar_w
            ax.bar(x + offset, vals, width=bar_w * 0.9,
                   color=METHOD_COLORS[method],
                   label=METHOD_LABELS.get(method, method),
                   edgecolor="white", linewidth=0.5)

        ax.set_xticks(x)
        ax.set_xticklabels(benchmarks, rotation=30, ha="right")
        ax.set_ylabel("Violating Paths")
        ax.set_title("Setup Violation Count")
        ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.0), framealpha=0.8)
        fig.tight_layout()

        path = self.out / "violation_histogram.png"
        _save(fig, path)
        return path

    # ------------------------------------------------------------------
    def summary_radar(self, df: pd.DataFrame) -> Path:
        """Radar/spider chart comparing methods across 3 normalized metrics."""
        _apply_style()
        methods = [m for m in METHOD_COLORS if m in df["method"].unique()]
        agg = df.groupby("method")[["wns", "tns", "violations", "composite_score"]].mean()

        labels = ["−WNS", "−TNS", "−Violations", "Score"]
        n = len(labels)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
        ax.set_facecolor("white")

        for method in methods:
            if method not in agg.index:
                continue
            row = agg.loc[method]
            vals = [
                -row["wns"],
                -row["tns"],
                -row["violations"],
                -row["composite_score"],
            ]
            # Normalize to [0, 1]
            max_abs = max(abs(v) for v in vals) or 1.0
            vals_norm = [v / max_abs for v in vals]
            vals_norm += vals_norm[:1]
            ax.plot(angles, vals_norm, color=METHOD_COLORS[method],
                    label=METHOD_LABELS.get(method, method))
            ax.fill(angles, vals_norm, color=METHOD_COLORS[method], alpha=0.08)

        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        ax.set_title("Method Comparison (normalized, higher=better)", pad=20)
        ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), framealpha=0.8)
        fig.tight_layout()

        path = self.out / "summary_radar.png"
        _save(fig, path)
        return path

    # ------------------------------------------------------------------
    def pareto_plot(self, df: pd.DataFrame, method: str = "choa") -> Path:
        """WNS vs violations Pareto scatter for a given method."""
        _apply_style()
        sub = df[df["method"] == method]
        fig, ax = plt.subplots(figsize=(7, 5))

        sc = ax.scatter(
            sub["violations"], sub["wns"],
            c=sub["composite_score"],
            cmap="RdYlGn_r", s=80, edgecolors="gray", linewidths=0.5, alpha=0.85,
        )
        cbar = fig.colorbar(sc, ax=ax, shrink=0.8)
        cbar.set_label("Composite Score")

        for _, row in sub.iterrows():
            ax.annotate(
                row["benchmark"],
                (row["violations"], row["wns"]),
                fontsize=7, xytext=(4, 4), textcoords="offset points",
            )

        ax.set_xlabel("Violating Paths")
        ax.set_ylabel("WNS (ns)")
        ax.set_title(f"Pareto View — {METHOD_LABELS.get(method, method)}")
        fig.tight_layout()

        path = self.out / f"pareto_{method}.png"
        _save(fig, path)
        return path

    # ------------------------------------------------------------------
    def runtime_comparison(self, df: pd.DataFrame) -> Path:
        """Horizontal bar chart of total runtime per method."""
        _apply_style()
        methods = [m for m in METHOD_COLORS if m in df["method"].unique()]
        runtimes = [df[df["method"] == m]["runtime_s"].sum() for m in methods]
        labels = [METHOD_LABELS.get(m, m) for m in methods]
        colors = [METHOD_COLORS[m] for m in methods]

        fig, ax = plt.subplots(figsize=(7, 3.5))
        bars = ax.barh(labels, runtimes, color=colors, edgecolor="white")
        for bar, val in zip(bars, runtimes):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}s", va="center", fontsize=9)
        ax.set_xlabel("Total Runtime (s)")
        ax.set_title("Runtime Comparison Across Methods")
        ax.set_xlim(0, max(runtimes) * 1.3 if runtimes else 1)
        fig.tight_layout()

        path = self.out / "runtime_comparison.png"
        _save(fig, path)
        return path

    # ------------------------------------------------------------------
    def per_benchmark_summary(self, df: pd.DataFrame) -> Path:
        """Multi-panel figure: WNS + violations side by side per benchmark."""
        _apply_style()
        benchmarks = df["benchmark"].unique()
        methods    = [m for m in METHOD_COLORS if m in df["method"].unique()]
        n_bm = len(benchmarks)
        n_m  = len(methods)

        fig, axes = plt.subplots(1, 2, figsize=(max(12, n_bm * 2.5), 5))
        bar_w = 0.8 / n_m
        x = np.arange(n_bm)

        for i, method in enumerate(methods):
            sub = df[df["method"] == method]
            offset = (i - n_m / 2 + 0.5) * bar_w
            wns_vals  = [sub[sub["benchmark"] == bm]["wns"].values[0] if bm in sub["benchmark"].values else 0.0 for bm in benchmarks]
            viol_vals = [int(sub[sub["benchmark"] == bm]["violations"].values[0]) if bm in sub["benchmark"].values else 0 for bm in benchmarks]
            label = METHOD_LABELS.get(method, method)
            color = METHOD_COLORS[method]
            axes[0].bar(x + offset, wns_vals,  width=bar_w * 0.9, color=color, label=label, edgecolor="white")
            axes[1].bar(x + offset, viol_vals, width=bar_w * 0.9, color=color, label=label, edgecolor="white")

        for ax, title, ylabel in zip(axes, ["WNS (ns)", "Violations"], ["WNS (ns)", "Count"]):
            ax.set_xticks(x)
            ax.set_xticklabels(benchmarks, rotation=35, ha="right", fontsize=8)
            ax.set_ylabel(ylabel)
            ax.set_title(title)
            ax.axhline(0, color="black", linewidth=0.6, linestyle="--")

        axes[0].legend(loc="lower right", framealpha=0.8, fontsize=8)
        fig.suptitle("Per-Benchmark Summary", fontsize=13, fontweight="bold", y=1.01)
        fig.tight_layout()

        path = self.out / "per_benchmark_summary.png"
        _save(fig, path)
        return path

    # ------------------------------------------------------------------
    def choa_parameter_heatmap(self, results: List[dict]) -> Path:
        """Heatmap of best ChOA parameter values across benchmarks."""
        _apply_style()
        rows = []
        for r in results:
            if r.get("method") not in ("choa", "choa_memory") or "best_params" not in r:
                continue
            row = {"benchmark": r["benchmark"]}
            row.update(r["best_params"])
            rows.append(row)

        if not rows:
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.text(0.5, 0.5, "No ChOA parameter data", ha="center", va="center", transform=ax.transAxes)
            path = self.out / "choa_parameter_heatmap.png"
            _save(fig, path)
            return path

        df = pd.DataFrame(rows).set_index("benchmark")
        from src.swarm.population import Population
        param_names = Population.PARAM_NAMES
        cols = [c for c in param_names if c in df.columns]
        heat_df = df[cols].astype(float)

        # Normalize each column to [0,1]
        normalized = (heat_df - heat_df.min()) / (heat_df.max() - heat_df.min() + 1e-10)

        fig, ax = plt.subplots(figsize=(max(8, len(cols) * 0.9), max(4, len(rows) * 0.5 + 1)))
        im = ax.imshow(normalized.values, aspect="auto", cmap="YlOrRd")
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Normalized Value")

        ax.set_xticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(len(normalized)))
        ax.set_yticklabels(normalized.index, fontsize=8)
        ax.set_title("ChOA Best Parameter Heatmap")
        fig.tight_layout()

        path = self.out / "choa_parameter_heatmap.png"
        _save(fig, path)
        return path

    def generate_all(self, results: List[dict]) -> List[Path]:
        """Generate every plot and return list of saved paths."""
        df = pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (list, dict))} for r in results])
        paths = []

        # Convergence — one per benchmark
        benchmarks = df["benchmark"].unique() if not df.empty else []
        for bm in benchmarks:
            try:
                paths.append(self.convergence_plot(results, benchmark=bm))
            except Exception as e:
                log.warning("convergence_plot failed for %s: %s", bm, e)

        if not df.empty:
            for fn in [self.wns_comparison, self.tns_comparison, self.violation_histogram,
                       self.summary_radar, self.runtime_comparison, self.per_benchmark_summary]:
                try:
                    paths.append(fn(df))
                except Exception as e:
                    log.warning("%s failed: %s", fn.__name__, e)

            for method in ["choa", "choa_memory"]:
                if method in df["method"].unique():
                    try:
                        paths.append(self.pareto_plot(df, method=method))
                    except Exception as e:
                        log.warning("pareto_plot failed for %s: %s", method, e)

        try:
            paths.append(self.choa_parameter_heatmap(results))
        except Exception as e:
            log.warning("parameter_heatmap failed: %s", e)

        return paths

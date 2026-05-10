#!/usr/bin/env python3
"""
sta-choa: Chimp Optimization Algorithm over OpenSTA for VLSI STA.
CLI entry point.
"""
import json
import logging
import sys
import time
from pathlib import Path

import click
import yaml

# ── path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.sta_engine.opensta_adapter import OpenSTAAdapter
from src.io.dataset_registry import DatasetRegistry
from src.eval.experiment_runner import ExperimentRunner
from src.eval.baseline_comparison import BaselineComparison
from src.eval.metric_aggregator import MetricAggregator
from src.viz.plots import TimingPlotter
from src.report.readme_updater import READMEUpdater

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("sta-choa")


def _load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def _build_registry(cfg: dict) -> DatasetRegistry:
    registry = DatasetRegistry()
    manifests = cfg.get("manifests", [])
    if not manifests:
        log.warning("No manifests in config — using synthetic benchmark only.")
        manifests = ["benchmarks/manifests/synthetic.yaml"]
    for mp in manifests:
        try:
            registry.load_manifest(mp)
        except FileNotFoundError as e:
            log.warning("%s", e)
    return registry


def _build_adapter(cfg: dict) -> OpenSTAAdapter:
    workdir = cfg.get("workdir", "outputs/sta_work")
    binary  = cfg.get("opensta_binary", "sta")
    timeout = cfg.get("sta_timeout", 300)
    return OpenSTAAdapter(binary=binary, workdir=workdir, timeout=timeout)


# ── CLI ───────────────────────────────────────────────────────────────────────
@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging")
def cli(verbose: bool):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command("run")
@click.option("--config", "-c", default="configs/default.yaml", show_default=True)
def cmd_run(config: str):
    """Quick single-benchmark ChOA run for interactive testing."""
    cfg = _load_config(config)
    registry = _build_registry(cfg)
    adapter  = _build_adapter(cfg)

    if not registry.benchmarks:
        log.error("No valid benchmarks found. Check manifests.")
        sys.exit(1)

    bm = registry.benchmarks[0]
    log.info("Quick run on benchmark: %s", bm["name"])

    runner = ExperimentRunner(cfg, adapter)
    results = runner.run_benchmark(bm)

    for r in results:
        click.echo(
            f"  [{r['method']:15s}] WNS={r['wns']:+.4f}  TNS={r['tns']:+.4f}  "
            f"violations={r['violations']:3d}  score={r['composite_score']:.4f}  "
            f"runtime={r['runtime_s']:.2f}s"
            + ("  [SIMULATED]" if r.get("simulated") else "")
        )


@cli.command("eval")
@click.option("--config", "-c", default="configs/default.yaml", show_default=True)
@click.option("--out-dir", default="outputs", show_default=True)
def cmd_eval(config: str, out_dir: str):
    """Full evaluation: all benchmarks × all methods → CSV + figures."""
    cfg      = _load_config(config)
    registry = _build_registry(cfg)
    adapter  = _build_adapter(cfg)

    if not registry.benchmarks:
        log.error("No valid benchmarks. Exiting.")
        sys.exit(1)

    summary = registry.summary()
    log.info("Registry: %d benchmarks (%d skipped) | families: %s",
             summary["total"], summary["skipped"], summary["families"])

    runner    = ExperimentRunner(cfg, adapter)
    results   = runner.run_all(registry)

    aggregator = MetricAggregator(output_dir=f"{out_dir}/tables")
    aggregator.save_results(results)
    aggregator.save_convergence(results)
    aggregator.save_eco_actions(results)
    aggregator.save_best_params(results)

    plotter  = TimingPlotter(output_dir=f"{out_dir}/figures")
    fig_paths = plotter.generate_all(results)
    log.info("Generated %d figures", len(fig_paths))

    comparison = BaselineComparison(results)
    imp_table  = comparison.improvement_table()
    meth_table = comparison.method_summary()

    click.echo("\n=== Method Summary ===")
    click.echo(meth_table.to_string(index=False))
    if not imp_table.empty:
        click.echo("\n=== WNS/TNS Improvement vs Baseline ===")
        click.echo(imp_table.to_string(index=False))

    _update_readme(results, fig_paths, registry.skipped)
    log.info("Evaluation complete. Outputs in %s/", out_dir)


@cli.command("ablation")
@click.option("--config", "-c", default="configs/ablation.yaml", show_default=True)
@click.option("--out-dir", default="outputs", show_default=True)
def cmd_ablation(config: str, out_dir: str):
    """Ablation study: baseline vs random vs ChOA vs ChOA+memory."""
    cfg      = _load_config(config)
    cfg["methods"] = ["baseline", "random", "choa", "choa_memory"]
    registry = _build_registry(cfg)
    adapter  = _build_adapter(cfg)

    if not registry.benchmarks:
        log.error("No valid benchmarks. Exiting.")
        sys.exit(1)

    runner   = ExperimentRunner(cfg, adapter)
    results  = runner.run_all(registry)

    aggregator = MetricAggregator(output_dir=f"{out_dir}/tables")
    aggregator.save_results(results, filename="ablation_results.csv")
    aggregator.save_convergence(results)

    plotter  = TimingPlotter(output_dir=f"{out_dir}/figures")
    fig_paths = plotter.generate_all(results)

    comparison = BaselineComparison(results)
    click.echo("\n=== Ablation — Method Summary ===")
    click.echo(comparison.method_summary().to_string(index=False))

    _update_readme(results, fig_paths, registry.skipped)


@cli.command("report")
@click.option("--results-csv", default="outputs/tables/all_results.csv", show_default=True)
@click.option("--figures-dir", default="outputs/figures", show_default=True)
def cmd_report(results_csv: str, figures_dir: str):
    """Regenerate README sections from saved CSV results."""
    aggregator = MetricAggregator()
    try:
        df = aggregator.load_results(results_csv)
    except FileNotFoundError:
        log.error("Results CSV not found: %s — run eval first", results_csv)
        sys.exit(1)

    results = df.to_dict(orient="records")
    fig_paths = list(Path(figures_dir).glob("*.png"))
    _update_readme(results, fig_paths, [])
    log.info("README updated from saved results.")


def _update_readme(results: list, fig_paths: list, skipped: list) -> None:
    updater = READMEUpdater("README.md")
    simulated = any(r.get("simulated") for r in results)
    updater.update_results_table(results)
    updater.update_figures(fig_paths)
    updater.update_summary(skipped, simulated)
    updater.update_commands()
    log.info("README.md updated")


if __name__ == "__main__":
    cli()

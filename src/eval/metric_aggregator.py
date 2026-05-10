"""Aggregates experiment results to CSV tables."""
import csv
import json
import logging
from pathlib import Path
from typing import List

import pandas as pd

log = logging.getLogger(__name__)


class MetricAggregator:
    def __init__(self, output_dir: str = "outputs/tables"):
        self.out = Path(output_dir)
        self.out.mkdir(parents=True, exist_ok=True)

    def save_results(self, results: List[dict], filename: str = "all_results.csv") -> Path:
        flat = []
        for r in results:
            row = {k: v for k, v in r.items() if not isinstance(v, (list, dict))}
            flat.append(row)
        df = pd.DataFrame(flat)
        path = self.out / filename
        df.to_csv(path, index=False)
        log.info("Saved results: %s (%d rows)", path, len(df))
        return path

    def save_convergence(self, results: List[dict]) -> Path:
        """Save convergence curves for ChOA runs."""
        rows = []
        for r in results:
            if "convergence" not in r:
                continue
            for i, val in enumerate(r["convergence"]):
                rows.append({
                    "benchmark": r["benchmark"],
                    "method": r["method"],
                    "iteration": i + 1,
                    "fitness": val,
                })
        df = pd.DataFrame(rows)
        path = self.out / "convergence.csv"
        df.to_csv(path, index=False)
        log.info("Saved convergence: %s", path)
        return path

    def save_eco_actions(self, results: List[dict]) -> Path:
        rows = []
        for r in results:
            if "eco_suggestions" not in r:
                continue
            for action in r["eco_suggestions"]:
                rows.append({"benchmark": r["benchmark"], **action})
        df = pd.DataFrame(rows)
        path = self.out / "eco_actions.csv"
        df.to_csv(path, index=False)
        log.info("Saved ECO actions: %s", path)
        return path

    def save_best_params(self, results: List[dict]) -> Path:
        rows = []
        for r in results:
            if "best_params" not in r:
                continue
            row = {"benchmark": r["benchmark"], "method": r["method"]}
            row.update(r["best_params"])
            rows.append(row)
        df = pd.DataFrame(rows)
        path = self.out / "best_params.csv"
        df.to_csv(path, index=False)
        log.info("Saved best params: %s", path)
        return path

    def load_results(self, filename: str = "all_results.csv") -> pd.DataFrame:
        path = self.out / filename
        if not path.exists():
            raise FileNotFoundError(f"Results file not found: {path}")
        return pd.read_csv(path)

    def to_markdown_table(self, df: pd.DataFrame, cols: list = None) -> str:
        sub = df[cols] if cols else df
        return sub.to_markdown(index=False)

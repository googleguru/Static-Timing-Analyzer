"""Computes improvement statistics between methods."""
import pandas as pd
import numpy as np
from typing import List


class BaselineComparison:
    def __init__(self, results: List[dict]):
        self.df = pd.DataFrame(results)

    def improvement_table(self) -> pd.DataFrame:
        """Return per-benchmark WNS/TNS improvement of ChOA vs baseline."""
        rows = []
        for bm in self.df["benchmark"].unique():
            sub = self.df[self.df["benchmark"] == bm]
            base = sub[sub["method"] == "baseline"]
            choa = sub[sub["method"] == "choa"]
            if base.empty or choa.empty:
                continue
            b_wns = base["wns"].iloc[0]
            c_wns = choa["wns"].iloc[0]
            b_tns = base["tns"].iloc[0]
            c_tns = choa["tns"].iloc[0]
            b_viol = base["violations"].iloc[0]
            c_viol = choa["violations"].iloc[0]
            rows.append({
                "benchmark": bm,
                "family": sub["family"].iloc[0],
                "baseline_wns": round(b_wns, 4),
                "choa_wns": round(c_wns, 4),
                "wns_delta": round(c_wns - b_wns, 4),
                "baseline_tns": round(b_tns, 4),
                "choa_tns": round(c_tns, 4),
                "tns_delta": round(c_tns - b_tns, 4),
                "baseline_violations": int(b_viol),
                "choa_violations": int(c_viol),
                "violation_delta": int(c_viol - b_viol),
            })
        return pd.DataFrame(rows)

    def method_summary(self) -> pd.DataFrame:
        """Aggregate metrics per method across all benchmarks."""
        return (
            self.df.groupby("method")[["wns", "tns", "violations", "composite_score", "runtime_s"]]
            .agg({"wns": "mean", "tns": "mean", "violations": "mean",
                  "composite_score": "mean", "runtime_s": "sum"})
            .round(4)
            .reset_index()
        )

    def best_method_per_benchmark(self) -> pd.DataFrame:
        idx = self.df.groupby("benchmark")["composite_score"].idxmin()
        return self.df.loc[idx][["benchmark", "method", "wns", "tns", "violations", "composite_score"]].reset_index(drop=True)

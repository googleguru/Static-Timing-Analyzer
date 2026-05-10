"""Timing-centric objective functions computed from STAReport."""
import math
import numpy as np
from dataclasses import dataclass
from typing import Optional

from src.sta_engine.report_parser import STAReport


@dataclass
class TimingScore:
    wns: float = 0.0
    tns: float = 0.0
    violations: int = 0
    path_criticality: float = 0.0
    uncertainty_penalty: float = 0.0
    composite: float = 0.0


class TimingObjectives:
    """
    Computes scalar timing objectives from an STAReport.
    All objectives are normalized so lower = better.
    """

    def __init__(
        self,
        w_wns: float = 1.0,
        w_tns: float = 0.5,
        w_violations: float = 0.3,
        w_criticality: float = 0.2,
        w_uncertainty: float = 0.1,
        wns_budget: float = 5.0,
        tns_budget: float = 50.0,
        violation_budget: int = 100,
    ):
        self.w_wns = w_wns
        self.w_tns = w_tns
        self.w_violations = w_violations
        self.w_criticality = w_criticality
        self.w_uncertainty = w_uncertainty
        self.wns_budget = wns_budget
        self.tns_budget = tns_budget
        self.violation_budget = violation_budget

    def compute(self, report: STAReport, params: dict) -> TimingScore:
        score = TimingScore(
            wns=report.wns,
            tns=report.tns,
            violations=report.violating_paths,
        )

        # WNS normalized: negative slack is bad; saturate at budget
        wns_norm = max(0.0, -report.wns) / self.wns_budget

        # TNS normalized
        tns_norm = max(0.0, -report.tns) / max(self.tns_budget, 1e-6)

        # Violation count normalized
        viol_norm = report.violating_paths / max(self.violation_budget, 1)

        # Path criticality: ratio of violating to total paths
        total = max(report.total_paths, 1)
        score.path_criticality = report.violating_paths / total
        crit_norm = score.path_criticality

        # Uncertainty penalty: penalize large clock_uncertainty exploration
        clock_unc = params.get("clock_uncertainty", 0.0)
        score.uncertainty_penalty = clock_unc * 0.5
        unc_norm = score.uncertainty_penalty

        score.composite = (
            self.w_wns * wns_norm
            + self.w_tns * tns_norm
            + self.w_violations * viol_norm
            + self.w_criticality * crit_norm
            + self.w_uncertainty * unc_norm
        )
        return score

    def wns_score(self, report: STAReport) -> float:
        return max(0.0, -report.wns)

    def tns_score(self, report: STAReport) -> float:
        return max(0.0, -report.tns)

    def violation_count(self, report: STAReport) -> int:
        return report.violating_paths

    def path_criticality_ranking(self, report: STAReport) -> list:
        """Return paths sorted by criticality (most negative slack first)."""
        return sorted(report.paths, key=lambda p: p.slack)

    def endpoint_criticality_map(self, report: STAReport) -> dict:
        """Return {endpoint: normalized_criticality} in [0,1]."""
        slacks = [p.slack for p in report.paths if p.endpoint]
        if not slacks:
            return {}
        min_s = min(slacks)
        max_s = max(slacks)
        span = max_s - min_s or 1.0
        return {
            p.endpoint: (max_s - p.slack) / span
            for p in report.paths if p.endpoint
        }

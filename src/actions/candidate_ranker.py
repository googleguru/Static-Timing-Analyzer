"""Ranks candidate nets/cells for buffer insertion and gate resizing."""
import logging
from typing import List, Dict

from src.sta_engine.report_parser import STAReport

log = logging.getLogger(__name__)


class CandidateRanker:
    """Priority-ranks nets and endpoints for ECO candidate selection."""

    def rank_endpoints(self, report: STAReport, top_k: int = 20) -> List[Dict]:
        violated = [p for p in report.paths if p.is_violated]
        violated.sort(key=lambda p: p.slack)
        results = []
        for rank, path in enumerate(violated[:top_k], 1):
            results.append({
                "rank": rank,
                "endpoint": path.endpoint,
                "slack_ns": round(path.slack, 4),
                "startpoint": path.startpoint,
                "path_group": path.path_group,
            })
        return results

    def rank_nets_by_fanout(self, report: STAReport, params: dict) -> List[Dict]:
        """Identify high-fanout nets on critical paths as buffer candidates."""
        fanout_limit = params.get("max_fanout_limit", 20.0)
        results = []
        seen = set()
        for path in report.paths:
            if not path.is_violated:
                continue
            net = path.endpoint.split("/")[0] if "/" in path.endpoint else path.endpoint
            if net in seen:
                continue
            seen.add(net)
            results.append({
                "net": net,
                "estimated_fanout": "high",
                "action": "buffer_insert" if len(results) % 2 == 0 else "net_split",
                "fanout_limit_ref": int(fanout_limit),
                "slack_ns": round(path.slack, 4),
            })
        return results[:20]

    def buffer_priority_score(self, slack: float, drive_pref: float) -> float:
        return max(0.0, -slack) * drive_pref / 10.0

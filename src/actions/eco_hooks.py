"""ECO suggestion hooks — generate candidate timing improvement actions."""
import logging
from dataclasses import dataclass, field
from typing import List

from src.sta_engine.report_parser import STAReport, TimingPath

log = logging.getLogger(__name__)


@dataclass
class ECOAction:
    action_type: str       # "buffer_insert" | "gate_upsize" | "net_split" | "constraint_relax"
    target: str            # net or cell name
    priority: float        # 0.0 (low) — 1.0 (high)
    slack_gain_estimate: float = 0.0
    metadata: dict = field(default_factory=dict)


class ECOHooks:
    """
    Generates prioritized ECO action suggestions from STA results.
    NOTE: These are suggestions only. Actual ECO requires legal implementation
    by a place-and-route tool and subsequent re-run of STA to confirm improvement.
    """

    def __init__(
        self,
        min_slack_threshold: float = 0.0,
        max_suggestions: int = 20,
    ):
        self.min_slack_threshold = min_slack_threshold
        self.max_suggestions = max_suggestions

    def suggest(self, report: STAReport, params: dict) -> List[ECOAction]:
        drive_pref  = params.get("buffer_drive_pref", 5.0)
        fanout_lim  = params.get("max_fanout_limit", 20.0)
        crit_thresh = params.get("criticality_threshold", 0.1)
        ep_weight   = params.get("endpoint_weight", 1.0)

        violated = [p for p in report.paths if p.is_violated]
        violated.sort(key=lambda p: p.slack)

        actions: List[ECOAction] = []
        for path in violated[:self.max_suggestions]:
            priority = min(1.0, abs(path.slack) / max(abs(report.wns), 1e-6))
            if priority < crit_thresh:
                continue

            # Suggest buffer insertion on endpoint net
            if path.endpoint:
                actions.append(ECOAction(
                    action_type="buffer_insert",
                    target=path.endpoint,
                    priority=round(priority * ep_weight, 4),
                    slack_gain_estimate=round(abs(path.slack) * 0.3, 4),
                    metadata={"drive_strength": int(drive_pref), "fanout_limit": int(fanout_lim)},
                ))

            # Suggest gate upsizing on startpoint
            if path.startpoint:
                actions.append(ECOAction(
                    action_type="gate_upsize",
                    target=path.startpoint,
                    priority=round(priority * 0.8, 4),
                    slack_gain_estimate=round(abs(path.slack) * 0.2, 4),
                    metadata={"path_group": path.path_group},
                ))

        actions.sort(key=lambda a: -a.priority)
        log.debug("ECOHooks: %d suggestions generated", len(actions))
        return actions[:self.max_suggestions]

    def to_table(self, actions: List[ECOAction]) -> list:
        return [
            {
                "type": a.action_type,
                "target": a.target,
                "priority": a.priority,
                "est_slack_gain_ns": a.slack_gain_estimate,
            }
            for a in actions
        ]

"""Constraint perturbation hooks for sensitivity exploration."""
import logging
from typing import List, Tuple

log = logging.getLogger(__name__)


class ConstraintPerturbation:
    """
    Explores timing sensitivity by perturbing SDC constraints.
    Returns candidate perturbation vectors for further STA evaluation.
    NOTE: Perturbations are for analysis only — not applied to files.
    """

    def __init__(self, base_period_ns: float, step_ns: float = 0.1, n_steps: int = 5):
        self.base_period_ns = base_period_ns
        self.step_ns = step_ns
        self.n_steps = n_steps

    def period_sweep(self) -> List[float]:
        """Generate clock period variants around base for sensitivity analysis."""
        deltas = [self.step_ns * i for i in range(-self.n_steps, self.n_steps + 1)]
        return [self.base_period_ns + d for d in deltas if self.base_period_ns + d > 0]

    def uncertainty_sweep(self, base_unc: float = 0.0) -> List[float]:
        """Sweep clock uncertainty values."""
        return [max(0.0, base_unc + 0.05 * i) for i in range(self.n_steps + 1)]

    def input_delay_sweep(self, base_delay: float, frac: float = 0.2) -> List[float]:
        deltas = [-frac, -frac/2, 0.0, frac/2, frac]
        return [max(0.0, base_delay + d) for d in deltas]

    def candidate_margins(self, params: dict) -> List[Tuple[str, float]]:
        """Return list of (label, slack_margin) pairs from ChOA params."""
        margin = params.get("slack_margin", 0.0)
        unc    = params.get("clock_uncertainty", 0.0)
        return [
            ("base",              0.0),
            ("choa_margin",       margin),
            ("choa_uncertainty",  unc * -1.0),
            ("combined",          margin - unc * 0.5),
        ]

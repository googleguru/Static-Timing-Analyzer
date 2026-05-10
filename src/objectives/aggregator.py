"""Multi-objective aggregation and Pareto front utilities."""
import numpy as np
from typing import List, Tuple


class ObjectiveAggregator:
    """Aggregates multiple timing metrics into a single fitness value."""

    def __init__(self, weights: dict):
        self.weights = weights

    def aggregate(self, metrics: dict) -> float:
        total = 0.0
        for key, w in self.weights.items():
            val = metrics.get(key, 0.0)
            total += w * max(0.0, float(val))
        return total

    def pareto_front(self, objective_matrix: np.ndarray) -> np.ndarray:
        """
        Identify Pareto-optimal solutions (minimization, 2D objectives).
        Returns boolean mask of non-dominated solutions.
        """
        n = len(objective_matrix)
        dominated = np.zeros(n, dtype=bool)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if np.all(objective_matrix[j] <= objective_matrix[i]) and \
                   np.any(objective_matrix[j] < objective_matrix[i]):
                    dominated[i] = True
                    break
        return ~dominated

    def normalize_objectives(self, matrix: np.ndarray) -> np.ndarray:
        mins = matrix.min(axis=0)
        maxs = matrix.max(axis=0)
        span = np.where(maxs - mins > 1e-10, maxs - mins, 1.0)
        return (matrix - mins) / span

"""Population initialization and management for ChOA."""
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Individual:
    position: np.ndarray
    fitness: float = float("inf")
    role: str = "follower"
    history: list = field(default_factory=list)


class Population:
    """
    Maintains the swarm population with bounded positions.

    Parameter vector dimensions (configurable via config):
      0  path_count_limit       [10, 500]
      1  criticality_threshold  [0.0, 1.0]
      2  slack_margin           [-0.5, 0.5]  ns
      3  endpoint_weight        [0.1, 10.0]
      4  path_weight            [0.1, 10.0]
      5  buffer_drive_pref      [1.0, 10.0]
      6  max_fanout_limit       [1.0, 50.0]
      7  clock_uncertainty      [0.0, 0.5]   ns
      8  setup_path_weight      [0.1, 10.0]
      9  exploration_factor     [0.1, 2.0]
    """

    LOWER = np.array([10.0,  0.0,  -0.5, 0.1, 0.1, 1.0,  1.0,  0.0, 0.1, 0.1])
    UPPER = np.array([500.0, 1.0,   0.5, 10.0, 10.0, 10.0, 50.0, 0.5, 10.0, 2.0])
    DIM   = 10

    PARAM_NAMES = [
        "path_count_limit",
        "criticality_threshold",
        "slack_margin",
        "endpoint_weight",
        "path_weight",
        "buffer_drive_pref",
        "max_fanout_limit",
        "clock_uncertainty",
        "setup_path_weight",
        "exploration_factor",
    ]

    def __init__(self, size: int, rng: np.random.Generator):
        self.size = size
        self.rng = rng
        self.individuals: list[Individual] = []
        self._best_fitness_history: list = []
        self._memory: Optional[np.ndarray] = None  # best ever seen

    def initialize(self) -> None:
        self.individuals = []
        for _ in range(self.size):
            pos = self.rng.uniform(self.LOWER, self.UPPER)
            self.individuals.append(Individual(position=pos.copy()))

    def clip(self, position: np.ndarray) -> np.ndarray:
        return np.clip(position, self.LOWER, self.UPPER)

    def positions(self) -> np.ndarray:
        return np.stack([ind.position for ind in self.individuals])

    def fitnesses(self) -> np.ndarray:
        return np.array([ind.fitness for ind in self.individuals])

    def best(self) -> Individual:
        return min(self.individuals, key=lambda x: x.fitness)

    def record_best(self) -> None:
        self._best_fitness_history.append(self.best().fitness)
        best_pos = self.best().position
        if self._memory is None or self.best().fitness < (self._memory_fitness or float("inf")):
            self._memory = best_pos.copy()
            self._memory_fitness = self.best().fitness

    @property
    def convergence_curve(self) -> list:
        return list(self._best_fitness_history)

    def inject_memory(self, idx: int = 0) -> None:
        """Replace individual at idx with historically best position."""
        if self._memory is not None:
            self.individuals[idx].position = self._memory.copy()

    def decode(self, position: np.ndarray) -> dict:
        """Decode a raw position vector to named parameter dict."""
        return {
            name: float(position[i])
            for i, name in enumerate(self.PARAM_NAMES)
        }

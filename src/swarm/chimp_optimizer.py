"""
Chimp Optimization Algorithm (ChOA) core.

Reference:
  Khishe, M., & Mosavi, M. R. (2020). Chimp optimization algorithm.
  Expert Systems with Applications, 149, 113338.
  https://doi.org/10.1016/j.eswa.2020.113338

Roles: Attacker (best), Barrier (2nd), Chaser (3rd), Driver (4th).
Position update uses chaotic logistic map for b1/b2 coefficients.
"""

import numpy as np
import logging
from typing import Callable, Optional

from .population import Population
from .roles import assign_roles, get_leader_positions, ChimpRole

log = logging.getLogger(__name__)


def _logistic_map(x: float, r: float = 3.99) -> float:
    """Chaotic logistic map to improve diversity."""
    return r * x * (1.0 - x)


class ChimpOptimizer:
    """
    ChOA optimizer that calls a fitness function (STA evaluation) per candidate.

    Parameters
    ----------
    fitness_fn   : callable(position) -> float (lower is better)
    pop_size     : swarm size
    max_iter     : maximum iterations
    seed         : random seed for reproducibility
    use_memory   : inject best-ever position at start of each iteration
    a_start/end  : linear range for coefficient 'a'
    """

    def __init__(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        pop_size: int = 20,
        max_iter: int = 50,
        seed: int = 42,
        use_memory: bool = False,
        a_start: float = 2.5,
        a_end: float = 0.5,
    ):
        self.fitness_fn = fitness_fn
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.seed = seed
        self.use_memory = use_memory
        self.a_start = a_start
        self.a_end = a_end

        self.rng = np.random.default_rng(seed)
        self.pop = Population(size=pop_size, rng=self.rng)

        self._chaos_x = self.rng.uniform(0.01, 0.99)
        self.convergence_curve: list = []
        self.best_position: Optional[np.ndarray] = None
        self.best_fitness: float = float("inf")

    def _chaos(self) -> float:
        self._chaos_x = _logistic_map(self._chaos_x)
        return self._chaos_x

    def _evaluate_all(self) -> None:
        for ind in self.pop.individuals:
            ind.fitness = self.fitness_fn(ind.position)

    def _update_positions(self, iteration: int) -> None:
        # Linearly decreasing a
        a = self.a_start - (self.a_start - self.a_end) * (iteration / self.max_iter)

        fitnesses = self.pop.fitnesses()
        roles = assign_roles(fitnesses)
        leaders = get_leader_positions(roles, self.pop.positions())

        x_att = leaders.get(ChimpRole.ATTACKER)
        x_bar = leaders.get(ChimpRole.BARRIER)
        x_cha = leaders.get(ChimpRole.CHASER)
        x_dri = leaders.get(ChimpRole.DRIVER)

        if any(v is None for v in [x_att, x_bar, x_cha, x_dri]):
            return  # not enough individuals to assign all roles

        for i, ind in enumerate(self.pop.individuals):
            if roles[i] != ChimpRole.FOLLOWER:
                continue  # leaders keep their position

            x = ind.position

            # Chaotic b1, b2 in [0, 2]
            b1 = 2.0 * self._chaos()
            b2 = 2.0 * self._chaos()
            r1 = self.rng.uniform()
            r2 = self.rng.uniform()

            def _step(x_leader: np.ndarray) -> np.ndarray:
                D = np.abs(b1 * x_leader - b2 * x)
                c = 2.0 * r1
                return x_leader - a * c * D

            x1 = _step(x_att)
            x2 = _step(x_bar)
            x3 = _step(x_cha)
            x4 = _step(x_dri)

            new_pos = (x1 + x2 + x3 + x4) / 4.0
            ind.position = self.pop.clip(new_pos)

    def optimize(self) -> dict:
        log.info("ChOA: pop=%d iter=%d seed=%d memory=%s", self.pop_size, self.max_iter, self.seed, self.use_memory)

        self.pop.initialize()
        if self.use_memory:
            self.pop.inject_memory(idx=0)

        self._evaluate_all()
        self.pop.record_best()

        for t in range(self.max_iter):
            self._update_positions(t)
            self._evaluate_all()
            self.pop.record_best()

            best = self.pop.best()
            if best.fitness < self.best_fitness:
                self.best_fitness = best.fitness
                self.best_position = best.position.copy()

            self.convergence_curve.append(self.best_fitness)
            log.debug("Iter %03d | best_fitness=%.6f", t + 1, self.best_fitness)

        self.convergence_curve = self.pop.convergence_curve

        return {
            "best_fitness": self.best_fitness,
            "best_params": self.pop.decode(self.best_position),
            "convergence": self.convergence_curve,
            "iterations": self.max_iter,
            "pop_size": self.pop_size,
        }

"""Chimp role definitions and assignment logic for ChOA."""
from enum import Enum
import numpy as np


class ChimpRole(Enum):
    ATTACKER = "attacker"   # best fitness — leads the hunt
    BARRIER  = "barrier"    # 2nd best
    CHASER   = "chaser"     # 3rd best
    DRIVER   = "driver"     # 4th best
    FOLLOWER = "follower"   # rest of population


def assign_roles(fitnesses: np.ndarray) -> list:
    """
    Return list of ChimpRole for each individual, sorted by fitness (lower is better).
    Top-4 get named roles; rest are FOLLOWERs.
    """
    # argsort ascending (lower fitness = better for minimization)
    order = np.argsort(fitnesses)
    roles = [ChimpRole.FOLLOWER] * len(fitnesses)
    role_map = [ChimpRole.ATTACKER, ChimpRole.BARRIER, ChimpRole.CHASER, ChimpRole.DRIVER]
    for idx, role in zip(order[:4], role_map):
        roles[idx] = role
    return roles


def get_leader_positions(
    roles: list,
    positions: np.ndarray,
) -> dict:
    """Return {role: position_vector} for the four named leaders."""
    leaders = {}
    for i, role in enumerate(roles):
        if role != ChimpRole.FOLLOWER:
            leaders[role] = positions[i].copy()
    return leaders

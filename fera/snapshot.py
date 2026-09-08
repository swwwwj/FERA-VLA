"""Replay-backed checkpoint: correctness reference, not fast simulator serialization.

A checkpoint includes fixed initial identity and executed prefix. Restore resets and
replays the prefix, reconstructing controller/task state through public stepping.
Its O(prefix length) cost is explicit. Fast direct-state snapshots require separate
controller/RNG/task serialization and may only replace this after equivalence tests.
"""
from dataclasses import dataclass
import copy
import numpy as np

@dataclass
class ReplaySnapshot:
    identity: dict
    actions: list
    state: np.ndarray

def capture(adapter):
    return ReplaySnapshot(copy.deepcopy(adapter.identity),
                          [a.copy() for a in adapter.actions], adapter.state())

def restore(adapter, snapshot, tolerance=1e-5):
    if adapter.identity != snapshot.identity:
        raise ValueError("Snapshot belongs to a different environment configuration")
    obs = adapter.reset()
    for action in snapshot.actions:
        obs, _, _, _ = adapter.step(action)
    state = adapter.state()
    error = float(np.max(np.abs(state - snapshot.state)))
    if not np.isfinite(error) or error > tolerance:
        raise RuntimeError(f"Replay snapshot mismatch: {error}")
    return obs

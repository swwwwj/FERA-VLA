# FERA-VLA pilot

Remote-first engineering framework for simulator-grounded functional equivalence.
Scope: original LIBERO, two pilot tasks, determinism before collection.
No pilot findings or successful trajectories are claimed by this scaffold.

## Quick start

Use an isolated Python environment, then:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/00_check_system.py
```

LIBERO source: https://github.com/Lifelong-Robot-Learning/LIBERO
The upstream revision is tracked in configs/libero.lock.json, not vendored.
Simulator installation is isolated from the other research projects.

## Protocol

1. Audit environment and install original LIBERO.
2. Inventory tasks; test both cameras, proprioception and seven-dimensional actions.
3. Validate initial replay and intermediate snapshots (10 repetitions, state 1e-5,
   outcome agreement 100%). Simulator state alone is not a complete snapshot:
   controller goals, task state, counters and RNG require validation.
4. Replay at least five successful demonstrations per task and select five states each.
5. Generate 16 bounded, unique candidates per state plus reference; identical suffix.
6. Extract outcomes using task-specific physical predicates; unknown fields remain
   unknown and produce ambiguous labels.
7. Split by trajectory; calibrate distances on training/calibration data only.
8. Compare action-only and state-conditioned models over three training seeds.

See reports/status.md for actual completed work and remaining stage acceptance.
configs/decision.yaml records provisional preregistered decision thresholds.
Do not interpret random-action smoke tests or unit tests as feasibility evidence.

## Synchronization

Remote is the code authoring source; synchronize every coherent tested change to
the local checkout and push that commit to GitHub. Credentials, raw demonstrations,
rendered observations, checkpoints, third-party source and runtime logs are excluded.
The sync script exports tracked remote HEAD, verifies file hashes, preserves local
uncommitted work by refusing to run when dirty, and pushes without force.

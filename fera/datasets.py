import hashlib
import json
import os
import tempfile
from pathlib import Path
import numpy as np

def grouped_split(rows, seed=17):
    """Split trajectory groups separately inside each task; retain all sibling states."""
    groups = {}
    for row in rows:
        groups.setdefault(str(row["task_id"]), set()).add(str(row["trajectory_id"]))
    rng = np.random.default_rng(seed)
    assignment = {}
    for task, group in sorted(groups.items()):
        ids = sorted(group)
        if len(ids) < 3:
            raise ValueError("Need >=3 trajectories per task for train/validation/test")
        rng.shuffle(ids)
        n = max(1, len(ids)//5)
        for split, selected in (("test", ids[:n]), ("validation", ids[n:2*n]), ("train", ids[2*n:])):
            for trajectory in selected:
                assignment[(task, trajectory)] = split
    return [{**r, "split": assignment[(str(r["task_id"]), str(r["trajectory_id"]))]} for r in rows]

def stable_id(metadata):
    return hashlib.sha256(json.dumps(metadata, sort_keys=True, allow_nan=False).encode()).hexdigest()[:24]

def write_once(path, record):
    """Exclusive create prevents silent overwrite; a completed record is immutable."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(record, indent=2, allow_nan=False)
    fd, temporary = tempfile.mkstemp(prefix=".record-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        # Atomic publication with no overwrite, unlike os.replace.
        os.link(temporary, path)
    finally:
        os.unlink(temporary)

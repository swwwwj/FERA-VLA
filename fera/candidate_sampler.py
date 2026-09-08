from dataclasses import dataclass
import numpy as np

@dataclass
class Candidate:
    candidate_id: str
    kind: str
    actions: np.ndarray
    seed: int
    attempts: int
    clipped: bool = False

def sample(reference, low, high, seed, count=16, small_sigma=.02,
           medium_sigma=.10, sparse_sigma=.15, max_attempts=2000):
    """Reject out-of-bounds and duplicate proposals; reference is not counted."""
    ref = np.asarray(reference, dtype=float)
    lo, hi = np.asarray(low), np.asarray(high)
    if ref.ndim != 2 or ref.shape[1] != 7 or not np.isfinite(ref).all():
        raise ValueError("Expected finite [H,7] reference")
    if ref.shape[0] < 2 or count < 4 or count % 4:
        raise ValueError("Need H>=2 and a positive multiple of four candidates")
    if lo.shape != (7,) or hi.shape != (7,) or np.any(lo >= hi):
        raise ValueError("Expected valid seven-dimensional bounds")
    if np.any(ref < lo) or np.any(ref > hi):
        raise ValueError("Reference exceeds controller bounds")
    if min(small_sigma, medium_sigma, sparse_sigma) <= 0:
        raise ValueError("Proposal scales must be positive")
    rng = np.random.default_rng(seed)
    def bounded_noise(base, lower, upper, sigma):
        # Coordinate rejection samples the truncated Gaussian without clipping;
        # avoids exponential rejection when gripper remains at a hard boundary.
        value = base + rng.normal(0, sigma, base.shape)
        for _ in range(max_attempts):
            bad = (value < lower) | (value > upper)
            if not np.any(bad):
                return value
            value[bad] = (base + rng.normal(0, sigma, base.shape))[bad]
        raise RuntimeError("Bounded Gaussian failed to converge")
    seen = {ref.tobytes()}
    result = []
    for kind in ("small", "medium", "sparse", "temporal"):
        accepted = 0
        for attempt in range(1, max_attempts + 1):
            value = ref.copy()
            if kind in ("small", "medium"):
                value = bounded_noise(ref, lo, hi, small_sigma if kind == "small" else medium_sigma)
            elif kind == "sparse":
                dim = int(rng.integers(7))
                value[:, dim] = bounded_noise(ref[:, dim], lo[dim], hi[dim], sparse_sigma)
            else:
                # Local replacement / temporal gripper event, including constant references.
                idx = int(rng.integers(len(ref)))
                value[idx:, 6] = rng.uniform(lo[6], hi[6])
            key = value.tobytes()
            if np.any(value < lo) or np.any(value > hi) or key in seen:
                continue
            seen.add(key)
            result.append(Candidate(f"{seed}-{kind}-{accepted}", kind, value, seed, attempt))
            accepted += 1
            if accepted == count // 4:
                break
        else:
            raise RuntimeError(f"Cannot sample {kind} within bounds; adjust proposal scales")
    return result

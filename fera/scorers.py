import numpy as np

def distances(a, b, scale=None):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 7:
        raise ValueError("Action blocks must have equal [H,7] shape")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Nonfinite action")
    d = a-b
    denom = np.linalg.norm(a)*np.linalg.norm(b)
    cosine = 0.0 if not np.any(a) and not np.any(b) else (1.0 if denom == 0 else float(1-np.sum(a*b)/denom))
    result = dict(l1=float(np.mean(np.abs(d))), l2=float(np.linalg.norm(d)),
                  cosine=cosine, max_step=float(np.linalg.norm(d, axis=1).max()),
                  gripper_change=float(np.mean((a[:,6]>0)!=(b[:,6]>0))))
    if scale is not None:
        scale = np.asarray(scale)
        if scale.shape != (7,) or np.any(scale <= 0):
            raise ValueError("Training-only normalization scale must be positive [7]")
        result["normalized_l2"] = float(np.linalg.norm(d/scale))
    return result

def make_mlp(input_dim, hidden=128):
    from torch import nn
    return nn.Sequential(nn.Linear(input_dim, hidden), nn.ReLU(),
                         nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))

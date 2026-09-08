import numpy as np
from .outcome_extractor import Outcome

def label(reference: Outcome, candidate: Outcome, pose_tolerance=.01, progress_tolerance=.05):
    if reference.status != "ok" or candidate.status != "ok":
        return "ambiguous"
    if not reference.task_success or reference.safety_violation is not False:
        return "ambiguous"
    required = ("subgoal_progress", "object_pose", "grasp_or_contact_state",
                "safety_violation", "recoverability")
    if any(getattr(x, k) is None for x in (reference, candidate) for k in required):
        return "ambiguous"
    if not candidate.task_success or candidate.safety_violation or not candidate.recoverability:
        return "harmful"
    if abs(reference.subgoal_progress - candidate.subgoal_progress) > progress_tolerance:
        return "ambiguous"
    # Position-only strictness; quaternion-aware orientation comparison is a future task hook.
    a, b = np.asarray(reference.object_pose), np.asarray(candidate.object_pose)
    if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        return "ambiguous"
    if np.max(np.abs(a-b), initial=0) <= pose_tolerance and reference.grasp_or_contact_state == candidate.grasp_or_contact_state:
        return "equivalent_strict"
    return "equivalent_task"

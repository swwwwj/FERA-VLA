import numpy as np
from .outcome_extractor import Outcome

def pose_errors(a,b):
    """Object pose rows are [x,y,z,qw,qx,qy,qz]; quaternion sign is immaterial."""
    a,b=np.asarray(a,float),np.asarray(b,float)
    if a.ndim==1: a=a[None,:]
    if b.ndim==1: b=b[None,:]
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=7 or len(a)==0:
        raise ValueError("Expected nonempty matching [objects,7] poses")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Nonfinite pose")
    qa,qb=a[:,3:],b[:,3:]
    na,nb=np.linalg.norm(qa,axis=1),np.linalg.norm(qb,axis=1)
    if np.any(np.abs(na-1)>.01) or np.any(np.abs(nb-1)>.01):
        raise ValueError("Quaternion must be normalized")
    dots=np.abs(np.sum(qa*qb,axis=1)/(na*nb))
    return float(np.linalg.norm(a[:,:3]-b[:,:3],axis=1).max()),float((2*np.arccos(np.clip(dots,0,1))).max())

def label(reference: Outcome, candidate: Outcome, pose_tolerance=.01,
          progress_tolerance=.05, angle_tolerance=.1):
    if reference.status!="ok" or candidate.status!="ok":
        return "ambiguous"
    if not reference.task_success or reference.safety_violation is not False or reference.recoverability is not True:
        return "ambiguous"
    required=("subgoal_progress","object_pose","grasp_or_contact_state",
              "safety_violation","recoverability")
    if any(getattr(x,k) is None for x in (reference,candidate) for k in required):
        return "ambiguous"
    if not np.isfinite([reference.subgoal_progress,candidate.subgoal_progress]).all():
        return "ambiguous"
    try:
        position,angle=pose_errors(reference.object_pose,candidate.object_pose)
    except ValueError:
        return "ambiguous"
    if not candidate.task_success or candidate.safety_violation or not candidate.recoverability:
        return "harmful"
    if abs(reference.subgoal_progress-candidate.subgoal_progress)>progress_tolerance:
        return "ambiguous"
    if position<=pose_tolerance and angle<=angle_tolerance and reference.grasp_or_contact_state==candidate.grasp_or_contact_state:
        return "equivalent_strict"
    return "equivalent_task"

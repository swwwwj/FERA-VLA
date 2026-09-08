from dataclasses import asdict, dataclass
from typing import Optional

@dataclass
class Outcome:
    task_success: bool
    reward_sum: float
    steps: int
    subgoal_progress: Optional[float] = None
    object_pose: Optional[list] = None
    grasp_or_contact_state: Optional[str] = None
    safety_violation: Optional[bool] = None
    recoverability: Optional[bool] = None
    status: str = "ok"
    def to_dict(self):
        return asdict(self)

# Task-specific progress and safety predicates must be validated before labels.
# Missing observations are unknown; they must never be silently encoded as zero.

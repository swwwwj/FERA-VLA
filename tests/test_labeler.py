import unittest
from fera.labeler import label
from fera.outcome_extractor import Outcome

def outcome(**kwargs):
    values=dict(task_success=True,reward_sum=1,steps=100,subgoal_progress=1.,
                object_pose=[[0,0,0,1,0,0,0]],grasp_or_contact_state="released",
                safety_violation=False,recoverability=True)
    values.update(kwargs)
    return Outcome(**values)

class LabelTests(unittest.TestCase):
    def test_quaternion_sign(self):
        self.assertEqual(label(outcome(),outcome(object_pose=[[0,0,0,-1,0,0,0]])),"equivalent_strict")
    def test_invalid_quaternion(self):
        self.assertEqual(label(outcome(),outcome(object_pose=[[0,0,0,0,0,0,0]])),"ambiguous")
    def test_harm(self):
        self.assertEqual(label(outcome(),outcome(task_success=False,recoverability=False)),"harmful")
    def test_unrecoverable_reference(self):
        self.assertEqual(label(outcome(recoverability=False),outcome()),"ambiguous")

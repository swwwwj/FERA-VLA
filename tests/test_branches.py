import tempfile
import unittest
from pathlib import Path
import numpy as np
from fera.branches import collect
from fera.candidate_sampler import Candidate
from fera.datasets import write_once
from fera.outcome_extractor import Outcome
from fera.snapshot import capture

class ToyAdapter:
    def __init__(self):
        self.identity={"seed":17}
        self.reset()
    def reset(self):
        self.actions=[]
        self.value=np.zeros(7)
        return {}
    def step(self, action):
        self.actions.append(np.asarray(action).copy())
        self.value+=action
        return {},0.,False,{}
    def state(self):
        return self.value.copy()
    def success(self):
        return False

class BranchTests(unittest.TestCase):
    def test_unapproved_gate_stops_before_step(self):
        with tempfile.TemporaryDirectory() as d:
            gate=Path(d)/"gate.json"
            write_once(gate,{"passed":True,"fingerprint":"test","collection_approved":False})
            env=ToyAdapter()
            with self.assertRaises(RuntimeError):
                collect(env,capture(env),[],[],{},None,gate,"test",Path(d)/"samples")
            self.assertEqual(len(env.actions),0)

    def test_common_snapshot_suffix_and_resume(self):
        with tempfile.TemporaryDirectory() as d:
            gate=Path(d)/"gate.json"
            write_once(gate,{"passed":True,"fingerprint":"test","collection_approved":True})
            env=ToyAdapter()
            env.step(np.ones(7))
            snap=capture(env)
            candidates=[Candidate(str(i),"test",np.ones((2,7))*i,17,1) for i in (1,2)]
            suffix=np.ones((1,7))*3
            def extract(adapter,trace,block_steps):
                return Outcome(False,sum(t["reward"] for t in trace),len(trace))
            records=collect(env,snap,candidates,suffix,{"state_id":1},extract,gate,"test",Path(d)/"samples")
            np.testing.assert_array_equal(records[0]["trace"][-1]["state"],np.ones(7)*6)
            np.testing.assert_array_equal(records[1]["trace"][-1]["state"],np.ones(7)*8)
            again=collect(env,snap,candidates,suffix,{"state_id":1},extract,gate,"test",Path(d)/"samples")
            self.assertEqual(records,again)

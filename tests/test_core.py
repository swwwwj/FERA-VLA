import tempfile
import unittest
from pathlib import Path
import numpy as np
from fera.candidate_sampler import sample
from fera.datasets import grouped_split, write_once
from fera.labeler import label
from fera.outcome_extractor import Outcome
from fera.scorers import distances
from fera.gates import require_gate

class CoreTests(unittest.TestCase):
    def test_sampler_reproducible_balanced_bounded(self):
        ref = np.zeros((8,7))
        a, b = [sample(ref, -np.ones(7), np.ones(7), 42) for _ in range(2)]
        self.assertEqual(len(a), 16)
        self.assertEqual(len({c.actions.tobytes() for c in a}), 16)
        for x,y in zip(a,b):
            np.testing.assert_array_equal(x.actions,y.actions)
            self.assertTrue(np.all(np.abs(x.actions)<=1))
        self.assertEqual({k:sum(c.kind==k for c in a) for k in ("small","medium","sparse","temporal")},
                         dict(small=4,medium=4,sparse=4,temporal=4))
    def test_sampler_bad_reference(self):
        with self.assertRaises(ValueError):
            sample(np.ones((8,7))*2, -np.ones(7), np.ones(7), 42)
    def test_split_no_sibling_leakage(self):
        rows=[dict(task_id=t,trajectory_id=i,state_id=s) for t in range(2) for i in range(5) for s in range(3)]
        result=grouped_split(rows)
        for t in range(2):
            for i in range(5):
                self.assertEqual(len({r["split"] for r in result if r["task_id"]==t and r["trajectory_id"]==i}),1)
        self.assertEqual({r["split"] for r in result},{"train","test","validation"})
    def test_unknown_outcomes_not_labels(self):
        self.assertEqual(label(Outcome(True,1,100),Outcome(True,1,100)),"ambiguous")
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"record.json"
            write_once(p,{"id":1})
            with self.assertRaises(FileExistsError):
                write_once(p,{"id":2})
    def test_stale_gate(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"gate.json"
            write_once(p,{"passed":True,"fingerprint":"old"})
            with self.assertRaises(RuntimeError):
                require_gate(p,"new")
    def test_zero_cosine(self):
        self.assertEqual(distances(np.zeros((8,7)),np.zeros((8,7)))["cosine"],0)
        self.assertEqual(distances(np.zeros((8,7)),np.ones((8,7)))["cosine"],1)

if __name__ == "__main__":
    unittest.main()

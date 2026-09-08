import unittest
import numpy as np
from fera.snapshot import capture, restore

class ToyAdapter:
    def __init__(self):
        self.identity={"seed":17}
        self.reset()
    def reset(self):
        self.value=np.zeros(2)
        self.actions=[]
        return self.value.copy()
    def step(self,action):
        self.value+=action
        self.actions.append(action.copy())
        return self.value.copy(),0,False,{}
    def state(self):
        return self.value.copy()

class SnapshotContractTests(unittest.TestCase):
    def test_restore_after_mutation_and_repeat(self):
        env=ToyAdapter()
        env.step(np.array([1.,2.]))
        snap=capture(env)
        for _ in range(3):
            env.step(np.array([3.,4.]))
            restore(env,snap)
            np.testing.assert_array_equal(env.state(),[1,2])
    def test_wrong_identity_fails(self):
        env=ToyAdapter()
        snap=capture(env)
        env.identity={"seed":18}
        with self.assertRaises(ValueError):
            restore(env,snap)

"""Original LIBERO integration. Imports are lazy so core tests do not require a GPU."""
import os
from pathlib import Path
import numpy as np

def configure_paths():
    import yaml
    root = Path(__file__).resolve().parents[1]
    upstream = root / "third_party/LIBERO/libero/libero"
    if not upstream.is_dir():
        raise FileNotFoundError("Install pinned official LIBERO source first")
    cfg = root / ".local/libero"
    cfg.mkdir(parents=True, exist_ok=True)
    os.environ["LIBERO_CONFIG_PATH"] = str(cfg)
    data = root / "data/raw"
    data.mkdir(parents=True, exist_ok=True)
    values = dict(benchmark_root=str(upstream), bddl_files=str(upstream/"bddl_files"),
                  init_states=str(upstream/"init_files"), assets=str(upstream/"assets"),
                  datasets=str(data))
    (cfg/"config.yaml").write_text(yaml.safe_dump(values))
    os.environ.setdefault("MUJOCO_GL", "egl")

class LiberoAdapter:
    def __init__(self, suite="libero_goal", task_id=0, seed=20260908, init_id=0, image_size=128):
        configure_paths()
        from libero.libero import benchmark, get_libero_path
        from libero.libero.envs import OffScreenRenderEnv
        self.suite = benchmark.get_benchmark_dict()[suite]()
        self.task = self.suite.get_task(task_id)
        self.initial_state = np.asarray(self.suite.get_task_init_states(task_id)[init_id]).copy()
        self.seed = seed
        self.env = OffScreenRenderEnv(
            bddl_file_name=str(Path(get_libero_path("bddl_files"))/self.task.problem_folder/self.task.bddl_file),
            camera_heights=image_size, camera_widths=image_size,
            camera_names=["agentview", "robot0_eye_in_hand"])
        self.low, self.high = (np.asarray(x) for x in self.env.env.action_spec)
        if self.low.shape != (7,):
            raise RuntimeError("Expected seven-dimensional OSC_POSE action")
        self.actions = []
        self.identity = dict(suite=suite, task_id=task_id, seed=seed, init_id=init_id, image_size=image_size)

    def reset(self):
        import random
        random.seed(self.seed)
        np.random.seed(self.seed)
        self.env.seed(self.seed)
        # Bypass upstream unbounded RandomizationError retry loop.
        self.env.env.reset()
        obs = self.env.set_init_state(self.initial_state.copy())
        self.actions = []
        return obs

    def step(self, action):
        action = np.asarray(action, dtype=float)
        if action.shape != (7,) or not np.isfinite(action).all():
            raise ValueError("Action must be finite [7]")
        if np.any(action < self.low) or np.any(action > self.high):
            raise ValueError("Out-of-bounds action")
        result = self.env.step(action)
        self.actions.append(action.copy())
        return result

    def state(self):
        return np.asarray(self.env.get_sim_state()).copy()

    def success(self):
        return bool(self.env.check_success())

    def close(self):
        self.env.close()

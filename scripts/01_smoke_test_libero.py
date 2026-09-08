import argparse
import json
from pathlib import Path
import numpy as np
from fera.env_adapter import LiberoAdapter

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task-id", type=int, default=0)
    p.add_argument("--suite", default="libero_goal")
    p.add_argument("--steps", type=int, default=100)
    args = p.parse_args()
    if args.steps < 100:
        p.error("Acceptance requires at least 100 steps")
    out = Path("outputs/smoke")
    out.mkdir(parents=True, exist_ok=True)
    env = LiberoAdapter(args.suite, args.task_id)
    try:
        obs = env.reset()
        rng = np.random.default_rng(20260908)
        frames = []
        for step in range(args.steps):
            action = rng.uniform(-.05,.05,7)
            action[6] = -1
            obs, reward, done, info = env.step(action)
            if not np.isfinite(env.state()).all() or not np.isfinite(reward):
                raise RuntimeError("Nonfinite simulator state or reward")
            for key in ("agentview_image","robot0_eye_in_hand_image"):
                im = np.asarray(obs[key])
                if im.shape != (128,128,3) or im.dtype != np.uint8:
                    raise RuntimeError(f"Invalid image {key}: {im.shape} {im.dtype}")
                if step % max(1,args.steps//10) == 0:
                    import imageio.v2 as imageio
                    imageio.imwrite(out/f"{key}-{step:04}.png",im[::-1])
                    frames.append(str(out/f"{key}-{step:04}.png"))
            for key in ("robot0_joint_pos","robot0_eef_pos","robot0_gripper_qpos"):
                if not np.isfinite(obs[key]).all():
                    raise RuntimeError(f"Invalid proprioception: {key}")
        report = dict(passed=True,steps=args.steps,task=env.task.name,identity=env.identity,
                      action_low=env.low.tolist(),action_high=env.high.tolist(),
                      final_success=env.success(),frames=frames,
                      note="Random actions test engineering only; not a successful expert rollout.")
        (out/"result.json").write_text(json.dumps(report,indent=2))
        print(json.dumps(report,indent=2))
    finally:
        env.close()
if __name__ == "__main__":
    main()

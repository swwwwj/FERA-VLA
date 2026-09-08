import argparse
import json
import subprocess
from pathlib import Path
import numpy as np
from fera.env_adapter import LiberoAdapter
from fera.snapshot import capture, restore
from fera.gates import fingerprint

def rollout(env, actions):
    states, rewards, success, images = [], [], [], []
    for action in actions:
        obs, reward, _, _ = env.step(action)
        states.append(env.state())
        rewards.append(reward)
        success.append(env.success())
        images.append(np.concatenate([obs[k].reshape(-1) for k in ("agentview_image","robot0_eye_in_hand_image")]))
    return np.asarray(states), np.asarray(rewards), np.asarray(success), np.asarray(images)

def compare(a,b):
    errors = [np.asarray(x,dtype=float)-np.asarray(y,dtype=float) for x,y in zip(a,b)]
    return dict(state_max=float(np.abs(errors[0]).max()),state_mse=float(np.square(errors[0]).mean()),
                reward_max=float(np.abs(errors[1]).max()),
                success_agreement=float(np.mean(a[2]==b[2])),
                rgb_max=float(np.abs(errors[3]).max()),rgb_mse=float(np.square(errors[3]).mean()))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--suite",default="libero_goal")
    p.add_argument("--task-id",type=int,default=0)
    p.add_argument("--repeats",type=int,default=10)
    args=p.parse_args()
    if args.repeats<10: p.error("Need >=10 repetitions")
    env=LiberoAdapter(args.suite,args.task_id)
    out=Path("outputs/determinism")
    out.mkdir(parents=True,exist_ok=True)
    try:
        rng=np.random.default_rng(20260908)
        actions=rng.uniform(-.05,.05,(40,7))
        actions[:,6]=-1
        env.reset()
        initial=rollout(env,actions)
        checks=[]
        for i in range(args.repeats):
            env.reset()
            checks.append(dict(mode="initial",repeat=i,**compare(initial,rollout(env,actions))))
        env.reset()
        rollout(env,actions[:20])
        snap=capture(env)
        reference=rollout(env,actions[20:])
        for i in range(args.repeats):
            restore(env,snap)
            checks.append(dict(mode="replay_snapshot",repeat=i,**compare(reference,rollout(env,actions[20:]))))
        passed=all(x["state_max"]<=1e-5 and x["reward_max"]==0 and x["success_agreement"]==1 and x["rgb_max"]==0 for x in checks)
        revision=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
        result=dict(passed=passed,fingerprint=fingerprint(env.identity,revision),
                    identity=env.identity,source_revision=revision,checks=checks,
                    scope="Random-action replay only. Contact-rich expert snapshots remain unvalidated.",
                    collection_approved=False)
        (out/"result.json").write_text(json.dumps(result,indent=2))
        Path("reports/determinism.md").write_text("# Replay determinism\n\n"+json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,indent=2))
        if not passed: raise SystemExit(1)
    finally:
        env.close()
if __name__=="__main__":
    main()

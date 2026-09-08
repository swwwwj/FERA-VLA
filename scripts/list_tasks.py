import json
from pathlib import Path
from fera.env_adapter import configure_paths

def main():
    configure_paths()
    from libero.libero import benchmark
    suite = benchmark.get_benchmark_dict()["libero_goal"]()
    rows=[dict(suite="libero_goal",task_id=i,name=suite.get_task(i).name,
               language=suite.get_task(i).language) for i in range(suite.n_tasks)]
    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/task_inventory.json").write_text(json.dumps(rows,indent=2))
    print(json.dumps(rows,indent=2))
if __name__=="__main__":
    main()

"""Read-only environment audit; no dependency installation or GPU allocation."""
import datetime
import json
import platform
import shutil
import subprocess
from pathlib import Path

def run(command):
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=30)
        return {"command": command, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"command": command, "error": repr(exc)}

def main():
    root = Path(__file__).resolve().parents[1]
    commands = [["uname","-a"], ["lscpu"], ["free","-h"], ["df","-h","."],
                ["nvidia-smi"], ["nvcc","--version"], ["gcc","--version"],
                ["cmake","--version"], ["git","--version"],
                ["git","-C","third_party/LIBERO","rev-parse","HEAD"]]
    report = {"timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "python": platform.python_version(), "disk_free_gb": shutil.disk_usage(root).free/1e9,
              "tools": {x: shutil.which(x) for x in ("conda","mamba","git","gcc","cmake")},
              "checks": [run(c) for c in commands]}
    out = root/"outputs/logs"
    out.mkdir(parents=True, exist_ok=True)
    (out/"system_check.json").write_text(json.dumps(report, indent=2))
    (out/"system_check.txt").write_text("\n\n".join(json.dumps(x, indent=2) for x in report["checks"]))
    (root/"reports").mkdir(exist_ok=True)
    (root/"reports/environment.md").write_text(
        "# Environment audit\n\nGenerated: " + report["timestamp_utc"] +
        "\n\nPython: " + report["python"] +
        "\n\nFree disk GB: %.1f\n" % report["disk_free_gb"] +
        "\nRaw audit: outputs/logs/system_check.json (local, excluded from Git).\n" +
        "\nGPU visibility is not proof of availability. No GPU reservation has been made.\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()

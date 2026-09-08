#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${CONDA_EXE:?Set CONDA_EXE to an existing conda executable}"
export PYTHONNOUSERSITE=1
if [[ ! -x .venv/bin/python ]]; then
  "$CONDA_EXE" create -y -p "$PWD/.venv" python=3.10 pip
fi
if [[ ! -d third_party/LIBERO/.git ]]; then
  git clone https://github.com/Lifelong-Robot-Learning/LIBERO.git third_party/LIBERO
fi
revision=$(.venv/bin/python -s -c 'import json; print(json.load(open("configs/libero.lock.json"))["commit"])')
actual=$(git -C third_party/LIBERO rev-parse HEAD)
[[ "$actual" == "$revision" ]] || { echo "LIBERO revision mismatch; refusing automatic checkout"; exit 1; }
.venv/bin/python -s -m pip install -r requirements-sim.txt -e . -e third_party/LIBERO
.venv/bin/python -s -m pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python -s -m pip check
.venv/bin/python -s -m pip freeze > outputs/logs/requirements-resolved.txt

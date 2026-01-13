#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VEV="$ROOT/.venv"
python3 -m venv "$VEV"
source "$VEV/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT/requirements.txt"
echo "Checking Ollama at http://127.0.0.1:11434/api/tags ..."
if curl -sSf "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
  echo "Ollama reachable"
else
  echo "Ollama not reachable. Please start Ollama locally before pulling models."
fi
echo "Bootstrap complete. To run a dry-run:"
echo "source $VEV/bin/activate && python -m leetcode_bot.run"

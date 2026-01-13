import subprocess
from pathlib import Path
from typing import Tuple
from .config import ROOT


def current_branch():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT)
        return out.decode().strip()
    except Exception:
        return "main"


def repo_clean() -> bool:
    out = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)
    return len(out.strip()) == 0


def commit_and_push(path: Path, message: str, branch: str = None) -> Tuple[bool, str]:
    branch = branch or current_branch()
    try:
        subprocess.check_output(["git", "add", str(path)], cwd=ROOT)
        subprocess.check_output(["git", "add", "README.md"], cwd=ROOT)
        subprocess.check_output(["git", "commit", "-m", message], cwd=ROOT)
        out = subprocess.check_output(["git", "push", "origin", branch], cwd=ROOT, stderr=subprocess.STDOUT)
        return True, out.decode()
    except subprocess.CalledProcessError as e:
        return False, e.output.decode()

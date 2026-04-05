import subprocess
from pathlib import Path
from typing import Iterable, Tuple

from .config import ROOT


def _run_git(args, check: bool = True):
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if check and completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            completed.args,
            output=completed.stdout,
            stderr=completed.stderr,
        )
    return completed


def current_branch():
    try:
        out = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        return out.stdout.strip()
    except Exception:
        return "main"


def repo_clean() -> bool:
    out = _run_git(["status", "--porcelain"])
    return len(out.stdout.strip()) == 0


def _relpath(path: Path) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(ROOT.resolve()))
    except Exception:
        return str(candidate)


def commit_and_push(paths: Iterable[Path], message: str, branch: str = None) -> Tuple[bool, str]:
    branch = branch or current_branch()
    try:
        staged_paths = [_relpath(path) for path in paths]
        _run_git(["add", "-A", "--", *staged_paths])
        staged_check = _run_git(["diff", "--cached", "--quiet"], check=False)
        if staged_check.returncode == 0:
            return False, "no staged changes for targeted files"
        if staged_check.returncode not in (0, 1):
            detail = (staged_check.stdout or "") + (staged_check.stderr or "")
            return False, detail.strip() or "unable to inspect staged diff"
        _run_git(["commit", "-m", message])
        push_result = _run_git(["push", "origin", branch])
        detail = (push_result.stdout or push_result.stderr or "").strip() or f"pushed to {branch}"
        return True, detail
    except subprocess.CalledProcessError as e:
        out = (e.output or "") + (e.stderr or "")
        return False, out.strip()

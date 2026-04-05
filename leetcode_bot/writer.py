import json
from pathlib import Path
from datetime import datetime

from .config import DRY_RUN_PREVIEWS_DIR, ROOT


def write_output(problem: dict, generated: dict, run_at: datetime, slot: dict = None, dry_run: bool = False):
    y = run_at.year
    mm = f"{run_at.month:02d}"
    day = run_at.date().isoformat()
    run_stamp = run_at.strftime("%Y-%m-%d_%H%M")
    slug = problem.get("slug") or "problem"
    if dry_run:
        base_root = DRY_RUN_PREVIEWS_DIR / day
    else:
        base_root = Path(ROOT) / "leetcode" / str(y) / mm
    base = base_root / f"{run_stamp}_{slug}"
    base.mkdir(parents=True, exist_ok=True)
    sol_path = base / "solution.py"
    notes_path = base / "notes.md"
    meta_path = base / "metadata.json"

    sol_path.write_text(generated.get("solution_py") or "")
    notes_path.write_text(generated.get("notes_md") or "")
    metadata = {
        "date": day,
        "run_at": run_at.isoformat(timespec="seconds"),
        "iso_week": run_at.isocalendar()[0:2],
        "model": generated.get("metadata", {}).get("model", None),
        "prompt_hash": generated.get("prompt_hash"),
        "retries": generated.get("attempts", 0),
        "validation_passed": generated.get("validation_passed", False),
        "selected_problem_id": problem.get("id"),
        "selected_title": problem.get("title"),
        "difficulty": problem.get("difficulty"),
        "tags": problem.get("tags"),
        "slot_id": slot.get("id") if slot else None,
        "scheduled_for": slot.get("scheduled_for") if slot else None,
        "run_mode": "dry-run" if dry_run else "normal",
    }
    meta_path.write_text(json.dumps(metadata, indent=2))
    return base

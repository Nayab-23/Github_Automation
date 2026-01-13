import json
from pathlib import Path
from datetime import date
from .config import ROOT


def write_output(problem: dict, generated: dict, run_date: date):
    y = run_date.year
    mm = f"{run_date.month:02d}"
    day = run_date.isoformat()
    slug = problem.get("slug")
    base = Path(ROOT) / "leetcode" / str(y) / mm / f"{day}_{slug}"
    base.mkdir(parents=True, exist_ok=True)
    sol_path = base / "solution.py"
    notes_path = base / "notes.md"
    meta_path = base / "metadata.json"

    sol_path.write_text(generated.get("solution_py") or "")
    notes_path.write_text(generated.get("notes_md") or "")
    metadata = {
        "date": day,
        "iso_week": run_date.isocalendar()[0:2],
        "model": generated.get("metadata", {}).get("model", None),
        "prompt_hash": generated.get("prompt_hash"),
        "retries": generated.get("attempts", 0),
        "validation_passed": generated.get("validation_passed", False),
        "selected_problem_id": problem.get("id"),
        "selected_title": problem.get("title"),
        "difficulty": problem.get("difficulty"),
        "tags": problem.get("tags"),
    }
    meta_path.write_text(json.dumps(metadata, indent=2))
    return base

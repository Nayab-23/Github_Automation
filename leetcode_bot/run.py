import hashlib
import fcntl
import sys
from contextlib import contextmanager

from .config import (
    LCB_BRANCH,
    LCB_DRY_RUN_USE_LLM,
    LCB_MODEL,
    LCB_NUM_PREDICT,
    LCB_OLLAMA_TIMEOUT,
    LCB_RUN_MODE,
    LOCK_PATH,
    README_PATH,
)
from .questions import pick_problem
from .generator import generate_solution
from .validator import py_compile_string
from .writer import write_output
from .git_ops import commit_and_push
from .indexer import update_readme
from .logging_utils import setup_logging
from .planner import find_due_slot, get_now, mark_slot, next_pending_slot, plan_for_day, schedule_summary, sync_schedule

logger = setup_logging("leetcode_bot")


@contextmanager
def run_lock():
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK_PATH.open("w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("another leetcode bot run is already in progress")
    try:
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _build_dry_run_solution(problem: dict, scheduled_for: str):
    title = problem.get("title") or "Untitled Problem"
    prompt_hash = hashlib.sha1(f"{title}:{scheduled_for}".encode()).hexdigest()
    solution = (
        '"""Dry-run preview generated without calling the LLM."""\n\n'
        "class Solution:\n"
        "    def solve(self):\n"
        f"        return {title!r}\n"
    )
    notes = (
        f"# Dry Run Preview\n\n"
        f"- Problem: {title}\n"
        f"- Scheduled for: {scheduled_for}\n"
        f"- Mode: dry-run\n"
        f"- Generation: stubbed preview\n"
    )
    return {
        "solution_py": solution,
        "notes_md": notes,
        "metadata": {
            "model": "dry-run-stub",
            "title": title,
            "difficulty": problem.get("difficulty"),
            "tags": problem.get("tags", []),
        },
        "prompt_hash": prompt_hash,
        "attempts": 0,
    }


def _generate(problem: dict, scheduled_for: str):
    if LCB_RUN_MODE == "dry-run" and not LCB_DRY_RUN_USE_LLM:
        return _build_dry_run_solution(problem, scheduled_for)
    return generate_solution(problem)


def main():
    try:
        with run_lock():
            return _main()
    except RuntimeError as exc:
        logger.warning(str(exc))
        return 0


def _main():
    now = get_now()
    today = now.date()
    logger.info("Running leetcode bot at %s", now.isoformat(timespec="seconds"))

    schedule = plan_for_day(today, now=now)
    schedule = sync_schedule(schedule, now)
    logger.info("Today's schedule: %s", schedule_summary(schedule))

    slot = find_due_slot(schedule, now)
    if not slot:
        upcoming = next_pending_slot(schedule)
        if upcoming:
            logger.info(
                "No slot due right now. Next pending slot is %s at %s.",
                upcoming.get("id"),
                upcoming.get("scheduled_for"),
            )
        else:
            logger.info("No pending slots remain for today.")
        return 0

    logger.info("Processing slot %s scheduled for %s", slot.get("id"), slot.get("scheduled_for"))
    dry_run = LCB_RUN_MODE == "dry-run"
    if not dry_run:
        schedule = mark_slot(
            schedule,
            slot["id"],
            "running",
            now,
            extra={"started_at": now.isoformat(timespec="seconds")},
        )

    problem = pick_problem(record_usage=not dry_run)
    if not problem:
        logger.error("No problems found. Exiting.")
        if not dry_run:
            mark_slot(schedule, slot["id"], "failed_no_problem", now, extra={"reason": "question bank is empty"})
        return 1

    logger.info("Selected problem: %s", problem.get("title"))
    logger.info(
        "Starting generation with model=%s num_predict=%s timeout=%ss",
        LCB_MODEL,
        LCB_NUM_PREDICT,
        LCB_OLLAMA_TIMEOUT,
    )
    try:
        generated = _generate(problem, slot.get("scheduled_for"))
    except Exception:
        logger.exception("Generation failed")
        if not dry_run:
            mark_slot(schedule, slot["id"], "failed_generation", now, extra={"reason": "generation raised an exception"})
        return 1
    logger.info("Generation finished after %s attempt(s)", int(generated.get("attempts", 0)) + 1)

    ok, err = py_compile_string(generated.get("solution_py") or "")
    generated["validation_passed"] = bool(ok)
    if not ok and not (dry_run and not LCB_DRY_RUN_USE_LLM):
        logger.error("Validation failed: %s", err)
        try:
            generated = generate_solution(problem)
            ok2, err2 = py_compile_string(generated.get("solution_py") or "")
            generated["validation_passed"] = bool(ok2)
            if not ok2:
                logger.error("Retry validation failed. Aborting without push.")
                if not dry_run:
                    mark_slot(schedule, slot["id"], "failed_validation", now, extra={"reason": err2})
                return 1
        except Exception:
            logger.exception("Retry generation failed")
            if not dry_run:
                mark_slot(schedule, slot["id"], "failed_generation", now, extra={"reason": "retry generation raised an exception"})
            return 1
    elif not ok:
        logger.error("Dry-run stub failed validation unexpectedly: %s", err)
        return 1

    outdir = write_output(problem, generated, now, slot=slot, dry_run=dry_run)
    if dry_run:
        logger.info("Dry-run preview written to %s", outdir)
        logger.info("Dry-run mode: skipping README update, git commit, and push")
        return 0

    logger.info("Wrote outputs to %s", outdir)
    update_readme()

    commit_msg = f"leetcode: {now.strftime('%Y-%m-%d %H:%M')} {problem.get('title')}"
    success, out = commit_and_push([outdir, README_PATH], commit_msg, branch=LCB_BRANCH)
    if not success:
        if out == "no staged changes for targeted files":
            logger.warning("Skipping commit because the staged diff is empty for targeted files.")
            mark_slot(
                schedule,
                slot["id"],
                "skipped_duplicate",
                now,
                extra={"path": str(outdir), "reason": out},
            )
            return 0
        logger.error("Commit or push failed: %s", out)
        mark_slot(
            schedule,
            slot["id"],
            "push_failed",
            now,
            extra={"path": str(outdir), "reason": out},
        )
        return 1

    finished_at = get_now()
    logger.info("Commit and push succeeded")
    mark_slot(
        schedule,
        slot["id"],
        "done",
        finished_at,
        extra={
            "path": str(outdir),
            "problem_id": problem.get("id"),
            "problem_title": problem.get("title"),
            "finished_at": finished_at.isoformat(timespec="seconds"),
        },
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

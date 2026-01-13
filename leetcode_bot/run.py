import sys
from datetime import date
from .logging_utils import setup_logging
from .planner import today_in_plan, ran_today, mark_ran, plan_for_week
from .questions import pick_problem
from .generator import generate_solution
from .validator import py_compile_string
from .writer import write_output
from .git_ops import commit_and_push
from .indexer import update_readme
from .config import LCB_RUN_MODE, LCB_BRANCH, LOGS_DIR

logger = setup_logging("leetcode_bot")


def main():
    today = date.today()
    logger.info(f"Running leetcode bot for {today.isoformat()}")
    plan = plan_for_week(today)
    logger.info(f"Week plan: {plan}")
    if not today_in_plan(today):
        logger.info("Today is not in weekly plan. Exiting.")
        return 0
    if ran_today(today):
        logger.info("Already ran today. Exiting.")
        return 0

    problem = pick_problem()
    if not problem:
        logger.error("No problems found. Exiting.")
        return 1

    logger.info(f"Selected problem: {problem.get('title')}")
    try:
        generated = generate_solution(problem)
    except Exception as e:
        logger.exception("Generation failed")
        return 1

    ok, err = py_compile_string(generated.get("solution_py") or "")
    generated["validation_passed"] = bool(ok)
    if not ok:
        logger.error(f"Validation failed: {err}")
        # retry once with feedback
        try:
            generated = generate_solution(problem)
            ok2, err2 = py_compile_string(generated.get("solution_py") or "")
            generated["validation_passed"] = bool(ok2)
            if not ok2:
                logger.error("Retry validation failed. Aborting without push.")
                mark_ran(today, {"status": "failed_validation"})
                return 1
        except Exception:
            logger.exception("Retry generation failed")
            mark_ran(today, {"status": "failed_generation"})
            return 1

    outdir = write_output(problem, generated, today)
    logger.info(f"Wrote outputs to {outdir}")
    update_readme()
    if LCB_RUN_MODE == "dry-run":
        logger.info("Dry-run mode: skipping git commit/push")
        mark_ran(today, {"status": "dry_run", "path": str(outdir)})
        return 0

    commit_msg = f"leetcode: {today.isoformat()} {problem.get('title')}"
    success, out = commit_and_push(outdir, commit_msg, branch=LCB_BRANCH)
    if not success:
        logger.error(f"Push failed: {out}")
        mark_ran(today, {"status": "push_failed", "path": str(outdir)})
        return 1

    logger.info("Commit and push succeeded")
    mark_ran(today, {"status": "ok", "path": str(outdir)})
    return 0


if __name__ == "__main__":
    sys.exit(main())

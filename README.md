# LeetCode Auto Practice + GitHub Pusher

This project runs on a Raspberry Pi and generates multiple LeetCode-style commits per day using a local Ollama model. The scheduler now persists a randomized daily plan to disk, spaces runs at least 45 minutes apart, skips missed slots instead of backfilling them, and pushes automatically after a successful commit.

## Behavior

- Default schedule: 3 to 8 commits per day.
- Active window: random slots between 09:00 and 22:00 local time.
- Minimum spacing: 45 minutes between scheduled runs.
- Persistent state: daily schedules are stored in `.state/schedules/YYYY-MM-DD.json`.
- Missed runs: old pending slots are marked `skipped_missed` and never replayed in a burst.
- Duplicate protection: the bot uses an exclusive lock, records slot state, avoids recently used problems, and skips empty staged diffs.
- Dry-run mode: evaluates scheduling and writes a preview under `.state/dry_run_previews` without touching the git repo.

## Configuration

Copy `.env.example` to `.env` and preserve your existing secrets, repo settings, and push configuration.

Key settings:

- `MIN_COMMITS_PER_DAY=3`
- `MAX_COMMITS_PER_DAY=8`
- `ACTIVE_HOURS_START=09:00`
- `ACTIVE_HOURS_END=22:00`
- `MIN_GAP_MINUTES=45`
- `DUE_GRACE_MINUTES=20`
- `RUNNING_STALE_MINUTES=180`
- `DRY_RUN=false`
- `LCB_RUN_MODE=normal`
- `LCB_DRY_RUN_USE_LLM=false`
- `LCB_OLLAMA_TIMEOUT=210`
- `LCB_NUM_PREDICT=160`

`LCB_NOW` is optional and useful only for local testing when you want to force the scheduler to evaluate a specific timestamp.

## Local Run

1. Create and activate the venv with `scripts/bootstrap.sh`.
2. Add problem blocks to `data/questions.txt`.
3. For a safe local smoke test, run `LCB_RUN_MODE=dry-run python -m leetcode_bot.run`.
4. If you want dry-run to call Ollama too, set `LCB_DRY_RUN_USE_LLM=true`.

## Raspberry Pi Deployment

1. SSH to the Pi and `cd ~/Github_Automation`.
2. Update the repo contents in place.
3. Preserve the existing `.env`, SSH keys, git remote, and branch setup.
4. Run `scripts/bootstrap.sh`.
5. Install the timer with `scripts/setup_systemd.sh`.
6. Verify the timer with `systemctl status leetcode-bot.timer`.
7. Inspect recent runs with `journalctl -u leetcode-bot.service -n 100 --no-pager`.

The service remains `systemd`-based. The timer now polls every 5 minutes; the Python scheduler decides whether a slot is actually due.

## Notes

- Solutions are LLM-assisted and only syntax-checked locally.
- On Raspberry Pi, the model now only has to return `solution.py`; concise notes are generated locally to reduce malformed JSON failures.
- If Ollama is unreachable, normal runs will fail fast and the slot will be recorded as failed.
- Generated solution folders now include the run time so multiple commits on the same day do not collide.

<!-- LCB:INDEX:START -->
## Generated Activity Snapshot

Last updated: 2026-05-03T03:12:25Z

Total solutions: 129

### By Difficulty
- Easy: 129

### Latest
- 2026-05-02: [Reverse Linked List](leetcode/2026/05/2026-05-02_2010_reverse-linked-list)
- 2026-05-02: [Reverse Linked List](leetcode/2026/05/2026-05-02_1550_reverse-linked-list)
- 2026-05-02: [Two Sum](leetcode/2026/05/2026-05-02_1300_two-sum)
- 2026-05-01: [Two Sum](leetcode/2026/05/2026-05-01_2045_two-sum)
- 2026-05-01: [Two Sum](leetcode/2026/05/2026-05-01_1935_two-sum)
- 2026-05-01: [Reverse Linked List](leetcode/2026/05/2026-05-01_1450_reverse-linked-list)
- 2026-04-30: [Two Sum](leetcode/2026/04/2026-04-30_2030_two-sum)
- 2026-04-30: [Reverse Linked List](leetcode/2026/04/2026-04-30_1600_reverse-linked-list)
- 2026-04-30: [Two Sum](leetcode/2026/04/2026-04-30_0910_two-sum)
- 2026-04-29: [Two Sum](leetcode/2026/04/2026-04-29_1930_two-sum)
<!-- LCB:INDEX:END -->

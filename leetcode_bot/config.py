import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_first_env(*names: str):
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return None


def _get_int(name: str, default: int, minimum: int = None, maximum: int = None) -> int:
    raw = _get_first_env(name)
    try:
        value = int(raw) if raw is not None else default
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def _get_bool(name: str, default: bool = False) -> bool:
    raw = _get_first_env(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int_alias(names, default: int, minimum: int = None, maximum: int = None) -> int:
    raw = _get_first_env(*names)
    try:
        value = int(raw) if raw is not None else default
    except (TypeError, ValueError):
        value = default
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def _parse_clock(raw: str, default_hour: int) -> int:
    if not raw:
        return default_hour * 60
    text = raw.strip()
    if ":" in text:
        hour_text, minute_text = text.split(":", 1)
        try:
            hour = int(hour_text)
            minute = int(minute_text)
        except ValueError:
            return default_hour * 60
        hour = max(0, min(23, hour))
        minute = max(0, min(59, minute))
        return (hour * 60) + minute
    try:
        hour = int(text)
    except ValueError:
        hour = default_hour
    hour = max(0, min(23, hour))
    return hour * 60


ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".state"
STATE_DIR.mkdir(parents=True, exist_ok=True)

SCHEDULES_DIR = STATE_DIR / "schedules"
SCHEDULES_DIR.mkdir(exist_ok=True)

DRY_RUN_PREVIEWS_DIR = STATE_DIR / "dry_run_previews"
DRY_RUN_PREVIEWS_DIR.mkdir(exist_ok=True)

LOGS_DIR = STATE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOCK_PATH = STATE_DIR / "run.lock"
PROBLEM_HISTORY_PATH = STATE_DIR / "problem_history.json"

LCB_MODEL = os.getenv("LCB_MODEL", "qwen2.5-coder:1.5b-instruct")
LCB_QUESTIONS_PATH = Path(os.getenv("LCB_QUESTIONS_PATH", str(ROOT / "data/questions.txt")))
LCB_RUN_MODE = _get_first_env("LCB_RUN_MODE") or "normal"
if _get_bool("DRY_RUN", default=False):
    LCB_RUN_MODE = "dry-run"
LCB_RUN_MODE = LCB_RUN_MODE.strip().lower()
LCB_BRANCH = os.getenv("LCB_BRANCH") or None

LCB_COMMITS_PER_DAY_MIN = _get_int_alias(("MIN_COMMITS_PER_DAY", "LCB_COMMITS_PER_DAY_MIN"), 3, minimum=1)
LCB_COMMITS_PER_DAY_MAX = _get_int_alias(
    ("MAX_COMMITS_PER_DAY", "LCB_COMMITS_PER_DAY_MAX"),
    6,
    minimum=LCB_COMMITS_PER_DAY_MIN,
)
LCB_ACTIVE_START_MINUTES = _parse_clock(_get_first_env("ACTIVE_HOURS_START", "LCB_ACTIVE_START_HOUR"), default_hour=9)
LCB_ACTIVE_END_MINUTES = _parse_clock(_get_first_env("ACTIVE_HOURS_END", "LCB_ACTIVE_END_HOUR"), default_hour=22)
if LCB_ACTIVE_END_MINUTES <= LCB_ACTIVE_START_MINUTES:
    LCB_ACTIVE_END_MINUTES = min((23 * 60) + 59, LCB_ACTIVE_START_MINUTES + 60)
LCB_MIN_GAP_MINUTES = _get_int_alias(("MIN_GAP_MINUTES", "LCB_MIN_GAP_MINUTES"), 45, minimum=1)
LCB_DUE_GRACE_MINUTES = _get_int_alias(("DUE_GRACE_MINUTES", "LCB_DUE_GRACE_MINUTES"), 20, minimum=1)
LCB_RUNNING_STALE_MINUTES = _get_int_alias(("RUNNING_STALE_MINUTES", "LCB_RUNNING_STALE_MINUTES"), 180, minimum=30)
LCB_RECENT_PROBLEM_WINDOW = _get_int_alias(("RECENT_PROBLEM_WINDOW", "LCB_RECENT_PROBLEM_WINDOW"), 10, minimum=1)

LCB_DRY_RUN_USE_LLM = _get_bool("LCB_DRY_RUN_USE_LLM", default=False)
LCB_NOW = _get_first_env("LCB_NOW")

LCB_OLLAMA_TIMEOUT = _get_int("LCB_OLLAMA_TIMEOUT", 180, minimum=30)
LCB_NUM_PREDICT = _get_int("LCB_NUM_PREDICT", 256, minimum=100)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

README_PATH = ROOT / "README.md"
README_INDEX_START = "<!-- LCB:INDEX:START -->"
README_INDEX_END = "<!-- LCB:INDEX:END -->"

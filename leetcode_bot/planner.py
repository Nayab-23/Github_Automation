import json
import random
from datetime import date
from pathlib import Path
from .config import STATE_DIR, LCB_DAYS_PER_WEEK


def iso_week_key(d: date):
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def plan_for_week(target_date: date):
    key = iso_week_key(target_date)
    path = STATE_DIR / f"plan_{key}.json"
    if path.exists():
        return json.loads(path.read_text())

    days = list(range(1, 8))
    k = min(max(1, LCB_DAYS_PER_WEEK), 7)
    chosen = sorted(random.sample(days, k))
    data = {"iso_week": key, "days": chosen}
    path.write_text(json.dumps(data, indent=2))
    return data


def today_in_plan(today: date):
    plan = plan_for_week(today)
    _, _, weekday = today.isocalendar()
    return weekday in plan.get("days", [])


def mark_ran(today: date, info: dict):
    path = STATE_DIR / f"ran_{today.isoformat()}.json"
    path.write_text(json.dumps(info, indent=2))


def ran_today(today: date):
    path = STATE_DIR / f"ran_{today.isoformat()}.json"
    return path.exists()

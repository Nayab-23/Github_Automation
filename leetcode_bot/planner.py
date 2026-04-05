import json
import random
from datetime import date, datetime, timedelta
from typing import Dict, Optional

from .config import (
    LCB_ACTIVE_END_MINUTES,
    LCB_ACTIVE_START_MINUTES,
    LCB_COMMITS_PER_DAY_MAX,
    LCB_COMMITS_PER_DAY_MIN,
    LCB_DUE_GRACE_MINUTES,
    LCB_MIN_GAP_MINUTES,
    LCB_NOW,
    LCB_RUNNING_STALE_MINUTES,
    SCHEDULES_DIR,
)


def get_now() -> datetime:
    if not LCB_NOW:
        return datetime.now().astimezone()

    parsed = datetime.fromisoformat(LCB_NOW)
    if parsed.tzinfo is None:
        local_tz = datetime.now().astimezone().tzinfo
        return parsed.replace(tzinfo=local_tz)
    return parsed.astimezone()


def _schedule_path(target_date: date):
    return SCHEDULES_DIR / f"{target_date.isoformat()}.json"


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _localize(target_date: date, hour: int, minute: int, tzinfo) -> datetime:
    return datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        hour,
        minute,
        tzinfo=tzinfo,
    )


def _feasible_slot_count() -> int:
    total_minutes = LCB_ACTIVE_END_MINUTES - LCB_ACTIVE_START_MINUTES
    return (total_minutes // LCB_MIN_GAP_MINUTES) + 1


def _build_slots(target_date: date, now: datetime):
    tzinfo = now.tzinfo
    start_hour, start_minute = divmod(LCB_ACTIVE_START_MINUTES, 60)
    end_hour, end_minute = divmod(LCB_ACTIVE_END_MINUTES, 60)
    window_start = _localize(target_date, start_hour, start_minute, tzinfo)
    window_end = _localize(target_date, end_hour, end_minute, tzinfo)
    total_minutes = int((window_end - window_start).total_seconds() // 60)
    feasible_count = max(1, _feasible_slot_count())
    slot_min = min(LCB_COMMITS_PER_DAY_MIN, feasible_count)
    slot_max = min(LCB_COMMITS_PER_DAY_MAX, feasible_count)
    if slot_max < slot_min:
        slot_min = slot_max
    count = random.randint(slot_min, slot_max)
    slack_minutes = total_minutes - ((count - 1) * LCB_MIN_GAP_MINUTES)
    offsets = sorted(random.randint(0, slack_minutes) for _ in range(count))

    slots = []
    for index, offset in enumerate(offsets, start=1):
        scheduled_for = window_start + timedelta(minutes=offset + ((index - 1) * LCB_MIN_GAP_MINUTES))
        slots.append(
            {
                "id": f"{target_date.isoformat()}-{index:02d}",
                "scheduled_for": scheduled_for.isoformat(timespec="minutes"),
                "status": "pending",
                "status_updated_at": now.isoformat(timespec="seconds"),
            }
        )
    return slots


def save_schedule(schedule: Dict) -> Dict:
    path = _schedule_path(date.fromisoformat(schedule["date"]))
    path.write_text(json.dumps(schedule, indent=2))
    return schedule


def plan_for_day(target_date: date, now: Optional[datetime] = None) -> Dict:
    path = _schedule_path(target_date)
    if path.exists():
        return json.loads(path.read_text())

    now = now or get_now()
    schedule = {
        "date": target_date.isoformat(),
        "created_at": now.isoformat(timespec="seconds"),
        "config": {
            "commits_per_day_min": LCB_COMMITS_PER_DAY_MIN,
            "commits_per_day_max": LCB_COMMITS_PER_DAY_MAX,
            "active_hours_start": f"{LCB_ACTIVE_START_MINUTES // 60:02d}:{LCB_ACTIVE_START_MINUTES % 60:02d}",
            "active_hours_end": f"{LCB_ACTIVE_END_MINUTES // 60:02d}:{LCB_ACTIVE_END_MINUTES % 60:02d}",
            "min_gap_minutes": LCB_MIN_GAP_MINUTES,
            "due_grace_minutes": LCB_DUE_GRACE_MINUTES,
        },
        "slots": _build_slots(target_date, now),
    }
    return save_schedule(schedule)


def _set_slot_status(slot: Dict, status: str, now: datetime, extra: Optional[Dict] = None):
    slot["status"] = status
    slot["status_updated_at"] = now.isoformat(timespec="seconds")
    if extra:
        slot.update(extra)


def sync_schedule(schedule: Dict, now: datetime) -> Dict:
    changed = False
    stale_running_cutoff = timedelta(minutes=LCB_RUNNING_STALE_MINUTES)
    missed_cutoff = timedelta(minutes=LCB_DUE_GRACE_MINUTES)

    for slot in schedule.get("slots", []):
        scheduled_for = _parse_dt(slot["scheduled_for"])
        status = slot.get("status", "pending")
        if status == "pending" and now > scheduled_for + missed_cutoff:
            _set_slot_status(
                slot,
                "skipped_missed",
                now,
                extra={"reason": "missed due window"},
            )
            changed = True
        elif status == "running":
            started_at_raw = slot.get("started_at") or slot.get("status_updated_at")
            started_at = _parse_dt(started_at_raw)
            if now > started_at + stale_running_cutoff:
                _set_slot_status(
                    slot,
                    "failed_interrupted",
                    now,
                    extra={"reason": "stale running slot after interruption"},
                )
                changed = True

    if changed:
        save_schedule(schedule)
    return schedule


def find_due_slot(schedule: Dict, now: datetime) -> Optional[Dict]:
    due_window = timedelta(minutes=LCB_DUE_GRACE_MINUTES)
    for slot in schedule.get("slots", []):
        if slot.get("status") != "pending":
            continue
        scheduled_for = _parse_dt(slot["scheduled_for"])
        if scheduled_for <= now <= scheduled_for + due_window:
            return slot
    return None


def next_pending_slot(schedule: Dict) -> Optional[Dict]:
    for slot in schedule.get("slots", []):
        if slot.get("status") == "pending":
            return slot
    return None


def mark_slot(schedule: Dict, slot_id: str, status: str, now: datetime, extra: Optional[Dict] = None) -> Dict:
    for slot in schedule.get("slots", []):
        if slot.get("id") == slot_id:
            _set_slot_status(slot, status, now, extra=extra)
            break
    return save_schedule(schedule)


def schedule_summary(schedule: Dict) -> str:
    parts = []
    for slot in schedule.get("slots", []):
        when = _parse_dt(slot["scheduled_for"]).strftime("%H:%M")
        parts.append(f"{slot['id']}@{when}={slot.get('status')}")
    return ", ".join(parts)

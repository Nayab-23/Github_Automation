import re
import json
import hashlib
import random
from datetime import datetime
from pathlib import Path
from typing import List

from .config import LCB_QUESTIONS_PATH, LCB_RECENT_PROBLEM_WINDOW, PROBLEM_HISTORY_PATH


def _slugify(text: str, max_len=50):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].strip("-")


def parse_questions() -> List[dict]:
    p = Path(LCB_QUESTIONS_PATH)
    if not p.exists():
        example = p.with_suffix(p.suffix + ".example")
        if example.exists():
            p = example
        else:
            return []
    raw = p.read_text()
    blocks = [b.strip() for b in re.split(r"^---$", raw, flags=re.MULTILINE) if b.strip()]
    problems = []
    for i, b in enumerate(blocks):
        prob = {"id": None, "title": None, "difficulty": None, "tags": [], "prompt": None, "examples": None, "raw_block": b}
        lines = b.splitlines()
        header_map = {}
        cur = None
        buffer = []
        for ln in lines:
            m = re.match(r"^(Title|Difficulty|Tags|Prompt|Examples)\s*:\s*(.*)$", ln)
            if m:
                if cur:
                    header_map[cur] = "\n".join(buffer).strip()
                cur = m.group(1)
                buffer = [m.group(2) or ""]
            else:
                if cur:
                    buffer.append(ln)
        if cur:
            header_map[cur] = "\n".join(buffer).strip()

        prob["title"] = header_map.get("Title") or (lines[0].strip() if lines else f"problem-{i+1}")
        prob["difficulty"] = header_map.get("Difficulty")
        tags = header_map.get("Tags")
        if tags:
            prob["tags"] = [t.strip() for t in re.split(r"[,;]", tags) if t.strip()]
        prob["prompt"] = header_map.get("Prompt") or header_map.get("Examples") or "\n".join(lines)
        prob["examples"] = header_map.get("Examples")
        h = hashlib.sha1(b.encode()).hexdigest()[:10]
        prob["id"] = f"p_{h}"
        prob["slug"] = _slugify(prob["title"]) or f"{prob['id']}"
        problems.append(prob)

    return problems


def _load_problem_history() -> List[dict]:
    if not PROBLEM_HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(PROBLEM_HISTORY_PATH.read_text())
    except Exception:
        return []
    if isinstance(data, list):
        return data
    return []


def _save_problem_history(history: List[dict]):
    PROBLEM_HISTORY_PATH.write_text(json.dumps(history[-500:], indent=2))


def pick_problem(record_usage: bool = True):
    problems = parse_questions()
    if not problems:
        return None

    history = _load_problem_history()
    used_ids = {entry.get("id") for entry in history}
    recent_ids = [
        entry.get("id")
        for entry in history[-LCB_RECENT_PROBLEM_WINDOW:]
        if entry.get("id")
    ]

    candidates = [problem for problem in problems if problem["id"] not in used_ids]
    if not candidates:
        candidates = [problem for problem in problems if problem["id"] not in recent_ids]
    if not candidates:
        candidates = problems

    chosen = random.choice(candidates)
    if record_usage:
        history.append(
            {
                "id": chosen["id"],
                "title": chosen.get("title"),
                "selected_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
        )
        _save_problem_history(history)
    return chosen

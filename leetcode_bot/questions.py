import re
import json
import hashlib
from pathlib import Path
from typing import List
from .config import LCB_QUESTIONS_PATH, STATE_DIR


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


def pick_problem():
    problems = parse_questions()
    if not problems:
        return None
    used_path = STATE_DIR / "used_problems.json"
    used = set()
    if used_path.exists():
        try:
            used = set(json.loads(used_path.read_text()))
        except Exception:
            used = set()
    # prefer unused
    unused = [p for p in problems if p["id"] not in used]
    if unused:
        chosen = unused[0]
    else:
        chosen = problems[0]
    used.add(chosen["id"])
    used_path.write_text(json.dumps(list(used), indent=2))
    return chosen

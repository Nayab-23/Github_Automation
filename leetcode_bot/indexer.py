import json
import re
from pathlib import Path
from datetime import datetime, timezone

from .config import README_INDEX_END, README_INDEX_START, README_PATH, ROOT


def scan_index():
    base = Path(ROOT) / "leetcode"
    total = 0
    by_diff = {}
    entries = []
    if not base.exists():
        return {"total": 0, "by_difficulty": {}, "entries": []}
    for y in sorted(base.iterdir(), reverse=True):
        for m in sorted(y.iterdir(), reverse=True):
            for s in sorted(m.iterdir(), reverse=True):
                total += 1
                meta = s / "metadata.json"
                if meta.exists():
                    md = json.loads(meta.read_text())
                    d = md.get("difficulty") or "unknown"
                    by_diff[d] = by_diff.get(d, 0) + 1
                    entries.append(
                        {
                            "path": str(s.relative_to(ROOT)),
                            "title": md.get("selected_title"),
                            "date": md.get("date"),
                            "run_at": md.get("run_at") or md.get("date"),
                        }
                    )
    entries.sort(key=lambda item: item.get("run_at") or "", reverse=True)
    return {"total": total, "by_difficulty": by_diff, "entries": entries}


def _build_index_block() -> str:
    data = scan_index()
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        README_INDEX_START,
        "## Generated Activity Snapshot",
        "",
        f"Last updated: {stamp}",
        "",
        f"Total solutions: {data['total']}",
        "",
        "### By Difficulty",
    ]
    for key, value in sorted(data["by_difficulty"].items()):
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("### Latest")
    for entry in data["entries"][:10]:
        lines.append(f"- {entry['date']}: [{entry['title']}]({entry['path']})")
    if not data["entries"]:
        lines.append("- No generated solutions yet.")
    lines.append(README_INDEX_END)
    return "\n".join(lines)


def update_readme():
    if README_PATH.exists():
        current = README_PATH.read_text()
    else:
        current = "# LeetCode Auto Practice + GitHub Pusher\n"

    block = _build_index_block()
    pattern = re.compile(
        re.escape(README_INDEX_START) + r".*?" + re.escape(README_INDEX_END),
        flags=re.DOTALL,
    )
    if pattern.search(current):
        updated = pattern.sub(block, current)
    else:
        updated = current.rstrip() + "\n\n" + block + "\n"
    README_PATH.write_text(updated)

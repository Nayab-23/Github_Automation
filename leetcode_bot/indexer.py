import json
from pathlib import Path
from datetime import datetime
from .config import ROOT, README_PATH


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
                    entries.append({"path": str(s.relative_to(ROOT)), "title": md.get("selected_title"), "date": md.get("date")})
    return {"total": total, "by_difficulty": by_diff, "entries": entries}


def update_readme():
    data = scan_index()
    lines = ["# LeetCode Auto Practice", "", f"Last updated: {datetime.utcnow().isoformat()} UTC", "", f"Total solutions: {data['total']}", ""]
    lines.append("## By difficulty")
    for k, v in data["by_difficulty"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Latest")
    for e in data["entries"][:10]:
        lines.append(f"- {e['date']}: [{e['title']}]({e['path']})")
    lines.append("")
    lines.append("*Note: Solutions are LLM-assisted and validated locally.*")
    README_PATH.write_text("\n".join(lines))

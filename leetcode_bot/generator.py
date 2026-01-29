import json
import hashlib
import re
from datetime import date
from .llm import generate_json
from .config import LCB_MODEL


BASE_PROMPT_TEMPLATE = '''You are a helpful coding assistant. Produce output STRICTLY as a single JSON object with keys: "solution_py", "notes_md", "metadata".
The "solution_py" value must be the full Python source file content and only Python code. Do not include markdown or fenced code blocks.
The "notes_md" value must be markdown explaining approach, complexity, and edge cases. Write it in a direct, natural tone and avoid boilerplate openers like "Based on the provided documentation."
The "metadata" value must be an object including title, difficulty, tags (list), and any assumptions.

Problem:
{prompt}

Examples:
{examples}

Return only valid JSON.
'''


def _clean_notes(notes: str) -> str:
    if not notes:
        return notes
    cleaned = re.sub(r'^\s*"?based on the provided documentation[,:.\s]*', '', notes, flags=re.IGNORECASE)
    return cleaned.lstrip()


def build_prompt(problem: dict):
    return BASE_PROMPT_TEMPLATE.format(prompt=problem.get("prompt", ""), examples=problem.get("examples", ""))


def generate_solution(problem: dict, model: str = None):
    model = model or LCB_MODEL
    prompt = build_prompt(problem)
    obj, attempts = generate_json(prompt, model=model, retries=2)
    # normalize
    solution = obj.get("solution_py")
    notes = _clean_notes(obj.get("notes_md") or "")
    metadata = obj.get("metadata") or {}
    metadata.setdefault("model", model)
    metadata.setdefault("title", problem.get("title"))
    metadata.setdefault("difficulty", problem.get("difficulty"))
    metadata.setdefault("tags", problem.get("tags", []))
    prompt_hash = hashlib.sha1(prompt.encode()).hexdigest()
    return {"solution_py": solution, "notes_md": notes, "metadata": metadata, "prompt_hash": prompt_hash, "attempts": attempts}

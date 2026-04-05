import json
import hashlib
from datetime import date
from .llm import generate_json
from .config import LCB_MODEL


BASE_PROMPT_TEMPLATE = '''You are a helpful coding assistant. Produce output STRICTLY as a single JSON object with keys: "solution_py" and "notes_md".
The "solution_py" value must be the full Python source file content and only Python code. Keep it short and do not include markdown or fenced code blocks.
The "notes_md" value must be a single markdown string with exactly 2 short bullet points covering approach and complexity. Do not return a list. Keep notes_md under 60 words.
Do not include extra keys.

Problem:
{prompt}

Examples:
{examples}

Return only valid JSON.
'''


def build_prompt(problem: dict):
    return BASE_PROMPT_TEMPLATE.format(prompt=problem.get("prompt", ""), examples=problem.get("examples", ""))


def generate_solution(problem: dict, model: str = None):
    model = model or LCB_MODEL
    prompt = build_prompt(problem)
    obj, attempts = generate_json(prompt, model=model, retries=0)
    # normalize
    solution = obj.get("solution_py")
    notes = obj.get("notes_md")
    if isinstance(solution, list):
        solution = "\n".join(str(part) for part in solution)
    if isinstance(solution, str):
        solution = solution.strip()
        if solution.startswith('"""') and solution.endswith('"""'):
            solution = solution[3:-3].strip()
    if isinstance(notes, list):
        notes = "\n".join(f"- {str(item).lstrip('- ').strip()}" for item in notes if str(item).strip())
    elif notes is not None and not isinstance(notes, str):
        notes = str(notes)
    metadata = obj.get("metadata") or {}
    metadata.setdefault("model", model)
    metadata.setdefault("title", problem.get("title"))
    metadata.setdefault("difficulty", problem.get("difficulty"))
    metadata.setdefault("tags", problem.get("tags", []))
    prompt_hash = hashlib.sha1(prompt.encode()).hexdigest()
    return {"solution_py": solution, "notes_md": notes, "metadata": metadata, "prompt_hash": prompt_hash, "attempts": attempts}

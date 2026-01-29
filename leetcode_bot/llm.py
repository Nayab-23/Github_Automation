import json
import time
from typing import Tuple
import requests
from .config import OLLAMA_URL, LCB_MODEL, LCB_OLLAMA_TIMEOUT, LCB_NUM_PREDICT


def _extract_response_text(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    # If the response is a single JSON object with a "response" field (Ollama non-streaming)
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and "response" in obj:
            return obj.get("response") or ""
    except Exception:
        pass
    # If the response is NDJSON streaming, stitch "response" chunks
    parts = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict) and "response" in obj:
                parts.append(obj.get("response") or "")
        except Exception:
            continue
    if parts:
        return "".join(parts)
    return text


def _post_generate(prompt: str, model: str, timeout: int, num_predict: int) -> Tuple[bool, str]:
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": num_predict},
    }
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return True, _extract_response_text(r.text)
    except Exception as e:
        return False, str(e)


def generate_json(prompt: str, model: str = None, retries=2):
    model = model or LCB_MODEL
    attempt = 0
    last_err = None
    while attempt <= retries:
        ok, resp = _post_generate(prompt, model, timeout=LCB_OLLAMA_TIMEOUT, num_predict=LCB_NUM_PREDICT)
        if not ok:
            last_err = resp
            attempt += 1
            time.sleep(1)
            continue
        # try to locate JSON in response
        text = (resp or "").strip()
        # Strip common code fences if present
        if text.startswith("```"):
            text = text.strip().strip("`")
            # remove optional language tag line
            lines = text.splitlines()
            if lines and lines[0].lower().startswith("json"):
                text = "\n".join(lines[1:]).strip()
        # directly try parse
        try:
            obj = json.loads(text)
            return obj, attempt
        except Exception:
            # try to extract first { ... }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                sub = text[start:end+1]
                try:
                    obj = json.loads(sub)
                    return obj, attempt
                except Exception:
                    last_err = text
        # repair prompt and retry
        repair = "\n\nIf you returned invalid JSON, please return valid JSON only exactly matching the schema."
        prompt = prompt + repair
        attempt += 1
        time.sleep(1)

    raise RuntimeError(f"LLM generation failed after {retries+1} attempts: {last_err}")

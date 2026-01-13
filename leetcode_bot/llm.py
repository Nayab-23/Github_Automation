import json
import hashlib
import time
from typing import Tuple
import requests
from .config import OLLAMA_URL, LCB_MODEL


def _post_generate(prompt: str, model: str, timeout=60) -> Tuple[bool, str]:
    url = f"{OLLAMA_URL}/api/generate"
    payload = {"model": model, "prompt": prompt, "max_tokens": 1500}
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return True, r.text
    except Exception as e:
        return False, str(e)


def generate_json(prompt: str, model: str = None, retries=2):
    model = model or LCB_MODEL
    attempt = 0
    last_err = None
    while attempt <= retries:
        ok, resp = _post_generate(prompt, model)
        if not ok:
            last_err = resp
            attempt += 1
            time.sleep(1)
            continue
        # try to locate JSON in response
        text = resp.strip()
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

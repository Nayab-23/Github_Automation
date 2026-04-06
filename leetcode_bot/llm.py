import json
import logging
import re
import time
from typing import Tuple
import requests
from .config import OLLAMA_URL, LCB_MODEL, LCB_OLLAMA_TIMEOUT, LCB_NUM_PREDICT

logger = logging.getLogger("leetcode_bot")


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


def _parse_json_candidate(text: str):
    text = (text or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = text.strip().strip("`")
        lines = text.splitlines()
        if lines and lines[0].lower().startswith("json"):
            text = "\n".join(lines[1:]).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return None
    return None


def _decode_json_string(value: str):
    try:
        return json.loads(f'"{value}"')
    except Exception:
        return None


def _extract_string_field(text: str, field: str):
    triple_pattern = rf'"{re.escape(field)}"\s*:\s*"""(.*?)"""'
    match = re.search(triple_pattern, text, re.S)
    if match:
        return match.group(1).strip()
    pattern = rf'"{re.escape(field)}"\s*:\s*"((?:\\.|[^"\\])*)"'
    match = re.search(pattern, text, re.S)
    if match:
        return _decode_json_string(match.group(1))
    return None


def _salvage_partial_object(text: str):
    solution = _extract_string_field(text, "solution_py")
    if not solution:
        return None
    notes = _extract_string_field(text, "notes_md")
    return {"solution_py": solution, "notes_md": notes}


def _classify_generation_failure(text: str) -> str:
    raw = (text or "").strip()
    lowered = raw.lower()
    if not raw:
        return "empty_response"
    if "timed out" in lowered:
        return "ollama_timeout"
    if '"""' in raw:
        return "schema_drift_triple_quotes"
    if '"solution_py"' in raw and raw.count("{") > raw.count("}"):
        return "truncated_json"
    if '"solution_py"' in raw:
        return "malformed_json"
    return "invalid_response"


def _post_generate(prompt: str, model: str, timeout: int, num_predict: int) -> Tuple[bool, str]:
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": True,
        "options": {"num_predict": num_predict},
    }
    req_timeout = None if timeout <= 0 else (10, timeout)
    try:
        r = requests.post(url, json=payload, stream=True, timeout=req_timeout)
        r.raise_for_status()
        chunks = []
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict) and obj.get("error"):
                return False, obj.get("error")
            if isinstance(obj, dict) and "response" in obj:
                chunks.append(obj.get("response") or "")
                if "}" in chunks[-1]:
                    parsed = _parse_json_candidate("".join(chunks))
                    if parsed is not None:
                        r.close()
                        return True, json.dumps(parsed)
            if isinstance(obj, dict) and obj.get("done"):
                break
        text = "".join(chunks)
        if not text:
            text = _extract_response_text(r.text)
        return True, text
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
        obj = _parse_json_candidate(text)
        if obj is not None:
            return obj, attempt
        obj = _salvage_partial_object(text)
        if obj is not None:
            logger.warning("Recovered solution from malformed model JSON on attempt %s", attempt + 1)
            return obj, attempt
        last_err = text
        # repair prompt and retry
        repair = "\n\nIf you returned invalid JSON, please return valid JSON only exactly matching the schema."
        prompt = prompt + repair
        attempt += 1
        time.sleep(1)

    classification = _classify_generation_failure(last_err)
    raise RuntimeError(f"LLM generation failed after {retries+1} attempts [{classification}]: {last_err}")

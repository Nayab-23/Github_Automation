import subprocess
import tempfile
import json
import re
from pathlib import Path


def py_compile_string(code: str):
    # write to temp file and compile
    tf = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
    tf.write(code.encode())
    tf.flush()
    tf.close()
    try:
        subprocess.check_output(["python3", "-m", "py_compile", tf.name], stderr=subprocess.STDOUT)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.output.decode()


def parse_examples_for_harness(examples_text: str):
    if not examples_text:
        return []
    examples = []
    # look for lines like Input: ...\nOutput: ...
    parts = re.split(r"\n\s*\n", examples_text.strip())
    for p in parts:
        m_in = re.search(r"Input\s*:\s*(.*)", p)
        m_out = re.search(r"Output\s*:\s*(.*)", p)
        if m_in and m_out:
            examples.append({"input": m_in.group(1).strip(), "output": m_out.group(1).strip()})
    return examples


def run_optional_harness(code: str, examples):
    # Very conservative: only run if examples small and look like literals
    if not examples:
        return True, None
    # create harness: assume solution defines a function named solve() that reads from input() or a function main()
    # We won't attempt complex introspection; return None meaning skipped
    return None, None

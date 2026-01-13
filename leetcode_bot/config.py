import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".state"
STATE_DIR.mkdir(exist_ok=True)

LCB_MODEL = os.getenv("LCB_MODEL", "qwen2.5-coder:1.5b-instruct")
LCB_QUESTIONS_PATH = Path(os.getenv("LCB_QUESTIONS_PATH", str(ROOT / "data/questions.txt")))
LCB_RUN_MODE = os.getenv("LCB_RUN_MODE", "normal")
LCB_BRANCH = os.getenv("LCB_BRANCH")
LCB_DAYS_PER_WEEK = int(os.getenv("LCB_DAYS_PER_WEEK", "4"))

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

LOGS_DIR = STATE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

README_PATH = ROOT / "README.md"

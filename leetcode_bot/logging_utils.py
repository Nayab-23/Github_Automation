import logging
from logging import handlers
from pathlib import Path
import datetime
from .config import LOGS_DIR

def setup_logging(name: str):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    logfile = LOGS_DIR / f"{datetime.date.today().isoformat()}.log"
    fh = handlers.RotatingFileHandler(logfile, maxBytes=5_000_000, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

from datetime import datetime
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Log file stored at project root
LOG_FILE = BASE_DIR / "access.log"


def log_access(username: str, role: str, query: str, confidence: float):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_line = f'{timestamp} {username} {role} "{query}" {confidence}\n'

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

import json
from datetime import datetime
from pathlib import Path


class AuditLogger:

    LOG_FILE = Path("audit.log")

    @classmethod
    def log_event(
        cls,
        event_type: str,
        username: str,
        role: str,
        details: dict
    ):

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "username": username,
            "role": role,
            "details": details,
        }

        with open(cls.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
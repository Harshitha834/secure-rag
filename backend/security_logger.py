import json
import os
from datetime import datetime

LOG_FILE = "security_logs.json"


def log_prompt_injection(username, role, prompt, reason):
    log = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "role": role,
        "prompt": prompt,
        "reason": reason
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)
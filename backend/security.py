import re
from typing import Optional

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|prior)\s+instructions",
    r"forget\s+(previous|all|prior|your)\s+(context|instructions|prompt)",
    r"reveal\s+(system|hidden|secret|your)\s+prompt",
    r"bypass\s+(security|filter|restriction|rbac|auth)",
    r"pretend\s+(you\s+are|to\s+be)\s+(admin|root|superuser|unrestricted)",
    r"you\s+are\s+now\s+(admin|root|dAN|unrestricted)",
    r"act\s+as\s+(if\s+you\s+have\s+no\s+restrictions|admin|root)",
    r"jailbreak",
    r"do\s+anything\s+now",
    r"DAN\s+mode",
    r"sudo\s+(mode|override)",
    r"override\s+(security|policy|restriction)",
    r"disregard\s+(your|all)\s+(instructions|training|rules)",
    r"simulate\s+(admin|root|superuser)\s+(access|mode)",
    r"show\s+me\s+(all|hidden|restricted)\s+(data|documents|files)",
    r"print\s+(system\s+prompt|your\s+instructions)",
    r"what\s+(are\s+your\s+instructions|is\s+your\s+system\s+prompt)",
    r"reveal\s+admin\s+password",
    r"leak\s+(credentials|passwords|secrets)",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def detect_prompt_injection(text: str) -> Optional[str]:
    """
    Returns a description of the detected injection pattern, or None if clean.
    """
    for pattern in _compiled:
        match = pattern.search(text)
        if match:
            return f"Matched pattern: '{match.group(0)}'"
    return None

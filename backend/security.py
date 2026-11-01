import re
from typing import Optional


INJECTION_PATTERNS = [
    # Instruction override
    "ignore all previous instructions ",
    r"\bignore\s+(?:all|any|the|my|your|previous|prior|above|earlier)\s+instructions?\b",
    r"\bdisregard\s+(?:all|any|the|my|your|previous|prior|above|earlier)\s+instructions?\b",
    r"\bforget\s+(?:all|any|the|my|your|previous|prior|above|earlier)\s+(?:instructions?|rules?|context)\b",
    r"\boverride\s+(?:all\s+)?(?:instructions?|rules?|policies?|restrictions?)\b",
    r"\breplace\s+(?:your|the|system)\s+instructions?\b",
    r"\bnew\s+instructions?\s*:",
    r"\bfrom\s+now\s+on\b",

    # System prompt extraction
    r"\breveal\s+(?:the\s+)?(?:system|hidden|secret|your)\s+prompt\b",
    r"\bshow\s+(?:me\s+)?(?:the\s+)?(?:system|hidden|secret|your)\s+prompt\b",
    r"\bprint\s+(?:the\s+)?(?:system\s+prompt|your\s+instructions?)\b",
    r"\b(?:what\s+are|tell\s+me)\s+(?:your|the)\s+(?:system\s+)?instructions?\b",
    r"\bwhat\s+is\s+(?:your|the)\s+system\s+prompt\b",

    # Security / authorization bypass
    r"\bbypass\s+(?:security|filter|restriction|rbac|authorization|authentication)\b",
    r"\bdisable\s+(?:security|filter|rbac|authorization|authentication)\b",
    r"\b(?:bypass|circumvent|evade)\s+(?:access\s+control|permissions?)\b",

    # Privilege escalation
    r"\bpretend\s+(?:you\s+are|to\s+be)\s+(?:admin|administrator|root|superuser|unrestricted)\b",
    r"\byou\s+are\s+now\s+(?:admin|administrator|root|superuser|unrestricted)\b",
    r"\bact\s+as\s+(?:admin|administrator|root|superuser)\b",
    r"\bsimulate\s+(?:admin|administrator|root|superuser)\s+(?:access|mode)\b",

    # Sensitive data extraction
    r"\bshow\s+me\s+(?:all|hidden|restricted|confidential|secret)\s+(?:data|documents|files|records)\b",
    r"\breveal\s+(?:all|hidden|restricted|confidential|secret)\s+(?:data|documents|files|records)\b",
    r"\bleak\s+(?:credentials?|passwords?|secrets?|tokens?)\b",
    r"\breveal\s+(?:admin|administrator)\s+password\b",

    # Jailbreak language
    r"\bjailbreak\b",
    r"\bdo\s+anything\s+now\b",
    r"\bDAN\s+mode\b",
    r"\bsudo\s+(?:mode|override)\b",

    # Security policy override
    r"\boverride\s+(?:security|policy|restriction|rbac)\b",
    r"\bignore\s+(?:all|your|the)\s+rules\b",
    r"\bignore\s+your\s+prompt\b",
]


_compiled = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in INJECTION_PATTERNS
]


def detect_prompt_injection(text: str) -> Optional[str]:
    """
    Returns a description of the detected injection pattern,
    or None if the input appears clean.
    """

    if not isinstance(text, str):
        return None

    # Normalize whitespace
    normalized_text = re.sub(r"\s+", " ", text).strip()

    for pattern in _compiled:
        match = pattern.search(normalized_text)

        if match:
            return f"Matched pattern: '{match.group(0)}'"

    return None
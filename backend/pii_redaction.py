import re


class PIIRedactor:

    PATTERNS = {
        "AADHAAR": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        "PHONE": r"\b[6-9]\d{9}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    }

    @classmethod
    def redact(cls, text: str) -> str:

        for label, pattern in cls.PATTERNS.items():

            text = re.sub(
                pattern,
                f"[{label}_REDACTED]",
                text,
                flags=re.IGNORECASE,
            )

        return text

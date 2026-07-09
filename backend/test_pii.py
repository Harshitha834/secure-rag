# test_pii.py

from pii_redaction import PIIRedactor

sample_text = """
Employee: Ravi Kumar
Phone: 9876543210
Email: ravi@gmail.com
PAN: ABCDE1234F
Aadhaar: 1234 5678 9012
"""

print("Original:")
print(sample_text)

print("\nRedacted:")
print(PIIRedactor.redact(sample_text))
import os
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None


class DocumentProcessor:

    ALLOWED_EXTENSIONS = {
        ".txt",
        ".pdf",
        ".docx",
    }

    MAX_FILE_SIZE_MB = 20

    @classmethod
    def validate_file(cls, filename: str, size_bytes: int):

        ext = Path(filename).suffix.lower()

        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {ext}"
            )

        size_mb = size_bytes / (1024 * 1024)

        if size_mb > cls.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"File exceeds {cls.MAX_FILE_SIZE_MB} MB limit"
            )

    @classmethod
    def extract_text(cls, filename: str, content: bytes) -> str:

        ext = Path(filename).suffix.lower()

        if ext == ".txt":
            return content.decode(
                "utf-8",
                errors="ignore"
            )

        elif ext == ".pdf":
            return cls._extract_pdf(content)

        elif ext == ".docx":
            return cls._extract_docx(content)

        raise ValueError("Unsupported file type")

    @staticmethod
    def _extract_pdf(content: bytes) -> str:

        if fitz is None:
            raise RuntimeError(
                "PyMuPDF not installed"
            )

        text = ""

        pdf = fitz.open(
            stream=content,
            filetype="pdf"
        )

        for page in pdf:
            text += page.get_text()

        return text

    @staticmethod
    def _extract_docx(content: bytes) -> str:

        if Document is None:
            raise RuntimeError(
                "python-docx not installed"
            )

        from io import BytesIO

        doc = Document(BytesIO(content))

        return "\n".join(
            para.text
            for para in doc.paragraphs
        )
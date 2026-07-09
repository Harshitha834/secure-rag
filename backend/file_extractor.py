"""
Universal document text extractor.
Supports: .pdf, .docx, .txt, .md, .csv, .json, .pptx, .xlsx
"""

import os
import io
import json
import csv as csv_module
from typing import Tuple

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md", ".csv", ".json", ".pptx", ".xlsx", ".log",
}


def is_supported(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_EXTENSIONS


def extract_text(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Extract plain text from any supported file type.
    Returns (text, warning) — warning is empty string if no issues.
    """
    ext = os.path.splitext(filename)[1].lower()
    warning = ""

    try:
        if ext == ".pdf":
            return _extract_pdf(file_bytes), warning

        elif ext == ".docx":
            return _extract_docx(file_bytes), warning

        elif ext in (".txt", ".md", ".log"):
            return _extract_plain(file_bytes), warning

        elif ext == ".csv":
            return _extract_csv(file_bytes), warning

        elif ext == ".json":
            return _extract_json(file_bytes), warning

        elif ext == ".pptx":
            return _extract_pptx(file_bytes), warning

        elif ext == ".xlsx":
            return _extract_xlsx(file_bytes), warning

        else:
            # Fallback: try decoding as plain text
            return _extract_plain(file_bytes), f"Unknown extension '{ext}' — read as plain text"

    except Exception as e:
        # Last-resort fallback so upload never hard-fails
        try:
            text = _extract_plain(file_bytes)
            return text, f"Extraction error with primary parser ({e}); fell back to plain text"
        except Exception:
            return "", f"Failed to extract text: {e}"


# ── Individual extractors ───────────────────────────────────────────────────

def _extract_plain(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def _extract_pdf(file_bytes: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(file_bytes))
    parts = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        if page_text.strip():
            parts.append(f"[Page {i + 1}]\n{page_text}")
    text = "\n\n".join(parts)

    if not text.strip():
        # Likely a scanned/image-only PDF — try OCR fallback
        text = _extract_pdf_ocr(file_bytes)
    return text


def _extract_pdf_ocr(file_bytes: bytes) -> str:
    """Fallback OCR for scanned PDFs with no embedded text layer."""
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(file_bytes)
        parts = []
        for i, image in enumerate(images):
            ocr_text = pytesseract.image_to_string(image)
            if ocr_text.strip():
                parts.append(f"[Page {i + 1} - OCR]\n{ocr_text}")
        return "\n\n".join(parts)
    except Exception:
        return ""


def _extract_docx(file_bytes: bytes) -> str:
    import docx
    doc = docx.Document(io.BytesIO(file_bytes))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]

    # Also extract table content
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells)
            if row_text.strip(" |"):
                parts.append(row_text)

    return "\n".join(parts)


def _extract_csv(file_bytes: bytes) -> str:
    text = file_bytes.decode("utf-8", errors="ignore")
    reader = csv_module.reader(io.StringIO(text))
    rows = [", ".join(row) for row in reader]
    return "\n".join(rows)


def _extract_json(file_bytes: bytes) -> str:
    data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
    return json.dumps(data, indent=2, ensure_ascii=False)


def _extract_pptx(file_bytes: bytes) -> str:
    from pptx import Presentation
    prs = Presentation(io.BytesIO(file_bytes))
    parts = []
    for i, slide in enumerate(prs.slides):
        slide_parts = [f"[Slide {i + 1}]"]
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                slide_parts.append(shape.text)
        if len(slide_parts) > 1:
            parts.append("\n".join(slide_parts))
    return "\n\n".join(parts)


def _extract_xlsx(file_bytes: bytes) -> str:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    parts = []
    for sheet in wb.worksheets:
        parts.append(f"[Sheet: {sheet.title}]")
        for row in sheet.iter_rows(values_only=True):
            row_vals = [str(v) for v in row if v is not None]
            if row_vals:
                parts.append(", ".join(row_vals))
    return "\n".join(parts)

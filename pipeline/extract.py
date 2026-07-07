"""
extract.py — Pull Malayalam text out of a PDF.

Strategy:
  1. Try the embedded text layer (fast, exact) with PyMuPDF.
  2. If a page has little/no text (a scanned image), fall back to
     Tesseract OCR with the Malayalam model (`mal`).

This handles both "real" ebooks and scanned books, which matters for a
500-page book where some pages may be images.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field

import fitz  # PyMuPDF


@dataclass
class Page:
    number: int
    text: str
    ocr_used: bool = False


@dataclass
class Book:
    title: str
    pages: list[Page] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.text for p in self.pages if p.text.strip())

    @property
    def ocr_page_count(self) -> int:
        return sum(1 for p in self.pages if p.ocr_used)


# A page is "empty enough" to warrant OCR if its text layer is basically blank.
_MIN_CHARS_PER_PAGE = 15


def _ocr_page(page: "fitz.Page", dpi: int = 300) -> str:
    """Render a page to an image and OCR it in Malayalam. Import is lazy so the
    module still works for text PDFs when tesseract isn't installed."""
    try:
        import pytesseract
        from PIL import Image
        import io
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "Scanned page found but OCR deps missing. Install: "
            "pip install pytesseract pillow  AND  apt-get install tesseract-ocr tesseract-ocr-mal"
        ) from e

    pix = page.get_pixmap(dpi=dpi)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang="mal")


def extract(pdf_path: str, ocr: str = "auto", dpi: int = 300) -> Book:
    """
    ocr: "auto" (OCR only near-empty pages), "always" (OCR every page),
         or "never" (text layer only).
    """
    doc = fitz.open(pdf_path)
    title = doc.metadata.get("title") or pdf_path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    book = Book(title=title)

    for i, page in enumerate(doc, start=1):
        text = "" if ocr == "always" else page.get_text("text")
        used_ocr = False
        if ocr == "always" or (ocr == "auto" and len(text.strip()) < _MIN_CHARS_PER_PAGE):
            if ocr != "never":
                text = _ocr_page(page, dpi=dpi)
                used_ocr = True
        book.pages.append(Page(number=i, text=text, ocr_used=used_ocr))

    doc.close()
    return book

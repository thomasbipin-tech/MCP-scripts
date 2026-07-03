"""Extract per-page text from a PDF.

Two backends:
  * a zero-dependency parser for the uncompressed text PDFs this project
    generates (``services/pdfgen``), so the full PDF -> report pipeline runs and
    is tested with nothing installed;
  * ``pypdf`` (if available) for arbitrary real-world PDFs.

Returns a list of strings, one per page. Page indices are 1-based when cited.
"""

from __future__ import annotations

import re
from typing import List

_STREAM = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.DOTALL)
_TJ = re.compile(r"\((?P<t>(?:\\.|[^\\()])*)\)\s*Tj")


def _unescape(s: str) -> str:
    return s.replace(r"\(", "(").replace(r"\)", ")").replace(r"\\", "\\")


def _pages_from_pdfgen(pdf_bytes: bytes) -> List[str]:
    """Parse the content streams our own writer produces (one stream per page)."""
    pages: List[str] = []
    for m in _STREAM.finditer(pdf_bytes):
        try:
            body = m.group(1).decode("latin-1")
        except Exception:  # pragma: no cover - defensive
            continue
        lines = [_unescape(t.group("t")) for t in _TJ.finditer(body)]
        pages.append("\n".join(lines))
    return pages


def extract_pages(pdf_bytes: bytes) -> List[str]:
    pages = _pages_from_pdfgen(pdf_bytes)
    if pages:
        return pages
    # Fall back to pypdf for PDFs we didn't generate.
    try:
        import io

        import pypdf  # type: ignore

        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        return [(p.extract_text() or "") for p in reader.pages]
    except Exception:  # pragma: no cover - optional dependency / unparsable
        return []


_MONEY = re.compile(r"\$\s*([\d,]+(?:\.\d+)?)")


def parse_amount(text: str) -> str | None:
    """Return the first currency amount in ``text`` as a plain numeric string."""
    m = _MONEY.search(text)
    if not m:
        return None
    return m.group(1).replace(",", "")


def find_line(pages: List[str], needle: str) -> tuple[int, str] | None:
    """Return (1-based page, line text) of the first line containing ``needle``
    (case-insensitive), or None."""
    low = needle.lower()
    for i, page in enumerate(pages, start=1):
        for line in page.splitlines():
            if low in line.lower():
                return i, line
    return None

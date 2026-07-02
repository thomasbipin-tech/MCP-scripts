"""Minimal, dependency-free PDF writer.

Enough to render the synthetic data-room documents (multi-page text) so the demo
report's evidence drawers deep-link into real, browsable PDFs via PDF.js. This
is NOT the report renderer — production report PDFs use WeasyPrint from the
print-CSS template. This exists so ``make seed-demo`` has genuine source files
on a clean clone with nothing installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

_LEADING = 16
_TOP = 780
_LEFT = 54
_FONT_SIZE = 11


def _esc(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _content_stream(lines: List[str]) -> bytes:
    parts = ["BT", f"/F1 {_FONT_SIZE} Tf", f"{_LEADING} TL", f"{_LEFT} {_TOP} Td"]
    for i, line in enumerate(lines):
        if i == 0:
            parts.append(f"({_esc(line)}) Tj")
        else:
            parts.append(f"T* ({_esc(line)}) Tj")
    parts.append("ET")
    return ("\n".join(parts)).encode("latin-1", "replace")


def write_text_pdf(path: str | Path, pages: List[List[str]]) -> Path:
    """Write a text PDF. ``pages`` is a list of pages, each a list of text lines."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not pages:
        pages = [["(empty document)"]]

    objects: List[bytes] = []

    def add(obj: bytes) -> int:
        objects.append(obj)
        return len(objects)  # 1-indexed object number

    font_num = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    # Reserve the Pages object number so page objects can reference it.
    pages_num = len(objects) + 1 + 2 * len(pages) + 1  # placeholder; fixed below

    page_obj_nums: List[int] = []
    kids: List[int] = []
    # First create content + page objects.
    for lines in pages:
        stream = _content_stream(lines)
        content_num = add(
            b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream)
        )
        page_body = (
            b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>"
        )
        # Parent (pages_num) filled after we know it; use a marker then patch.
        page_num = add(page_body % (0, font_num, content_num))
        page_obj_nums.append(page_num)
        kids.append(page_num)

    kids_str = " ".join(f"{n} 0 R" for n in kids).encode("latin-1")
    real_pages_num = add(
        b"<< /Type /Pages /Kids [%s] /Count %d >>" % (kids_str, len(kids))
    )
    catalog_num = add(b"<< /Type /Catalog /Pages %d 0 R >>" % real_pages_num)

    # Patch each page's /Parent to the real Pages object number.
    for pn in page_obj_nums:
        objects[pn - 1] = objects[pn - 1].replace(
            b"/Parent 0 0 R", b"/Parent %d 0 R" % real_pages_num, 1
        )

    # Serialize with an xref table.
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (len(objects) + 1)
    for i, obj in enumerate(objects, start=1):
        offsets[i] = len(out)
        out += b"%d 0 obj\n" % i
        out += obj
        out += b"\nendobj\n"

    xref_pos = len(out)
    out += b"xref\n"
    out += b"0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for i in range(1, len(objects) + 1):
        out += b"%010d 00000 n \n" % offsets[i]
    out += b"trailer\n<< /Size %d /Root %d 0 R >>\n" % (
        len(objects) + 1,
        catalog_num,
    )
    out += b"startxref\n%d\n%%%%EOF\n" % xref_pos

    path.write_bytes(bytes(out))
    return path

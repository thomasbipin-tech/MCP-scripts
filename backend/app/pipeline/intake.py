"""Stage 0 — intake: hashing, dedupe, page count.

Virus scanning (ClamAV) is a deployment concern wired at the storage boundary;
this module handles the content-addressing that dedupe and audit rely on."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List

from ..services.pdftext import extract_pages


@dataclass
class Intake:
    sha256: str
    page_count: int
    pages: List[str]
    duplicate: bool = False


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def intake_document(data: bytes, seen_hashes: set) -> Intake:
    digest = sha256_bytes(data)
    pages = extract_pages(data)
    return Intake(
        sha256=digest,
        page_count=len(pages),
        pages=pages,
        duplicate=digest in seen_hashes,
    )

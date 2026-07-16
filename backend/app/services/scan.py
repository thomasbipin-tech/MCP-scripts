"""Upload safety gate — runs before an uploaded byte touches storage or the parser.

Two lines of defense a production intake must have and a demo usually skips:

  1. **Content validation** — reject anything that is not a well-formed PDF
     within a size limit, so a renamed executable, an office macro archive, or a
     oversized file never reaches the parser.
  2. **Malware scan** — a pluggable hook that FAILS CLOSED. If a scanner
     (ClamAV) is configured it must pass; if the scan errors we refuse the file
     rather than wave it through. With no scanner configured, content validation
     is the guard and the EICAR test signature is still caught.

``UnsafeUpload`` carries the HTTP status the API should return (422 bad content,
413 too large, 503 scanner unavailable).
"""

from __future__ import annotations

from ..core.config import settings

_PDF_MAGIC = b"%PDF-"

# Signatures we refuse outright even when the file is renamed to .pdf.
_BAD_MAGIC = {
    b"MZ": "Windows executable",
    b"\x7fELF": "Linux executable",
    b"PK\x03\x04": "zip / office archive",
    b"\xca\xfe\xba\xbe": "Mach-O / Java class",
    b"\x1f\x8b": "gzip archive",
    b"#!": "script",
}

# The EICAR anti-malware test string. Lets the malware-rejection path be
# exercised deterministically without a live daemon or a real virus.
_EICAR = rb"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR"


class UnsafeUpload(Exception):
    def __init__(self, reason: str, status: int = 422):
        super().__init__(reason)
        self.reason = reason
        self.status = status


def _max_bytes() -> int:
    return settings.max_upload_mb * 1024 * 1024


def validate_pdf(data: bytes) -> None:
    """Reject empty, oversized, or non-PDF content before parsing."""
    if not data:
        raise UnsafeUpload("empty file")
    if len(data) > _max_bytes():
        raise UnsafeUpload(f"file exceeds the {settings.max_upload_mb} MB limit", status=413)
    head = data[:8]
    for sig, label in _BAD_MAGIC.items():
        if head.startswith(sig):
            raise UnsafeUpload(f"rejected: this looks like a {label}, not a PDF")
    if not head.startswith(_PDF_MAGIC):
        raise UnsafeUpload("not a valid PDF (missing %PDF- header)")


def scan_malware(data: bytes) -> None:
    """Malware check. Catches the EICAR test signature always; delegates to
    ClamAV when configured and fails closed if the scan cannot complete."""
    if _EICAR in data:
        raise UnsafeUpload("rejected: malware signature detected")
    if not settings.clamav_host:
        return  # no scanner configured — content validation is the guard
    try:
        _clamav_instream(settings.clamav_host, settings.clamav_port, data)
    except UnsafeUpload:
        raise
    except Exception as e:  # pragma: no cover - needs a live daemon
        # A configured scanner that errors means we do NOT know the file is
        # safe. Refuse it rather than accept unscanned content.
        raise UnsafeUpload(f"malware scan unavailable: {e}", status=503)


def check_upload(data: bytes) -> None:
    """The single call the API makes: content validation then malware scan."""
    validate_pdf(data)
    scan_malware(data)


def _clamav_instream(host: str, port: int, data: bytes) -> None:  # pragma: no cover
    """Stream the bytes to clamd via the INSTREAM protocol."""
    import socket
    import struct

    with socket.create_connection((host, port), timeout=10) as s:
        s.sendall(b"zINSTREAM\x00")
        # Chunk the payload; clamd wants <length><bytes> frames then a zero frame.
        view = memoryview(data)
        for i in range(0, len(view), 65536):
            chunk = view[i : i + 65536]
            s.sendall(struct.pack("!L", len(chunk)) + chunk)
        s.sendall(struct.pack("!L", 0))
        resp = s.recv(4096)
    if b"FOUND" in resp:
        raise UnsafeUpload("rejected: malware signature detected")

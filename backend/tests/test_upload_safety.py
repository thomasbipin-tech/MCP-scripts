"""Upload safety gate: content validation + malware scan (fail-closed)."""

import pytest

from app.services import scan
from app.services.scan import UnsafeUpload, check_upload

_VALID_PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
_EICAR_IN_PDF = b"%PDF-1.4\n" + rb"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR" + b"\n%%EOF"


def test_valid_pdf_passes():
    check_upload(_VALID_PDF)  # no exception


def test_empty_file_rejected():
    with pytest.raises(UnsafeUpload):
        check_upload(b"")


def test_non_pdf_rejected():
    with pytest.raises(UnsafeUpload) as e:
        check_upload(b"just some text, not a pdf at all")
    assert "PDF" in e.value.reason


def test_renamed_executable_rejected():
    for magic in (b"MZ\x90\x00", b"\x7fELF\x02\x01", b"PK\x03\x04\x14\x00"):
        with pytest.raises(UnsafeUpload):
            check_upload(magic + b"\x00" * 32)


def test_oversized_rejected(monkeypatch):
    monkeypatch.setattr(scan.settings, "max_upload_mb", 0)
    with pytest.raises(UnsafeUpload) as e:
        check_upload(_VALID_PDF)
    assert e.value.status == 413


def test_eicar_signature_rejected():
    with pytest.raises(UnsafeUpload) as e:
        check_upload(_EICAR_IN_PDF)
    assert "malware" in e.value.reason.lower()
    assert e.value.status == 422


# --- API-level -------------------------------------------------------------

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("multipart")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="module")
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _login(client, email):
    t = client.post("/api/auth/request", json={"email": email}).json()["magic_token"]
    return client.post("/api/auth/verify", json={"token": t}).json()["access_token"]


def test_api_rejects_non_pdf_upload(client):
    tok = _login(client, "safety-buyer@example.com")
    h = {"Authorization": f"Bearer {tok}"}
    did = client.post("/api/deals", headers=h, json={"codename": "Safety Co", "vertical": "hvac"}).json()["id"]
    r = client.post(
        f"/api/deals/{did}/documents",
        headers=h,
        files={"file": ("evil.pdf", b"MZ\x90\x00 this is an exe", "application/pdf")},
    )
    assert r.status_code == 422
    assert "PDF" in r.json()["detail"]

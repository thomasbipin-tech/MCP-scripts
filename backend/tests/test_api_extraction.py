"""Full lifecycle over the API: create -> upload PDFs -> process -> publish ->
pay -> read the unlocked report. Exercises the real extraction path end to end.
"""

from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("multipart")
from fastapi.testclient import TestClient  # noqa: E402

DOCS_DIR = Path(__file__).resolve().parents[1].parent / "frontend" / "public" / "demo-docs"


@pytest.fixture(scope="module")
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def _login(client, email):
    t = client.post("/api/auth/request", json={"email": email}).json()["magic_token"]
    return client.post("/api/auth/verify", json={"token": t}).json()["access_token"]


def _ensure_docs():
    if not DOCS_DIR.exists() or not any(DOCS_DIR.glob("*.pdf")):
        from app.seeder.export import main

        main()


def test_upload_process_publish_pay_flow(client):
    _ensure_docs()
    buyer = _login(client, "extract-buyer@example.com")
    hb = {"Authorization": f"Bearer {buyer}"}
    admin = _login(client, "admin@dealproof.test")
    ha = {"Authorization": f"Bearer {admin}"}

    deal = client.post("/api/deals", headers=hb, json={
        "codename": "Extract Co", "vertical": "hvac", "deal_type": "asset",
        "asking_price": "1560000", "claimed_sde": "520000",
    }).json()
    did = deal["id"]

    # Upload every demo PDF.
    uploaded = 0
    for pdf in sorted(DOCS_DIR.glob("*.pdf")):
        with open(pdf, "rb") as fh:
            r = client.post(f"/api/deals/{did}/documents", headers=hb,
                            files={"file": (pdf.name, fh, "application/pdf")})
        assert r.status_code == 200
        if not r.json().get("duplicate"):
            uploaded += 1
    assert uploaded >= 10

    docs = client.get(f"/api/deals/{did}/documents", headers=hb).json()
    assert any(d["doc_type"] == "bank_statement" for d in docs)
    assert any(d["doc_type"] == "lease" for d in docs)

    # Process -> flags computed, report unpublished.
    proc = client.post(f"/api/deals/{did}/process", headers=hb).json()
    assert proc["severity_counts"]["CRITICAL"] == 4

    # Buyer can't see it until published.
    assert client.get(f"/api/deals/{did}/report", headers=hb).status_code == 409

    # Admin publishes.
    assert client.post(f"/api/admin/deals/{did}/publish", headers=ha).json()["published"] is True

    # Published but unpaid -> locked (counts only).
    locked = client.get(f"/api/deals/{did}/report", headers=hb).json()
    assert locked["locked"] is True
    assert locked["severity_counts"]["CRITICAL"] == 4

    # Pay: demo mode returns a payment id we unlock via /simulate (org-scoped).
    checkout = client.post(f"/api/payments/deals/{did}/checkout", headers=hb,
                           json={"tier": "Full Diligence Report"}).json()
    assert checkout["mode"] == "demo"
    r = client.post(f"/api/payments/deals/{did}/simulate", headers=hb,
                    json={"payment_id": checkout["payment_id"]})
    assert r.status_code == 200 and r.json()["paid"] is True

    # Now unlocked with the full report.
    body = client.get(f"/api/deals/{did}/report", headers=hb).json()
    assert body["locked"] is False
    assert body["report"]["severity_counts"]["CRITICAL"] == 4
    rule_ids = {f["rule_id"] for f in body["report"]["flags"]}
    assert {"TT2", "A1", "C22", "D24"} <= rule_ids

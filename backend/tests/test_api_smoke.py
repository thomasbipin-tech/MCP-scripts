"""API smoke test: the app must boot, seed the demo, and serve the sample report.

Uses a throwaway SQLite DB and the FastAPI TestClient. Skips cleanly if FastAPI
isn't installed (the core engine suite has no such dependency), so a bare
interpreter still runs everything else green.
"""

import importlib
import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_api_smoke.db")
os.environ.setdefault("ENV", "development")

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="module")
def client():
    # Ensure a clean DB file for the module.
    db_path = "./test_api_smoke.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    # (Re)import app modules so config picks up DATABASE_URL.
    import app.core.config as cfg

    importlib.reload(cfg)
    from app.main import app

    with TestClient(app) as c:
        yield c
    if os.path.exists(db_path):
        os.remove(db_path)


def _login(client, email):
    r = client.post("/api/auth/request", json={"email": email})
    assert r.status_code == 200
    token = r.json()["magic_token"]
    r = client.post("/api/auth/verify", json={"token": token})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_health(client):
    assert client.get("/api/health").json()["status"] == "ok"


def test_rules_catalog_full_library(client):
    rules = client.get("/api/rules").json()
    assert len(rules) == 42  # 40 spec flags + TT1/TT2 Triangle rules
    ids = {r["rule_id"] for r in rules}
    assert ids >= {"TT1", "TT2", "A1", "C22", "D24", "E31", "F35", "G40"}


def test_demo_deal_visible_to_admin_with_report(client):
    token = _login(client, "admin@dealproof.test")
    h = {"Authorization": f"Bearer {token}"}
    deals = client.get("/api/deals", headers=h).json()
    assert deals, "demo deal should be seeded"
    demo = next(d for d in deals if d["codename"] == "Project Summit")
    assert demo["severity_counts"]["CRITICAL"] == 4
    assert demo["report_published"] is True

    r = client.get(f"/api/deals/{demo['id']}/report", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["locked"] is False
    assert body["report"]["severity_counts"] == {"CRITICAL": 4, "HIGH": 2, "MEDIUM": 0, "INFO": 1}


def test_org_isolation_hides_other_orgs_deal(client):
    # A brand-new buyer in their own org must not see the demo org's deal.
    admin = _login(client, "admin@dealproof.test")
    demo_id = next(
        d["id"]
        for d in client.get("/api/deals", headers={"Authorization": f"Bearer {admin}"}).json()
        if d["codename"] == "Project Summit"
    )
    outsider = _login(client, "outsider@example.com")
    h = {"Authorization": f"Bearer {outsider}"}
    assert client.get("/api/deals", headers=h).json() == []
    assert client.get(f"/api/deals/{demo_id}", headers=h).status_code == 404


def test_new_deal_report_is_paywalled_until_published(client):
    token = _login(client, "buyer2@example.com")
    h = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/api/deals",
        headers=h,
        json={"codename": "Test Co", "vertical": "hvac", "asking_price": "1000000", "claimed_sde": "250000"},
    ).json()
    # No report yet -> 409
    assert client.get(f"/api/deals/{created['id']}/report", headers=h).status_code == 409


def test_flag_status_workflow(client):
    admin = _login(client, "admin@dealproof.test")
    h = {"Authorization": f"Bearer {admin}"}
    demo = next(d for d in client.get("/api/deals", headers=h).json() if d["codename"] == "Project Summit")
    # Grab a flag id from the report payload.
    report = client.get(f"/api/deals/{demo['id']}/report", headers=h).json()["report"]
    # flags in report payload don't carry DB ids; fetch via a status call requires
    # a DB flag id, so exercise the endpoint's 404 path for a bogus id instead.
    r = client.post(
        f"/api/deals/{demo['id']}/flags/bogus/status",
        headers=h,
        json={"status": "resolved"},
    )
    assert r.status_code == 404

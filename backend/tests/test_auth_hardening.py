"""Auth hardening: the magic token is a bearer credential — it must never be
returned in a production response, and production without email must fail loudly."""

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import settings  # noqa: E402


@pytest.fixture(scope="module")
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_dev_exposes_token_for_convenience(client):
    r = client.post("/api/auth/request", json={"email": "dev-user@example.com"})
    assert r.status_code == 200
    assert "magic_token" in r.json()  # development default


def test_production_never_exposes_token_and_fails_without_email(client, monkeypatch):
    # Simulate production with no email provider configured.
    monkeypatch.setattr(settings, "env", "production")
    monkeypatch.setattr(settings, "resend_api_key", "")
    r = client.post("/api/auth/request", json={"email": "prod-user@example.com"})
    # Fails loudly rather than silently stranding the user...
    assert r.status_code == 503
    # ...and under no circumstances leaks the token.
    assert "magic_token" not in r.json()


def test_production_with_email_hides_token(client, monkeypatch):
    monkeypatch.setattr(settings, "env", "production")
    # Pretend an email provider accepted the message.
    monkeypatch.setattr("app.services.email.send_email", lambda *a, **k: True)
    r = client.post("/api/auth/request", json={"email": "prod-user2@example.com"})
    assert r.status_code == 200
    assert "magic_token" not in r.json()

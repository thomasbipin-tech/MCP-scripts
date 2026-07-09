"""Auth: stdlib HMAC-signed tokens (magic-link + session) and access guards.

Deliberately uses only ``hmac``/``hashlib`` — no JWT/cryptography dependency —
so it is portable and has no native-build failure modes. Two token audiences:
``magic`` (short-lived, emailed) and ``session`` (bearer). Org isolation is
enforced by a FastAPI dependency (SPEC §7: "row-level org isolation enforced in
a dependency, not ad hoc in queries").
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models import User
from .config import settings


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _sign(payload: dict) -> str:
    body = _b64e(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(settings.jwt_secret.encode(), body.encode(), hashlib.sha256).digest()
    return f"{body}.{_b64e(sig)}"


def _verify(token: str) -> dict:
    try:
        body, sig = token.split(".", 1)
    except ValueError:
        raise _unauth("malformed token")
    expected = _b64e(
        hmac.new(settings.jwt_secret.encode(), body.encode(), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(sig, expected):
        raise _unauth("bad signature")
    payload = json.loads(_b64d(body))
    if payload.get("exp", 0) < int(time.time()):
        raise _unauth("token expired")
    return payload


def _unauth(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def issue_magic_token(user_id: str) -> str:
    return _sign({"sub": user_id, "aud": "magic", "exp": int(time.time()) + settings.magic_link_ttl})


def issue_session_token(user: User) -> str:
    return _sign(
        {
            "sub": user.id,
            "org": user.org_id,
            "role": user.role,
            "aud": "session",
            "exp": int(time.time()) + 60 * 60 * 24 * 7,
        }
    )


def redeem_magic_token(token: str) -> str:
    payload = _verify(token)
    if payload.get("aud") != "magic":
        raise _unauth("wrong token audience")
    return payload["sub"]


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauth("missing bearer token")
    payload = _verify(authorization.split(" ", 1)[1])
    if payload.get("aud") != "session":
        raise _unauth("not a session token")
    user = db.get(User, payload["sub"])
    if user is None:
        raise _unauth("unknown user")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    return user


def sign_storage_token(key: str) -> str:
    """Short-lived (config TTL) signed token for a storage object, so document
    URLs can be embedded in an <iframe> without leaking access to anyone who
    guesses the key."""
    return _sign({"k": key, "aud": "storage", "exp": int(time.time()) + settings.signed_url_ttl})


def verify_storage_token(key: str, token: str) -> bool:
    try:
        payload = _verify(token)
    except HTTPException:
        return False
    return payload.get("aud") == "storage" and payload.get("k") == key

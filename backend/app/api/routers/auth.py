"""Email magic-link auth (SPEC §1 v1 scope).

In development the magic token is returned in the response (and logged) so the
flow is testable without an email provider; in production it is emailed via
Resend and only the verify step returns a session token.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.security import (
    get_current_user,
    issue_magic_token,
    issue_session_token,
    redeem_magic_token,
)
from ...db.session import get_db
from ...models import Org, User
from ...services import audit
from ..schemas import MagicRequest, MagicVerify, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request")
def request_magic_link(body: MagicRequest, db: Session = Depends(get_db)) -> dict:
    email = body.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        # Self-serve signup: create a personal org + buyer user.
        org = Org(name=f"{email} (personal)", kind="direct")
        db.add(org)
        db.flush()
        user = User(email=email, role="buyer", org_id=org.id)
        db.add(user)
        db.flush()
        audit.record(db, actor=email, action="user.create", entity_type="user", entity_id=user.id, after={"email": email})
    token = issue_magic_token(user.id)
    db.commit()
    resp = {"sent": True, "email": email}
    if settings.env != "production":
        # Dev convenience: hand back the link target so tests/UX can proceed.
        resp["magic_token"] = token
    return resp


@router.post("/verify", response_model=TokenOut)
def verify_magic_link(body: MagicVerify, db: Session = Depends(get_db)) -> TokenOut:
    user_id = redeem_magic_token(body.token)
    user = db.get(User, user_id)
    if user is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="unknown user")
    return TokenOut(access_token=issue_session_token(user))


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return {"id": user.id, "email": user.email, "role": user.role, "org_id": user.org_id}

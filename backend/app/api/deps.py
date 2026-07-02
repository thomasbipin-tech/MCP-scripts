"""Shared route dependencies — notably org-scoped deal access."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..db.session import get_db
from ..models import Deal, User


def get_scoped_deal(
    deal_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Deal:
    """Fetch a deal, enforcing org isolation. Admins may access any deal."""
    deal = db.get(Deal, deal_id)
    if deal is None:
        raise HTTPException(status_code=404, detail="deal not found")
    if user.role != "admin" and deal.org_id != user.org_id:
        # Same 404 as "not found" — never leak existence across orgs.
        raise HTTPException(status_code=404, detail="deal not found")
    return deal

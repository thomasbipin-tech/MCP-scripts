"""Pydantic request/response models for the API layer."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr


class MagicRequest(BaseModel):
    email: str  # EmailStr requires email-validator; keep loose for dev


class MagicVerify(BaseModel):
    token: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DealCreate(BaseModel):
    codename: str
    vertical: str
    state: Optional[str] = None
    asking_price: Optional[str] = None
    claimed_sde: Optional[str] = None
    deal_type: str = "asset"
    entity_name: Optional[str] = None
    tier: Optional[str] = "Full Diligence Report"


class FlagStatusUpdate(BaseModel):
    status: str  # resolved|accepted|disputed|open
    note: Optional[str] = None


class QASubmit(BaseModel):
    human_verdict: str  # approve|edit|suppress
    reason_code: str
    edited_severity: Optional[str] = None
    edited_title: Optional[str] = None


class CheckoutRequest(BaseModel):
    tier: str  # "Snapshot" | "Full Diligence Report"

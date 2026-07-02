"""Stripe checkout + webhook (SPEC §4 / build prompt §6).

Checkout is per-deal one-time payment (Snapshot $499 / Full $2,950). The report
unlocks on the webhook. Stripe is imported lazily so the module loads without
the SDK; when unconfigured, checkout returns a stub URL for local flows."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.security import get_current_user
from ...db.session import get_db
from ...models import Deal, Payment, User
from ...services import audit
from ..deps import get_scoped_deal
from ..schemas import CheckoutRequest

router = APIRouter(prefix="/payments", tags=["payments"])

PRICES = {"Snapshot": Decimal("499.00"), "Full Diligence Report": Decimal("2950.00")}


@router.post("/deals/{deal_id}/checkout")
def checkout(
    body: CheckoutRequest,
    deal: Deal = Depends(get_scoped_deal),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    amount = PRICES.get(body.tier)
    if amount is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=422, detail="unknown tier")
    payment = Payment(deal_id=deal.id, tier=body.tier, amount=amount, status="pending")
    db.add(payment)
    db.flush()
    audit.record(db, actor=user.email, action="payment.checkout", entity_type="payment", entity_id=payment.id, after={"tier": body.tier})

    if not settings.stripe_secret_key:
        # Local/dev: no Stripe configured -> return a stub that the UI can call
        # back to /webhook/simulate to unlock. Never used in production.
        db.commit()
        return {"checkout_url": f"/dev-checkout?payment_id={payment.id}", "stub": True, "amount": str(amount)}

    import stripe  # lazy

    stripe.api_key = settings.stripe_secret_key
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"DealProof — {body.tier} ({deal.codename})"},
                "unit_amount": int(amount * 100),
            },
            "quantity": 1,
        }],
        success_url=f"{settings.frontend_origin}/deals/{deal.id}?paid=1",
        cancel_url=f"{settings.frontend_origin}/deals/{deal.id}",
        metadata={"payment_id": payment.id, "deal_id": deal.id},
    )
    payment.stripe_ref = session.id
    db.commit()
    return {"checkout_url": session.url, "stub": False}


def _unlock(db: Session, payment_id: str) -> bool:
    payment = db.get(Payment, payment_id)
    if payment is None:
        return False
    payment.status = "paid"
    deal = db.get(Deal, payment.deal_id)
    if deal:
        deal.paid = True
    audit.record(db, actor="stripe", action="payment.paid", entity_type="payment", entity_id=payment.id, after={"status": "paid"})
    db.commit()
    return True


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    if settings.stripe_webhook_secret:
        import stripe  # lazy

        try:
            event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
        except Exception:
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail="invalid signature")
        if event["type"] == "checkout.session.completed":
            _unlock(db, event["data"]["object"]["metadata"]["payment_id"])
        return {"received": True}
    # Dev fallback: accept a simple JSON {payment_id} to simulate payment.
    import json

    try:
        data = json.loads(payload or b"{}")
    except json.JSONDecodeError:
        data = {}
    if data.get("payment_id"):
        _unlock(db, data["payment_id"])
    return {"received": True, "dev": True}

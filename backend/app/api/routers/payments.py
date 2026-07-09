"""Payments: per-deal one-time checkout (Snapshot $499 / Full $2,950).

Two clean paths:
  * **Stripe configured** — checkout returns a real Stripe Checkout URL; the
    browser redirects there and the report unlocks on the signed webhook.
  * **Demo (no Stripe key)** — checkout creates a pending payment and returns
    its id; the UI calls the org-scoped `/simulate` endpoint to unlock it. The
    browser never touches the Stripe webhook.
Stripe is imported lazily so the module loads without the SDK."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.security import get_current_user
from ...db.session import get_db
from ...models import Deal, Payment, User
from ...services import audit
from ..deps import get_scoped_deal
from ..schemas import CheckoutRequest, SimulatePayment

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
        raise HTTPException(status_code=422, detail="unknown tier")
    payment = Payment(deal_id=deal.id, tier=body.tier, amount=amount, status="pending")
    db.add(payment)
    db.flush()
    audit.record(db, actor=user.email, action="payment.checkout", entity_type="payment", entity_id=payment.id, after={"tier": body.tier})

    if not settings.stripe_secret_key:
        # Demo mode: hand the UI the payment id to unlock via /simulate.
        db.commit()
        return {"mode": "demo", "payment_id": payment.id, "amount": str(amount), "tier": body.tier}

    import stripe  # lazy

    stripe.api_key = settings.stripe_secret_key
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"DealProofing — {body.tier} ({deal.codename})"},
                "unit_amount": int(amount * 100),
            },
            "quantity": 1,
        }],
        success_url=f"{settings.frontend_origin}/#/deals/{deal.id}?paid=1",
        cancel_url=f"{settings.frontend_origin}/#/deals/{deal.id}",
        metadata={"payment_id": payment.id, "deal_id": deal.id},
    )
    payment.stripe_ref = session.id
    db.commit()
    return {"mode": "stripe", "checkout_url": session.url, "amount": str(amount), "tier": body.tier}


def _unlock(db: Session, payment: Payment, actor: str) -> None:
    payment.status = "paid"
    deal = db.get(Deal, payment.deal_id)
    if deal:
        deal.paid = True
    audit.record(db, actor=actor, action="payment.paid", entity_type="payment", entity_id=payment.id, after={"status": "paid"})
    db.commit()


@router.post("/deals/{deal_id}/simulate")
def simulate_payment(
    body: SimulatePayment,
    deal: Deal = Depends(get_scoped_deal),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Demo-only unlock. Disabled when Stripe is configured (real money must go
    through Stripe's signed webhook)."""
    if settings.stripe_secret_key:
        raise HTTPException(status_code=403, detail="simulate is disabled when Stripe is configured")
    payment = db.get(Payment, body.payment_id)
    if payment is None or payment.deal_id != deal.id:
        raise HTTPException(status_code=404, detail="payment not found for this deal")
    _unlock(db, payment, actor=user.email)
    return {"paid": True, "deal_id": deal.id}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    """Stripe -> us. Requires a signing secret; unsigned calls are rejected."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=400, detail="webhook not configured")
    import stripe  # lazy

    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid signature")
    if event["type"] == "checkout.session.completed":
        pid = event["data"]["object"]["metadata"].get("payment_id")
        payment = db.get(Payment, pid) if pid else None
        if payment:
            _unlock(db, payment, actor="stripe")
    return {"received": True}

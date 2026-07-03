"""Deals CRUD, report retrieval (paywall + publish aware), and flag workflow."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.security import get_current_user
from ...db.session import get_db
from ...models import Deal, FlagRow, Report, User
from ...services import audit
from ..deps import get_scoped_deal
from ..schemas import DealCreate, FlagStatusUpdate

router = APIRouter(prefix="/deals", tags=["deals"])

VALID_FLAG_STATUS = {"open", "resolved", "accepted", "disputed"}


def _deal_out(deal: Deal, db: Session) -> dict:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "INFO": 0}
    for f in db.scalars(select(FlagRow).where(FlagRow.deal_id == deal.id)):
        counts[f.severity] = counts.get(f.severity, 0) + 1
    published = db.scalar(
        select(Report).where(Report.deal_id == deal.id, Report.published_at.is_not(None))
    )
    return {
        "id": deal.id,
        "codename": deal.codename,
        "entity_name": deal.entity_name,
        "vertical": deal.vertical,
        "state": deal.state,
        "asking_price": str(deal.asking_price) if deal.asking_price is not None else None,
        "claimed_sde": str(deal.claimed_sde) if deal.claimed_sde is not None else None,
        "deal_type": deal.deal_type,
        "stage": deal.stage,
        "completeness_score": deal.completeness_score,
        "tier": deal.tier,
        "paid": deal.paid,
        "severity_counts": counts,
        "report_published": published is not None,
    }


@router.get("")
def list_deals(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list:
    q = select(Deal)
    if user.role != "admin":
        q = q.where(Deal.org_id == user.org_id)
    return [_deal_out(d, db) for d in db.scalars(q.order_by(Deal.created_at.desc()))]


@router.post("", status_code=201)
def create_deal(body: DealCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    deal = Deal(
        org_id=user.org_id,
        codename=body.codename,
        entity_name=body.entity_name,
        vertical=body.vertical,
        state=body.state,
        asking_price=Decimal(body.asking_price) if body.asking_price else None,
        claimed_sde=Decimal(body.claimed_sde) if body.claimed_sde else None,
        deal_type=body.deal_type,
        tier=body.tier,
        stage="Uploading",
    )
    db.add(deal)
    db.flush()
    audit.record(db, actor=user.email, action="deal.create", entity_type="deal", entity_id=deal.id, after={"codename": deal.codename})
    db.commit()
    return _deal_out(deal, db)


@router.get("/{deal_id}")
def get_deal(deal: Deal = Depends(get_scoped_deal), db: Session = Depends(get_db)) -> dict:
    return _deal_out(deal, db)


@router.get("/{deal_id}/report")
def get_report(deal: Deal = Depends(get_scoped_deal), db: Session = Depends(get_db)) -> dict:
    """Return the report.

    Gating (SPEC §3.3 / build prompt §6): the report is only visible once an
    admin has published it AND payment has unlocked it. Before payment the flag
    counts are visible but the body is withheld (the frontend blurs it).
    """
    report = db.scalar(
        select(Report).where(Report.deal_id == deal.id).order_by(Report.version.desc())
    )
    if report is None or report.published_at is None:
        raise HTTPException(status_code=409, detail="report not yet published")
    counts = report.payload.get("severity_counts", {})
    if not deal.paid:
        return {"locked": True, "severity_counts": counts, "reason": "payment_required"}
    return {"locked": False, "report": report.payload, "watermark": report.watermark}


@router.get("/{deal_id}/report.pdf")
def get_report_pdf(deal: Deal = Depends(get_scoped_deal), db: Session = Depends(get_db)):
    """WeasyPrint PDF of the report. Same publish + payment gating as the web report."""
    from fastapi.responses import Response

    from ...services.report_pdf import PDFUnavailable, render_pdf

    report = db.scalar(
        select(Report).where(Report.deal_id == deal.id).order_by(Report.version.desc())
    )
    if report is None or report.published_at is None:
        raise HTTPException(status_code=409, detail="report not yet published")
    if not deal.paid:
        raise HTTPException(status_code=402, detail="payment required")
    try:
        pdf = render_pdf(report.payload)
    except PDFUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="dealproof-{deal.codename}.pdf"'},
    )


@router.post("/{deal_id}/flags/{flag_id}/status")
def set_flag_status(
    flag_id: str,
    body: FlagStatusUpdate,
    deal: Deal = Depends(get_scoped_deal),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if body.status not in VALID_FLAG_STATUS:
        raise HTTPException(status_code=422, detail="invalid status")
    flag = db.get(FlagRow, flag_id)
    if flag is None or flag.deal_id != deal.id:
        raise HTTPException(status_code=404, detail="flag not found")
    before = {"status": flag.status, "note": flag.buyer_note}
    flag.status = body.status
    flag.buyer_note = body.note
    audit.record(db, actor=user.email, action="flag.status", entity_type="flag", entity_id=flag.id, before=before, after={"status": flag.status})
    db.commit()
    return {"id": flag.id, "status": flag.status, "note": flag.buyer_note}

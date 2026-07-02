"""Admin console API (SPEC §5): review queue, publish, QA labels, cost view.

Every QA verdict writes a ``qa_labels`` row — the moat table. Reports are not
visible to buyers until an admin publishes."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException

from ...core.security import require_admin
from ...db.base import utcnow
from ...db.session import get_db
from ...models import Deal, FlagRow, LLMCall, QALabel, Report, User
from ...services import audit
from ..schemas import QASubmit

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/review-queue")
def review_queue(admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> list:
    """Deals with an unpublished report awaiting Stage 6 QA."""
    rows = []
    for deal in db.scalars(select(Deal)):
        report = db.scalar(
            select(Report).where(Report.deal_id == deal.id).order_by(Report.version.desc())
        )
        if report is None or report.published_at is not None:
            continue
        rows.append(
            {
                "deal_id": deal.id,
                "codename": deal.codename,
                "stage": deal.stage,
                "sla_due_at": deal.sla_due_at.isoformat() if deal.sla_due_at else None,
                "flag_count": db.scalar(
                    select(func.count()).select_from(FlagRow).where(FlagRow.deal_id == deal.id)
                ),
            }
        )
    return rows


@router.post("/deals/{deal_id}/publish")
def publish_report(deal_id: str, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    deal = db.get(Deal, deal_id)
    if deal is None:
        raise HTTPException(status_code=404, detail="deal not found")
    report = db.scalar(
        select(Report).where(Report.deal_id == deal.id).order_by(Report.version.desc())
    )
    if report is None:
        raise HTTPException(status_code=409, detail="no report to publish")
    report.published_at = utcnow()
    deal.stage = "Report Ready"
    audit.record(db, actor=admin.email, action="report.publish", entity_type="report", entity_id=report.id, after={"published": True})
    db.commit()
    return {"published": True, "report_id": report.id}


@router.post("/flags/{flag_id}/qa")
def submit_qa(flag_id: str, body: QASubmit, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    flag = db.get(FlagRow, flag_id)
    if flag is None:
        raise HTTPException(status_code=404, detail="flag not found")
    if body.human_verdict not in ("approve", "edit", "suppress"):
        raise HTTPException(status_code=422, detail="invalid verdict")

    model_output = {
        "severity": flag.severity,
        "title": flag.title,
        "detail": flag.detail,
        "computed_values": flag.computed_values,
    }
    # Capture the labeled training row BEFORE mutating the flag.
    label = QALabel(
        flag_id=flag.id,
        rule_id=flag.rule_id,
        model_output=model_output,
        human_verdict=body.human_verdict,
        reason_code=body.reason_code,
        created_by=admin.email,
    )
    db.add(label)

    flag.admin_verdict = body.human_verdict
    flag.admin_reason = body.reason_code
    if body.human_verdict == "suppress":
        flag.status = "suppressed"
    if body.human_verdict == "edit":
        if body.edited_severity:
            flag.severity = body.edited_severity
        if body.edited_title:
            flag.title = body.edited_title
    audit.record(db, actor=admin.email, action="flag.qa", entity_type="flag", entity_id=flag.id, after={"verdict": body.human_verdict})
    db.commit()
    return {"flag_id": flag.id, "verdict": body.human_verdict, "label_id": label.id}


@router.get("/deals/{deal_id}/cost")
def deal_cost(deal_id: str, admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    calls = list(db.scalars(select(LLMCall).where(LLMCall.deal_id == deal_id)))
    return {
        "deal_id": deal_id,
        "llm_calls": len(calls),
        "total_cost_usd": round(sum(c.cost_usd for c in calls), 4),
        "total_tokens": sum(c.input_tokens + c.output_tokens for c in calls),
    }

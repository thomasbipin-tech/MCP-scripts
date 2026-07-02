"""Assemble a ``DealContext`` from persisted DB rows (real-deal path).

Reads the ``financial_lines`` table (produced by extraction stages 0-2) back into
engine ``FinancialLine`` objects and reconciles them. Non-statement facts
(customers, contracts, lease, bank signals) are read from any extraction payloads
attached to the deal; in v1 these are populated as those extractors ship, so a
real deal reconciles its financials immediately and gains richer flags as
extraction coverage grows.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..engine.model import FinancialLine, LineCode, PageRef, StatementType
from ..engine.reconcile import reconcile
from ..models import Deal, FinancialLineRow
from ..rules.context import DealContext, DealFacts


def assemble_context_from_db(db: Session, deal_id: str) -> DealContext:
    deal = db.get(Deal, deal_id)
    if deal is None:
        raise ValueError("deal not found")

    lines = []
    for row in db.scalars(select(FinancialLineRow).where(FinancialLineRow.deal_id == deal_id)):
        pr = row.page_ref or {}
        lines.append(
            FinancialLine(
                statement_type=StatementType(row.statement_type),
                period=row.period,
                line_code=LineCode(row.line_code),
                amount=Decimal(str(row.amount)),
                source=PageRef(pr.get("document_id", row.source_doc_id), pr.get("page", 1), pr.get("label", "")),
                entity_name=deal.entity_name or "",
            )
        )

    facts = DealFacts(
        vertical=deal.vertical,
        deal_type=deal.deal_type,
        asking_price=str(deal.asking_price or 0),
        claimed_sde=str(deal.claimed_sde or 0),
    )
    return DealContext(lines=lines, reconciliation=reconcile(lines), facts=facts)

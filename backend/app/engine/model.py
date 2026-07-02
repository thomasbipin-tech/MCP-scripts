"""Normalized financial domain model.

These are the *only* inputs the deterministic engine reads. Extraction (the LLM
stage) is responsible for producing them with page citations; the engine never
re-reads a document. Keeping the model as plain stdlib dataclasses means the
math layer has zero third-party dependencies and its tests are hermetic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from .money import money


class StatementType(str, Enum):
    TAX_RETURN = "tax_return"
    PNL = "pnl"
    BALANCE_SHEET = "balance_sheet"
    BANK_STATEMENT = "bank_statement"


class LineCode(str, Enum):
    """Canonical, source-agnostic line codes.

    Extraction maps each source-specific label (e.g. an 1120-S "gross receipts"
    box, a QuickBooks "Total Income" row, a bank "total deposits") onto exactly
    one of these codes so the reconciliation math is uniform.
    """

    REVENUE = "revenue"
    COGS = "cogs"
    GROSS_PROFIT = "gross_profit"
    OPERATING_EXPENSES = "operating_expenses"
    OFFICER_COMP = "officer_comp"
    RENT_EXPENSE = "rent_expense"
    DEPRECIATION = "depreciation"
    AMORTIZATION = "amortization"
    CAPEX = "capex"
    NET_INCOME = "net_income"
    # Balance sheet
    CURRENT_ASSETS = "current_assets"
    CURRENT_LIABILITIES = "current_liabilities"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    AR_PAST_90 = "ar_past_90"
    INVENTORY = "inventory"
    SHAREHOLDER_LOAN = "shareholder_loan"
    # Bank
    BANK_DEPOSITS = "bank_deposits"


@dataclass(frozen=True)
class PageRef:
    """A pointer back to the source page a value was extracted from.

    Every reported number must be traceable to one of these (SPEC §2.3). The
    frontend deep-links to ``/deals/:id/docs/:document_id#p{page}``.
    """

    document_id: str
    page: int
    label: str = ""  # verbatim source label, e.g. "Gross receipts (1120-S line 1a)"

    def as_dict(self) -> dict:
        return {"document_id": self.document_id, "page": self.page, "label": self.label}


@dataclass(frozen=True)
class FinancialLine:
    """One normalized statement line for one fiscal period.

    Mirrors the ``financial_lines`` table (SPEC §7): the reconciliation engine
    reads ONLY these. ``amount`` is always a 2-dp ``Decimal``.
    """

    statement_type: StatementType
    period: int  # fiscal year, e.g. 2023
    line_code: LineCode
    amount: Decimal
    source: PageRef
    entity_name: str = ""

    def __post_init__(self) -> None:
        # Normalize amount to money once, at construction, so nothing downstream
        # can smuggle in a float or an unrounded Decimal.
        object.__setattr__(self, "amount", money(self.amount))

    def as_evidence(self) -> dict:
        return {
            "statement_type": self.statement_type.value,
            "period": self.period,
            "line_code": self.line_code.value,
            "amount": str(self.amount),
            "source": self.source.as_dict(),
        }


def get_line(
    lines: List[FinancialLine],
    statement_type: StatementType,
    period: int,
    line_code: LineCode,
) -> Optional[FinancialLine]:
    """Return the single line for (statement, period, code) or ``None``.

    If extraction produced duplicates for the same coordinate the amounts are
    summed into a synthetic line — a defensive choice so a duplicated document
    never silently drops a value. (Dedupe by SHA-256 happens upstream at intake;
    this is belt-and-suspenders.)
    """
    matches = [
        ln
        for ln in lines
        if ln.statement_type == statement_type
        and ln.period == period
        and ln.line_code == line_code
    ]
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    combined = sum((m.amount for m in matches), Decimal("0"))
    return FinancialLine(
        statement_type=statement_type,
        period=period,
        line_code=line_code,
        amount=combined,
        source=matches[0].source,
        entity_name=matches[0].entity_name,
    )


def periods_present(lines: List[FinancialLine]) -> List[int]:
    """Sorted list of distinct fiscal years present in the line set."""
    return sorted({ln.period for ln in lines})

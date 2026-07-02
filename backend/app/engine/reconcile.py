"""Stage 3 — deterministic reconciliation (the Triangle of Truth).

NO LLM calls here (SPEC §2.3). This module turns normalized ``FinancialLine``
rows into derived, citable metrics: the three-way revenue reconciliation, gross
margin, working-capital trend, and capex-vs-depreciation trend. The rules engine
(Stage 4) reads these results plus the raw lines; the narrator (Stage 5) reads
the evidence bundle built from them.

Every derived number carries the ``PageRef``s of the source lines it came from,
so the report can trace it back to a document page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

from .model import (
    FinancialLine,
    LineCode,
    PageRef,
    StatementType,
    get_line,
    periods_present,
)
from .money import divergence_pct, money, pct


@dataclass
class TriangleYear:
    """Three-way revenue reconciliation for a single fiscal year.

    ``deposit_coverage_pct`` = bank deposits / reported (P&L) revenue. A value
    materially under 100% means the cash never showed up — the hardest-to-fake
    signal in the whole product.
    """

    period: int
    tax_revenue: Optional[Decimal]
    pnl_revenue: Optional[Decimal]
    bank_deposits: Optional[Decimal]
    tax_vs_pnl_divergence_pct: Optional[Decimal]
    deposit_coverage_pct: Optional[Decimal]
    sources: List[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "period": self.period,
            "tax_revenue": _s(self.tax_revenue),
            "pnl_revenue": _s(self.pnl_revenue),
            "bank_deposits": _s(self.bank_deposits),
            "tax_vs_pnl_divergence_pct": _s(self.tax_vs_pnl_divergence_pct),
            "deposit_coverage_pct": _s(self.deposit_coverage_pct),
            "sources": self.sources,
        }


@dataclass
class YearMetric:
    period: int
    value: Optional[Decimal]
    sources: List[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"period": self.period, "value": _s(self.value), "sources": self.sources}


@dataclass
class ReconciliationResult:
    triangle: List[TriangleYear]
    gross_margin_pct: List[YearMetric]
    working_capital: List[YearMetric]
    capex_vs_depreciation: List[YearMetric]  # value = capex - depreciation
    pnl_revenue: List[YearMetric]
    periods: List[int]

    def latest_period(self) -> Optional[int]:
        return self.periods[-1] if self.periods else None

    def triangle_for(self, period: int) -> Optional[TriangleYear]:
        for t in self.triangle:
            if t.period == period:
                return t
        return None

    def as_dict(self) -> dict:
        return {
            "periods": self.periods,
            "triangle": [t.as_dict() for t in self.triangle],
            "gross_margin_pct": [m.as_dict() for m in self.gross_margin_pct],
            "working_capital": [m.as_dict() for m in self.working_capital],
            "capex_vs_depreciation": [m.as_dict() for m in self.capex_vs_depreciation],
            "pnl_revenue": [m.as_dict() for m in self.pnl_revenue],
        }


def _s(v: Optional[Decimal]) -> Optional[str]:
    return None if v is None else str(v)


def _src(*lines: Optional[FinancialLine]) -> List[dict]:
    return [ln.source.as_dict() for ln in lines if ln is not None]


def reconcile(lines: List[FinancialLine]) -> ReconciliationResult:
    """Compute all derived reconciliation metrics from normalized lines."""
    periods = periods_present(lines)

    triangle: List[TriangleYear] = []
    gross_margin: List[YearMetric] = []
    working_capital: List[YearMetric] = []
    capex_vs_dep: List[YearMetric] = []
    pnl_rev: List[YearMetric] = []

    for yr in periods:
        tax = get_line(lines, StatementType.TAX_RETURN, yr, LineCode.REVENUE)
        pnl = get_line(lines, StatementType.PNL, yr, LineCode.REVENUE)
        bank = get_line(lines, StatementType.BANK_STATEMENT, yr, LineCode.BANK_DEPOSITS)

        tax_amt = tax.amount if tax else None
        pnl_amt = pnl.amount if pnl else None
        bank_amt = bank.amount if bank else None

        # Divergence of tax revenue relative to the P&L baseline. Sellers tend to
        # understate on the tax return (IRS motive) and overstate on the P&L
        # (sale-price motive), so a negative value is the classic pattern.
        tvp = (
            divergence_pct(tax_amt, pnl_amt)
            if (tax_amt is not None and pnl_amt is not None)
            else None
        )
        # Deposit coverage measured against reported (P&L) revenue — the number
        # the seller is asking to be paid on.
        coverage = (
            pct(bank_amt, pnl_amt)
            if (bank_amt is not None and pnl_amt is not None)
            else None
        )
        triangle.append(
            TriangleYear(
                period=yr,
                tax_revenue=tax_amt,
                pnl_revenue=pnl_amt,
                bank_deposits=bank_amt,
                tax_vs_pnl_divergence_pct=tvp,
                deposit_coverage_pct=coverage,
                sources=_src(tax, pnl, bank),
            )
        )

        # Gross margin from the P&L.
        cogs = get_line(lines, StatementType.PNL, yr, LineCode.COGS)
        if pnl_amt is not None and cogs is not None and pnl_amt != 0:
            gm = pct(pnl_amt - cogs.amount, pnl_amt)
            gross_margin.append(YearMetric(yr, gm, _src(pnl, cogs)))
        else:
            gross_margin.append(YearMetric(yr, None, _src(pnl, cogs)))

        pnl_rev.append(YearMetric(yr, pnl_amt, _src(pnl)))

        # Working capital = current assets - current liabilities.
        ca = get_line(lines, StatementType.BALANCE_SHEET, yr, LineCode.CURRENT_ASSETS)
        cl = get_line(
            lines, StatementType.BALANCE_SHEET, yr, LineCode.CURRENT_LIABILITIES
        )
        if ca is not None and cl is not None:
            working_capital.append(
                YearMetric(yr, money(ca.amount - cl.amount), _src(ca, cl))
            )
        else:
            working_capital.append(YearMetric(yr, None, _src(ca, cl)))

        # Capex vs depreciation (starvation signal when persistently negative).
        capex = get_line(lines, StatementType.PNL, yr, LineCode.CAPEX)
        dep = get_line(lines, StatementType.PNL, yr, LineCode.DEPRECIATION)
        if capex is not None and dep is not None:
            capex_vs_dep.append(
                YearMetric(yr, money(capex.amount - dep.amount), _src(capex, dep))
            )
        else:
            capex_vs_dep.append(YearMetric(yr, None, _src(capex, dep)))

    return ReconciliationResult(
        triangle=triangle,
        gross_margin_pct=gross_margin,
        working_capital=working_capital,
        capex_vs_depreciation=capex_vs_dep,
        pnl_revenue=pnl_rev,
        periods=periods,
    )

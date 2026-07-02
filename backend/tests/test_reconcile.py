from decimal import Decimal

from app.engine.model import FinancialLine, LineCode, PageRef, StatementType
from app.engine.reconcile import reconcile


def _pref(doc="d", page=1):
    return PageRef(doc, page, "x")


def _line(st, yr, code, amt):
    return FinancialLine(st, yr, code, amt, _pref())


def test_triangle_divergence_and_coverage():
    lines = [
        _line(StatementType.TAX_RETURN, 2023, LineCode.REVENUE, "980000"),
        _line(StatementType.PNL, 2023, LineCode.REVENUE, "1000000"),
        _line(StatementType.BANK_STATEMENT, 2023, LineCode.BANK_DEPOSITS, "780000"),
    ]
    r = reconcile(lines)
    t = r.triangle_for(2023)
    assert t is not None
    assert t.tax_vs_pnl_divergence_pct == Decimal("-2.0")
    assert t.deposit_coverage_pct == Decimal("78.0")


def test_triangle_missing_sources_are_none_not_zero():
    # Only a P&L present: divergence/coverage must be None (no false 0%).
    lines = [_line(StatementType.PNL, 2023, LineCode.REVENUE, "1000000")]
    r = reconcile(lines)
    t = r.triangle_for(2023)
    assert t.tax_vs_pnl_divergence_pct is None
    assert t.deposit_coverage_pct is None
    assert t.tax_revenue is None and t.bank_deposits is None


def test_gross_margin_and_working_capital_and_capex():
    lines = [
        _line(StatementType.PNL, 2023, LineCode.REVENUE, "1000000"),
        _line(StatementType.PNL, 2023, LineCode.COGS, "600000"),
        _line(StatementType.PNL, 2023, LineCode.CAPEX, "40000"),
        _line(StatementType.PNL, 2023, LineCode.DEPRECIATION, "60000"),
        _line(StatementType.BALANCE_SHEET, 2023, LineCode.CURRENT_ASSETS, "500000"),
        _line(StatementType.BALANCE_SHEET, 2023, LineCode.CURRENT_LIABILITIES, "300000"),
    ]
    r = reconcile(lines)
    assert r.gross_margin_pct[0].value == Decimal("40.0")
    assert r.working_capital[0].value == Decimal("200000.00")
    # capex - depreciation = -20000 (starvation signal)
    assert r.capex_vs_depreciation[0].value == Decimal("-20000.00")


def test_periods_sorted_and_evidence_present():
    lines = [
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "10"),
        _line(StatementType.PNL, 2022, LineCode.REVENUE, "10"),
    ]
    r = reconcile(lines)
    assert r.periods == [2022, 2024]
    assert r.latest_period() == 2024

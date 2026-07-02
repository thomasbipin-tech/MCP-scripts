"""Table-driven per-rule tests: every rule has a fire case AND a no-fire case.

Each test builds the minimal context a rule needs, runs that single rule, and
asserts the flag count and severity. No-fire cases guard against the most
dangerous failure for this product — a false positive that scares a buyer off a
clean deal.
"""

from decimal import Decimal

import pytest

from app.engine.model import FinancialLine, LineCode, PageRef, StatementType
from app.rules.context import (
    AddBack,
    BankSignals,
    Benchmark,
    Channel,
    ContractFact,
    Customer,
    LeaseFact,
    MonthlyRevenue,
    RealEstate,
    Severity,
)
from app.rules.engine import evaluate_rule
from app.rules.registry import RULES_BY_ID
from tests.helpers import make_ctx, pref


def run(rule_id, ctx):
    return evaluate_rule(RULES_BY_ID[rule_id], ctx)


def _line(st, yr, code, amt, doc="d", page=1):
    return FinancialLine(st, yr, code, amt, PageRef(doc, page, "x"))


# --- TT1 tax vs P&L divergence ----------------------------------------------


def test_tt1_fires_and_scales_severity():
    ctx = make_ctx([
        _line(StatementType.TAX_RETURN, 2023, LineCode.REVENUE, "700000"),
        _line(StatementType.PNL, 2023, LineCode.REVENUE, "1000000"),  # -30% -> CRITICAL
    ])
    flags = run("TT1", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.CRITICAL


def test_tt1_silent_within_tolerance():
    ctx = make_ctx([
        _line(StatementType.TAX_RETURN, 2023, LineCode.REVENUE, "970000"),  # -3%
        _line(StatementType.PNL, 2023, LineCode.REVENUE, "1000000"),
    ])
    assert run("TT1", ctx) == []


# --- TT2 deposit shortfall ---------------------------------------------------


def test_tt2_critical_under_80():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.BANK_STATEMENT, 2024, LineCode.BANK_DEPOSITS, "780000"),
    ])
    flags = run("TT2", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.CRITICAL


def test_tt2_high_between_80_and_92():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.BANK_STATEMENT, 2024, LineCode.BANK_DEPOSITS, "880000"),
    ])
    flags = run("TT2", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.HIGH


def test_tt2_silent_at_full_coverage():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.BANK_STATEMENT, 2024, LineCode.BANK_DEPOSITS, "980000"),
    ])
    assert run("TT2", ctx) == []


# --- A1 customer concentration ----------------------------------------------


def test_a1_critical_over_35():
    ctx = make_ctx(
        [_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")],
        customers=[Customer("BigCo", "420000", 2024, pref())],
    )
    flags = run("A1", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.CRITICAL


def test_a1_high_between_20_and_35():
    ctx = make_ctx(
        [_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")],
        customers=[Customer("MidCo", "250000", 2024, pref())],
    )
    flags = run("A1", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.HIGH


def test_a1_silent_when_diversified():
    ctx = make_ctx(
        [_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")],
        customers=[Customer("A", "150000", 2024, pref()), Customer("B", "120000", 2024, pref())],
    )
    assert run("A1", ctx) == []


# --- A2 revenue cliff --------------------------------------------------------


def _months(y2022_amt, y2023_amt):
    m = []
    for mo in range(1, 13):
        m.append(MonthlyRevenue(2023, mo, y2022_amt, pref()))
    for mo in range(1, 13):
        m.append(MonthlyRevenue(2024, mo, y2023_amt, pref()))
    return m


def test_a2_fires_on_ttm_decline():
    ctx = make_ctx(monthly_revenue=_months("100000", "80000"))  # -20%
    flags = run("A2", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.HIGH


def test_a2_silent_when_flat():
    ctx = make_ctx(monthly_revenue=_months("100000", "98000"))  # -2%
    assert run("A2", ctx) == []


def test_a2_silent_without_24_months():
    partial = [MonthlyRevenue(2024, mo, "80000", pref()) for mo in range(1, 13)]
    ctx = make_ctx(monthly_revenue=partial)
    assert run("A2", ctx) == []


# --- A4 one-time revenue -----------------------------------------------------


def test_a4_fires_when_recurring_classified():
    from app.rules.context import OneTimeItem

    ctx = make_ctx(
        [_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")],
        one_time_items=[OneTimeItem("PPP forgiveness", "150000", 2024, True, pref())],
    )
    flags = run("A4", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.CRITICAL  # 15% > 10%


def test_a4_silent_when_properly_excluded():
    from app.rules.context import OneTimeItem

    ctx = make_ctx(
        [_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")],
        one_time_items=[OneTimeItem("Insurance payout", "50000", 2024, False, pref())],
    )
    assert run("A4", ctx) == []


# --- A5 channel dependency ---------------------------------------------------


def test_a5_fires_over_50():
    ctx = make_ctx(
        [_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")],
        channels=[Channel("Amazon", "600000", 2024, pref())],
    )
    assert len(run("A5", ctx)) == 1


def test_a5_silent_when_balanced():
    ctx = make_ctx(
        [_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")],
        channels=[Channel("Amazon", "480000", 2024, pref()), Channel("Web", "300000", 2024, pref())],
    )
    assert run("A5", ctx) == []


# --- B9 add-back magnitude ---------------------------------------------------


def test_b9_critical_over_40():
    ctx = make_ctx(
        claimed_sde="300000",
        addbacks=[AddBack("x", "130000", "owner_salary", True, 2024, pref())],  # 43.3%
    )
    flags = run("B9", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.CRITICAL


def test_b9_high_between_25_and_40():
    ctx = make_ctx(
        claimed_sde="300000",
        addbacks=[AddBack("x", "90000", "owner_salary", True, 2024, pref())],  # 30%
    )
    flags = run("B9", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.HIGH


def test_b9_silent_when_modest():
    ctx = make_ctx(
        claimed_sde="300000",
        addbacks=[AddBack("x", "30000", "owner_salary", True, 2024, pref())],  # 10%
    )
    assert run("B9", ctx) == []


# --- B10 undocumented add-backs ---------------------------------------------


def test_b10_fires_on_undocumented_personal():
    ctx = make_ctx(addbacks=[AddBack("meals", "12000", "personal", False, 2024, pref())])
    assert len(run("B10", ctx)) == 1


def test_b10_silent_when_documented():
    ctx = make_ctx(addbacks=[AddBack("meals", "12000", "personal", True, 2024, pref())])
    assert run("B10", ctx) == []


# --- B12 below-market rent ---------------------------------------------------


def test_b12_fires_when_owner_owns_and_rent_low():
    ctx = make_ctx(real_estate=RealEstate(True, "60000", "120000", pref()))
    assert len(run("B12", ctx)) == 1


def test_b12_silent_when_tenant():
    ctx = make_ctx(real_estate=RealEstate(False, "60000", "120000", pref()))
    assert run("B12", ctx) == []


# --- B14 capex starvation ----------------------------------------------------


def test_b14_fires_on_two_years_starved():
    ctx = make_ctx([
        _line(StatementType.PNL, 2023, LineCode.CAPEX, "10000"),
        _line(StatementType.PNL, 2023, LineCode.DEPRECIATION, "60000"),
        _line(StatementType.PNL, 2024, LineCode.CAPEX, "12000"),
        _line(StatementType.PNL, 2024, LineCode.DEPRECIATION, "62000"),
    ])
    assert len(run("B14", ctx)) == 1


def test_b14_silent_when_reinvesting():
    ctx = make_ctx([
        _line(StatementType.PNL, 2023, LineCode.CAPEX, "70000"),
        _line(StatementType.PNL, 2023, LineCode.DEPRECIATION, "60000"),
        _line(StatementType.PNL, 2024, LineCode.CAPEX, "80000"),
        _line(StatementType.PNL, 2024, LineCode.DEPRECIATION, "62000"),
    ])
    assert run("B14", ctx) == []


# --- C17 working capital -----------------------------------------------------


def test_c17_fires_when_negative():
    ctx = make_ctx([
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.CURRENT_ASSETS, "100000"),
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.CURRENT_LIABILITIES, "150000"),
    ])
    assert len(run("C17", ctx)) == 1


def test_c17_silent_when_healthy():
    ctx = make_ctx([
        _line(StatementType.BALANCE_SHEET, 2023, LineCode.CURRENT_ASSETS, "400000"),
        _line(StatementType.BALANCE_SHEET, 2023, LineCode.CURRENT_LIABILITIES, "300000"),
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.CURRENT_ASSETS, "500000"),
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.CURRENT_LIABILITIES, "300000"),
    ])
    assert run("C17", ctx) == []


# --- C18 A/R aging -----------------------------------------------------------


def test_c18_fires_when_stale():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.ACCOUNTS_RECEIVABLE, "200000"),
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.AR_PAST_90, "50000"),  # 25%
    ])
    assert len(run("C18", ctx)) == 1


def test_c18_silent_when_current():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.ACCOUNTS_RECEIVABLE, "200000"),
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.AR_PAST_90, "20000"),  # 10%
    ])
    assert run("C18", ctx) == []


# --- C21 NSF -----------------------------------------------------------------


def test_c21_fires_on_nsf():
    ctx = make_ctx(bank_signals=BankSignals(nsf_count=3, source=pref()))
    assert len(run("C21", ctx)) == 1


def test_c21_silent_when_clean():
    ctx = make_ctx(bank_signals=BankSignals(nsf_count=0))
    assert run("C21", ctx) == []


# --- C22 MCA -----------------------------------------------------------------


def test_c22_fires_and_is_critical():
    ctx = make_ctx(bank_signals=BankSignals(mca_detected=True, mca_debits=["X"], source=pref()))
    flags = run("C22", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.CRITICAL


def test_c22_silent_when_none():
    ctx = make_ctx(bank_signals=BankSignals(mca_detected=False))
    assert run("C22", ctx) == []


# --- D24 change of control ---------------------------------------------------


def test_d24_fires_on_key_contract():
    ctx = make_ctx(contracts=[ContractFact("BigCo", "customer", True, True, False, "S14", pref())])
    flags = run("D24", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.CRITICAL


def test_d24_silent_when_assignable():
    ctx = make_ctx(contracts=[ContractFact("BigCo", "customer", True, False, True, "S9", pref())])
    assert run("D24", ctx) == []


def test_d24_silent_when_not_key():
    ctx = make_ctx(contracts=[ContractFact("SmallCo", "customer", False, True, False, "S1", pref())])
    assert run("D24", ctx) == []


# --- D25 lease risk ----------------------------------------------------------


def test_d25_fires_on_short_term():
    ctx = make_ctx(lease=LeaseFact(Decimal("2"), True, False, pref()))
    assert len(run("D25", ctx)) == 1


def test_d25_fires_on_personal_guarantee_even_if_long():
    ctx = make_ctx(lease=LeaseFact(Decimal("10"), True, True, pref()))
    assert len(run("D25", ctx)) == 1


def test_d25_silent_when_clean_lease():
    ctx = make_ctx(lease=LeaseFact(Decimal("8"), True, False, pref()))
    assert run("D25", ctx) == []


# --- G39 asking multiple -----------------------------------------------------


def _bm():
    return {"sde_multiple": Benchmark("sde_multiple", Decimal("2.5"), Decimal("3.0"), Decimal("3.7"), 40, "src")}


def test_g39_info_at_median():
    ctx = make_ctx(asking_price="900000", claimed_sde="300000", benchmarks=_bm())  # 3.0x
    flags = run("G39", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.INFO


def test_g39_high_over_1_5x_norm():
    ctx = make_ctx(asking_price="1500000", claimed_sde="300000", benchmarks=_bm())  # 5.0x -> 1.67x median
    flags = run("G39", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.HIGH


def test_g39_silent_without_benchmark():
    ctx = make_ctx(asking_price="900000", claimed_sde="300000", benchmarks={})
    assert run("G39", ctx) == []

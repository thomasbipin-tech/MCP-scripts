"""Fire + no-fire tests for the 25 rules that complete the 40-flag library.

Same discipline as test_rules.py: each rule must fire on its signal and stay
silent without it. Because these rules read fact fields the demo deal leaves
empty, the golden demo (test_seed_golden) still fires exactly six red flags.
"""

from decimal import Decimal

from app.engine.model import FinancialLine, LineCode, PageRef, StatementType
from app.rules.context import (
    AddBack,
    Benchmark,
    ComplianceFacts,
    InvoiceStats,
    PeopleFacts,
    RelatedParty,
    Severity,
    YearAmount,
)
from app.rules.engine import evaluate_rule
from app.rules.registry import RULES_BY_ID
from tests.helpers import make_ctx, pref


def run(rule_id, ctx):
    return evaluate_rule(RULES_BY_ID[rule_id], ctx)


def _line(st, yr, code, amt):
    return FinancialLine(st, yr, code, amt, PageRef("d", 1, "x"))


def test_registry_has_full_library():
    assert len(RULES_BY_ID) == 46  # 40 named + TT1/TT2 + DQ1-DQ4 data-quality


# A3
def test_a3_related_party():
    ctx = make_ctx(related_parties=[RelatedParty("SellerCo LLC", "100000", 2024, "shared owner", pref())])
    assert len(run("A3", ctx)) == 1
    assert run("A3", make_ctx()) == []


# A6
def test_a6_deferred_revenue():
    ctx = make_ctx(compliance=ComplianceFacts(deferred_revenue=[YearAmount(2024, "80000", pref())]))
    assert len(run("A6", ctx)) == 1
    assert run("A6", make_ctx()) == []


# A7
def test_a7_round_number():
    fire = make_ctx(invoice_stats=InvoiceStats(total_count=100, round_count=45, source=pref()))
    assert len(run("A7", fire)) == 1
    quiet = make_ctx(invoice_stats=InvoiceStats(total_count=100, round_count=5, source=pref()))
    assert run("A7", quiet) == []


# A8
def test_a8_seasonality():
    assert len(run("A8", make_ctx(compliance=ComplianceFacts(seasonality_anomaly=True)))) == 1
    assert run("A8", make_ctx(compliance=ComplianceFacts(seasonality_anomaly=None))) == []


# B11
def test_b11_owner_salary_replacement():
    ab = [AddBack("owner comp", "90000", "owner_salary", True, 2024, pref())]
    assert len(run("B11", make_ctx(addbacks=ab, people=PeopleFacts(owner_hours_per_week=55)))) == 1
    # No hours known -> silent (this is why the demo doesn't fire B11)
    assert run("B11", make_ctx(addbacks=ab)) == []


# B13
def test_b13_family_payroll():
    assert len(run("B13", make_ctx(people=PeopleFacts(family_below_market_payroll="40000")))) == 1
    assert run("B13", make_ctx()) == []


# B15
def _gm_bm():
    return {"gross_margin": Benchmark("gross_margin", Decimal("40"), Decimal("45"), Decimal("50"), 30, "src")}


def test_b15_margin_drift():
    lines = [
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.PNL, 2024, LineCode.COGS, "800000"),  # GM 20% -> below band
    ]
    assert len(run("B15", make_ctx(lines, benchmarks=_gm_bm()))) == 1
    in_band = [
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.PNL, 2024, LineCode.COGS, "550000"),  # GM 45% in band
    ]
    assert run("B15", make_ctx(in_band, benchmarks=_gm_bm())) == []


# B16
def test_b16_cogs_reclassification():
    lines = [
        _line(StatementType.PNL, 2023, LineCode.REVENUE, "1000000"),
        _line(StatementType.PNL, 2023, LineCode.COGS, "600000"),  # GM 40%
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.PNL, 2024, LineCode.COGS, "450000"),  # GM 55% -> +15pt swing
    ]
    assert len(run("B16", make_ctx(lines))) == 1
    flat = [
        _line(StatementType.PNL, 2023, LineCode.REVENUE, "1000000"),
        _line(StatementType.PNL, 2023, LineCode.COGS, "600000"),
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.PNL, 2024, LineCode.COGS, "600000"),
    ]
    assert run("B16", make_ctx(flat)) == []


# C19
def test_c19_inventory_bloat():
    lines = [
        _line(StatementType.PNL, 2023, LineCode.REVENUE, "1000000"),
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1050000"),  # +5%
        _line(StatementType.BALANCE_SHEET, 2023, LineCode.INVENTORY, "200000"),
        _line(StatementType.BALANCE_SHEET, 2024, LineCode.INVENTORY, "280000"),  # +40%
    ]
    assert len(run("C19", make_ctx(lines))) == 1
    assert run("C19", make_ctx()) == []


# C20
def test_c20_shareholder_loans():
    lines = [_line(StatementType.BALANCE_SHEET, 2024, LineCode.SHAREHOLDER_LOAN, "75000")]
    assert len(run("C20", make_ctx(lines))) == 1
    assert run("C20", make_ctx()) == []


# C23
def test_c23_undisclosed_debt_service():
    ctx = make_ctx(compliance=ComplianceFacts(undisclosed_debt_service=["Kabbage"]))
    assert len(run("C23", ctx)) == 1
    assert run("C23", make_ctx()) == []


# D26-D30
def test_d26_licenses():
    assert len(run("D26", make_ctx(compliance=ComplianceFacts(non_assignable_licenses=["Liquor"])))) == 1
    assert run("D26", make_ctx()) == []


def test_d27_missing_contracts():
    assert len(run("D27", make_ctx(compliance=ComplianceFacts(missing_top_customer_contracts=["Acme"])))) == 1
    assert run("D27", make_ctx()) == []


def test_d28_litigation():
    assert len(run("D28", make_ctx(compliance=ComplianceFacts(litigation_mentions=["Smith v. Co"])))) == 1
    assert run("D28", make_ctx()) == []


def test_d29_noncompete_only_on_explicit_false():
    assert len(run("D29", make_ctx(compliance=ComplianceFacts(seller_noncompete_ok=False)))) == 1
    assert run("D29", make_ctx(compliance=ComplianceFacts(seller_noncompete_ok=None))) == []
    assert run("D29", make_ctx(compliance=ComplianceFacts(seller_noncompete_ok=True))) == []


def test_d30_franchise():
    assert len(run("D30", make_ctx(compliance=ComplianceFacts(franchise_transfer_restriction=True)))) == 1
    assert run("D30", make_ctx()) == []


# E31-E34
def test_e31_key_person():
    assert len(run("E31", make_ctx(people=PeopleFacts(key_person_roles=["chief technician"])))) == 1
    assert run("E31", make_ctx()) == []


def test_e32_misclassification():
    fire = make_ctx(people=PeopleFacts(count_1099=8, count_w2_typical_roles=2))  # 80%
    assert len(run("E32", fire)) == 1
    quiet = make_ctx(people=PeopleFacts(count_1099=1, count_w2_typical_roles=9))  # 10%
    assert run("E32", quiet) == []


def test_e33_tenure_cliff():
    assert len(run("E33", make_ctx(people=PeopleFacts(near_retirement_count=3)))) == 1
    assert run("E33", make_ctx(people=PeopleFacts(near_retirement_count=1))) == []


def test_e34_missing_insurance():
    assert len(run("E34", make_ctx(compliance=ComplianceFacts(missing_insurance=["workers comp"])))) == 1
    assert run("E34", make_ctx()) == []


# F35-F38
def test_f35_nexus():
    assert len(run("F35", make_ctx(compliance=ComplianceFacts(sales_tax_nexus_states=["CA", "TX"])))) == 1
    assert run("F35", make_ctx()) == []


def test_f36_payroll_tax():
    assert len(run("F36", make_ctx(compliance=ComplianceFacts(payroll_tax_irregularities=True)))) == 1
    assert run("F36", make_ctx()) == []


def test_f37_cash_heavy():
    assert len(run("F37", make_ctx(compliance=ComplianceFacts(cash_heavy_inconsistency=True)))) == 1
    assert run("F37", make_ctx()) == []


def test_f38_erc_severity_scales_with_deal_type():
    asset = make_ctx(deal_type="asset", compliance=ComplianceFacts(aggressive_erc="120000"))
    stock = make_ctx(deal_type="stock", compliance=ComplianceFacts(aggressive_erc="120000"))
    assert run("F38", asset)[0].severity == Severity.MEDIUM
    assert run("F38", stock)[0].severity == Severity.HIGH
    assert run("F38", make_ctx()) == []


# G40
def test_g40_wc_peg_only_on_explicit_false():
    assert len(run("G40", make_ctx(compliance=ComplianceFacts(working_capital_peg_in_loi=False)))) == 1
    assert run("G40", make_ctx(compliance=ComplianceFacts(working_capital_peg_in_loi=None))) == []

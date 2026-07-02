"""Synthetic demo deal: 'Summit Air Mechanical LLC' (HVAC / home services).

Engineered so the rules engine fires EXACTLY six red flags plus one INFO
benchmark, with every other rule deliberately silent. The golden test
(``tests/test_seed_golden.py``) pins this contract so a regression in any
evaluator is caught immediately.

Planted red flags:
    TT2  bank deposits only 78% of 2024 revenue        CRITICAL  (Triangle gap)
    A1   Metro Regional Hospital = 42% of revenue       CRITICAL  (concentration)
    C22  merchant cash advance debits in bank feed      CRITICAL  (hidden distress)
    D24  change-of-control clause on the key contract   CRITICAL  (deal killer)
    B9   add-backs = 30.8% of claimed SDE               HIGH
    D25  lease: 2 yrs left, no assignment, personal gtee HIGH
    G39  asking multiple vs HVAC benchmark              INFO      (always shown)

Deliberately kept silent (documented in the golden test): TT1, A2, A4, A5, B10,
B12, B14, C17, C18, C21.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Tuple

from ..engine.model import FinancialLine, LineCode, PageRef, StatementType
from ..engine.reconcile import reconcile
from ..rules.context import (
    AddBack,
    BankSignals,
    Benchmark,
    Channel,
    ContractFact,
    Customer,
    DealContext,
    DealFacts,
    LeaseFact,
    MonthlyRevenue,
    RealEstate,
)

ENTITY = "Summit Air Mechanical LLC"
CODENAME = "Project Summit"

# Reported (P&L) revenue by year.
PNL_REV = {2022: "2150000", 2023: "2380000", 2024: "2410000"}
# Tax-return revenue ~2% under the P&L each year -> divergence < 5% -> TT1 silent.
TAX_REV = {2022: "2107000", 2023: "2332400", 2024: "2361800"}
# Bank deposits: 2022/2023 healthy (>92% coverage); 2024 only 78% -> TT2 CRITICAL.
BANK_DEP = {2022: "2120000", 2023: "2340000", 2024: "1879800"}
COGS = {2022: "1182500", 2023: "1309000", 2024: "1325500"}  # ~55% of revenue
DEPREC = {2022: "60000", 2023: "62000", 2024: "64000"}
CAPEX = {2022: "70000", 2023: "80000", 2024: "90000"}  # capex > deprec -> B14 silent
CUR_ASSETS = {2022: "450000", 2023: "480000", 2024: "520000"}
CUR_LIABS = {2022: "300000", 2023: "290000", 2024: "300000"}  # WC grows -> C17 silent

CLAIMED_SDE = "520000"
ASKING_PRICE = "1560000"  # 3.0x SDE == HVAC median -> G39 stays INFO


def _doc(kind: str, year: int) -> str:
    return f"doc-{kind}-{year}"


def _financial_lines() -> List[FinancialLine]:
    lines: List[FinancialLine] = []
    for yr in (2022, 2023, 2024):
        # Tax return revenue
        lines.append(
            FinancialLine(
                StatementType.TAX_RETURN, yr, LineCode.REVENUE, TAX_REV[yr],
                PageRef(_doc("tax", yr), 1, "Gross receipts (1120-S line 1a)"), ENTITY,
            )
        )
        # P&L revenue + COGS + capex + depreciation
        lines.append(
            FinancialLine(
                StatementType.PNL, yr, LineCode.REVENUE, PNL_REV[yr],
                PageRef(_doc("pnl", yr), 1, "Total Income"), ENTITY,
            )
        )
        lines.append(
            FinancialLine(
                StatementType.PNL, yr, LineCode.COGS, COGS[yr],
                PageRef(_doc("pnl", yr), 1, "Total Cost of Goods Sold"), ENTITY,
            )
        )
        lines.append(
            FinancialLine(
                StatementType.PNL, yr, LineCode.DEPRECIATION, DEPREC[yr],
                PageRef(_doc("pnl", yr), 2, "Depreciation expense"), ENTITY,
            )
        )
        lines.append(
            FinancialLine(
                StatementType.PNL, yr, LineCode.CAPEX, CAPEX[yr],
                PageRef(_doc("pnl", yr), 2, "Capital expenditures (schedule)"), ENTITY,
            )
        )
        # Bank deposits
        lines.append(
            FinancialLine(
                StatementType.BANK_STATEMENT, yr, LineCode.BANK_DEPOSITS, BANK_DEP[yr],
                PageRef(_doc("bank", yr), 1, "Total deposits and credits (annual)"), ENTITY,
            )
        )
        # Balance sheet
        lines.append(
            FinancialLine(
                StatementType.BALANCE_SHEET, yr, LineCode.CURRENT_ASSETS, CUR_ASSETS[yr],
                PageRef(_doc("bs", yr), 1, "Total current assets"), ENTITY,
            )
        )
        lines.append(
            FinancialLine(
                StatementType.BALANCE_SHEET, yr, LineCode.CURRENT_LIABILITIES, CUR_LIABS[yr],
                PageRef(_doc("bs", yr), 1, "Total current liabilities"), ENTITY,
            )
        )
    # A/R aging for the latest year: 10% past 90 -> C18 silent.
    lines.append(
        FinancialLine(
            StatementType.BALANCE_SHEET, 2024, LineCode.ACCOUNTS_RECEIVABLE, "240000",
            PageRef(_doc("bs", 2024), 2, "Accounts receivable, net"), ENTITY,
        )
    )
    lines.append(
        FinancialLine(
            StatementType.BALANCE_SHEET, 2024, LineCode.AR_PAST_90, "24000",
            PageRef(_doc("ar", 2024), 1, "A/R aging: >90 days bucket"), ENTITY,
        )
    )
    return lines


def _monthly_revenue() -> List[MonthlyRevenue]:
    """24 roughly-flat months (2023-2024) -> no TTM cliff -> A2 silent."""
    months: List[MonthlyRevenue] = []
    plans = {2023: "198333", 2024: "200833"}  # ~ annual/12, gentle growth
    for yr in (2023, 2024):
        for mo in range(1, 13):
            months.append(
                MonthlyRevenue(
                    yr, mo, plans[yr],
                    PageRef(_doc("pnl", yr), 3, f"Monthly revenue {yr}-{mo:02d}"),
                )
            )
    return months


def build_demo_context() -> DealContext:
    lines = _financial_lines()
    recon = reconcile(lines)

    customers = [
        Customer("Metro Regional Hospital", "1012200", 2024,
                 PageRef(_doc("pnl", 2024), 4, "Revenue by customer")),  # 42% -> A1 CRITICAL
        Customer("Downtown Property Group", "361500", 2024,
                 PageRef(_doc("pnl", 2024), 4, "Revenue by customer")),  # 15% -> below 20
        Customer("Riverside School District", "192800", 2024,
                 PageRef(_doc("pnl", 2024), 4, "Revenue by customer")),  # 8%
    ]
    channels = [
        Channel("Residential service", "1156800", 2024,
                PageRef(_doc("pnl", 2024), 5, "Revenue by channel")),  # 48% -> below 50
        Channel("Commercial new-construction", "723000", 2024,
                PageRef(_doc("pnl", 2024), 5, "Revenue by channel")),  # 30%
        Channel("Maintenance contracts", "530200", 2024,
                PageRef(_doc("pnl", 2024), 5, "Revenue by channel")),  # 22%
    ]
    # All documented -> B10 silent; total 160000 / 520000 SDE = 30.8% -> B9 HIGH.
    addbacks = [
        AddBack("Owner compensation normalization", "95000", "owner_salary", True, 2024,
                PageRef(_doc("addbacks", 2024), 1, "SDE add-back schedule")),
        AddBack("One-time legal settlement", "30000", "one_time", True, 2024,
                PageRef(_doc("addbacks", 2024), 1, "SDE add-back schedule")),
        AddBack("Owner auto and travel", "20000", "auto", True, 2024,
                PageRef(_doc("addbacks", 2024), 1, "SDE add-back schedule")),
        AddBack("Owner health insurance", "15000", "personal", True, 2024,
                PageRef(_doc("addbacks", 2024), 1, "SDE add-back schedule")),
    ]
    contracts = [
        ContractFact("Metro Regional Hospital", "customer", True, True, False,
                     "Section 14.3 — assignment triggers termination on change of control",
                     PageRef(_doc("contract-metro", 2024), 6, "Master Services Agreement")),  # D24
        ContractFact("Carrier Distribution Partners", "supplier", True, False, True,
                     "Section 9 — freely assignable",
                     PageRef(_doc("contract-supplier", 2024), 2, "Distributor Agreement")),
        ContractFact("Downtown Property Group", "customer", True, False, True,
                     "Section 7 — assignable with notice",
                     PageRef(_doc("contract-dpg", 2024), 3, "Facilities Agreement")),
    ]
    lease = LeaseFact(  # 2 yrs left, no assignment, personal guarantee -> D25 HIGH
        term_remaining_years=Decimal("2"),
        assignment_allowed=False,
        personal_guarantee=True,
        source=PageRef(_doc("lease", 2024), 1, "Commercial lease — term & assignment"),
    )
    bank_signals = BankSignals(  # MCA present -> C22 CRITICAL; no NSF -> C21 silent
        nsf_count=0,
        mca_detected=True,
        mca_debits=["Rapid Capital Funding", "Fox Capital Group"],
        source=PageRef(_doc("bank", 2024), 3, "Recurring ACH debits — daily remittance"),
    )
    real_estate = RealEstate(seller_owns_operating_property=False)  # B12 silent
    benchmarks = {
        "sde_multiple": Benchmark("sde_multiple", Decimal("2.5"), Decimal("3.0"),
                                  Decimal("3.7"), 42, "DealProof HVAC benchmark set v1"),
    }

    facts = DealFacts(
        vertical="hvac",
        deal_type="asset",
        asking_price=ASKING_PRICE,
        claimed_sde=CLAIMED_SDE,
        customers=customers,
        monthly_revenue=_monthly_revenue(),
        channels=channels,
        addbacks=addbacks,
        one_time_items=[],  # A4 silent
        contracts=contracts,
        lease=lease,
        bank_signals=bank_signals,
        real_estate=real_estate,
        benchmarks=benchmarks,
    )
    return DealContext(lines=lines, reconciliation=recon, facts=facts)


# The contract the golden test enforces.
EXPECTED_RED_FLAGS = {"TT2", "A1", "C22", "D24", "B9", "D25"}
EXPECTED_CRITICAL = {"TT2", "A1", "C22", "D24"}
EXPECTED_INFO = {"G39"}

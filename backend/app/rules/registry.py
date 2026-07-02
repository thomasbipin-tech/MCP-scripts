"""The red-flag rule library as *data*.

SPEC §2.2 / §5 require rules to be data (a versioned ``flag_rules`` row with a
JSONB ``logic_spec`` and ``thresholds``), not hardcoded branches, so the pattern
library can be CRUD-edited and back-tested without a deploy. Each ``RuleDef``
below is exactly that row; ``evaluators.py`` interprets the ``kind`` + thresholds.

v1 launch set = the 15 flags named in the build prompt
(A1 A2 A4 A5 B9 B10 B12 B14 C17 C18 C21 C22 D24 D25 G39) plus the two Triangle
of Truth reconciliation rules from SPEC §2.1 (TT1 tax-vs-P&L divergence, TT2
bank-deposit shortfall) — the core differentiator. Thresholds are copied
verbatim from the spec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .context import Severity


@dataclass(frozen=True)
class RuleDef:
    rule_id: str
    version: int
    category: str
    kind: str  # evaluator key
    default_severity: Severity
    thresholds: Dict[str, object]
    title: str
    buyer_action: str
    ask_seller: List[str]
    what_resolves: str
    vertical_overrides: Dict[str, Dict] = field(default_factory=dict)
    active: bool = True

    def resolved_thresholds(self, vertical: str) -> Dict[str, object]:
        """Thresholds with any per-vertical overrides applied."""
        merged = dict(self.thresholds)
        merged.update(self.vertical_overrides.get(vertical, {}))
        return merged

    def as_row(self) -> dict:
        """Serialize as a ``flag_rules`` DB row (JSONB logic + thresholds)."""
        return {
            "rule_id": self.rule_id,
            "version": self.version,
            "category": self.category,
            "logic_spec": {"kind": self.kind},
            "thresholds": self.thresholds,
            "vertical_overrides": self.vertical_overrides,
            "default_severity": self.default_severity.value,
            "title": self.title,
            "buyer_action": self.buyer_action,
            "ask_seller": self.ask_seller,
            "what_resolves": self.what_resolves,
            "active": self.active,
        }


RULES: List[RuleDef] = [
    # --- Triangle of Truth (SPEC §2.1) --------------------------------------
    RuleDef(
        rule_id="TT1",
        version=1,
        category="Revenue Quality",
        kind="tax_pnl_divergence",
        default_severity=Severity.MEDIUM,
        thresholds={"warn_pct": 5, "high_pct": 10, "critical_pct": 20},
        title="Tax-return revenue diverges from the P&L",
        buyer_action="Reconcile the gap line by line; understated tax revenue signals unreported income risk, overstated P&L signals sale-price inflation.",
        ask_seller=[
            "Why does {year} revenue on the tax return differ from the internal P&L by {divergence}%?",
            "Which figure did you file with the IRS, and can you provide the reconciliation?",
        ],
        what_resolves="A signed reconciliation tying the tax return to the P&L for each year, or a corrected/amended return.",
    ),
    RuleDef(
        rule_id="TT2",
        version=1,
        category="Revenue Quality",
        kind="deposit_shortfall",
        default_severity=Severity.HIGH,
        thresholds={"high_coverage_pct": 92, "critical_coverage_pct": 80},
        title="Bank deposits do not cover reported revenue",
        buyer_action="Cash is the hardest number to fake. Deposits well under claimed revenue mean the revenue may not be real.",
        ask_seller=[
            "Bank deposits in {year} were only {coverage}% of the revenue you reported. Where is the rest of the cash?",
            "Do you accept payment outside these bank accounts? If so, provide those statements.",
        ],
        what_resolves="Complete bank statements for every operating account, reconciled to reported revenue with timing differences itemized.",
    ),
    # --- Category A: Revenue Quality ----------------------------------------
    RuleDef(
        rule_id="A1",
        version=1,
        category="Revenue Quality",
        kind="customer_concentration",
        default_severity=Severity.HIGH,
        thresholds={"high_pct": 20, "critical_pct": 35},
        title="Customer concentration risk",
        buyer_action="Model the deal assuming the top customer leaves within 12 months of close.",
        ask_seller=[
            "What is the written contract term and renewal status for {customer}?",
            "Has {customer} been notified of the sale, and is there a change-of-control clause?",
        ],
        what_resolves="Signed, assignable contracts for the top customers with terms extending past close, plus a reference call.",
    ),
    RuleDef(
        rule_id="A2",
        version=1,
        category="Revenue Quality",
        kind="revenue_cliff",
        default_severity=Severity.HIGH,
        thresholds={"decline_pct": 15},
        title="Trailing-12-month revenue decline masked by annual totals",
        buyer_action="Price on the current run-rate, not the trailing full-year figure.",
        ask_seller=[
            "The most recent 12 months are down {decline}% versus the prior 12. What changed?",
            "Provide month-by-month revenue for the last 24 months.",
        ],
        what_resolves="A credible, documented explanation for the decline and evidence it has stabilized (recent monthly detail).",
    ),
    RuleDef(
        rule_id="A4",
        version=1,
        category="Revenue Quality",
        kind="one_time_revenue",
        default_severity=Severity.HIGH,
        thresholds={"critical_pct_of_revenue": 10},
        title="One-time revenue treated as recurring",
        buyer_action="Strip the one-time items out of revenue before applying any multiple.",
        ask_seller=[
            "Item '{item}' of {amount} looks non-recurring. Why is it in ongoing revenue?",
            "List every PPP, ERC, insurance, grant, or asset-sale amount in each year's revenue.",
        ],
        what_resolves="Revenue restated with one-time items removed, agreed in writing.",
    ),
    RuleDef(
        rule_id="A5",
        version=1,
        category="Revenue Quality",
        kind="channel_dependency",
        default_severity=Severity.HIGH,
        thresholds={"high_pct": 50},
        title="Single-channel revenue dependency",
        buyer_action="Assess platform risk: a policy change or account suspension could end the business.",
        ask_seller=[
            "{channel} accounts for {share}% of revenue. What is your account standing and history there?",
            "What is your contingency if that channel is lost?",
        ],
        what_resolves="Evidence of account health (standing, tenure) and a demonstrated second channel.",
    ),
    # --- Category B: Earnings Quality ---------------------------------------
    RuleDef(
        rule_id="B9",
        version=1,
        category="Earnings Quality",
        kind="addback_magnitude",
        default_severity=Severity.HIGH,
        thresholds={"high_pct": 25, "critical_pct": 40},
        title="Add-backs are a large share of claimed earnings",
        buyer_action="Verify every add-back with documentation; treat unverified ones as real expenses.",
        ask_seller=[
            "Add-backs total {addback_pct}% of claimed SDE. Provide documentation for each.",
            "Which add-backs will genuinely not recur under new ownership?",
        ],
        what_resolves="Line-by-line add-back support (invoices, bank detail) and agreement on which are legitimate.",
    ),
    RuleDef(
        rule_id="B10",
        version=1,
        category="Earnings Quality",
        kind="undocumented_addbacks",
        default_severity=Severity.MEDIUM,
        thresholds={},
        title="Undocumented 'personal expense' add-backs",
        buyer_action="Reject undocumented add-backs from adjusted earnings until proven.",
        ask_seller=[
            "Provide receipts/statements for the personal-expense add-backs totaling {amount}.",
        ],
        what_resolves="Documentation for each personal add-back, or its removal from adjusted SDE.",
    ),
    RuleDef(
        rule_id="B12",
        version=1,
        category="Earnings Quality",
        kind="below_market_rent",
        default_severity=Severity.HIGH,
        thresholds={"below_market_ratio": 0.80},
        title="Below-market rent (seller owns the building)",
        buyer_action="Re-cast earnings at market rent; the post-sale lease will reprice.",
        ask_seller=[
            "Current rent is {rent} but market is ~{market}. What lease terms will a buyer get?",
            "Will you sign a market-rate lease with assignment rights at close?",
        ],
        what_resolves="A market-rate lease commitment with assignment rights, and earnings re-cast to reflect it.",
    ),
    RuleDef(
        rule_id="B14",
        version=1,
        category="Earnings Quality",
        kind="capex_starvation",
        default_severity=Severity.HIGH,
        thresholds={"consecutive_years": 2},
        title="Capex starvation (capex below depreciation)",
        buyer_action="Budget for deferred maintenance/replacement capex in year one.",
        ask_seller=[
            "Capex has been below depreciation for {years} years. What equipment is near end of life?",
            "Provide a fixed-asset register with ages and condition.",
        ],
        what_resolves="A fixed-asset condition report and a realistic near-term capex estimate.",
    ),
    # --- Category C: Cash & Balance Sheet -----------------------------------
    RuleDef(
        rule_id="C17",
        version=1,
        category="Cash & Balance Sheet",
        kind="working_capital_trend",
        default_severity=Severity.MEDIUM,
        thresholds={"decline_pct": 20},
        title="Negative or declining working capital",
        buyer_action="Negotiate a working-capital peg so you don't inherit a cash hole.",
        ask_seller=[
            "Working capital is negative/declining. How is the business funding operations?",
            "What working capital will be delivered at close?",
        ],
        what_resolves="An agreed working-capital target/peg in the LOI and a monthly working-capital history.",
    ),
    RuleDef(
        rule_id="C18",
        version=1,
        category="Cash & Balance Sheet",
        kind="ar_aging",
        default_severity=Severity.HIGH,
        thresholds={"past_90_pct": 15},
        title="Aged accounts receivable",
        buyer_action="Discount stale receivables; they may never collect.",
        ask_seller=[
            "{past_90_pct}% of receivables are past 90 days. Which are collectible?",
            "Provide a detailed A/R aging by customer.",
        ],
        what_resolves="A customer-level A/R aging and a reserve/holdback for uncollectible balances.",
    ),
    RuleDef(
        rule_id="C21",
        version=1,
        category="Cash & Balance Sheet",
        kind="nsf_overdraft",
        default_severity=Severity.MEDIUM,
        thresholds={"count": 1},
        title="Overdraft / NSF events in bank statements",
        buyer_action="Treat NSF events as a liquidity-stress signal; investigate cash timing.",
        ask_seller=[
            "There were {count} NSF/overdraft events. What caused them?",
        ],
        what_resolves="An explanation of each event and evidence the cash-flow issue is resolved.",
    ),
    RuleDef(
        rule_id="C22",
        version=1,
        category="Cash & Balance Sheet",
        kind="mca_factoring",
        default_severity=Severity.CRITICAL,
        thresholds={},
        title="Merchant cash advance / factoring detected (hidden distress)",
        buyer_action="Stop and investigate: MCA/factoring usually signals a business that could not get bank credit.",
        ask_seller=[
            "Bank statements show payments to {lenders}. What is the full balance and payoff of every MCA/factoring facility?",
            "Are there confessions of judgment tied to these advances?",
        ],
        what_resolves="Full disclosure and payoff of all MCA/factoring facilities at or before close.",
    ),
    # --- Category D: Legal & Contracts --------------------------------------
    RuleDef(
        rule_id="D24",
        version=1,
        category="Legal & Contracts",
        kind="change_of_control",
        default_severity=Severity.CRITICAL,
        thresholds={},
        title="Change-of-control clause in a key contract (deal killer)",
        buyer_action="Confirm each key contract survives the sale before wiring earnest money.",
        ask_seller=[
            "The {counterparty} contract has a change-of-control clause. Will they consent to assignment?",
            "Provide written consent-to-assignment for every key contract.",
        ],
        what_resolves="Written counterparty consent to assignment for each affected contract.",
    ),
    RuleDef(
        rule_id="D25",
        version=1,
        category="Legal & Contracts",
        kind="lease_risk",
        default_severity=Severity.HIGH,
        thresholds={"min_term_years": 3},
        title="Lease risk: short term, no assignment, or personal guarantee",
        buyer_action="A location-dependent business needs a long, assignable lease; fix this before close.",
        ask_seller=[
            "The lease has {issues}. Will the landlord extend and permit assignment?",
            "Provide the full lease and any landlord consent.",
        ],
        what_resolves="A lease with adequate remaining term, assignment rights, and no buyer personal guarantee.",
    ),
    # --- Category G: Deal Structure -----------------------------------------
    RuleDef(
        rule_id="G39",
        version=1,
        category="Deal Structure",
        kind="asking_multiple",
        default_severity=Severity.INFO,
        thresholds={"high_ratio_vs_benchmark": 1.5},
        title="Asking multiple versus vertical benchmark",
        buyer_action="Use the benchmark band as a negotiating anchor; a premium multiple needs a documented reason.",
        ask_seller=[
            "The asking multiple is {multiple}x SDE versus a {p50}x benchmark median. What justifies the premium?",
        ],
        what_resolves="A documented rationale for any premium (growth, contracts, moat) or a price adjustment toward the band.",
    ),
]


RULES_BY_ID: Dict[str, RuleDef] = {r.rule_id: r for r in RULES}


def active_rules() -> List[RuleDef]:
    return [r for r in RULES if r.active]

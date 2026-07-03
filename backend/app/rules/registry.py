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
    RuleDef(
        rule_id="G40",
        version=1,
        category="Deal Structure",
        kind="wc_peg_absent",
        default_severity=Severity.MEDIUM,
        thresholds={},
        title="No working-capital peg in the LOI",
        buyer_action="Negotiate a working-capital target so the seller can't strip cash/receivables before close.",
        ask_seller=["Will the LOI include a working-capital peg and a true-up at close?"],
        what_resolves="A working-capital target and true-up mechanism added to the LOI.",
    ),
    # ---- Category A (additional) -------------------------------------------
    RuleDef(
        rule_id="A3", version=1, category="Revenue Quality", kind="related_party_revenue",
        default_severity=Severity.HIGH, thresholds={},
        title="Related-party revenue",
        buyer_action="Exclude related-party sales from run-rate revenue; they may not survive the sale.",
        ask_seller=["Revenue from {name} appears related-party ({note}). Will it continue post-sale at arm's length?"],
        what_resolves="Arm's-length contracts (or removal of the revenue) for each related party.",
    ),
    RuleDef(
        rule_id="A6", version=1, category="Revenue Quality", kind="deferred_revenue",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Deferred revenue is a buyer liability",
        buyer_action="Deferred revenue is work you must perform without new cash — fund it in the deal.",
        ask_seller=["There is {amount} of deferred revenue in {year}. How much unearned work transfers at close?"],
        what_resolves="A deferred-revenue schedule and a purchase-price/working-capital adjustment for it.",
    ),
    RuleDef(
        rule_id="A7", version=1, category="Revenue Quality", kind="round_number",
        default_severity=Severity.MEDIUM, thresholds={"round_ratio_pct": 30},
        title="Improbable frequency of round-number invoices",
        buyer_action="Statistically improbable round invoicing can indicate fabricated revenue — sample and verify.",
        ask_seller=["{round_pct}% of invoices are round amounts. Provide the underlying invoices and bank receipts."],
        what_resolves="A sample of invoices matched to bank deposits confirming the revenue is real.",
    ),
    RuleDef(
        rule_id="A8", version=1, category="Revenue Quality", kind="seasonality_mismatch",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Revenue seasonality inconsistent with the vertical",
        buyer_action="An off-pattern seasonal curve can hide pulled-forward or smoothed revenue.",
        ask_seller=["The monthly revenue pattern is atypical for this vertical. What explains it?"],
        what_resolves="Month-by-month revenue with an explanation reconciling the pattern to bank deposits.",
    ),
    # ---- Category B (additional) -------------------------------------------
    RuleDef(
        rule_id="B11", version=1, category="Earnings Quality", kind="owner_salary_replacement",
        default_severity=Severity.MEDIUM, thresholds={"hours_threshold": 40},
        title="Owner-salary add-back ignores replacement cost",
        buyer_action="A working owner must be replaced; deduct a market manager salary from adjusted earnings.",
        ask_seller=["The owner works {hours} hrs/week but the salary is fully added back. What does a replacement manager cost?"],
        what_resolves="A market replacement-manager salary deducted from adjusted SDE.",
    ),
    RuleDef(
        rule_id="B13", version=1, category="Earnings Quality", kind="family_below_market_payroll",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Family members paid below market (hidden labor cost)",
        buyer_action="Re-cast payroll at market rates; below-market family labor understates true cost.",
        ask_seller=["Family payroll of {amount} looks below market. What would market-rate staff cost?"],
        what_resolves="Payroll re-cast at market rates for family/related roles.",
    ),
    RuleDef(
        rule_id="B15", version=1, category="Earnings Quality", kind="margin_drift",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Gross margin outside the vertical benchmark band",
        buyer_action="Margins away from the benchmark band merit a COGS/pricing review.",
        ask_seller=["Gross margin of {margin}% is outside the {p25}%-{p75}% benchmark band. Why?"],
        what_resolves="A COGS/pricing walk explaining the variance to benchmark.",
    ),
    RuleDef(
        rule_id="B16", version=1, category="Earnings Quality", kind="cogs_reclassification",
        default_severity=Severity.MEDIUM, thresholds={"margin_swing_pts": 8},
        title="Gross-margin swing suggests COGS reclassification",
        buyer_action="A sharp final-year margin jump can be expense-shifting to inflate EBITDA — verify the classification.",
        ask_seller=["Gross margin moved {swing} points into the most recent year. What reclassifications occurred?"],
        what_resolves="A consistent chart of accounts across years and an explanation of any reclassification.",
    ),
    # ---- Category C (additional) -------------------------------------------
    RuleDef(
        rule_id="C19", version=1, category="Cash & Balance Sheet", kind="inventory_bloat",
        default_severity=Severity.MEDIUM, thresholds={"excess_growth_pts": 15},
        title="Inventory growing faster than revenue (write-down risk)",
        buyer_action="Inventory outpacing sales signals obsolescence/write-down risk — inspect and reserve.",
        ask_seller=["Inventory grew {inv_growth}% vs revenue {rev_growth}%. What is aged or obsolete?"],
        what_resolves="An inventory aging report and a write-down reserve for slow-moving stock.",
    ),
    RuleDef(
        rule_id="C20", version=1, category="Cash & Balance Sheet", kind="shareholder_loans",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Loans to/from shareholders on the balance sheet",
        buyer_action="Confirm shareholder loans are settled at close and not a hidden distribution/obligation.",
        ask_seller=["There is a {amount} shareholder loan. Will it be settled at close?"],
        what_resolves="Shareholder loans repaid or cleared at close, documented in the agreement.",
    ),
    RuleDef(
        rule_id="C23", version=1, category="Cash & Balance Sheet", kind="undisclosed_debt_service",
        default_severity=Severity.HIGH, thresholds={},
        title="Undisclosed debt-service payments in bank debits",
        buyer_action="Debt service not on the balance sheet means undisclosed liabilities — reconcile every recurring debit.",
        ask_seller=["Recurring debits to {lenders} aren't in the disclosed debt. What are these obligations?"],
        what_resolves="A complete debt schedule reconciling every recurring bank debit.",
    ),
    # ---- Category D (additional) -------------------------------------------
    RuleDef(
        rule_id="D26", version=1, category="Legal & Contracts", kind="non_assignable_licenses",
        default_severity=Severity.HIGH, thresholds={},
        title="Non-assignable licenses or permits",
        buyer_action="A non-transferable license (liquor, contractor, medical) can stop the business at close.",
        ask_seller=["Are the {licenses} license(s) transferable, and what is the process/timeline?"],
        what_resolves="Confirmation each required license transfers, or a plan to re-license before close.",
    ),
    RuleDef(
        rule_id="D27", version=1, category="Legal & Contracts", kind="missing_top_customer_contracts",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Missing contracts for claimed top customers",
        buyer_action="Unpapered top relationships may be at-will and walk after close.",
        ask_seller=["No contract was provided for {customers}. Are these relationships contracted or at-will?"],
        what_resolves="Signed contracts (or written confirmation of terms) for each claimed top customer.",
    ),
    RuleDef(
        rule_id="D28", version=1, category="Legal & Contracts", kind="litigation",
        default_severity=Severity.HIGH, thresholds={},
        title="Litigation referenced in the documents",
        buyer_action="Quantify exposure and indemnity for any pending or threatened litigation before close.",
        ask_seller=["The documents reference litigation ({matters}). Provide status, exposure, and counsel contact."],
        what_resolves="A litigation schedule with exposure estimates and indemnification in the agreement.",
    ),
    RuleDef(
        rule_id="D29", version=1, category="Legal & Contracts", kind="seller_noncompete",
        default_severity=Severity.HIGH, thresholds={},
        title="Seller non-compete absent or unenforceable",
        buyer_action="Without an enforceable non-compete the seller can reopen and take the customers.",
        ask_seller=["Will the seller sign an enforceable non-compete (scope, geography, term)?"],
        what_resolves="An enforceable seller non-compete executed at close.",
    ),
    RuleDef(
        rule_id="D30", version=1, category="Legal & Contracts", kind="franchise_transfer",
        default_severity=Severity.HIGH, thresholds={},
        title="Franchise agreement transfer restrictions/fees",
        buyer_action="Franchisor consent and transfer fees can gate or reprice the deal — confirm early.",
        ask_seller=["What are the franchisor's transfer approval requirements and fees?"],
        what_resolves="Franchisor consent to transfer and clarity on all transfer fees.",
    ),
    # ---- Category E: People & Operations -----------------------------------
    RuleDef(
        rule_id="E31", version=1, category="People & Operations", kind="key_person_risk",
        default_severity=Severity.HIGH, thresholds={},
        title="Key-person dependency on the owner",
        buyer_action="If the owner holds the key relationships/skills, plan a transition and retention structure.",
        ask_seller=["The owner appears central as {roles}. What is the transition and knowledge-transfer plan?"],
        what_resolves="A documented transition plan and, if needed, an earnout/consulting period.",
    ),
    RuleDef(
        rule_id="E32", version=1, category="People & Operations", kind="worker_misclassification",
        default_severity=Severity.MEDIUM, thresholds={"contractor_ratio_pct": 50},
        title="Worker-misclassification risk (heavy 1099 use)",
        buyer_action="Heavy 1099 use in W-2-typical roles is a back-tax/penalty exposure — assess reclassification cost.",
        ask_seller=["{ratio}% of workers are 1099 in typically-W-2 roles. Has classification been reviewed?"],
        what_resolves="A worker-classification review and quantified reclassification exposure.",
    ),
    RuleDef(
        rule_id="E33", version=1, category="People & Operations", kind="tenure_cliff",
        default_severity=Severity.MEDIUM, thresholds={"count": 2},
        title="Key staff near retirement (tenure cliff)",
        buyer_action="Several key staff nearing retirement is a continuity risk — plan succession.",
        ask_seller=["{count} key staff are near retirement. What is the succession/retention plan?"],
        what_resolves="A succession plan and retention terms for at-risk key staff.",
    ),
    RuleDef(
        rule_id="E34", version=1, category="People & Operations", kind="missing_insurance",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Missing insurance policies for the vertical",
        buyer_action="Gaps in GL/workers-comp/E&O leave you exposed on day one — bind coverage at close.",
        ask_seller=["No {policies} coverage was provided. Is it in force? Provide certificates."],
        what_resolves="Current certificates for all required coverage, bound effective at close.",
    ),
    # ---- Category F: Tax & Compliance --------------------------------------
    RuleDef(
        rule_id="F35", version=1, category="Tax & Compliance", kind="sales_tax_nexus",
        default_severity=Severity.HIGH, thresholds={},
        title="Sales-tax nexus exposure",
        buyer_action="Multi-state sales without filings creates back-tax liability that can transfer — quantify it.",
        ask_seller=["Sales into {states} without matching filings suggest nexus exposure. Has this been assessed?"],
        what_resolves="A nexus study and a reserve/indemnity for any back sales tax.",
    ),
    RuleDef(
        rule_id="F36", version=1, category="Tax & Compliance", kind="payroll_tax_irregularities",
        default_severity=Severity.HIGH, thresholds={},
        title="Payroll-tax deposit irregularities",
        buyer_action="Late/missed payroll-tax deposits carry trust-fund penalties — confirm all filings are current.",
        ask_seller=["Bank activity suggests irregular payroll-tax deposits. Are all 941s and deposits current?"],
        what_resolves="Proof of current payroll-tax filings and deposits (IRS transcripts).",
    ),
    RuleDef(
        rule_id="F37", version=1, category="Tax & Compliance", kind="cash_heavy_inconsistency",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Cash-sales pattern inconsistent with deposits",
        buyer_action="A cash business whose deposits don't match reported cash sales warrants a cash-controls review.",
        ask_seller=["Reported cash sales don't match deposit patterns. Walk through the cash handling process."],
        what_resolves="A cash-reconciliation showing reported cash sales tie to deposits.",
    ),
    RuleDef(
        rule_id="F38", version=1, category="Tax & Compliance", kind="aggressive_erc",
        default_severity=Severity.MEDIUM, thresholds={},
        title="Aggressive ERC claim (clawback risk)",
        buyer_action="An aggressive ERC claim can be clawed back — the risk is higher in a stock deal.",
        ask_seller=["The {amount} ERC claim looks aggressive. Provide the eligibility analysis and preparer."],
        what_resolves="ERC eligibility documentation, and an indemnity/holdback for clawback risk.",
    ),
]


RULES_BY_ID: Dict[str, RuleDef] = {r.rule_id: r for r in RULES}


def active_rules() -> List[RuleDef]:
    return [r for r in RULES if r.active]

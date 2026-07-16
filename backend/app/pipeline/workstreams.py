"""Diligence workstreams — the "command center" view.

Real due diligence spans far more than the financials: commercial/market
research, competitor and customer work, tax, insurance, legal & deal structuring,
background checks, and the owner-transition/key-person question. This module maps
DealProofing's automated findings onto those standard workstreams and, for the
parts a machine can't do, generates the checklist, data-request, and interview
guidance a buyer needs — so the product is a coverage map of the *whole*
engagement, honest about what's automated vs. human-led.

``coverage`` per workstream:
  * ``automated`` — the tool derives findings directly from the documents
  * ``partial``   — some automated signal, but material human work remains
  * ``guided``    — human-led; the tool supplies the checklist and questions
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from ..rules.context import DealContext
from ..engine.money import pct

# key, title, description, coverage, matching flag categories / rule ids, checklist
_WORKSTREAMS = [
    {
        "key": "financial",
        "title": "Financial review",
        "coverage": "automated",
        "description": "Reconcile revenue and earnings across tax returns, the P&L, and bank deposits; test add-backs, margins, working capital and cash.",
        "categories": {"Revenue Quality", "Earnings Quality", "Cash & Balance Sheet", "Data Quality"},
        "checklist": [
            "3 years of business tax returns, P&Ls, and 12 months of bank statements",
            "A/R and A/P aging detail; inventory listing",
            "Add-back schedule with documentation for each item",
            "Trailing-12-month P&L to catch a recent decline",
            "Confirm the Triangle of Truth gaps with the seller",
        ],
    },
    {
        "key": "tax",
        "title": "Tax diligence",
        "coverage": "automated",
        "description": "Surface tax exposures that can transfer to a buyer — sales-tax nexus, payroll-tax irregularities, aggressive ERC claims.",
        "categories": {"Tax & Compliance"},
        "checklist": [
            "Filed sales-tax returns for every state with sales (nexus study)",
            "Payroll-tax (941) transcripts confirming deposits are current",
            "ERC claim eligibility analysis and preparer details",
            "IRS account transcripts; any open audits or notices",
        ],
    },
    {
        "key": "legal",
        "title": "Legal & contract diligence",
        "coverage": "automated",
        "description": "Contracts that could break on sale — change-of-control clauses, non-assignable licenses, litigation, the lease, and non-competes.",
        "categories": {"Legal & Contracts"},
        "checklist": [
            "Written consent-to-assignment for every key customer/supplier contract",
            "Litigation, lien (UCC) and judgment searches on the entity and owner",
            "Confirm all licenses/permits transfer (or plan to re-license)",
            "Full lease with assignment rights and adequate remaining term",
            "Enforceable seller non-compete executed at close",
        ],
    },
    {
        "key": "insurance",
        "title": "Insurance diligence",
        "coverage": "partial",
        "description": "Confirm the coverage a business of this type must carry, and check the claims history.",
        "rule_ids": {"E34"},
        "checklist": [
            "Current certificates: general liability, workers' comp, and E&O where relevant",
            "5-year claims/loss-run history",
            "Coverage limits vs. the risk profile of the vertical",
            "Bind equivalent coverage effective at close",
        ],
    },
    {
        "key": "people",
        "title": "People & owner transition",
        "coverage": "partial",
        "description": "Understand exactly what changes when the owner steps down: who holds the relationships and skills, and how the business runs without them.",
        "categories": {"People & Operations"},
        "checklist": [
            "Org chart with roles, tenure, and compensation",
            "Owner's true weekly hours and every hat they wear (sales, technician, relationships)",
            "Documented transition plan; consulting/earnout period if the owner is central",
            "Retention plan for key staff; identify anyone near retirement",
            "Standard operating procedures for owner-held processes",
        ],
    },
    {
        "key": "customers",
        "title": "Customer diligence & reference calls",
        "coverage": "partial",
        "description": "Test the durability of the revenue directly with the people who pay for it — especially any concentrated accounts.",
        "rule_ids": {"A1", "A5", "D24", "D27"},
        "checklist": [
            "Reference calls with the top customers (see targets below)",
            "Written, assignable contracts for concentrated accounts",
            "Churn/retention history and pipeline",
            "Confirm no customer plans to leave on a change of ownership",
        ],
    },
    {
        "key": "commercial",
        "title": "Commercial & market research",
        "coverage": "guided",
        "description": "Is the market growing, flat, or shrinking? What drives demand, and how exposed is this business to it?",
        "checklist": [
            "Market size and 3–5 year growth trend for the vertical and region",
            "Demand drivers and their outlook (housing, weather, regulation, etc.)",
            "Seasonality vs. the vertical norm",
            "Channel/platform dependency and its risk",
            "Pricing power and how it has moved recently",
        ],
    },
    {
        "key": "competitor",
        "title": "Competitor analysis",
        "coverage": "guided",
        "description": "Who else serves these customers, and why do they choose this business?",
        "checklist": [
            "Identify the top 3–5 competitors and their positioning",
            "Relative pricing and service differentiation",
            "Customer switching costs and barriers to entry",
            "Online reputation vs. competitors (reviews, ratings)",
        ],
    },
    {
        "key": "background",
        "title": "Background & entity checks",
        "coverage": "guided",
        "description": "Verify the seller and the entity are what they claim to be.",
        "checklist": [
            "Owner/principal background and litigation/judgment history",
            "Entity good-standing, corporate records, and cap table",
            "UCC/lien filings and any undisclosed debt",
            "Licensing status and disciplinary history",
        ],
    },
    {
        "key": "structuring",
        "title": "Deal & legal structuring",
        "coverage": "partial",
        "description": "Shape the deal to protect the buyer — price, structure, protections, and financing.",
        "categories": {"Deal Structure"},
        "checklist": [
            "Asset vs. stock deal and purchase-price allocation",
            "Working-capital peg with a true-up at close",
            "Escrow/holdback and indemnification tied to the red flags found",
            "Earnout or seller note where the owner is central",
            "Reps & warranties; financing plan (e.g. SBA 7(a))",
        ],
    },
    # --- Software / SaaS target modules -------------------------------------
    # Honest scoping: these only matter when the target is a software company,
    # and a credible version requires connecting a *real* scanner — not a stub
    # that would give false confidence. Shown as roadmap so the coverage map is
    # complete without ever implying analysis we haven't actually run.
    {
        "key": "code_audit",
        "title": "Code & tech-stack audit",
        "coverage": "roadmap",
        "description": "For software/SaaS targets: source-code security, open-source licence exposure, and structural risk.",
        "checklist": [
            "Software composition analysis (SCA): open-source components and their licences",
            "Known-vulnerability (CVE) scan of dependencies",
            "Static analysis for security defects and hardcoded secrets",
            "Architecture, test coverage, and key-person code ownership review",
            "IP provenance — confirm the company owns/licences all shipped code",
        ],
        "note": (
            "Roadmap module for software targets. DealProofing does not yet run code scanning — "
            "we will not fake it. Until the module ships, pair this checklist with a specialist "
            "(e.g. an SCA/security review) rather than assume coverage."
        ),
    },
    {
        "key": "product_metrics",
        "title": "Product & user-metric audit",
        "coverage": "roadmap",
        "description": "For software/SaaS targets: verify that reported users, activity and retention are real.",
        "checklist": [
            "Separate active users from dead/trial/duplicate accounts in the raw data",
            "Reconcile reported MRR/ARR to the billing system and bank deposits",
            "Cohort retention and churn from event logs, not summary slides",
            "Confirm no bot/synthetic traffic inflates usage metrics",
        ],
        "note": (
            "Roadmap module for software targets. Requires read access to real product telemetry "
            "and the billing system; DealProofing does not infer these from documents alone."
        ),
    },
]

_COVERAGE_LABEL = {
    "automated": "Automated by DealProofing",
    "partial": "Partly automated — human work remains",
    "guided": "Human-led — checklist provided",
    "roadmap": "Software-target module — roadmap",
}


def _interview_targets(ctx: DealContext) -> List[dict]:
    """Top customers to reference-call, with a short script. Drawn from the
    concentration data so the buyer knows exactly who to talk to."""
    period = ctx.reconciliation.latest_period()
    customers = [c for c in ctx.facts.customers if period is None or c.period == period]
    if not customers:
        return []
    base: Optional[Decimal] = None
    for m in ctx.reconciliation.pnl_revenue:
        if m.period == period and m.value:
            base = m.value
            break
    script = [
        "How long have you worked with them, and how did the relationship start?",
        "Is there a written contract, and when does it renew?",
        "How likely are you to stay if the business changes hands?",
        "What would make you leave, and are you considering alternatives?",
    ]
    out = []
    for c in sorted(customers, key=lambda x: x.revenue, reverse=True)[:3]:
        share = pct(c.revenue, base) if base else None
        out.append({
            "name": c.name,
            "revenue": str(c.revenue),
            "share_pct": None if share is None else str(share),
            "script": script,
        })
    return out


def build_workstreams(flags: List[dict], ctx: DealContext) -> List[dict]:
    """Map fired flags onto the diligence workstreams and attach guidance."""
    result = []
    for ws in _WORKSTREAMS:
        cats = ws.get("categories", set())
        rids = ws.get("rule_ids", set())
        matched = [
            {"rule_id": f["rule_id"], "severity": f["severity"], "title": f["title"]}
            for f in flags
            if f["category"] in cats or f["rule_id"] in rids
        ]
        # The legal workstream also inherits the clause-scanner's findings, so the
        # coverage map reflects the deterministic contract review, not just the
        # structured-fact rules.
        if ws["key"] == "legal":
            for cf in ctx.facts.contract_clauses:
                matched.append({
                    "rule_id": "clause",
                    "severity": cf.severity.value,
                    "title": f"{cf.counterparty}: {cf.label}",
                })
        entry = {
            "key": ws["key"],
            "title": ws["title"],
            "description": ws["description"],
            "coverage": ws["coverage"],
            "coverage_label": _COVERAGE_LABEL[ws["coverage"]],
            "findings": matched,
            "finding_count": len(matched),
            "checklist": ws["checklist"],
        }
        if ws.get("note"):
            entry["note"] = ws["note"]
        if ws["key"] == "customers":
            entry["interview_targets"] = _interview_targets(ctx)
        result.append(entry)
    return result

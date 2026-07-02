"""Assemble the full report payload — the single contract consumed by the web
report, the WeasyPrint PDF, and the golden fixture the frontend renders.

Pure functions over a ``DealContext`` + fired flags + narrative. No LLM math."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from ..core.disclaimer import DISCLAIMER, NO_SCORE_POLICY
from ..engine.money import money
from ..rules.context import DealContext, Flag
from ..rules.engine import severity_counts

# Documents we expect for a complete Full report; anything missing becomes a gap.
EXPECTED_DOC_TYPES = {
    "tax_return": "3 years of business tax returns",
    "pnl": "3 years of profit & loss statements",
    "bank_statement": "12 months of bank statements",
    "balance_sheet": "Balance sheets",
    "ar_aging": "Accounts-receivable aging detail",
    "payroll_941": "Payroll tax filings (Form 941)",
    "insurance": "Insurance policies (GL, workers comp, E&O)",
    "lease": "Premises lease",
    "contract_customer": "Top-customer contracts",
}


def build_normalization(ctx: DealContext) -> dict:
    """Claimed SDE -> DealProof-adjusted SDE with a verdict per add-back.

    Deterministic verdicts:
      * documented         -> "Verified"      (retained)
      * undocumented       -> "Undocumented"  (removed from adjusted SDE)
      * owner_salary       -> "Review"        (replacement-cost question; retained
                                               but flagged, never silently removed)
    """
    claimed = ctx.facts.claimed_sde
    removed = Decimal("0")
    rows = []
    for ab in ctx.facts.addbacks:
        if ab.category == "owner_salary":
            verdict = "Review"
        elif ab.documented:
            verdict = "Verified"
        else:
            verdict = "Undocumented"
            removed += ab.amount
        rows.append(
            {
                "description": ab.description,
                "amount": str(ab.amount),
                "category": ab.category,
                "verdict": verdict,
                "source": ab.source.as_dict(),
            }
        )
    adjusted = money(claimed - removed)
    return {
        "claimed_sde": str(claimed),
        "adjusted_sde": str(adjusted),
        "removed_undocumented": str(money(removed)),
        "rows": rows,
        "note": (
            "Add-backs marked 'Review' (e.g. owner compensation) require a "
            "market replacement-cost assessment and are not removed automatically."
        ),
    }


def build_data_gaps(ctx: DealContext) -> List[dict]:
    present_types = set()
    for ln in ctx.lines:
        st = ln.statement_type.value
        present_types.add(st)
    # Map statement types onto expected keys.
    have = set()
    if "tax_return" in present_types:
        have.add("tax_return")
    if "pnl" in present_types:
        have.add("pnl")
    if "bank_statement" in present_types:
        have.add("bank_statement")
    if "balance_sheet" in present_types:
        have.add("balance_sheet")
    # AR aging present if we have an AR_PAST_90 line.
    from ..engine.model import LineCode

    if any(ln.line_code == LineCode.AR_PAST_90 for ln in ctx.lines):
        have.add("ar_aging")
    if ctx.facts.lease is not None:
        have.add("lease")
    if any(c.is_key for c in ctx.facts.contracts):
        have.add("contract_customer")

    gaps = []
    for key, label in EXPECTED_DOC_TYPES.items():
        if key not in have:
            gaps.append({"key": key, "label": label})
    return gaps


def completeness_score(ctx: DealContext) -> int:
    total = len(EXPECTED_DOC_TYPES)
    gaps = len(build_data_gaps(ctx))
    return round((total - gaps) / total * 100)


def build_seller_questions(flags: List[Flag]) -> List[dict]:
    pack = []
    for f in flags:
        for q in f.ask_seller:
            pack.append({"rule_id": f.rule_id, "severity": f.severity.value, "question": q})
    return pack


def assemble_report(
    ctx: DealContext,
    flags: List[Flag],
    narrative: dict,
    deal_meta: dict,
) -> dict:
    """Merge everything into the report payload."""
    narr_by_id = {n["rule_id"]: n for n in narrative.get("flag_narratives", [])}
    flag_payload = []
    for f in flags:
        d = f.as_dict()
        d["narrative"] = narr_by_id.get(f.rule_id, {})
        flag_payload.append(d)

    gaps = build_data_gaps(ctx)
    score = completeness_score(ctx)

    return {
        "deal": deal_meta,
        "policy": {"no_score": NO_SCORE_POLICY},
        "completeness_score": score,
        "watermark": "PRELIMINARY — MATERIAL GAPS" if score < 70 else None,
        "severity_counts": severity_counts(flags),
        "triangle": ctx.reconciliation.as_dict()["triangle"],
        "reconciliation": ctx.reconciliation.as_dict(),
        "flags": flag_payload,
        "normalization": build_normalization(ctx),
        "benchmarks": {
            k: {
                "metric": b.metric,
                "p25": str(b.p25),
                "p50": str(b.p50),
                "p75": str(b.p75),
                "n_deals": b.n_deals,
                "source": b.source,
            }
            for k, b in ctx.facts.benchmarks.items()
        },
        "data_gaps": gaps,
        "seller_question_pack": build_seller_questions(flags),
        "executive_summary": narrative.get("executive_summary", []),
        "narrative": narrative,
        "disclaimer": DISCLAIMER,
    }

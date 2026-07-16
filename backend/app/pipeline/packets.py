"""Expert hand-off packets — the "AI surfaces, your experts decide" layer.

Real diligence ends with humans making the call: a CPA issues the Quality of
Earnings, an M&A attorney rules on the contracts, a lender underwrites the loan.
DealProofing's job is to hand each of them a focused, evidence-cited packet so
they start at the finish line instead of re-reading the data room.

Everything here is assembled deterministically from the report the engine has
already produced — no new numbers are invented, so the packets can never say
something the cited report does not. This is also the honest positioning: the
tool prepares the experts, it does not replace them.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from ..engine.money import money, ratio

_FIN_CATS = {"Revenue Quality", "Earnings Quality", "Cash & Balance Sheet", "Data Quality"}
_LEGAL_CATS = {"Legal & Contracts"}
_DEBT_CATS = {"Cash & Balance Sheet"}


def _by_cat(flags: List[dict], cats: set) -> List[dict]:
    return [f for f in flags if f.get("category") in cats]


def _questions(flags: List[dict], cap: int = 8) -> List[str]:
    seen, out = set(), []
    for f in flags:
        for q in f.get("ask_seller", []) or []:
            if q not in seen:
                seen.add(q)
                out.append(q)
            if len(out) >= cap:
                return out
    return out


def _section(heading: str, items: List[str]) -> Optional[dict]:
    items = [i for i in items if i]
    return {"heading": heading, "items": items} if items else None


def _compact(sections: List[Optional[dict]]) -> List[dict]:
    return [s for s in sections if s]


def _qofe_packet(deal_meta, flags, normalization, triangle, gaps) -> dict:
    recon_items = []
    for p in triangle:
        div = p.get("tax_vs_pnl_divergence_pct")
        cov = p.get("deposit_coverage_pct")
        recon_items.append(
            f"FY{p.get('period')}: tax ${p.get('tax_revenue')} vs P&L ${p.get('pnl_revenue')} "
            f"(divergence {div}%); bank deposits cover {cov}% of booked revenue."
        )

    norm_items = [
        f"Seller-claimed SDE ${normalization.get('claimed_sde')} → DealProofing-adjusted "
        f"${normalization.get('adjusted_sde')} after removing ${normalization.get('removed_undocumented')} "
        "of undocumented add-backs.",
    ]
    for r in normalization.get("rows", []):
        if r.get("verdict") in ("Review", "Undocumented"):
            norm_items.append(
                f"Verify add-back: {r.get('description')} ${r.get('amount')} — currently '{r.get('verdict')}'."
            )

    rq = _by_cat(flags, {"Revenue Quality", "Earnings Quality"})
    cash = _by_cat(flags, {"Cash & Balance Sheet"})
    gap_items = [g.get("label") for g in gaps]

    return {
        "key": "qofe",
        "audience": "CPA / Quality-of-Earnings",
        "title": "Quality-of-Earnings prep packet",
        "purpose": (
            "Everything your CPA needs to scope a QofE: where the three revenue sources diverge, "
            "which earnings adjustments are unproven, and the quality flags to test."
        ),
        "sections": _compact([
            _section("Earnings reconciliation (Triangle of Truth)", recon_items),
            _section("SDE normalization to verify", norm_items),
            _section("Revenue & earnings-quality flags", [f"{f['rule_id']} · {f['title']}" for f in rq]),
            _section("Cash & working-capital flags", [f"{f['rule_id']} · {f['title']}" for f in cash]),
            _section("Data gaps affecting the QofE", gap_items),
        ]),
        "questions": _questions(_by_cat(flags, _FIN_CATS)),
    }


def _attorney_packet(deal_meta, flags, contract_review) -> dict:
    clause_items, consent_items, clause_questions = [], [], []
    if contract_review:
        for c in contract_review.get("contracts", []):
            labels = ", ".join(sorted({f["label"] for f in c["findings"]}))
            clause_items.append(
                f"{c['counterparty']} ({c['doc_type'].replace('contract_', '').replace('_', ' ')}): "
                f"{len(c['findings'])} clause risk(s), highest {c['highest_severity']} — {labels}."
            )
            types = {f["clause_type"] for f in c["findings"]}
            if types & {"change_of_control", "non_assignable"}:
                consent_items.append(
                    f"{c['counterparty']}: obtain written consent-to-assignment (or novation) as a closing condition."
                )
                clause_questions.append(
                    f"Will {c['counterparty']} consent to assignment of its contract on the change of ownership?"
                )

    legal_flags = _by_cat(flags, _LEGAL_CATS)
    searches = [
        "UCC / lien search on the entity and owner (undisclosed secured debt).",
        "Litigation and judgment search (entity, owner, key principals).",
        "Entity good-standing, corporate records and cap-table confirmation.",
        "Confirm every license/permit transfers, or plan to re-license before close.",
    ]
    covenants = ["Ensure an enforceable seller non-compete is executed at closing."]

    return {
        "key": "attorney",
        "audience": "M&A attorney",
        "title": "Legal review packet",
        "purpose": (
            "The contracts and clauses your attorney should rule on — each quoted from the "
            "document and page-cited — plus the searches and protections to put in place."
        ),
        "sections": _compact([
            _section("Contract clause risks (see contract review for quotes)", clause_items),
            _section("Consents / novations required before close", consent_items),
            _section("Legal & contract flags", [f"{f['rule_id']} · {f['title']}" for f in legal_flags]),
            _section("Searches to run", searches),
            _section("Restrictive covenants", covenants),
        ]),
        "questions": (clause_questions + _questions(legal_flags))[:8],
    }


def _lender_packet(deal_meta, flags, normalization, severity_counts, ctx) -> dict:
    asking = money(deal_meta.get("asking_price") or "0")
    adjusted = money(normalization.get("adjusted_sde") or "0")
    mult = ratio(asking, adjusted)
    snapshot = [
        f"Asking price: ${asking}.",
        f"Seller-claimed SDE ${normalization.get('claimed_sde')}; DealProofing-adjusted SDE ${adjusted}.",
        (f"Implied multiple on adjusted SDE: {mult}×." if mult is not None else
         "Adjusted SDE is non-positive — the implied multiple is not meaningful; underwrite with care."),
    ]

    debt_flags = _by_cat(flags, _DEBT_CATS)
    bank = ctx.facts.bank_signals
    debt_items = [f"{f['rule_id']} · {f['title']}" for f in debt_flags]
    if bank and bank.mca_detected:
        debt_items.append(
            "Merchant-cash-advance daily ACH remittances detected — these reduce free cash flow "
            "and depress DSCR; confirm payoff at or before close."
        )

    lease = ctx.facts.lease
    collateral = []
    if lease is not None:
        term = lease.term_remaining_years
        collateral.append(
            f"Premises lease: {term if term is not None else 'unknown'} years remaining"
            + ("; assignment restricted" if lease.assignment_allowed is False else "")
            + ("; personal guarantee present" if lease.personal_guarantee else "")
            + "."
        )
    collateral.append("Confirm FF&E / equipment schedule and any titled assets for collateral coverage.")

    sev = severity_counts
    return {
        "key": "lender",
        "audience": "SBA / acquisition lender",
        "title": "Lender package",
        "purpose": (
            "A one-look underwriting brief: valuation snapshot, the cash-flow and debt items that "
            "move DSCR, collateral, and the red-flag summary."
        ),
        "sections": _compact([
            _section("Deal snapshot", snapshot),
            _section("Cash-flow & debt risks (DSCR)", debt_items),
            _section("Collateral & lease", collateral),
            _section("Red-flag summary", [
                f"{sev.get('CRITICAL', 0)} critical, {sev.get('HIGH', 0)} high, "
                f"{sev.get('MEDIUM', 0)} medium, {sev.get('INFO', 0)} informational."
            ]),
        ]),
        "questions": [
            "Provide 3 years of tax returns and interim financials to the lender.",
            "Confirm any MCA / short-term debt will be paid off at close.",
            "Prepare a debt-service coverage projection on the adjusted SDE.",
        ],
    }


def build_expert_packets(deal_meta, flags, normalization, contract_review, triangle, gaps, severity_counts, ctx) -> dict:
    """Assemble all three expert hand-off packets from the finished report."""
    return {
        "qofe": _qofe_packet(deal_meta, flags, normalization, triangle, gaps),
        "attorney": _attorney_packet(deal_meta, flags, contract_review),
        "lender": _lender_packet(deal_meta, flags, normalization, severity_counts, ctx),
    }

"""Deterministic contract clause-risk scanner (Stage 2.5).

The legal analog of the Triangle of Truth: instead of an LLM "reading" a
contract and hoping it flags the right thing, this scans the contract text for a
fixed catalog of clause risks a small-business buyer must know about —
change-of-control, non-assignability, personal guarantees, auto-renewal,
exclusivity, termination-for-convenience, non-competes, most-favored-nation and
uncapped liability.

Every finding is:
  * **deterministic** — the same contract always yields the same findings,
  * **grounded** — it quotes the contract's own words and cites the page, so a
    buyer's attorney can verify it in seconds and it can never be hallucinated,
  * **explained** — why it matters to a buyer and what to do about it.

It does not give legal advice; it surfaces the clauses an M&A attorney should
review, and packages them (see ``packets.py``) for exactly that hand-off.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from ..engine.model import PageRef
from ..rules.context import ClauseFinding, Severity

# A clause carries a base severity, optionally escalated by contract kind: a
# change-of-control termination in a *customer* contract can vaporize revenue on
# the sale itself, so it is CRITICAL there but merely HIGH with a supplier.
_S = Severity


def _sev(entry: dict, doc_type: str) -> Severity:
    table = entry["severity"]
    return table.get(doc_type, table["default"])


# clause_type, label, patterns, per-doc-type severity, risk, buyer_action.
# Patterns are lowercase regexes; [^.] spans (incl. newlines) tolerate wrapping.
_CATALOG: List[dict] = [
    {
        "clause_type": "change_of_control",
        "label": "Change-of-control / anti-assignment on sale",
        "patterns": [
            r"change (of|in) control",
            r"sale of substantially all",
            r"transfer of (a )?controlling interest",
        ],
        "severity": {"default": _S.HIGH, "contract_customer": _S.CRITICAL},
        "risk": (
            "The contract can terminate — or requires the counterparty's consent — the "
            "moment the business is sold. For a concentrated customer, the revenue you are "
            "paying for may not survive the closing you are paying for it at."
        ),
        "buyer_action": (
            "Get written consent-to-assignment (or a novation) signed as a condition of "
            "closing. Treat it as a deal gate, not a post-close cleanup item."
        ),
    },
    {
        "clause_type": "non_assignable",
        "label": "Non-assignable (consent may be withheld)",
        "patterns": [
            r"(may|shall|will) not be assigned",
            r"(may|shall|will) not assign",
            r"not assignable",
            r"non-assignable",
            r"not (be )?permitted without",
            r"sole discretion",
            r"may be withheld",
        ],
        "severity": {"default": _S.HIGH, "contract_customer": _S.CRITICAL},
        "risk": (
            "Assignment is blocked or gated by a consent the counterparty can refuse. In an "
            "asset deal the contract does not transfer to you automatically — without consent "
            "you may not inherit it at all."
        ),
        "buyer_action": (
            "Obtain the counterparty's written consent before close. If consent is "
            "'at sole discretion', assume it may be refused and price/structure accordingly."
        ),
    },
    {
        "clause_type": "assignment_consent",
        "label": "Assignment allowed with notice/consent",
        "patterns": [
            r"assignable with",
            r"assign[^.]{0,40}(written notice|written consent)",
            r"consent[^.]{0,40}not (be )?unreasonably withheld",
        ],
        "severity": {"default": _S.MEDIUM},
        "risk": (
            "The contract can be assigned to you, but only after giving notice or obtaining "
            "consent — a procedural hurdle that must be completed correctly to keep it in force."
        ),
        "buyer_action": "Complete the notice/consent step before or at close and keep the signed record.",
    },
    {
        "clause_type": "termination_for_convenience",
        "label": "Termination for convenience",
        "patterns": [
            r"terminate[^.]{0,60}(without cause|for convenience|for any reason|no reason)",
            r"terminate[^.]{0,40}upon\s+\d+\s+days",
        ],
        "severity": {"default": _S.MEDIUM, "contract_customer": _S.HIGH},
        "risk": (
            "The counterparty can walk away on short notice for any reason. Revenue under this "
            "contract is not contracted revenue — it is at-will."
        ),
        "buyer_action": "Discount the durability of this revenue; confirm the real notice period and history of use.",
    },
    {
        "clause_type": "auto_renewal",
        "label": "Auto-renewal / evergreen term",
        "patterns": [
            r"automatically renew",
            r"auto-?renew",
            r"evergreen",
            r"renew[^.]{0,40}unless[^.]{0,40}notice",
        ],
        "severity": {"default": _S.MEDIUM},
        "risk": (
            "The term rolls over automatically unless notice is given in a specific window — a "
            "trap that can silently lock the business (or a customer) in or out."
        ),
        "buyer_action": "Diary every renewal/notice date; confirm which party benefits and whether it survives the sale.",
    },
    {
        "clause_type": "exclusivity",
        "label": "Exclusivity / exclusive dealing",
        "patterns": [
            r"exclusiv",
            r"sole (supplier|provider|source)",
        ],
        "severity": {"default": _S.MEDIUM, "contract_supplier": _S.HIGH},
        "risk": (
            "The business is locked to a single counterparty. With a supplier that is "
            "concentration and pricing-power risk; with a customer it can block competing revenue."
        ),
        "buyer_action": "Map the dependency and any alternate sources; test pricing exposure over the remaining term.",
    },
    {
        "clause_type": "personal_guarantee",
        "label": "Personal guarantee",
        "patterns": [
            r"personally guarant",
            r"personal guarant",
            r"guarant[^.]{0,25}personally",
        ],
        "severity": {"default": _S.HIGH},
        "risk": (
            "An obligation is personally guaranteed by the current owner. That guarantee does "
            "not transfer to you — the counterparty (e.g. a landlord) will want a new guarantee, "
            "which may fall on you personally."
        ),
        "buyer_action": "Negotiate release of the seller's guarantee and understand what the counterparty will require from you.",
    },
    {
        "clause_type": "non_compete",
        "label": "Non-compete / restrictive covenant",
        "patterns": [
            r"non-?compete",
            r"covenant not to compete",
            r"shall not (directly or indirectly )?compete",
        ],
        "severity": {"default": _S.MEDIUM},
        "risk": (
            "A non-compete binds the business or its people. Confirm it protects you post-close "
            "(a seller non-compete is an asset) rather than constraining the business you are buying."
        ),
        "buyer_action": "Confirm scope, geography and term; ensure an enforceable seller non-compete is executed at close.",
    },
    {
        "clause_type": "most_favored_nation",
        "label": "Most-favored-nation pricing",
        "patterns": [
            r"most[- ]favored",
            r"\bmfn\b",
        ],
        "severity": {"default": _S.MEDIUM},
        "risk": "An MFN clause caps what you can charge this customer relative to others, limiting future pricing power.",
        "buyer_action": "Model the pricing constraint across the customer base; factor it into the growth thesis.",
    },
    {
        "clause_type": "uncapped_liability",
        "label": "Uncapped / unlimited liability",
        "patterns": [
            r"unlimited liability",
            r"liability[^.]{0,40}(not (be )?limited|without limitation|uncapped)",
        ],
        "severity": {"default": _S.HIGH},
        "risk": "Liability under the contract is not capped, exposing the business to open-ended claims you would inherit.",
        "buyer_action": "Have counsel quantify the exposure and seek a liability cap or indemnity protection.",
    },
]

# Benign signals that must suppress the non-assignment finding: a contract that
# is explicitly freely assignable is a *good* thing, not a risk.
_ASSIGN_OK = re.compile(r"freely assignable|assignable by either party", re.I)


def _locate(pages: List[str], pattern: re.Pattern) -> Optional[tuple]:
    """First (page_number, snippet) where the pattern matches. Snippet is the
    surrounding sentence, whitespace-collapsed, so the quote reads cleanly."""
    for idx, page in enumerate(pages, start=1):
        m = pattern.search(page)
        if not m:
            continue
        start = page.rfind(".", 0, m.start())
        end = page.find(".", m.end())
        seg = page[(start + 1 if start != -1 else 0) : (end if end != -1 else len(page))]
        snippet = re.sub(r"\s+", " ", seg).strip()
        if len(snippet) > 240:
            snippet = snippet[:237].rstrip() + "…"
        return idx, snippet
    return None


def scan_document_clauses(doc_type: str, pages: List[str], doc_id: str, title: str = "") -> List[ClauseFinding]:
    """Scan one contract/lease document for every catalogued clause risk."""
    if doc_type not in ("contract_customer", "contract_supplier", "lease"):
        return []
    joined = "\n".join(pages)
    counterparty = _counterparty(doc_type, title, joined)
    assign_ok = bool(_ASSIGN_OK.search(joined))

    findings: List[ClauseFinding] = []
    for entry in _CATALOG:
        # A freely-assignable contract is good news — never flag it as blocked.
        if entry["clause_type"] in ("non_assignable", "assignment_consent") and assign_ok:
            continue
        for raw in entry["patterns"]:
            pat = re.compile(raw, re.I)
            loc = _locate(pages, pat)
            if loc is None:
                continue
            page, snippet = loc
            findings.append(
                ClauseFinding(
                    clause_type=entry["clause_type"],
                    label=entry["label"],
                    severity=_sev(entry, doc_type),
                    counterparty=counterparty,
                    doc_type=doc_type,
                    quote=snippet,
                    risk=entry["risk"],
                    buyer_action=entry["buyer_action"],
                    source=PageRef(doc_id, page, entry["label"]),
                )
            )
            break  # one finding per clause type per document
    return findings


def _counterparty(doc_type: str, title: str, text: str) -> str:
    if doc_type == "lease":
        return title or "Premises lease"
    # Prefer a proper name after "and" (…Agreement between X and <Counterparty>).
    m = re.search(r"\band\s+([A-Z][\w &.\-]{2,60})", text)
    if m:
        return m.group(1).strip()
    if title:
        return re.sub(r"^.*?—\s*", "", title).strip() or title
    return "Counterparty"


def build_contract_review(findings: List[ClauseFinding]) -> Optional[dict]:
    """Group clause findings by contract into the report's contract-review
    section. Returns ``None`` when no contracts were analysed at all, so the
    report can omit the section rather than show an empty one."""
    if not findings:
        return None

    by_doc: Dict[str, dict] = {}
    order: List[str] = []
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "INFO": 0}
    for f in findings:
        key = f.source.document_id
        if key not in by_doc:
            by_doc[key] = {
                "document_id": key,
                "counterparty": f.counterparty,
                "doc_type": f.doc_type,
                "findings": [],
                "highest_severity": Severity.INFO.value,
            }
            order.append(key)
        by_doc[key]["findings"].append(f.as_dict())
        counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
        cur = Severity(by_doc[key]["highest_severity"])
        if f.severity.rank < cur.rank:
            by_doc[key]["highest_severity"] = f.severity.value

    contracts = [by_doc[k] for k in order]
    contracts.sort(key=lambda c: Severity(c["highest_severity"]).rank)
    return {
        "documents_reviewed": len(contracts),
        "clauses_flagged": len(findings),
        "severity_summary": counts,
        "contracts": contracts,
        "note": (
            "A deterministic scan of the contract text — every item quotes the contract and "
            "cites the page. This surfaces clauses for your M&A attorney to review; it is not "
            "legal advice."
        ),
    }

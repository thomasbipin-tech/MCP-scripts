"""Stage 2 — structured extraction from classified documents.

The offline extractor parses the predictable ledger lines in the data-room PDFs
(``Label ......... $amount`` and clause phrasing) into normalized
``FinancialLine``s and fact objects, each carrying a page citation. The five
financial doc types required by v1 (tax return, P&L, balance sheet, bank
statement, customer contract) plus A/R aging, add-back schedule, and lease are
covered. A ``DocExtract`` bundles the lines + facts a single document yields.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from ..engine.model import FinancialLine, LineCode, PageRef, StatementType
from ..rules.context import (
    AddBack,
    BankSignals,
    Channel,
    ContractFact,
    Customer,
    LeaseFact,
    MonthlyRevenue,
)
from ..services.pdftext import find_line, parse_amount

_MONTH_ROW = re.compile(r"(\d{4})-(\d{2})\b")
_PCT_NAME = re.compile(r"^\s*(.+?)\s*\.{2,}.*\$")


@dataclass
class DocExtract:
    lines: List[FinancialLine] = field(default_factory=list)
    customers: List[Customer] = field(default_factory=list)
    channels: List[Channel] = field(default_factory=list)
    monthly_revenue: List[MonthlyRevenue] = field(default_factory=list)
    addbacks: List[AddBack] = field(default_factory=list)
    contracts: List[ContractFact] = field(default_factory=list)
    lease: Optional[LeaseFact] = None
    bank_signals: Optional[BankSignals] = None
    claimed_sde: Optional[str] = None


def _amt_on(pages, needle) -> Optional[tuple]:
    hit = find_line(pages, needle)
    if not hit:
        return None
    amount = parse_amount(hit[1])
    if amount is None:
        return None
    return hit[0], amount  # (page, amount)


def _fl(doc_id, st, period, code, page, amount, label) -> FinancialLine:
    return FinancialLine(st, period, code, amount, PageRef(doc_id, page, label))


def extract(doc_type: str, pages: List[str], doc_id: str, period: Optional[int]) -> DocExtract:
    out = DocExtract()
    yr = period or 0

    if doc_type.startswith("tax_return"):
        h = _amt_on(pages, "Gross receipts")
        if h:
            out.lines.append(_fl(doc_id, StatementType.TAX_RETURN, yr, LineCode.REVENUE, h[0], h[1], "Gross receipts (tax return)"))

    elif doc_type == "pnl":
        for needle, code, label in [
            ("Total Income", LineCode.REVENUE, "Total Income"),
            ("Total Cost of Goods Sold", LineCode.COGS, "Total COGS"),
            ("Depreciation expense", LineCode.DEPRECIATION, "Depreciation expense"),
            ("Capital expenditures", LineCode.CAPEX, "Capital expenditures"),
        ]:
            h = _amt_on(pages, needle)
            if h:
                out.lines.append(_fl(doc_id, StatementType.PNL, yr, code, h[0], h[1], label))
        out.customers = _extract_breakdown(pages, "Revenue by customer", doc_id, yr, Customer)
        out.channels = _extract_breakdown(pages, "Revenue by channel", doc_id, yr, Channel)
        out.monthly_revenue = _extract_monthly(pages, doc_id)

    elif doc_type == "balance_sheet":
        for needle, code, label in [
            ("Total current assets", LineCode.CURRENT_ASSETS, "Total current assets"),
            ("Total current liabilities", LineCode.CURRENT_LIABILITIES, "Total current liabilities"),
            ("Accounts receivable, net", LineCode.ACCOUNTS_RECEIVABLE, "Accounts receivable, net"),
        ]:
            h = _amt_on(pages, needle)
            if h:
                out.lines.append(_fl(doc_id, StatementType.BALANCE_SHEET, yr, code, h[0], h[1], label))

    elif doc_type == "bank_statement":
        h = _amt_on(pages, "deposits and credits")
        if h:
            out.lines.append(_fl(doc_id, StatementType.BANK_STATEMENT, yr, LineCode.BANK_DEPOSITS, h[0], h[1], "Total deposits and credits"))
        out.bank_signals = _extract_bank_signals(pages, doc_id)

    elif doc_type == "ar_aging":
        total = _amt_on(pages, "Total A/R")
        past = _amt_on(pages, "Over 90 days")
        if total:
            out.lines.append(_fl(doc_id, StatementType.BALANCE_SHEET, yr, LineCode.ACCOUNTS_RECEIVABLE, total[0], total[1], "Total A/R"))
        if past:
            out.lines.append(_fl(doc_id, StatementType.BALANCE_SHEET, yr, LineCode.AR_PAST_90, past[0], past[1], "A/R over 90 days"))

    elif doc_type == "addbacks":
        out.addbacks, out.claimed_sde = _extract_addbacks(pages, doc_id, yr)

    elif doc_type in ("contract_customer", "contract_supplier"):
        c = _extract_contract(pages, doc_id, doc_type)
        if c:
            out.contracts.append(c)

    elif doc_type == "lease":
        out.lease = _extract_lease(pages, doc_id)

    return out


def _extract_breakdown(pages, header, doc_id, period, cls):
    hit = find_line(pages, header)
    if not hit:
        return []
    page = hit[0]
    rows = []
    for line in pages[page - 1].splitlines():
        if header.lower() in line.lower():
            continue
        amount = parse_amount(line)
        if amount is None:
            continue
        m = _PCT_NAME.match(line)
        name = m.group(1).strip() if m else line.split("..")[0].strip()
        if not name:
            continue
        rows.append(cls(name, amount, period, PageRef(doc_id, page, header)))
    return rows


def _extract_monthly(pages, doc_id):
    hit = find_line(pages, "Revenue by month")
    if not hit:
        return []
    page = hit[0]
    out = []
    for line in pages[page - 1].splitlines():
        m = _MONTH_ROW.search(line)
        amount = parse_amount(line)
        if m and amount:
            out.append(MonthlyRevenue(int(m.group(1)), int(m.group(2)), amount, PageRef(doc_id, page, "Monthly revenue")))
    return out


def _classify_addback(desc: str) -> str:
    d = desc.lower()
    if "owner comp" in d or "owner compensation" in d or "salary" in d:
        return "owner_salary"
    if "legal" in d or "settlement" in d or "one-time" in d or "one time" in d:
        return "one_time"
    if "auto" in d or "vehicle" in d or "travel" in d:
        return "auto"
    if "health" in d or "insurance" in d or "personal" in d:
        return "personal"
    return "other"


def _extract_addbacks(pages, doc_id, period):
    hit = find_line(pages, "Add-back Schedule")
    addbacks, claimed = [], None
    if not hit:
        return addbacks, claimed
    page = hit[0]
    for line in pages[page - 1].splitlines():
        amount = parse_amount(line)
        if amount is None:
            continue
        low = line.lower()
        if "claimed sde" in low:
            claimed = amount
            continue
        if "total add-back" in low or "add-back schedule" in low:
            continue
        m = _PCT_NAME.match(line)
        desc = m.group(1).strip() if m else line.split("..")[0].strip()
        documented = "[documented]" in low
        addbacks.append(AddBack(desc, amount, _classify_addback(desc), documented, period, PageRef(doc_id, page, "SDE add-back schedule")))
    return addbacks, claimed


def _extract_bank_signals(pages, doc_id):
    text = "\n".join(pages).lower()
    mca_terms = ["merchant cash advance", "daily ach", "rapid capital", "fox capital", "factoring"]
    detected = any(t in text for t in mca_terms)
    lenders = []
    for name in ("Rapid Capital Funding", "Fox Capital Group"):
        if name.lower() in text:
            lenders.append(name)
    nsf = text.count("nsf") + text.count("overdraft")
    hit = find_line(pages, "ACH") or find_line(pages, "deposits and credits")
    src = PageRef(doc_id, hit[0] if hit else 1, "Bank statement signals")
    return BankSignals(nsf_count=nsf if "returned" in text or "overdraft" in text else 0,
                       mca_detected=detected, mca_debits=lenders, source=src)


def _extract_contract(pages, doc_id, doc_type):
    text = "\n".join(pages)
    low = text.lower()
    title = pages[0].splitlines()[0] if pages and pages[0].splitlines() else "Contract"
    # Counterparty: prefer a name after "and" on the title/first lines.
    counterparty = title
    m = re.search(r"and\s+([A-Z][\w &.\-]+)", text)
    if m:
        counterparty = m.group(1).strip()
    change_of_control = "change of control" in low
    assignment_allowed = None
    if "freely assignable" in low or "assignable with" in low:
        assignment_allowed = True
    if "not be assigned" in low or "not permitted" in low:
        assignment_allowed = False
    hit = find_line(pages, "change of control") or find_line(pages, "assign")
    page = hit[0] if hit else 1
    clause = hit[1].strip() if hit else ""
    return ContractFact(counterparty, "supplier" if doc_type == "contract_supplier" else "customer",
                        True, change_of_control, assignment_allowed, clause,
                        PageRef(doc_id, page, "Contract clause"))


def _extract_lease(pages, doc_id):
    text = "\n".join(pages)
    low = text.lower()
    term = None
    m = re.search(r"remaining term:\s*(\d+(?:\.\d+)?)\s*year", low)
    if m:
        term = Decimal(m.group(1))
    assignment_allowed = None
    if "assignment: not permitted" in low or "not permitted without" in low:
        assignment_allowed = False
    elif "assignment permitted" in low or "assignable" in low:
        assignment_allowed = True
    personal_guarantee = "personally guarantee" in low or "personal guarant" in low
    hit = find_line(pages, "term") or find_line(pages, "lease")
    return LeaseFact(term, assignment_allowed, personal_guarantee,
                     PageRef(doc_id, hit[0] if hit else 1, "Lease terms"))

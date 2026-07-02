"""Synthetic data-room document content for the demo deal.

Built from the SAME constants as ``hvac_demo`` so the text on each cited page
matches the extracted value the report shows — the whole point of click-to-source
traceability. Each document lists its pages; ``export`` renders them to PDF.
"""

from __future__ import annotations

from typing import Dict, List

from . import hvac_demo as H

ENTITY = H.ENTITY


def _pad(pages: List[List[str]], count: int) -> List[List[str]]:
    while len(pages) < count:
        pages.append([f"{ENTITY}", "", f"(page {len(pages) + 1} — continued)"])
    return pages


def _c(n: str) -> str:
    """Format a numeric string as currency for display."""
    return "${:,.2f}".format(float(n))


def build_documents() -> List[dict]:
    docs: List[dict] = []

    for yr in (2022, 2023, 2024):
        # --- Tax return (Form 1120-S), 2 pages ---
        docs.append(
            {
                "id": H._doc("tax", yr),
                "title": f"{yr} Form 1120-S — {ENTITY}",
                "doc_type": "tax_return_1120S",
                "period": yr,
                "pages": [
                    [
                        f"FORM 1120-S  U.S. Income Tax Return for an S Corporation",
                        f"Tax year: {yr}     Entity: {ENTITY}",
                        "",
                        f"Line 1a  Gross receipts or sales ......... {_c(H.TAX_REV[yr])}",
                        f"Line 2   Cost of goods sold ............. {_c(H.COGS[yr])}",
                        "",
                        "This return was prepared from the books and records of the",
                        "taxpayer. Figures are as filed with the IRS.",
                    ],
                    [
                        "Schedule K — Shareholders' Pro Rata Share Items",
                        f"Depreciation (Form 4562) ............... {_c(H.DEPREC[yr])}",
                        "Officer compensation ................... see Schedule E",
                    ],
                ],
            }
        )

        # --- P&L, 5 pages (income, expense, monthly, by-customer, by-channel) ---
        pnl_pages = [
            [
                f"{ENTITY} — Profit & Loss",
                f"January 1 – December 31, {yr}",
                "",
                f"Total Income ........................... {_c(H.PNL_REV[yr])}",
                f"Total Cost of Goods Sold ............... {_c(H.COGS[yr])}",
                f"Gross Profit ........................... "
                + _c(str(float(H.PNL_REV[yr]) - float(H.COGS[yr]))),
            ],
            [
                "Operating Expenses (detail)",
                f"Depreciation expense ................... {_c(H.DEPREC[yr])}",
                f"Capital expenditures (per schedule) .... {_c(H.CAPEX[yr])}",
                "Payroll, rent, insurance, other ........ (see attached)",
            ],
            [f"Revenue by month — {yr}"] + _monthly_lines(yr),
        ]
        if yr == 2024:
            pnl_pages.append(
                [
                    "Revenue by customer — 2024",
                    "  Metro Regional Hospital ............. " + _c("1012200") + "  (42%)",
                    "  Downtown Property Group ............. " + _c("361500") + "  (15%)",
                    "  Riverside School District .......... " + _c("192800") + "  (8%)",
                    "  Fragmented residential accounts ..... remainder",
                ]
            )
            pnl_pages.append(
                [
                    "Revenue by channel — 2024",
                    "  Residential service ................. " + _c("1156800") + "  (48%)",
                    "  Commercial new-construction ........ " + _c("723000") + "  (30%)",
                    "  Maintenance contracts .............. " + _c("530200") + "  (22%)",
                ]
            )
        docs.append(
            {
                "id": H._doc("pnl", yr),
                "title": f"{yr} Profit & Loss — {ENTITY}",
                "doc_type": "pnl",
                "period": yr,
                "pages": _pad(pnl_pages, 5),
            }
        )

        # --- Bank statement, 3 pages ---
        bank_pages = [
            [
                f"{ENTITY} — Operating Account Statement Summary",
                f"Period: Jan – Dec {yr}",
                "",
                f"Total deposits and credits ............. {_c(H.BANK_DEP[yr])}",
                f"Reported revenue (per P&L) ............. {_c(H.PNL_REV[yr])}",
            ],
            ["Deposit detail (monthly totals available on request)."],
        ]
        if yr == 2024:
            bank_pages.append(
                [
                    "Recurring ACH debits — daily remittance pattern",
                    "  RAPID CAPITAL FUNDING   daily ACH ..... variable",
                    "  FOX CAPITAL GROUP       daily ACH ..... variable",
                    "",
                    "Note: daily fixed/percentage ACH remittances are characteristic",
                    "of merchant cash advance (MCA) financing.",
                ]
            )
        else:
            bank_pages.append(["No merchant-cash-advance or factoring debits detected."])
        docs.append(
            {
                "id": H._doc("bank", yr),
                "title": f"{yr} Bank Statement — {ENTITY}",
                "doc_type": "bank_statement",
                "period": yr,
                "pages": bank_pages,
            }
        )

        # --- Balance sheet, 2 pages ---
        bs_pages = [
            [
                f"{ENTITY} — Balance Sheet",
                f"As of December 31, {yr}",
                "",
                f"Total current assets ................... {_c(H.CUR_ASSETS[yr])}",
                f"Total current liabilities .............. {_c(H.CUR_LIABS[yr])}",
            ],
            ["Accounts receivable, net ............... "
             + (_c("240000") if yr == 2024 else "(prior year)")],
        ]
        docs.append(
            {
                "id": H._doc("bs", yr),
                "title": f"{yr} Balance Sheet — {ENTITY}",
                "doc_type": "balance_sheet",
                "period": yr,
                "pages": bs_pages,
            }
        )

    # --- A/R aging (2024) ---
    docs.append(
        {
            "id": H._doc("ar", 2024),
            "title": "2024 A/R Aging — Summit Air Mechanical LLC",
            "doc_type": "ar_aging",
            "period": 2024,
            "pages": [
                [
                    "Accounts Receivable Aging — as of Dec 31, 2024",
                    "  Current (0–30) ...................... " + _c("180000"),
                    "  31–60 ............................... " + _c("24000"),
                    "  61–90 ............................... " + _c("12000"),
                    "  Over 90 days ........................ " + _c("24000") + "  (10%)",
                    "  Total A/R ........................... " + _c("240000"),
                ]
            ],
        }
    )

    # --- Add-back schedule (2024) ---
    docs.append(
        {
            "id": H._doc("addbacks", 2024),
            "title": "2024 SDE Add-back Schedule — Summit Air Mechanical LLC",
            "doc_type": "other",
            "period": 2024,
            "pages": [
                [
                    "Seller's Discretionary Earnings — Add-back Schedule (2024)",
                    "  Owner compensation normalization .... " + _c("95000") + "  [documented]",
                    "  One-time legal settlement ........... " + _c("30000") + "  [documented]",
                    "  Owner auto and travel ............... " + _c("20000") + "  [documented]",
                    "  Owner health insurance .............. " + _c("15000") + "  [documented]",
                    "  Total add-backs ..................... " + _c("160000"),
                    "  Claimed SDE ......................... " + _c(H.CLAIMED_SDE),
                ]
            ],
        }
    )

    # --- Contracts ---
    docs.append(
        {
            "id": H._doc("contract-metro", 2024),
            "title": "Master Services Agreement — Metro Regional Hospital",
            "doc_type": "contract_customer",
            "period": 2024,
            "pages": _pad(
                [
                    ["MASTER SERVICES AGREEMENT", "Between Summit Air Mechanical LLC and",
                     "Metro Regional Hospital"],
                ],
                6,
            )[:5]
            + [
                [
                    "Section 14 — Assignment and Change of Control",
                    "",
                    "14.3  This Agreement may not be assigned, and shall terminate",
                    "      automatically, upon a change of control of the Contractor,",
                    "      including a sale of substantially all of its assets, without",
                    "      the prior written consent of Metro Regional Hospital.",
                ]
            ],
        }
    )
    docs.append(
        {
            "id": H._doc("contract-supplier", 2024),
            "title": "Distributor Agreement — Carrier Distribution Partners",
            "doc_type": "contract_supplier",
            "period": 2024,
            "pages": [
                ["DISTRIBUTOR AGREEMENT", "Carrier Distribution Partners"],
                ["Section 9 — Assignment", "This Agreement is freely assignable by either party."],
            ],
        }
    )
    docs.append(
        {
            "id": H._doc("contract-dpg", 2024),
            "title": "Facilities Agreement — Downtown Property Group",
            "doc_type": "contract_customer",
            "period": 2024,
            "pages": _pad(
                [
                    ["FACILITIES AGREEMENT", "Downtown Property Group"],
                    ["Section 7 — Assignment", "Assignable with 30 days' written notice."],
                ],
                3,
            ),
        }
    )

    # --- Lease ---
    docs.append(
        {
            "id": H._doc("lease", 2024),
            "title": "Commercial Lease — 1400 Industrial Pkwy",
            "doc_type": "lease",
            "period": 2024,
            "pages": [
                [
                    "COMMERCIAL LEASE AGREEMENT",
                    "Premises: 1400 Industrial Pkwy",
                    "",
                    "Remaining term: 2 years (expires Dec 31, 2026).",
                    "Assignment: NOT permitted without landlord consent, which may be",
                    "  withheld at landlord's sole discretion.",
                    "Guaranty: Tenant's principal personally guarantees all obligations.",
                ]
            ],
        }
    )

    return docs


def _monthly_lines(yr: int) -> List[str]:
    plan = {2022: "179166", 2023: "198333", 2024: "200833"}
    amt = plan.get(yr, str(round(float(H.PNL_REV[yr]) / 12)))
    return [f"  {yr}-{mo:02d} ......................... " + _c(amt) for mo in range(1, 13)]


DOCUMENT_INDEX: Dict[str, dict] = {d["id"]: d for d in build_documents()}

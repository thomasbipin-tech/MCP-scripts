"""Deterministic contract clause-risk scanner."""

from app.pipeline.clauses import build_contract_review, scan_document_clauses
from app.rules.context import Severity

_CUSTOMER = [
    "MASTER SERVICES AGREEMENT\nBetween Acme LLC and Metro Regional Hospital",
    (
        "Section 14 — Assignment and Change of Control.\n"
        "This Agreement may not be assigned, and shall terminate automatically upon a "
        "change of control of the Contractor, without the prior written consent of Metro "
        "Regional Hospital."
    ),
]

_BENIGN = [
    "DISTRIBUTOR AGREEMENT\nCarrier Distribution Partners",
    "Section 9 — Assignment. This Agreement is freely assignable by either party.",
]

_LEASE = [
    (
        "COMMERCIAL LEASE AGREEMENT. Premises: 1400 Industrial Pkwy.\n"
        "Assignment: NOT permitted without landlord consent, which may be withheld at "
        "landlord's sole discretion.\n"
        "Guaranty: Tenant's principal personally guarantees all obligations."
    )
]


def _types(findings):
    return {f.clause_type for f in findings}


def test_customer_contract_flags_change_of_control_and_non_assignment_critical():
    f = scan_document_clauses("contract_customer", _CUSTOMER, "doc-1", "MSA — Metro")
    assert {"change_of_control", "non_assignable"} <= _types(f)
    for cf in f:
        if cf.clause_type in ("change_of_control", "non_assignable"):
            # a concentrated customer relationship that can vanish on sale is CRITICAL
            assert cf.severity is Severity.CRITICAL
        # grounded: every finding quotes the contract and cites a page
        assert cf.quote.strip()
        assert cf.source.page >= 1
        assert cf.counterparty


def test_freely_assignable_is_not_flagged():
    f = scan_document_clauses("contract_supplier", _BENIGN, "doc-2", "Distributor")
    assert "non_assignable" not in _types(f)
    assert "assignment_consent" not in _types(f)


def test_lease_flags_personal_guarantee_and_non_assignment():
    f = scan_document_clauses("lease", _LEASE, "doc-3", "Commercial Lease")
    assert {"personal_guarantee", "non_assignable"} <= _types(f)
    for cf in f:
        assert cf.severity is Severity.HIGH


def test_non_contract_documents_are_skipped():
    assert scan_document_clauses("pnl", ["Total Income ... $1,000,000"], "doc-4") == []


def test_one_finding_per_clause_type_per_document():
    f = scan_document_clauses("contract_customer", _CUSTOMER, "doc-1")
    types = [cf.clause_type for cf in f]
    assert len(types) == len(set(types))


def test_contract_review_groups_and_summarizes():
    findings = (
        scan_document_clauses("contract_customer", _CUSTOMER, "doc-1", "MSA — Metro")
        + scan_document_clauses("lease", _LEASE, "doc-3", "Commercial Lease")
    )
    review = build_contract_review(findings)
    assert review["documents_reviewed"] == 2
    assert review["clauses_flagged"] == len(findings)
    assert review["severity_summary"]["CRITICAL"] == 2
    # contracts sorted worst-first
    assert review["contracts"][0]["highest_severity"] == "CRITICAL"
    # each contract carries its own findings, page-cited
    for c in review["contracts"]:
        assert c["findings"]
        assert all(f["source"]["page"] >= 1 for f in c["findings"])


def test_contract_review_is_none_when_no_contracts():
    assert build_contract_review([]) is None

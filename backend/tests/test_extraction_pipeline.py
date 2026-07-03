"""End-to-end: real PDF bytes -> intake -> classify -> extract -> report.

Reads the generated data-room PDFs (not the seed structures) and drives the full
Stage 0-4 pipeline, asserting the extracted numbers match the source documents
and that the same six red flags fire. This proves the production path — from a
document a user uploads to a grounded flag — works, not just the in-memory demo.
"""

from decimal import Decimal
from pathlib import Path

import pytest

from app.pipeline.classify import classify_offline
from app.pipeline.ingest import ingest_documents
from app.rules.engine import run_rules, severity_counts
from app.services.pdftext import extract_pages
from app.seeder.export import main as export_main

DOCS_DIR = Path(__file__).resolve().parents[1].parent / "frontend" / "public" / "demo-docs"


def _ensure_docs():
    if not DOCS_DIR.exists() or not any(DOCS_DIR.glob("*.pdf")):
        export_main()


def _load_docs():
    _ensure_docs()
    docs = []
    for pdf in sorted(DOCS_DIR.glob("*.pdf")):
        docs.append({"doc_id": pdf.stem, "filename": pdf.name, "pdf_bytes": pdf.read_bytes()})
    return docs


DEAL_META = {"vertical": "hvac", "deal_type": "asset", "asking_price": "1560000", "claimed_sde": "520000"}
BENCHMARKS = {"sde_multiple": {"p25": Decimal("2.5"), "p50": Decimal("3.0"), "p75": Decimal("3.7"), "n_deals": 42, "source": "v1"}}


def test_classifier_labels_each_doc_type():
    _ensure_docs()
    tax = extract_pages((DOCS_DIR / "doc-tax-2024.pdf").read_bytes())
    assert classify_offline(tax).doc_type == "tax_return_1120S"
    pnl = extract_pages((DOCS_DIR / "doc-pnl-2024.pdf").read_bytes())
    assert classify_offline(pnl).doc_type == "pnl"
    bank = extract_pages((DOCS_DIR / "doc-bank-2024.pdf").read_bytes())
    assert classify_offline(bank).doc_type == "bank_statement"
    lease = extract_pages((DOCS_DIR / "doc-lease-2024.pdf").read_bytes())
    assert classify_offline(lease).doc_type == "lease"


def test_extracted_financials_match_source_documents():
    result = ingest_documents(_load_docs(), DEAL_META, BENCHMARKS)
    tri = {t.period: t for t in result.context.reconciliation.triangle}
    # Numbers pulled from the PDFs must equal the figures printed on the pages.
    assert tri[2024].pnl_revenue == Decimal("2410000.00")
    assert tri[2024].tax_revenue == Decimal("2361800.00")
    assert tri[2024].bank_deposits == Decimal("1879800.00")
    assert tri[2024].deposit_coverage_pct == Decimal("78.0")


def test_full_pipeline_from_pdfs_fires_the_six_flags():
    result = ingest_documents(_load_docs(), DEAL_META, BENCHMARKS)
    flags = run_rules(result.context)
    red = {f.rule_id for f in flags if f.severity.value != "INFO"}
    assert {"TT2", "A1", "C22", "D24", "B9", "D25"} <= red
    counts = severity_counts(flags)
    assert counts["CRITICAL"] == 4


def test_dedupe_drops_identical_bytes():
    docs = _load_docs()
    dup = dict(docs[0])
    dup["doc_id"] = docs[0]["doc_id"] + "-copy"
    result = ingest_documents(docs + [dup], DEAL_META, BENCHMARKS)
    copy = next(d for d in result.documents if d.doc_id.endswith("-copy"))
    assert copy.duplicate is True

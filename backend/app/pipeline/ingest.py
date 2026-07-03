"""Orchestrate Stages 0-2 across a document set into a ``DealContext``.

Given raw PDFs, this runs intake -> classify -> extract for each, dedupes by
SHA-256, merges the per-document lines and facts into one deal-level fact set,
and reconciles. The result feeds the same Stage 3-5 pipeline the demo uses, so a
real uploaded data room and the synthetic demo share one code path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ..rules.context import BankSignals, Benchmark, DealContext, DealFacts
from ..engine.reconcile import reconcile
from .classify import classify
from .extract import extract
from .intake import intake_document


@dataclass
class IngestedDoc:
    doc_id: str
    filename: str
    sha256: str
    doc_type: str
    confidence: float
    period: Optional[int]
    page_count: int
    duplicate: bool


@dataclass
class IngestResult:
    context: DealContext
    documents: List[IngestedDoc] = field(default_factory=list)


def _merge_bank_signals(a: Optional[BankSignals], b: Optional[BankSignals]) -> Optional[BankSignals]:
    if a is None:
        return b
    if b is None:
        return a
    lenders = list(dict.fromkeys(a.mca_debits + b.mca_debits))
    detected = a.mca_detected or b.mca_detected
    # Prefer a source that actually observed the MCA signal.
    src = a.source if a.mca_detected else (b.source if b.mca_detected else a.source)
    return BankSignals(nsf_count=a.nsf_count + b.nsf_count, mca_detected=detected, mca_debits=lenders, source=src)


def ingest_documents(
    docs: List[dict],
    deal_meta: dict,
    benchmarks: Optional[dict] = None,
    client=None,
) -> IngestResult:
    """``docs`` = [{"doc_id","filename","pdf_bytes", "doc_type"?}]. ``deal_meta``
    supplies vertical/deal_type/asking_price (from the deal record, not the PDFs).

    If a doc carries an explicit ``doc_type`` (a user override from the UI), it is
    honored instead of re-classifying — period/entity are still detected from the
    text so extraction stays fully cited."""
    seen: set = set()
    all_lines = []
    customers, channels, monthly, addbacks, contracts = [], [], [], [], []
    lease = None
    bank_signals: Optional[BankSignals] = None
    claimed_sde: Optional[str] = None
    ingested: List[IngestedDoc] = []

    for d in docs:
        intake = intake_document(d["pdf_bytes"], seen)
        override = d.get("doc_type")
        if override:
            from .classify import Classification, _detect_entity, _detect_period

            text = "\n".join(intake.pages)
            cls = Classification(
                doc_type=override, confidence=1.0,
                period=_detect_period(text), entity_name=_detect_entity(text),
            )
        else:
            cls = classify(intake.pages, d.get("filename", ""), client=client)
        ingested.append(IngestedDoc(
            doc_id=d["doc_id"], filename=d.get("filename", ""), sha256=intake.sha256,
            doc_type=cls.doc_type, confidence=cls.confidence, period=cls.period,
            page_count=intake.page_count, duplicate=intake.duplicate,
        ))
        if intake.duplicate:
            continue
        seen.add(intake.sha256)

        ex = extract(cls.doc_type, intake.pages, d["doc_id"], cls.period)
        all_lines.extend(ex.lines)
        customers.extend(ex.customers)
        channels.extend(ex.channels)
        monthly.extend(ex.monthly_revenue)
        addbacks.extend(ex.addbacks)
        contracts.extend(ex.contracts)
        if ex.lease and lease is None:
            lease = ex.lease
        bank_signals = _merge_bank_signals(bank_signals, ex.bank_signals)
        if ex.claimed_sde:
            claimed_sde = ex.claimed_sde

    bm = {}
    for k, v in (benchmarks or {}).items():
        bm[k] = v if isinstance(v, Benchmark) else Benchmark(
            k, v["p25"], v["p50"], v["p75"], v.get("n_deals", 0), v.get("source", ""))

    facts = DealFacts(
        vertical=deal_meta.get("vertical", "other"),
        deal_type=deal_meta.get("deal_type", "asset"),
        asking_price=str(deal_meta.get("asking_price") or "0"),
        claimed_sde=str(claimed_sde or deal_meta.get("claimed_sde") or "0"),
        customers=customers,
        channels=channels,
        monthly_revenue=monthly,
        addbacks=addbacks,
        contracts=contracts,
        lease=lease,
        bank_signals=bank_signals or BankSignals(),
        benchmarks=bm,
    )
    ctx = DealContext(lines=all_lines, reconciliation=reconcile(all_lines), facts=facts)
    return IngestResult(context=ctx, documents=ingested)

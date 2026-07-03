"""Document upload + the real extraction/processing path (Stages 0-5).

Upload runs intake + classification synchronously (fast) and returns the
classification with a user-override option. `process` runs the full ingest ->
reconcile -> flag -> narrate pipeline over the deal's stored documents and
persists an unpublished report for admin QA.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.security import get_current_user
from ...db.session import get_db
from ...models import Benchmark, Deal, Document, FinancialLineRow, FlagRow, Report, User
from ...pipeline.classify import classify
from ...pipeline.ingest import ingest_documents
from ...pipeline.report import assemble_report
from ...pipeline.narrate import Narrator
from ...engine.evidence import build_evidence_bundle
from ...rules.engine import run_rules
from ...services import audit, storage
from ...pipeline.intake import intake_document
from ..deps import get_scoped_deal

router = APIRouter(prefix="/deals", tags=["documents"])


@router.post("/{deal_id}/documents")
async def upload_document(
    file: UploadFile,
    deal: Deal = Depends(get_scoped_deal),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=422, detail="empty file")

    seen = {d.sha256 for d in db.scalars(select(Document).where(Document.deal_id == deal.id))}
    intake = intake_document(data, seen)
    if intake.duplicate:
        return {"duplicate": True, "sha256": intake.sha256}

    doc_id = uuid.uuid4().hex
    key = storage.storage_key(deal.id, doc_id)
    storage.put_object(key, data)

    cls = classify(intake.pages, file.filename or "")
    doc = Document(
        id=doc_id, deal_id=deal.id, sha256=intake.sha256, storage_key=key,
        doc_type=cls.doc_type, entity_name=cls.entity_name, page_count=intake.page_count,
        classification_confidence=cls.confidence,
    )
    db.add(doc)
    if deal.stage == "Uploading":
        deal.stage = "Uploading"
    audit.record(db, actor=user.email, action="document.upload", entity_type="document", entity_id=doc_id, after={"doc_type": cls.doc_type})
    db.commit()
    return {
        "id": doc_id, "doc_type": cls.doc_type, "confidence": cls.confidence,
        "period": cls.period, "entity_name": cls.entity_name, "page_count": intake.page_count,
    }


@router.get("/{deal_id}/documents")
def list_documents(deal: Deal = Depends(get_scoped_deal), db: Session = Depends(get_db)) -> list:
    return [
        {"id": d.id, "doc_type": d.doc_type, "confidence": d.classification_confidence,
         "page_count": d.page_count, "entity_name": d.entity_name}
        for d in db.scalars(select(Document).where(Document.deal_id == deal.id))
    ]


@router.post("/{deal_id}/documents/{doc_id}/reclassify")
def reclassify(
    doc_id: str, doc_type: str,
    deal: Deal = Depends(get_scoped_deal),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    doc = db.get(Document, doc_id)
    if doc is None or doc.deal_id != deal.id:
        raise HTTPException(status_code=404, detail="document not found")
    before = {"doc_type": doc.doc_type}
    doc.user_override = doc_type
    doc.doc_type = doc_type
    audit.record(db, actor=user.email, action="document.reclassify", entity_type="document", entity_id=doc_id, before=before, after={"doc_type": doc_type})
    db.commit()
    return {"id": doc_id, "doc_type": doc_type}


@router.post("/{deal_id}/process")
def process_deal(
    deal: Deal = Depends(get_scoped_deal),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    docs_rows = list(db.scalars(select(Document).where(Document.deal_id == deal.id)))
    if not docs_rows:
        raise HTTPException(status_code=409, detail="no documents to process")

    docs = []
    for d in docs_rows:
        data = storage.get_object(d.storage_key)
        # Honor a user override of the classification; else let ingest classify.
        docs.append({
            "doc_id": d.id,
            "filename": d.doc_type or "",
            "pdf_bytes": data,
            "doc_type": d.user_override or None,
        })

    benchmarks = {}
    for b in db.scalars(select(Benchmark).where(Benchmark.vertical == deal.vertical)):
        benchmarks[b.metric] = {"p25": b.p25, "p50": b.p50, "p75": b.p75, "n_deals": b.n_deals, "source": b.source}

    meta = {"vertical": deal.vertical, "deal_type": deal.deal_type,
            "asking_price": str(deal.asking_price or 0), "claimed_sde": str(deal.claimed_sde or 0)}
    result = ingest_documents(docs, meta, benchmarks)
    ctx = result.context

    # Persist normalized financial_lines (the only table the engine reads).
    db.query(FinancialLineRow).filter(FinancialLineRow.deal_id == deal.id).delete()
    for ln in ctx.lines:
        db.add(FinancialLineRow(
            deal_id=deal.id, source_doc_id=ln.source.document_id, statement_type=ln.statement_type.value,
            period=ln.period, line_code=ln.line_code.value, amount=ln.amount, page_ref=ln.source.as_dict()))

    flags = run_rules(ctx)
    bundle = build_evidence_bundle(ctx, flags)
    narrative = Narrator().narrate(bundle)
    report = assemble_report(ctx, flags, narrative, {
        "codename": deal.codename, "entity_name": deal.entity_name, "vertical": deal.vertical,
        "state": deal.state, "deal_type": deal.deal_type, "asking_price": str(deal.asking_price or 0),
        "claimed_sde": str(deal.claimed_sde or 0), "tier": deal.tier, "stage": "In Review"})
    report["documents"] = [
        {"id": d.doc_id, "doc_type": d.doc_type, "period": d.period, "page_count": d.page_count,
         "confidence": d.confidence, "url": storage.signed_url(storage.storage_key(deal.id, d.doc_id))}
        for d in result.documents
    ]

    db.query(FlagRow).filter(FlagRow.deal_id == deal.id).delete()
    for f in flags:
        fd = f.as_dict()
        db.add(FlagRow(
            deal_id=deal.id, rule_id=fd["rule_id"], rule_version=fd["rule_version"], severity=fd["severity"],
            category=fd["category"], title=fd["title"], detail=fd["detail"],
            computed_values=fd["computed_values"], evidence_refs=fd["evidence_refs"]))

    db.add(Report(deal_id=deal.id, version=1, payload=report, watermark=report.get("watermark")))
    deal.stage = "In Review"
    deal.completeness_score = report.get("completeness_score", 0)
    audit.record(db, actor=user.email, action="deal.process", entity_type="deal", entity_id=deal.id, after={"flags": len(flags)})
    db.commit()
    return {"deal_id": deal.id, "severity_counts": report["severity_counts"], "documents": len(docs), "stage": deal.stage}

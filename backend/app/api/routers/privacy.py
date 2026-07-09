"""Confidentiality & data-rights controls (SPEC §5/§8).

The buyer's documents are the seller's confidential information under an NDA.
DealProofing operates as the buyer's bound representative/processor, which is
what keeps use of the tool consistent with a typical NDA's advisor carve-out.
These endpoints make that concrete:
  * ``attest`` records the buyer's confirmation that they have the right to
    share the documents and that their NDA permits disclosure to advisors.
  * ``DELETE .../data`` purges every stored document, extraction, and derived
    record for a deal and returns a signed **deletion certificate** the buyer
    can hand to the seller.
"""

from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.security import get_current_user
from ...db.base import utcnow
from ...db.session import get_db
from ...models import Deal, Document, Extraction, FinancialLineRow, FlagRow, Report, User
from ...services import audit, storage
from ..deps import get_scoped_deal
from ..schemas import ConfidentialityAttestation

router = APIRouter(prefix="/deals", tags=["privacy"])


@router.post("/{deal_id}/attest")
def attest(
    body: ConfidentialityAttestation,
    deal: Deal = Depends(get_scoped_deal),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    audit.record(
        db, actor=user.email, action="deal.confidentiality_attested",
        entity_type="deal", entity_id=deal.id,
        after={"right_to_share": body.right_to_share, "nda_permits_advisors": body.nda_permits_advisors},
    )
    db.commit()
    return {"attested": True, "right_to_share": body.right_to_share, "nda_permits_advisors": body.nda_permits_advisors}


@router.delete("/{deal_id}/data")
def purge_deal_data(
    deal: Deal = Depends(get_scoped_deal),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Irreversibly delete the seller's documents and everything derived from
    them, and return a deletion certificate."""
    doc_ids = [d.id for d in db.scalars(select(Document).where(Document.deal_id == deal.id))]

    if doc_ids:
        db.query(Extraction).filter(Extraction.document_id.in_(doc_ids)).delete(synchronize_session=False)
    db.query(FinancialLineRow).filter(FinancialLineRow.deal_id == deal.id).delete(synchronize_session=False)
    db.query(FlagRow).filter(FlagRow.deal_id == deal.id).delete(synchronize_session=False)
    db.query(Report).filter(Report.deal_id == deal.id).delete(synchronize_session=False)
    db.query(Document).filter(Document.deal_id == deal.id).delete(synchronize_session=False)

    objects_removed = storage.delete_prefix(f"deals/{deal.id}")

    deal.stage = "Archived"
    deal.paid = False

    cert = {
        "deal_id": deal.id,
        "codename": deal.codename,
        "purged_at": utcnow().isoformat(),
        "actor": user.email,
        "documents_deleted": len(doc_ids),
        "storage_objects_removed": objects_removed,
    }
    cert["sha256"] = hashlib.sha256(json.dumps(cert, sort_keys=True).encode()).hexdigest()

    row = audit.record(
        db, actor=user.email, action="deal.data_purged",
        entity_type="deal", entity_id=deal.id, after=cert,
    )
    cert["certificate_id"] = row.id
    db.commit()
    return {"deleted": True, "certificate": cert}

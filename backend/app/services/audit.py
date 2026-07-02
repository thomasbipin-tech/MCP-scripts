"""Append-only audit logging (SPEC §7).

Every entity mutation records a row with content hashes of the before/after
state. Rows are inserted, never updated or deleted."""

from __future__ import annotations

import hashlib
import json
from typing import Optional

from sqlalchemy.orm import Session

from ..models import AuditLog


def _hash(obj: Optional[dict]) -> Optional[str]:
    if obj is None:
        return None
    blob = json.dumps(obj, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()


def record(
    db: Session,
    *,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    before: Optional[dict] = None,
    after: Optional[dict] = None,
) -> AuditLog:
    row = AuditLog(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_hash=_hash(before),
        after_hash=_hash(after),
    )
    db.add(row)
    db.flush()
    return row

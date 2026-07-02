"""Health and the public rule catalog."""

from __future__ import annotations

from fastapi import APIRouter

from ...core.disclaimer import DISCLAIMER, NO_SCORE_POLICY
from ...rules.registry import active_rules

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "dealproof-api"}


@router.get("/rules")
def rules() -> list:
    """The active red-flag rule library (data, not code)."""
    return [
        {
            "rule_id": r.rule_id,
            "version": r.version,
            "category": r.category,
            "kind": r.kind,
            "default_severity": r.default_severity.value,
            "title": r.title,
            "thresholds": r.thresholds,
        }
        for r in active_rules()
    ]


@router.get("/policy")
def policy() -> dict:
    return {"disclaimer": DISCLAIMER, "no_score": NO_SCORE_POLICY}

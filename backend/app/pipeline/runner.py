"""End-to-end pipeline orchestration (Stages 3-5 for a prepared context).

Stages 0-2 (intake, classify, extract) produce the ``DealContext``; from there
this is fully deterministic except the narration call, which is grounded and
falls back to the template narrator. The Celery task in ``app/pipeline/tasks``
calls the same function so the demo path and the production path share code.
"""

from __future__ import annotations

from typing import Optional

from ..engine.evidence import build_evidence_bundle
from ..rules.context import DealContext
from ..rules.engine import run_rules
from .narrate import Narrator
from .report import assemble_report


def run_pipeline(
    ctx: DealContext, deal_meta: dict, narrator: Optional[Narrator] = None
) -> dict:
    # Fail-soft in production: a rule that trips on malformed/inaccurate input
    # is skipped, never crashing the whole analysis.
    flags = run_rules(ctx, strict=False)
    bundle = build_evidence_bundle(ctx, flags)
    narrative = (narrator or Narrator()).narrate(bundle)
    return assemble_report(ctx, flags, narrative, deal_meta)

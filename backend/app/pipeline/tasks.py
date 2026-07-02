"""Celery app + the pipeline task.

Imported only by the worker process (never by the API or the test suite), so it
may hard-import Celery. The task is resumable-by-stage in spirit: each stage
persists its output, and re-running skips completed stages by checking state.
For v1 the heavy stages (0-2, intake/classify/extract) are represented by the
context builder; stages 3-5 run via ``run_pipeline``.
"""

from __future__ import annotations

from celery import Celery

from ..core.config import settings
from ..db.base import SessionLocal, utcnow
from ..models import Deal, FlagRow, LLMCall, Report
from .runner import run_pipeline

celery_app = Celery("dealproof", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_track_started = True


@celery_app.task(bind=True, max_retries=2, default_retry_delay=10)
def process_deal(self, deal_id: str, context_builder: str = "demo") -> dict:
    """Run reconciliation → flags → narration → report for a deal and persist it.

    ``context_builder`` selects how the ``DealContext`` is assembled. In v1 the
    only implemented builder is the demo builder; real deals assemble the context
    from persisted ``financial_lines`` + ``extractions`` (stages 0-2).
    """
    db = SessionLocal()
    try:
        deal = db.get(Deal, deal_id)
        if deal is None:
            return {"error": "deal not found"}

        if context_builder == "demo":
            from ..seeder.hvac_demo import build_demo_context

            ctx = build_demo_context()
        else:
            from .assemble import assemble_context_from_db

            ctx = assemble_context_from_db(db, deal_id)

        deal.stage = "Processing"
        db.commit()

        meta = {
            "codename": deal.codename,
            "entity_name": deal.entity_name,
            "vertical": deal.vertical,
            "state": deal.state,
            "deal_type": deal.deal_type,
            "asking_price": str(deal.asking_price),
            "claimed_sde": str(deal.claimed_sde),
            "tier": deal.tier,
            "stage": "In Review",
        }
        report = run_pipeline(ctx, meta)

        # Persist flags
        db.query(FlagRow).filter(FlagRow.deal_id == deal_id).delete()
        for f in report["flags"]:
            db.add(FlagRow(
                deal_id=deal_id, rule_id=f["rule_id"], rule_version=f.get("rule_version", 1),
                severity=f["severity"], category=f["category"], title=f["title"],
                detail=f.get("detail", ""), computed_values=f.get("computed_values", {}),
                evidence_refs=f.get("evidence_refs", []),
            ))

        db.add(Report(deal_id=deal_id, version=1, payload=report,
                      watermark=report.get("watermark")))
        deal.stage = "In Review"
        deal.completeness_score = report.get("completeness_score", 0)
        db.commit()
        return {"deal_id": deal_id, "severity_counts": report["severity_counts"]}
    except Exception as exc:  # pragma: no cover - worker retry path
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()

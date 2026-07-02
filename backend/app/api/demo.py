"""Idempotent demo bootstrap: seed rules, benchmarks, and the demo deal.

Runs on API startup so a clean `docker compose up` immediately has a browsable,
published, paid sample report on the synthetic HVAC deal (build-prompt DoD)."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.base import utcnow
from ..models import Benchmark, Deal, FlagRow, FlagRule, Org, Report, User
from ..rules.registry import RULES

DEMO_REPORT = Path(__file__).resolve().parent.parent / "seeder" / "out" / "demo_report.json"
DEMO_ADMIN = "admin@dealproof.test"
DEMO_BUYER = "buyer@dealproof.test"


def _load_demo_report() -> dict:
    if not DEMO_REPORT.exists():
        from ..seeder.export import main as export_main

        export_main()
    return json.loads(DEMO_REPORT.read_text())


def seed_rules(db: Session) -> None:
    for r in RULES:
        existing = db.get(FlagRule, {"rule_id": r.rule_id, "version": r.version})
        if existing:
            continue
        row = r.as_row()
        db.add(FlagRule(**{k: row[k] for k in (
            "rule_id", "version", "category", "logic_spec", "thresholds",
            "vertical_overrides", "default_severity", "title", "buyer_action",
            "ask_seller", "what_resolves", "active",
        )}))
    db.commit()


def seed_benchmarks(db: Session) -> None:
    if db.scalar(select(Benchmark).limit(1)):
        return
    db.add(Benchmark(vertical="hvac", metric="sde_multiple", p25=Decimal("2.5"),
                     p50=Decimal("3.0"), p75=Decimal("3.7"), n_deals=42,
                     source="DealProof HVAC benchmark set v1"))
    db.commit()


def seed_demo_deal(db: Session) -> None:
    if db.scalar(select(User).where(User.email == DEMO_ADMIN)):
        return  # already seeded

    org = Org(name="DealProof Demo", kind="acquirer")
    db.add(org)
    db.flush()
    db.add(User(email=DEMO_ADMIN, role="admin", org_id=org.id))
    db.add(User(email=DEMO_BUYER, role="buyer", org_id=org.id))

    report = _load_demo_report()
    meta = report["deal"]
    deal = Deal(
        org_id=org.id,
        codename=meta["codename"],
        entity_name=meta["entity_name"],
        vertical=meta["vertical"],
        state=meta.get("state"),
        deal_type=meta.get("deal_type", "asset"),
        asking_price=Decimal(meta["asking_price"]),
        claimed_sde=Decimal(meta["claimed_sde"]),
        tier=meta.get("tier"),
        stage="Report Ready",
        completeness_score=report.get("completeness_score", 0),
        paid=True,  # demo report is unlocked
    )
    db.add(deal)
    db.flush()

    for f in report["flags"]:
        db.add(FlagRow(
            deal_id=deal.id,
            rule_id=f["rule_id"],
            rule_version=f.get("rule_version", 1),
            severity=f["severity"],
            category=f["category"],
            title=f["title"],
            detail=f.get("detail", ""),
            computed_values=f.get("computed_values", {}),
            evidence_refs=f.get("evidence_refs", []),
        ))

    db.add(Report(
        deal_id=deal.id,
        version=1,
        payload=report,
        watermark=report.get("watermark"),
        published_at=utcnow(),
    ))
    db.commit()


def bootstrap(db: Session) -> None:
    seed_rules(db)
    seed_benchmarks(db)
    seed_demo_deal(db)

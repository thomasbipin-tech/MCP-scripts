"""Shared builders for rule tests."""

from __future__ import annotations

from decimal import Decimal
from typing import List

from app.engine.model import FinancialLine, PageRef
from app.engine.reconcile import reconcile
from app.rules.context import DealContext, DealFacts


def pref(doc="doc", page=1, label="x") -> PageRef:
    return PageRef(doc, page, label)


def make_ctx(lines: List[FinancialLine] | None = None, **facts_kwargs) -> DealContext:
    lines = lines or []
    facts_kwargs.setdefault("vertical", "hvac")
    facts_kwargs.setdefault("deal_type", "asset")
    facts_kwargs.setdefault("asking_price", "1000000")
    facts_kwargs.setdefault("claimed_sde", "300000")
    facts = DealFacts(**facts_kwargs)
    return DealContext(lines=lines, reconciliation=reconcile(lines), facts=facts)


def fired_ids(flags) -> set:
    return {f.rule_id for f in flags}

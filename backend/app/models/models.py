"""SQLAlchemy models mirroring SPEC §7's data model.

Kept portable (JSON + Numeric) so the same models run on SQLite (dev/smoke test)
and Postgres 16 (production). Money columns are ``Numeric`` — never Float.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, utcnow


def _uid() -> str:
    return uuid.uuid4().hex


class Org(Base, TimestampMixin):
    __tablename__ = "orgs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    name: Mapped[str] = mapped_column(String(255))
    kind: Mapped[str] = mapped_column(String(32), default="direct")  # broker|acquirer|direct
    white_label: Mapped[dict] = mapped_column(JSON, default=dict)
    users: Mapped[list["User"]] = relationship(back_populates="org")
    deals: Mapped[list["Deal"]] = relationship(back_populates="org")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(16), default="buyer")  # buyer|admin
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"))
    totp_secret: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    org: Mapped[Org] = relationship(back_populates="users")


class Deal(Base, TimestampMixin):
    __tablename__ = "deals"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), index=True)
    codename: Mapped[str] = mapped_column(String(255))
    entity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vertical: Mapped[str] = mapped_column(String(64))
    state: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    asking_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2), nullable=True)
    claimed_sde: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2), nullable=True)
    deal_type: Mapped[str] = mapped_column(String(16), default="asset")  # asset|stock
    stage: Mapped[str] = mapped_column(String(32), default="Uploading")
    completeness_score: Mapped[int] = mapped_column(Integer, default=0)
    sla_due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    tier: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    org: Mapped[Org] = relationship(back_populates="deals")
    documents: Mapped[list["Document"]] = relationship(back_populates="deal")
    flags: Mapped[list["FlagRow"]] = relationship(back_populates="deal")


class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), index=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    storage_key: Mapped[str] = mapped_column(String(512))
    doc_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    entity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    classification_confidence: Mapped[Optional[float]] = mapped_column(nullable=True)
    user_override: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    deal: Mapped[Deal] = relationship(back_populates="documents")


class Extraction(Base, TimestampMixin):
    __tablename__ = "extractions"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    page_citations: Mapped[list] = mapped_column(JSON, default=list)
    model: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="ok")


class FinancialLineRow(Base):
    """The ONLY table the reconciliation engine reads from (SPEC §7)."""

    __tablename__ = "financial_lines"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), index=True)
    source_doc_id: Mapped[str] = mapped_column(String(64))
    statement_type: Mapped[str] = mapped_column(String(32))
    period: Mapped[int] = mapped_column(Integer)
    line_code: Mapped[str] = mapped_column(String(48))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    page_ref: Mapped[dict] = mapped_column(JSON, default=dict)


class FlagRule(Base, TimestampMixin):
    __tablename__ = "flag_rules"
    rule_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    category: Mapped[str] = mapped_column(String(64))
    logic_spec: Mapped[dict] = mapped_column(JSON, default=dict)
    thresholds: Mapped[dict] = mapped_column(JSON, default=dict)
    vertical_overrides: Mapped[dict] = mapped_column(JSON, default=dict)
    default_severity: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(Text)
    buyer_action: Mapped[str] = mapped_column(Text, default="")
    ask_seller: Mapped[list] = mapped_column(JSON, default=list)
    what_resolves: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class FlagRow(Base, TimestampMixin):
    __tablename__ = "flags"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), index=True)
    rule_id: Mapped[str] = mapped_column(String(16))
    rule_version: Mapped[int] = mapped_column(Integer, default=1)
    severity: Mapped[str] = mapped_column(String(16))
    category: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(Text)
    detail: Mapped[str] = mapped_column(Text, default="")
    computed_values: Mapped[dict] = mapped_column(JSON, default=dict)
    evidence_refs: Mapped[list] = mapped_column(JSON, default=list)
    # buyer workflow
    status: Mapped[str] = mapped_column(String(16), default="open")
    buyer_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # admin QA
    admin_verdict: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    admin_reason: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    deal: Mapped[Deal] = relationship(back_populates="flags")


class Report(Base, TimestampMixin):
    __tablename__ = "reports"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    html_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    pdf_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    watermark: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class QALabel(Base, TimestampMixin):
    """The moat table (SPEC §5, §9): human verdicts become training labels."""

    __tablename__ = "qa_labels"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    flag_id: Mapped[str] = mapped_column(ForeignKey("flags.id"), index=True)
    rule_id: Mapped[str] = mapped_column(String(16))
    model_output: Mapped[dict] = mapped_column(JSON, default=dict)
    human_verdict: Mapped[str] = mapped_column(String(16))  # approve|edit|suppress
    reason_code: Mapped[str] = mapped_column(String(64))
    created_by: Mapped[str] = mapped_column(String(64))


class Benchmark(Base, TimestampMixin):
    __tablename__ = "benchmarks"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    vertical: Mapped[str] = mapped_column(String(64), index=True)
    metric: Mapped[str] = mapped_column(String(64))
    p25: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    p50: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    p75: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    n_deals: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(255), default="")


class AuditLog(Base):
    """Append-only. Rows are never updated or deleted (SPEC §7 security)."""

    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    actor: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    before_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    after_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), index=True)
    stripe_ref: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    tier: Mapped[str] = mapped_column(String(64))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(24), default="pending")


class LLMCall(Base):
    __tablename__ = "llm_calls"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uid)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    deal_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    prompt_id: Mapped[str] = mapped_column(String(32))
    prompt_version: Mapped[int] = mapped_column(Integer)
    model: Mapped[str] = mapped_column(String(64))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=1)

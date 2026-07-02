"""Structured facts the rules engine reads, plus the ``Flag`` output type.

The financial *math* comes from ``engine.reconcile``; the *non-statement* facts
here (customers, channels, contracts, lease terms, bank behaviour, add-backs)
come from extraction of the same documents. Together with the reconciliation
result they form the ``DealContext`` — the sole input to Stage 4.

All amounts are ``Decimal``. Every fact carries a ``PageRef`` so a fired flag
can point at the exact page that produced it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from ..engine.model import FinancialLine, PageRef
from ..engine.money import money
from ..engine.reconcile import ReconciliationResult


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    INFO = "INFO"

    @property
    def rank(self) -> int:
        return {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}[self.value]


# --- extracted, non-statement facts -----------------------------------------


@dataclass
class Customer:
    name: str
    revenue: Decimal
    period: int
    source: PageRef

    def __post_init__(self) -> None:
        self.revenue = money(self.revenue)


@dataclass
class MonthlyRevenue:
    """One month of revenue, used by A2 to catch a trailing-12-month decline
    that calendar-year totals would hide."""

    year: int
    month: int  # 1..12
    amount: Decimal
    source: PageRef

    def __post_init__(self) -> None:
        self.amount = money(self.amount)

    @property
    def key(self) -> int:
        return self.year * 12 + (self.month - 1)


@dataclass
class Channel:
    name: str
    revenue: Decimal
    period: int
    source: PageRef

    def __post_init__(self) -> None:
        self.revenue = money(self.revenue)


@dataclass
class AddBack:
    description: str
    amount: Decimal
    category: str  # e.g. "personal", "owner_salary", "one_time", "rent", "auto"
    documented: bool
    period: int
    source: PageRef

    def __post_init__(self) -> None:
        self.amount = money(self.amount)


@dataclass
class OneTimeItem:
    description: str  # e.g. "PPP forgiveness", "ERC credit", "equipment sale"
    amount: Decimal
    period: int
    classified_as_recurring: bool
    source: PageRef

    def __post_init__(self) -> None:
        self.amount = money(self.amount)


@dataclass
class ContractFact:
    counterparty: str
    kind: str  # "customer" | "supplier"
    is_key: bool  # a claimed top-10 relationship
    change_of_control: bool
    assignment_allowed: Optional[bool]
    clause_ref: str
    source: PageRef


@dataclass
class LeaseFact:
    term_remaining_years: Optional[Decimal]
    assignment_allowed: Optional[bool]
    personal_guarantee: bool
    source: PageRef

    def __post_init__(self) -> None:
        if self.term_remaining_years is not None:
            self.term_remaining_years = Decimal(str(self.term_remaining_years))


@dataclass
class BankSignals:
    nsf_count: int = 0
    mca_detected: bool = False
    mca_debits: List[str] = field(default_factory=list)  # e.g. lender names seen
    source: Optional[PageRef] = None


@dataclass
class RealEstate:
    seller_owns_operating_property: bool = False
    rent_expense: Optional[Decimal] = None
    market_rent_estimate: Optional[Decimal] = None
    source: Optional[PageRef] = None

    def __post_init__(self) -> None:
        if self.rent_expense is not None:
            self.rent_expense = money(self.rent_expense)
        if self.market_rent_estimate is not None:
            self.market_rent_estimate = money(self.market_rent_estimate)


@dataclass
class Benchmark:
    metric: str
    p25: Decimal
    p50: Decimal
    p75: Decimal
    n_deals: int
    source: str


@dataclass
class DealFacts:
    vertical: str
    deal_type: str  # "asset" | "stock"
    asking_price: Decimal
    claimed_sde: Decimal
    customers: List[Customer] = field(default_factory=list)
    monthly_revenue: List[MonthlyRevenue] = field(default_factory=list)
    channels: List[Channel] = field(default_factory=list)
    addbacks: List[AddBack] = field(default_factory=list)
    one_time_items: List[OneTimeItem] = field(default_factory=list)
    contracts: List[ContractFact] = field(default_factory=list)
    lease: Optional[LeaseFact] = None
    bank_signals: BankSignals = field(default_factory=BankSignals)
    real_estate: RealEstate = field(default_factory=RealEstate)
    benchmarks: Dict[str, Benchmark] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.asking_price = money(self.asking_price)
        self.claimed_sde = money(self.claimed_sde)


@dataclass
class DealContext:
    lines: List[FinancialLine]
    reconciliation: ReconciliationResult
    facts: DealFacts


# --- rule output -------------------------------------------------------------


@dataclass
class Flag:
    rule_id: str
    rule_version: int
    category: str
    severity: Severity
    title: str  # one-line finding
    detail: str  # short, number-bearing explanation
    computed_values: Dict[str, object]
    evidence_refs: List[dict]
    buyer_action: str
    ask_seller: List[str]
    what_resolves: str

    def as_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "category": self.category,
            "severity": self.severity.value,
            "title": self.title,
            "detail": self.detail,
            "computed_values": self.computed_values,
            "evidence_refs": self.evidence_refs,
            "buyer_action": self.buyer_action,
            "ask_seller": self.ask_seller,
            "what_resolves": self.what_resolves,
        }

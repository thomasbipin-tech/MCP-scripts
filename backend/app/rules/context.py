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
class YearAmount:
    """A dated amount with a citation (deferred revenue, ERC, etc.)."""

    period: int
    amount: Decimal
    source: PageRef
    label: str = ""

    def __post_init__(self) -> None:
        self.amount = money(self.amount)


@dataclass
class RelatedParty:
    """Revenue booked with an entity connected to the seller (A3)."""

    name: str
    amount: Decimal
    period: int
    note: str
    source: PageRef

    def __post_init__(self) -> None:
        self.amount = money(self.amount)


@dataclass
class InvoiceStats:
    """Aggregate invoice shape used for the round-number fabrication signal (A7)."""

    total_count: int
    round_count: int  # invoices landing on a round amount ($X,000 etc.)
    source: Optional[PageRef] = None


@dataclass
class PeopleFacts:
    """Org/people signals (E31-E33, E32 misclassification)."""

    key_person_roles: List[str] = field(default_factory=list)  # E31
    count_1099: int = 0  # E32
    count_w2_typical_roles: int = 0  # E32 denominator
    near_retirement_count: int = 0  # E33
    owner_hours_per_week: Optional[int] = None  # B11
    family_below_market_payroll: Optional[Decimal] = None  # B13
    source: Optional[PageRef] = None

    def __post_init__(self) -> None:
        if self.family_below_market_payroll is not None:
            self.family_below_market_payroll = money(self.family_below_market_payroll)


@dataclass
class ComplianceFacts:
    """Legal / tax / compliance signals detected across the data room.

    Every field defaults to 'absent' (empty / None) so a rule only fires when
    extraction actually surfaced the signal — never on missing data."""

    non_assignable_licenses: List[str] = field(default_factory=list)  # D26
    missing_top_customer_contracts: List[str] = field(default_factory=list)  # D27
    litigation_mentions: List[str] = field(default_factory=list)  # D28
    seller_noncompete_ok: Optional[bool] = None  # D29 (fires only when explicitly False)
    franchise_transfer_restriction: Optional[bool] = None  # D30
    missing_insurance: List[str] = field(default_factory=list)  # E34
    sales_tax_nexus_states: List[str] = field(default_factory=list)  # F35
    payroll_tax_irregularities: bool = False  # F36
    cash_heavy_inconsistency: bool = False  # F37
    aggressive_erc: Optional[Decimal] = None  # F38
    undisclosed_debt_service: List[str] = field(default_factory=list)  # C23
    deferred_revenue: List[YearAmount] = field(default_factory=list)  # A6
    seasonality_anomaly: Optional[bool] = None  # A8
    working_capital_peg_in_loi: Optional[bool] = None  # G40 (fires only when False)
    source: Optional[PageRef] = None

    def __post_init__(self) -> None:
        if self.aggressive_erc is not None:
            self.aggressive_erc = money(self.aggressive_erc)


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
    related_parties: List[RelatedParty] = field(default_factory=list)
    invoice_stats: Optional[InvoiceStats] = None
    people: PeopleFacts = field(default_factory=PeopleFacts)
    compliance: ComplianceFacts = field(default_factory=ComplianceFacts)

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

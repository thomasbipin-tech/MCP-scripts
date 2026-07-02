"""Rule evaluators — the interpreters for each ``RuleDef.kind``.

Each evaluator reads the ``DealContext`` and the rule's (vertical-resolved)
thresholds and returns zero or more ``Flag``s. All arithmetic uses ``Decimal``
via the money helpers; evaluators never call an LLM and never mutate the
context. A rule fires only when its condition is met — the table-driven tests in
``tests/test_rules.py`` assert both the fire and the no-fire cases.
"""

from __future__ import annotations

import string
from decimal import Decimal
from typing import Callable, Dict, List, Optional

from ..engine.model import LineCode, StatementType, get_line
from ..engine.money import money, pct, ratio
from .context import DealContext, Flag, Severity
from .registry import RuleDef


class _Safe(dict):
    """format_map backing that leaves unknown placeholders untouched."""

    def __missing__(self, key):  # pragma: no cover - trivial
        return "{" + key + "}"


def _fmt(template: str, values: Dict[str, object]) -> str:
    return string.Formatter().vformat(template, (), _Safe(values))


def _mk(
    rule: RuleDef,
    severity: Severity,
    values: Dict[str, object],
    evidence: List[dict],
    title: Optional[str] = None,
) -> Flag:
    return Flag(
        rule_id=rule.rule_id,
        rule_version=rule.version,
        category=rule.category,
        severity=severity,
        title=title or rule.title,
        detail=_fmt(rule.title, values),
        computed_values=values,
        evidence_refs=evidence,
        buyer_action=rule.buyer_action,
        ask_seller=[_fmt(q, values) for q in rule.ask_seller],
        what_resolves=rule.what_resolves,
    )


# --- Triangle of Truth -------------------------------------------------------


def eval_tax_pnl_divergence(rule, ctx, th) -> List[Flag]:
    warn, high, crit = th["warn_pct"], th["high_pct"], th["critical_pct"]
    out: List[Flag] = []
    for t in ctx.reconciliation.triangle:
        d = t.tax_vs_pnl_divergence_pct
        if d is None:
            continue
        mag = abs(d)
        if mag <= warn:
            continue
        sev = (
            Severity.CRITICAL
            if mag > crit
            else Severity.HIGH if mag > high else Severity.MEDIUM
        )
        out.append(
            _mk(
                rule,
                sev,
                {
                    "year": t.period,
                    "tax_revenue": str(t.tax_revenue),
                    "pnl_revenue": str(t.pnl_revenue),
                    "divergence": str(mag),
                },
                t.sources,
            )
        )
    return out


def eval_deposit_shortfall(rule, ctx, th) -> List[Flag]:
    high_c, crit_c = th["high_coverage_pct"], th["critical_coverage_pct"]
    out: List[Flag] = []
    for t in ctx.reconciliation.triangle:
        cov = t.deposit_coverage_pct
        if cov is None or cov >= high_c:
            continue
        sev = Severity.CRITICAL if cov < crit_c else Severity.HIGH
        out.append(
            _mk(
                rule,
                sev,
                {
                    "year": t.period,
                    "coverage": str(cov),
                    "bank_deposits": str(t.bank_deposits),
                    "pnl_revenue": str(t.pnl_revenue),
                },
                t.sources,
            )
        )
    return out


# --- Category A --------------------------------------------------------------


def _latest_period(ctx: DealContext) -> Optional[int]:
    return ctx.reconciliation.latest_period()


def _pnl_revenue(ctx: DealContext, period: int) -> Optional[Decimal]:
    for m in ctx.reconciliation.pnl_revenue:
        if m.period == period and m.value is not None:
            return m.value
    return None


def eval_customer_concentration(rule, ctx, th) -> List[Flag]:
    period = _latest_period(ctx)
    if period is None:
        return []
    customers = [c for c in ctx.facts.customers if c.period == period]
    if not customers:
        return []
    base = _pnl_revenue(ctx, period) or sum((c.revenue for c in customers), Decimal("0"))
    if base == 0:
        return []
    out: List[Flag] = []
    for c in sorted(customers, key=lambda x: x.revenue, reverse=True):
        share = pct(c.revenue, base)
        if share is None or share < th["high_pct"]:
            continue
        sev = Severity.CRITICAL if share >= th["critical_pct"] else Severity.HIGH
        out.append(
            _mk(
                rule,
                sev,
                {
                    "customer": c.name,
                    "share": str(share),
                    "revenue": str(c.revenue),
                    "year": period,
                },
                [c.source.as_dict()],
            )
        )
    return out


def eval_revenue_cliff(rule, ctx, th) -> List[Flag]:
    months = sorted(ctx.facts.monthly_revenue, key=lambda m: m.key)
    if len(months) < 24:
        return []
    last12 = months[-12:]
    prev12 = months[-24:-12]
    cur = sum((m.amount for m in last12), Decimal("0"))
    prior = sum((m.amount for m in prev12), Decimal("0"))
    if prior == 0:
        return []
    change = pct(cur - prior, prior)  # negative = decline
    if change is None or change > -Decimal(str(th["decline_pct"])):
        return []
    decline = abs(change)
    ev = [last12[0].source.as_dict(), last12[-1].source.as_dict()]
    return [
        _mk(
            rule,
            rule.default_severity,
            {
                "decline": str(decline),
                "ttm_revenue": str(cur),
                "prior_ttm_revenue": str(prior),
            },
            ev,
        )
    ]


def eval_one_time_revenue(rule, ctx, th) -> List[Flag]:
    out: List[Flag] = []
    crit_pct = Decimal(str(th["critical_pct_of_revenue"]))
    for item in ctx.facts.one_time_items:
        if not item.classified_as_recurring:
            continue
        rev = _pnl_revenue(ctx, item.period)
        share = pct(item.amount, rev) if rev else None
        sev = (
            Severity.CRITICAL
            if (share is not None and share >= crit_pct)
            else rule.default_severity
        )
        out.append(
            _mk(
                rule,
                sev,
                {
                    "item": item.description,
                    "amount": str(item.amount),
                    "year": item.period,
                    "share": None if share is None else str(share),
                },
                [item.source.as_dict()],
            )
        )
    return out


def eval_channel_dependency(rule, ctx, th) -> List[Flag]:
    period = _latest_period(ctx)
    if period is None:
        return []
    channels = [c for c in ctx.facts.channels if c.period == period]
    if not channels:
        return []
    base = _pnl_revenue(ctx, period) or sum((c.revenue for c in channels), Decimal("0"))
    if base == 0:
        return []
    out: List[Flag] = []
    for c in channels:
        share = pct(c.revenue, base)
        if share is None or share < th["high_pct"]:
            continue
        out.append(
            _mk(
                rule,
                rule.default_severity,
                {"channel": c.name, "share": str(share), "year": period},
                [c.source.as_dict()],
            )
        )
    return out


# --- Category B --------------------------------------------------------------


def eval_addback_magnitude(rule, ctx, th) -> List[Flag]:
    sde = ctx.facts.claimed_sde
    if sde <= 0 or not ctx.facts.addbacks:
        return []
    total_ab = sum((a.amount for a in ctx.facts.addbacks), Decimal("0"))
    p = pct(total_ab, sde)
    if p is None or p < th["high_pct"]:
        return []
    sev = Severity.CRITICAL if p >= th["critical_pct"] else Severity.HIGH
    ev = [a.source.as_dict() for a in ctx.facts.addbacks]
    return [
        _mk(
            rule,
            sev,
            {
                "addback_pct": str(p),
                "addback_total": str(money(total_ab)),
                "claimed_sde": str(sde),
            },
            ev,
        )
    ]


def eval_undocumented_addbacks(rule, ctx, th) -> List[Flag]:
    undoc = [
        a
        for a in ctx.facts.addbacks
        if not a.documented and a.category in ("personal", "one_time", "auto")
    ]
    if not undoc:
        return []
    amt = sum((a.amount for a in undoc), Decimal("0"))
    return [
        _mk(
            rule,
            rule.default_severity,
            {"amount": str(money(amt)), "count": len(undoc)},
            [a.source.as_dict() for a in undoc],
        )
    ]


def eval_below_market_rent(rule, ctx, th) -> List[Flag]:
    re = ctx.facts.real_estate
    if not (
        re.seller_owns_operating_property
        and re.rent_expense is not None
        and re.market_rent_estimate is not None
        and re.market_rent_estimate > 0
    ):
        return []
    threshold = re.market_rent_estimate * Decimal(str(th["below_market_ratio"]))
    if re.rent_expense >= threshold:
        return []
    ev = [re.source.as_dict()] if re.source else []
    return [
        _mk(
            rule,
            rule.default_severity,
            {
                "rent": str(re.rent_expense),
                "market": str(re.market_rent_estimate),
                "gap": str(money(re.market_rent_estimate - re.rent_expense)),
            },
            ev,
        )
    ]


def eval_capex_starvation(rule, ctx, th) -> List[Flag]:
    series = ctx.reconciliation.capex_vs_depreciation
    # Count consecutive most-recent years where capex - depreciation < 0.
    streak = 0
    ev: List[dict] = []
    for m in reversed(series):
        if m.value is not None and m.value < 0:
            streak += 1
            ev.extend(m.sources)
        else:
            break
    if streak < th["consecutive_years"]:
        return []
    return [
        _mk(rule, rule.default_severity, {"years": streak}, ev)
    ]


# --- Category C --------------------------------------------------------------


def eval_working_capital_trend(rule, ctx, th) -> List[Flag]:
    series = [m for m in ctx.reconciliation.working_capital if m.value is not None]
    if not series:
        return []
    latest = series[-1]
    negative = latest.value < 0
    declining = False
    if len(series) >= 2 and series[-2].value not in (None, 0):
        change = pct(latest.value - series[-2].value, abs(series[-2].value))
        declining = change is not None and change < -Decimal(str(th["decline_pct"]))
    if not (negative or declining):
        return []
    return [
        _mk(
            rule,
            rule.default_severity,
            {
                "working_capital": str(latest.value),
                "negative": negative,
                "declining": declining,
                "year": latest.period,
            },
            latest.sources,
        )
    ]


def eval_ar_aging(rule, ctx, th) -> List[Flag]:
    period = _latest_period(ctx)
    if period is None:
        return []
    ar = get_line(ctx.lines, StatementType.BALANCE_SHEET, period, LineCode.ACCOUNTS_RECEIVABLE)
    past = get_line(ctx.lines, StatementType.BALANCE_SHEET, period, LineCode.AR_PAST_90)
    if ar is None or past is None or ar.amount == 0:
        return []
    p = pct(past.amount, ar.amount)
    if p is None or p < th["past_90_pct"]:
        return []
    return [
        _mk(
            rule,
            rule.default_severity,
            {"past_90_pct": str(p), "ar_total": str(ar.amount), "ar_past_90": str(past.amount)},
            [ar.source.as_dict(), past.source.as_dict()],
        )
    ]


def eval_nsf_overdraft(rule, ctx, th) -> List[Flag]:
    n = ctx.facts.bank_signals.nsf_count
    if n < th["count"]:
        return []
    ev = []
    if ctx.facts.bank_signals.source:
        ev = [ctx.facts.bank_signals.source.as_dict()]
    return [_mk(rule, rule.default_severity, {"count": n}, ev)]


def eval_mca_factoring(rule, ctx, th) -> List[Flag]:
    bs = ctx.facts.bank_signals
    if not bs.mca_detected:
        return []
    ev = [bs.source.as_dict()] if bs.source else []
    return [
        _mk(
            rule,
            rule.default_severity,
            {"lenders": ", ".join(bs.mca_debits) or "unnamed lender(s)"},
            ev,
        )
    ]


# --- Category D --------------------------------------------------------------


def eval_change_of_control(rule, ctx, th) -> List[Flag]:
    out: List[Flag] = []
    for c in ctx.facts.contracts:
        if c.change_of_control and c.is_key:
            out.append(
                _mk(
                    rule,
                    rule.default_severity,
                    {"counterparty": c.counterparty, "clause": c.clause_ref},
                    [c.source.as_dict()],
                )
            )
    return out


def eval_lease_risk(rule, ctx, th) -> List[Flag]:
    lease = ctx.facts.lease
    if lease is None:
        return []
    issues: List[str] = []
    if (
        lease.term_remaining_years is not None
        and lease.term_remaining_years < Decimal(str(th["min_term_years"]))
    ):
        issues.append(f"only {lease.term_remaining_years} years remaining")
    if lease.assignment_allowed is False:
        issues.append("no assignment right")
    if lease.personal_guarantee:
        issues.append("personal guarantee required")
    if not issues:
        return []
    return [
        _mk(
            rule,
            rule.default_severity,
            {"issues": "; ".join(issues)},
            [lease.source.as_dict()],
        )
    ]


# --- Category G --------------------------------------------------------------


def eval_asking_multiple(rule, ctx, th) -> List[Flag]:
    bm = ctx.facts.benchmarks.get("sde_multiple")
    if bm is None or ctx.facts.claimed_sde <= 0:
        return []
    multiple = ratio(ctx.facts.asking_price, ctx.facts.claimed_sde)
    if multiple is None:
        return []
    vs = ratio(multiple, bm.p50) if bm.p50 else None
    sev = (
        Severity.HIGH
        if (vs is not None and vs >= Decimal(str(th["high_ratio_vs_benchmark"])))
        else Severity.INFO
    )
    return [
        _mk(
            rule,
            sev,
            {
                "multiple": str(multiple),
                "p25": str(bm.p25),
                "p50": str(bm.p50),
                "p75": str(bm.p75),
                "vs_median": None if vs is None else str(vs),
            },
            [],
        )
    ]


EVALUATORS: Dict[str, Callable] = {
    "tax_pnl_divergence": eval_tax_pnl_divergence,
    "deposit_shortfall": eval_deposit_shortfall,
    "customer_concentration": eval_customer_concentration,
    "revenue_cliff": eval_revenue_cliff,
    "one_time_revenue": eval_one_time_revenue,
    "channel_dependency": eval_channel_dependency,
    "addback_magnitude": eval_addback_magnitude,
    "undocumented_addbacks": eval_undocumented_addbacks,
    "below_market_rent": eval_below_market_rent,
    "capex_starvation": eval_capex_starvation,
    "working_capital_trend": eval_working_capital_trend,
    "ar_aging": eval_ar_aging,
    "nsf_overdraft": eval_nsf_overdraft,
    "mca_factoring": eval_mca_factoring,
    "change_of_control": eval_change_of_control,
    "lease_risk": eval_lease_risk,
    "asking_multiple": eval_asking_multiple,
}

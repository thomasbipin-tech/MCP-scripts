"""Decimal money primitives for the DealProof reconciliation engine.

Hard rule (SPEC §2.3): the LLM never does arithmetic that reaches the report.
Every number the engine computes flows through this module so that:
  * money is ``Decimal`` end to end (never ``float``) — no binary rounding drift,
  * comparisons use a single, documented rounding convention,
  * percentages are computed one way, everywhere.

Nothing here imports third-party code; the whole engine runs on the stdlib so
its test suite is deterministic and dependency-free.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Iterable, Optional, Union

Number = Union[int, str, Decimal]

CENTS = Decimal("0.01")
PCT = Decimal("0.1")  # percentages reported to one decimal place


def money(value: Number) -> Decimal:
    """Coerce a value to a 2-dp ``Decimal`` amount.

    Accepts ``int``, ``str`` or ``Decimal``. Rejects ``float`` deliberately —
    floats are how rounding bugs get into financial software. Callers holding a
    float must convert via ``str(x)`` at the boundary and own that decision.
    """
    if isinstance(value, float):  # pragma: no cover - guard rail
        raise TypeError(
            "float is not accepted by money(); convert via str() at the boundary"
        )
    try:
        return Decimal(value).quantize(CENTS, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:  # pragma: no cover - defensive
        raise ValueError(f"cannot interpret {value!r} as money") from exc


def pct(numerator: Decimal, denominator: Decimal) -> Optional[Decimal]:
    """Return ``numerator / denominator`` as a percentage (0..100 scale).

    Returns ``None`` when the denominator is zero, so callers must handle the
    "no basis for comparison" case explicitly rather than dividing by zero or
    silently producing a misleading 0%.
    """
    if denominator == 0:
        return None
    result = (Decimal(numerator) / Decimal(denominator)) * Decimal(100)
    return result.quantize(PCT, rounding=ROUND_HALF_UP)


def ratio(numerator: Decimal, denominator: Decimal) -> Optional[Decimal]:
    """Return ``numerator / denominator`` as a multiple (e.g. price/SDE)."""
    if denominator == 0:
        return None
    return (Decimal(numerator) / Decimal(denominator)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def divergence_pct(a: Decimal, b: Decimal) -> Optional[Decimal]:
    """Signed divergence of ``a`` from baseline ``b``, as a percentage.

    Positive means ``a`` exceeds ``b``. Used for tax-vs-P&L revenue gaps where
    the *direction* of the gap matters (overstatement vs understatement).
    """
    if b == 0:
        return None
    return pct(Decimal(a) - Decimal(b), Decimal(b))


def total(values: Iterable[Number]) -> Decimal:
    """Sum an iterable of amounts as money."""
    acc = Decimal("0")
    for v in values:
        acc += money(v)
    return acc.quantize(CENTS, rounding=ROUND_HALF_UP)

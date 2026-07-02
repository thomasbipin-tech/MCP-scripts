"""Stage 5 support — the grounded evidence bundle and its guard.

The narrator (Claude) writes the report prose FROM this bundle only. SPEC §2.3:
"the LLM may not introduce numbers not in the evidence." We enforce that
mechanically here — ``assert_grounded`` scans generated prose for numeric tokens
and rejects any that don't appear in the bundle. This is both the accuracy story
and the liability story, so it is code, not a prompt suggestion.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Iterable, List, Set

from ..rules.context import DealContext, Flag
from ..rules.engine import severity_counts


def build_evidence_bundle(ctx: DealContext, flags: List[Flag]) -> dict:
    """Assemble the JSON the narrator is allowed to see."""
    return {
        "deal": {
            "vertical": ctx.facts.vertical,
            "deal_type": ctx.facts.deal_type,
            "asking_price": str(ctx.facts.asking_price),
            "claimed_sde": str(ctx.facts.claimed_sde),
        },
        "reconciliation": ctx.reconciliation.as_dict(),
        "severity_counts": severity_counts(flags),
        "flags": [f.as_dict() for f in flags],
    }


# --- grounding guard ---------------------------------------------------------

# Matches numbers with optional $, commas, decimals, and a trailing %.
_NUM_RE = re.compile(r"-?\$?\d[\d,]*(?:\.\d+)?%?")
# Small integers and years are allowed as free prose (counts, "3 years", 2023).
_ALLOWED_BARE_INTS = set(range(0, 13)) | set(range(1990, 2100))


def _canonical_numbers(value) -> Set[str]:
    """Recursively collect canonical numeric strings from an evidence value."""
    found: Set[str] = set()

    def add(tok: str) -> None:
        norm = _normalize(tok)
        if norm is not None:
            found.add(norm)

    if isinstance(value, dict):
        for v in value.values():
            found |= _canonical_numbers(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            found |= _canonical_numbers(v)
    elif isinstance(value, (int, float, Decimal)):
        add(str(value))
    elif isinstance(value, str):
        for m in _NUM_RE.findall(value):
            add(m)
    return found


def _normalize(token: str) -> str | None:
    """Normalize a numeric token to a comparable canonical form.

    ``$1,234.50`` -> ``1234.50`` -> ``1234.5``; ``92.0%`` -> ``92`` etc. Returns
    ``None`` if the token isn't actually numeric.
    """
    t = token.strip().lstrip("$").rstrip("%").replace(",", "")
    if t in ("", "-", "."):
        return None
    try:
        d = Decimal(t)
    except InvalidOperation:
        return None
    d = d.normalize()
    # Avoid scientific notation from normalize() for integers like 1E+3.
    return format(d, "f")


def assert_grounded(prose: str, bundle: dict) -> List[str]:
    """Return the list of numeric tokens in ``prose`` NOT present in ``bundle``.

    An empty list means the narration is fully grounded. Callers (the narration
    stage) reject-and-retry when this is non-empty, so no ungrounded number ever
    reaches a report.
    """
    allowed = _canonical_numbers(bundle)
    violations: List[str] = []
    for raw in _NUM_RE.findall(prose):
        norm = _normalize(raw)
        if norm is None:
            continue
        if norm in allowed:
            continue
        # Permit bare small integers / years used as ordinary prose.
        try:
            as_int = int(Decimal(norm))
            if Decimal(norm) == as_int and as_int in _ALLOWED_BARE_INTS:
                continue
        except (InvalidOperation, ValueError):
            pass
        violations.append(raw)
    return violations

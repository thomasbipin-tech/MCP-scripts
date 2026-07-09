"""Stage 4 — the rules engine.

Runs every active ``RuleDef`` through its evaluator against a ``DealContext`` and
returns the fired ``Flag``s, sorted most-severe first. Deterministic and
side-effect free: same context in, same flags out — which is what makes the
golden test in ``tests/test_seed_golden.py`` a meaningful contract.
"""

from __future__ import annotations

from typing import List

from .context import DealContext, Flag
from .evaluators import EVALUATORS
from .registry import RuleDef, active_rules


class RuleExecutionError(RuntimeError):
    def __init__(self, rule_id: str, original: Exception):
        super().__init__(f"rule {rule_id} raised: {original!r}")
        self.rule_id = rule_id
        self.original = original


def evaluate_rule(rule: RuleDef, ctx: DealContext) -> List[Flag]:
    evaluator = EVALUATORS.get(rule.kind)
    if evaluator is None:  # pragma: no cover - registry/evaluator drift guard
        raise RuleExecutionError(rule.rule_id, KeyError(f"no evaluator for {rule.kind}"))
    thresholds = rule.resolved_thresholds(ctx.facts.vertical)
    try:
        return list(evaluator(rule, ctx, thresholds) or [])
    except Exception as exc:  # fail loud per-rule; never poison the whole run
        raise RuleExecutionError(rule.rule_id, exc) from exc


def run_rules(
    ctx: DealContext,
    rules: List[RuleDef] | None = None,
    strict: bool = True,
) -> List[Flag]:
    """Evaluate all rules and return the fired flags, most-severe first.

    ``strict=True`` (default, used by tests) surfaces any evaluator error so
    regressions are caught. ``strict=False`` (used by the pipeline) is
    fail-soft: a rule that trips on malformed/inaccurate input is skipped and
    recorded, so one bad figure can never sink the entire report. Use
    ``run_rules_verbose`` when you need the skipped-rule list."""
    flags, _ = run_rules_verbose(ctx, rules, strict=strict)
    return flags


def run_rules_verbose(
    ctx: DealContext,
    rules: List[RuleDef] | None = None,
    strict: bool = True,
) -> tuple[List[Flag], List["RuleExecutionError"]]:
    rules = rules if rules is not None else active_rules()
    flags: List[Flag] = []
    errors: List[RuleExecutionError] = []
    for rule in rules:
        try:
            flags.extend(evaluate_rule(rule, ctx))
        except RuleExecutionError as exc:
            if strict:
                raise
            errors.append(exc)
    # Sort by severity rank, then rule id, for a stable, readable ledger.
    flags.sort(key=lambda f: (f.severity.rank, f.rule_id))
    return flags, errors


def severity_counts(flags: List[Flag]) -> dict:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "INFO": 0}
    for f in flags:
        counts[f.severity.value] += 1
    return counts

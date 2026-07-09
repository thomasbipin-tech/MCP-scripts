"""Adversarial / robustness tests: what happens when the data is *wrong*.

The whole point of the product is inaccurate seller data, so the engine must (a)
never crash on garbage, contradictory, missing, or implausible figures, and (b)
surface the right Data-Quality caveats instead of silently trusting bad numbers.
"""

from decimal import Decimal

from app.engine.model import FinancialLine, LineCode, PageRef, StatementType
from app.engine.reconcile import reconcile
from app.pipeline.ingest import ingest_documents
from app.pipeline.runner import run_pipeline
from app.rules.context import Severity
from app.rules.engine import evaluate_rule, run_rules, run_rules_verbose
from app.rules.registry import RULES_BY_ID
from tests.helpers import make_ctx, pref

BENCH = {"sde_multiple": {"p25": Decimal("2.5"), "p50": Decimal("3.0"), "p75": Decimal("3.7"), "n_deals": 9, "source": "t"}}
META = {"vertical": "hvac", "deal_type": "asset", "asking_price": "1000000", "claimed_sde": "300000"}


def _line(st, yr, code, amt):
    return FinancialLine(st, yr, code, amt, PageRef("d", 1, "x"))


def run(rid, ctx):
    return evaluate_rule(RULES_BY_ID[rid], ctx)


# --- the engine never crashes on degenerate input ---------------------------


def test_empty_context_does_not_crash():
    ctx = make_ctx([])
    flags = run_rules(ctx)  # strict path
    assert isinstance(flags, list)


def test_zero_revenue_no_division_error():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "0"),
        _line(StatementType.PNL, 2024, LineCode.COGS, "0"),
        _line(StatementType.BANK_STATEMENT, 2024, LineCode.BANK_DEPOSITS, "0"),
    ])
    # Must not raise; coverage/margin are undefined, not zero-division.
    run_rules(ctx)


def test_huge_and_negative_numbers_are_handled():
    ctx = make_ctx([
        _line(StatementType.TAX_RETURN, 2024, LineCode.REVENUE, "-500000"),
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "999999999999"),
    ])
    run_rules(ctx)  # no overflow / no crash


def test_garbage_pdf_bytes_do_not_crash_ingest():
    docs = [
        {"doc_id": "g1", "filename": "junk.pdf", "pdf_bytes": b"this is not a pdf"},
        {"doc_id": "g2", "filename": "empty.pdf", "pdf_bytes": b""},
    ]
    result = ingest_documents(docs, META, BENCH)
    # Nothing extractable -> no financial lines, classified 'other'/low-conf.
    assert result.context.lines == []
    assert all(d.page_count == 0 for d in result.documents)


def test_full_pipeline_on_empty_deal_produces_valid_report():
    docs = [{"doc_id": "g", "filename": "junk.pdf", "pdf_bytes": b"nonsense"}]
    ctx = ingest_documents(docs, META, BENCH).context
    report = run_pipeline(ctx, {"codename": "Empty Co", "vertical": "hvac",
                                "asking_price": "1000000", "claimed_sde": "300000"})
    # A real, serializable report with everything flagged as a data gap.
    assert report["severity_counts"]["CRITICAL"] == 0
    assert len(report["data_gaps"]) >= 3
    assert report["watermark"] == "PRELIMINARY — MATERIAL GAPS"


# --- Data-Quality rules fire on inaccurate figures --------------------------


def test_dq1_missing_triangulation_when_only_one_source():
    ctx = make_ctx([_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")])
    flags = run("DQ1", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.MEDIUM


def test_dq1_silent_when_two_sources_present():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.BANK_STATEMENT, 2024, LineCode.BANK_DEPOSITS, "950000"),
    ])
    assert run("DQ1", ctx) == []


def test_dq2_cogs_exceeds_revenue():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "500000"),
        _line(StatementType.PNL, 2024, LineCode.COGS, "650000"),  # negative gross margin
    ])
    flags = run("DQ2", ctx)
    assert len(flags) == 1
    assert run("DQ2", make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "500000"),
        _line(StatementType.PNL, 2024, LineCode.COGS, "300000"),
    ])) == []


def test_dq3_nonpositive_revenue():
    ctx = make_ctx([_line(StatementType.TAX_RETURN, 2024, LineCode.REVENUE, "0")])
    assert len(run("DQ3", ctx)) == 1
    ok = make_ctx([_line(StatementType.TAX_RETURN, 2024, LineCode.REVENUE, "100000")])
    assert run("DQ3", ok) == []


def test_dq4_deposits_far_exceed_revenue():
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.BANK_STATEMENT, 2024, LineCode.BANK_DEPOSITS, "1800000"),  # 180%
    ])
    flags = run("DQ4", ctx)
    assert len(flags) == 1 and flags[0].severity == Severity.INFO
    # Normal coverage stays silent.
    assert run("DQ4", make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
        _line(StatementType.BANK_STATEMENT, 2024, LineCode.BANK_DEPOSITS, "980000"),
    ])) == []


# --- fail-soft: a broken evaluator can't sink the whole run -----------------


def test_strict_false_skips_a_broken_rule(monkeypatch):
    import app.rules.evaluators as ev

    def boom(rule, ctx, th):
        raise ValueError("simulated bad data")

    # Break one rule's evaluator and confirm the run still returns other flags.
    monkeypatch.setitem(ev.EVALUATORS, "customer_concentration", boom)
    ctx = make_ctx([
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000"),
    ])
    flags, errors = run_rules_verbose(ctx, strict=False)
    assert any(e.rule_id == "A1" for e in errors)  # the broken one was recorded
    assert isinstance(flags, list)  # and the report still came back


def test_strict_true_raises_on_broken_rule(monkeypatch):
    import pytest

    import app.rules.evaluators as ev

    def boom(rule, ctx, th):
        raise ValueError("simulated bad data")

    monkeypatch.setitem(ev.EVALUATORS, "customer_concentration", boom)
    ctx = make_ctx([_line(StatementType.PNL, 2024, LineCode.REVENUE, "1000000")])
    with pytest.raises(Exception):
        run_rules(ctx, strict=True)


# --- contradictory duplicate lines are summed, not silently dropped ---------


def test_duplicate_contradictory_lines_are_combined():
    lines = [
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "600000"),
        _line(StatementType.PNL, 2024, LineCode.REVENUE, "400000"),
    ]
    r = reconcile(lines)
    assert r.triangle_for(2024).pnl_revenue == Decimal("1000000.00")

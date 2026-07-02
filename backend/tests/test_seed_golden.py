"""Golden test for the seeded demo deal (build-prompt requirement §9).

Asserts the synthetic HVAC data room fires EXACTLY the six planted red flags
(and the one INFO benchmark), with no CRITICAL false positives, and that every
reported flag is backed by at least one page citation. If any evaluator drifts,
this test breaks — which is the point.
"""

from app.engine.evidence import assert_grounded, build_evidence_bundle
from app.rules.engine import run_rules, severity_counts
from app.seeder.hvac_demo import (
    EXPECTED_CRITICAL,
    EXPECTED_INFO,
    EXPECTED_RED_FLAGS,
    build_demo_context,
)


def _flags():
    return run_rules(build_demo_context())


def test_exactly_the_planted_red_flags_fire():
    flags = _flags()
    red = {f.rule_id for f in flags if f.severity.value != "INFO"}
    assert red == EXPECTED_RED_FLAGS, f"unexpected red-flag set: {sorted(red)}"


def test_no_critical_false_positives():
    flags = _flags()
    criticals = {f.rule_id for f in flags if f.severity.value == "CRITICAL"}
    assert criticals == EXPECTED_CRITICAL, f"critical set drifted: {sorted(criticals)}"


def test_info_benchmark_present():
    flags = _flags()
    info = {f.rule_id for f in flags if f.severity.value == "INFO"}
    assert info == EXPECTED_INFO


def test_severity_counts():
    counts = severity_counts(_flags())
    assert counts == {"CRITICAL": 4, "HIGH": 2, "MEDIUM": 0, "INFO": 1}


def test_every_flag_has_evidence():
    for f in _flags():
        # G39 is a benchmark comparison with no single source page; every other
        # flag must cite at least one document page.
        if f.rule_id == "G39":
            continue
        assert f.evidence_refs, f"{f.rule_id} has no evidence_refs"
        for ref in f.evidence_refs:
            assert ref["document_id"] and ref["page"] >= 1


def test_tt2_fires_once_for_the_2024_gap_only():
    tt2 = [f for f in _flags() if f.rule_id == "TT2"]
    assert len(tt2) == 1
    assert tt2[0].computed_values["year"] == 2024
    assert tt2[0].computed_values["coverage"] == "78.0"


def test_evidence_bundle_is_serializable_and_grounded_sample():
    ctx = build_demo_context()
    flags = run_rules(ctx)
    bundle = build_evidence_bundle(ctx, flags)
    # A narration that only cites numbers from the bundle must pass the guard.
    prose = (
        "In 2024, bank deposits of 1879800 covered only 78.0% of reported "
        "revenue of 2410000. The Metro Regional Hospital relationship is 42.0% "
        "of revenue."
    )
    assert assert_grounded(prose, bundle) == []

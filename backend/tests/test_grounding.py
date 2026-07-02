"""Tests for the narration grounding guard (SPEC §2.3, §8).

The guard is the mechanical enforcement of "the LLM may not introduce numbers
not in the evidence." These tests pin the two directions that matter: real
ungrounded numbers are caught, and legitimate prose (grounded figures, years,
small counts) is not falsely flagged.
"""

from app.engine.evidence import assert_grounded


BUNDLE = {
    "reconciliation": {
        "triangle": [
            {"period": 2024, "pnl_revenue": "2410000", "bank_deposits": "1879800",
             "deposit_coverage_pct": "78.0"}
        ]
    },
    "flags": [{"computed_values": {"share": "42.0", "amount": "160000"}}],
}


def test_grounded_prose_passes():
    prose = "Deposits of 1879800 were 78.0% of the 2410000 reported in 2024."
    assert assert_grounded(prose, BUNDLE) == []


def test_currency_and_comma_formatting_is_normalized():
    prose = "Deposits of $1,879,800 covered 78.0% of $2,410,000."
    assert assert_grounded(prose, BUNDLE) == []


def test_ungrounded_number_is_caught():
    prose = "We estimate the business is worth $4,200,000."
    violations = assert_grounded(prose, BUNDLE)
    assert any("4,200,000" in v or "4200000" in v for v in violations)


def test_hallucinated_percentage_is_caught():
    prose = "Margins are a healthy 63.5%."
    violations = assert_grounded(prose, BUNDLE)
    assert violations  # 63.5 is not in the bundle


def test_years_and_small_counts_are_allowed():
    prose = "Across 3 documents spanning 2022 to 2024 we found 2 critical issues."
    assert assert_grounded(prose, BUNDLE) == []

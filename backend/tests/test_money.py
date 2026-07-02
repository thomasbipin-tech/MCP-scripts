from decimal import Decimal

import pytest

from app.engine.money import divergence_pct, money, pct, ratio, total


def test_money_rejects_float():
    with pytest.raises(TypeError):
        money(1.23)


def test_money_from_str_and_int():
    assert money("1234.5") == Decimal("1234.50")
    assert money(1000) == Decimal("1000.00")


def test_money_half_up_rounding():
    assert money("0.005") == Decimal("0.01")
    assert money("0.004") == Decimal("0.00")


def test_pct_basic_and_zero_denominator():
    assert pct(Decimal("50"), Decimal("200")) == Decimal("25.0")
    assert pct(Decimal("1"), Decimal("0")) is None


def test_pct_one_decimal_place():
    assert pct(Decimal("1"), Decimal("3")) == Decimal("33.3")


def test_divergence_sign():
    # tax below p&l -> negative divergence
    assert divergence_pct(Decimal("98"), Decimal("100")) == Decimal("-2.0")
    assert divergence_pct(Decimal("110"), Decimal("100")) == Decimal("10.0")
    assert divergence_pct(Decimal("1"), Decimal("0")) is None


def test_ratio_multiple():
    assert ratio(Decimal("1560000"), Decimal("520000")) == Decimal("3.00")
    assert ratio(Decimal("1"), Decimal("0")) is None


def test_total_sums_as_money():
    assert total(["10.01", "20.02", 30]) == Decimal("60.03")

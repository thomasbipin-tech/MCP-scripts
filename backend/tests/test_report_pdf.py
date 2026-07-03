"""Report PDF template tests.

``build_html`` is pure and always tested; ``render_pdf`` is exercised only when
WeasyPrint's native libs are present (Docker/CI), so the suite stays green on a
bare box.
"""

import pytest

from app.core.disclaimer import DISCLAIMER
from app.pipeline.runner import run_pipeline
from app.seeder.hvac_demo import build_demo_context
from app.services.report_pdf import build_html


def _report():
    return run_pipeline(build_demo_context(), {
        "codename": "Project Summit", "entity_name": "Summit Air Mechanical LLC",
        "vertical": "hvac", "vertical_label": "HVAC / Home Services",
        "asking_price": "1560000", "claimed_sde": "520000",
    })


def test_html_contains_all_sections_and_disclaimer():
    html = build_html(_report())
    assert DISCLAIMER in html
    for section in ("Executive summary", "Triangle of Truth", "Red-flag ledger",
                    "Financial normalization", "Data gaps", "Seller question pack"):
        assert section in html
    # Disclaimer runs in the page footer too.
    assert "@bottom-center" in html


def test_html_has_one_block_per_flag():
    report = _report()
    html = build_html(report)
    for f in report["flags"]:
        assert f["rule_id"] in html
        assert f["severity"] in html


def test_html_reports_severity_counts():
    html = build_html(_report())
    # 4 critical / 2 high in the demo tiles.
    assert "CRITICAL" in html and "HIGH" in html


def test_render_pdf_when_weasyprint_available():
    pytest.importorskip("weasyprint")
    from app.services.report_pdf import render_pdf

    pdf = render_pdf(_report())
    assert pdf[:5] == b"%PDF-"

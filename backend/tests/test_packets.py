"""Expert hand-off packets (CPA / attorney / lender)."""

from app.pipeline.runner import run_pipeline
from app.seeder.export import _demo_contract_clauses, deal_meta
from app.seeder.hvac_demo import build_demo_context


def _report():
    ctx = build_demo_context()
    ctx.facts.contract_clauses = _demo_contract_clauses()
    return run_pipeline(ctx, deal_meta())


def test_all_three_packets_present_and_non_empty():
    packets = _report()["expert_packets"]
    assert set(packets) == {"qofe", "attorney", "lender"}
    for p in packets.values():
        assert p["title"] and p["purpose"] and p["audience"]
        assert p["sections"], f"{p['key']} has no sections"
        for s in p["sections"]:
            assert s["heading"] and s["items"]


def test_qofe_packet_carries_reconciliation_and_normalization():
    qofe = _report()["expert_packets"]["qofe"]
    headings = {s["heading"] for s in qofe["sections"]}
    assert any("reconciliation" in h.lower() for h in headings)
    assert any("normalization" in h.lower() for h in headings)
    # reconciliation section references a fiscal year from the triangle
    recon = next(s for s in qofe["sections"] if "reconciliation" in s["heading"].lower())
    assert any("FY2024" in i for i in recon["items"])


def test_attorney_packet_requires_metro_consent_before_close():
    attorney = _report()["expert_packets"]["attorney"]
    all_items = [i for s in attorney["sections"] for i in s["items"]]
    assert any("Metro Regional Hospital" in i and "consent" in i.lower() for i in all_items)
    # and asks the seller the corresponding question
    assert any("Metro Regional Hospital" in q for q in attorney["questions"])


def test_lender_packet_reports_snapshot_and_severity_summary():
    lender = _report()["expert_packets"]["lender"]
    all_items = [i for s in lender["sections"] for i in s["items"]]
    assert any("Asking price" in i for i in all_items)
    assert any("critical" in i.lower() and "high" in i.lower() for i in all_items)


def test_contract_review_present_in_report():
    review = _report()["contract_review"]
    assert review["documents_reviewed"] >= 2
    assert review["severity_summary"]["CRITICAL"] >= 2

"""Diligence workstreams: the full-engagement coverage map."""

from app.pipeline.workstreams import build_workstreams
from app.rules.engine import run_rules
from app.seeder.hvac_demo import build_demo_context


def _workstreams():
    ctx = build_demo_context()
    flags = [f.as_dict() for f in run_rules(ctx)]
    return {w["key"]: w for w in build_workstreams(flags, ctx)}


def test_all_diligence_areas_present():
    ws = _workstreams()
    assert set(ws) == {
        "financial", "tax", "legal", "insurance", "people", "customers",
        "commercial", "competitor", "background", "structuring",
        # software-target modules, honestly scoped as roadmap
        "code_audit", "product_metrics",
    }


def test_every_workstream_has_a_checklist_and_coverage():
    for w in _workstreams().values():
        assert w["checklist"], f"{w['key']} has no checklist"
        assert w["coverage"] in ("automated", "partial", "guided", "roadmap")
        assert w["coverage_label"]


def test_software_target_modules_are_roadmap_and_carry_no_findings():
    ws = _workstreams()
    for key in ("code_audit", "product_metrics"):
        assert ws[key]["coverage"] == "roadmap"
        assert ws[key]["finding_count"] == 0
        # honest scoping note that we do not fake code/metric analysis
        assert "roadmap" in ws[key]["note"].lower()


def test_automated_workstreams_carry_the_demo_findings():
    ws = _workstreams()
    # The demo's flags land under financial (A1/TT2/B9), legal (D24/D25), structuring (G39).
    assert ws["financial"]["finding_count"] >= 2
    assert {f["rule_id"] for f in ws["legal"]["findings"]} >= {"D24", "D25"}
    assert {f["rule_id"] for f in ws["structuring"]["findings"]} >= {"G39"}


def test_guided_workstreams_have_no_findings_but_guide_the_buyer():
    ws = _workstreams()
    for key in ("commercial", "competitor", "background"):
        assert ws[key]["finding_count"] == 0
        assert ws[key]["coverage"] == "guided"
        assert len(ws[key]["checklist"]) >= 3


def test_customer_workstream_generates_interview_targets():
    ws = _workstreams()
    targets = ws["customers"]["interview_targets"]
    assert any(t["name"] == "Metro Regional Hospital" for t in targets)
    metro = next(t for t in targets if t["name"] == "Metro Regional Hospital")
    assert metro["share_pct"] == "42.0"
    assert len(metro["script"]) >= 3

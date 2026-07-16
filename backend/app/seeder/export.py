"""Run the full pipeline on the demo deal and emit artifacts.

Produces:
  * ``frontend/public/demo_report.json`` — the report payload the web UI renders,
  * ``frontend/public/demo-docs/<doc_id>.pdf`` — real source PDFs for the viewer,
  * ``backend/app/seeder/out/demo_report.json`` — a copy the API serves.

Runs offline (template narrator) unless ANTHROPIC_API_KEY is set. Invoked by
``make seed-demo`` and by the golden export test.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..pipeline.runner import run_pipeline
from ..services.pdfgen import write_text_pdf
from .documents import build_documents
from .hvac_demo import ASKING_PRICE, CLAIMED_SDE, CODENAME, ENTITY, build_demo_context

REPO_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_PUBLIC = REPO_ROOT / "frontend" / "public"
BACKEND_OUT = Path(__file__).resolve().parent / "out"


def deal_meta() -> dict:
    return {
        "codename": CODENAME,
        "entity_name": ENTITY,
        "vertical": "hvac",
        "vertical_label": "HVAC / Home Services",
        "state": "OH",
        "deal_type": "asset",
        "asking_price": ASKING_PRICE,
        "claimed_sde": CLAIMED_SDE,
        "stage": "Report Ready",
        "tier": "Full Diligence Report",
    }


def generate_pdfs(target_dir: Path) -> list:
    target_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for doc in build_documents():
        filename = f"{doc['id']}.pdf"
        pages = [[doc["title"], ""] + page for page in doc["pages"]]
        write_text_pdf(target_dir / filename, pages)
        index.append(
            {
                "id": doc["id"],
                "title": doc["title"],
                "doc_type": doc["doc_type"],
                "period": doc["period"],
                "page_count": len(doc["pages"]),
                "confidence": 0.96,  # synthetic docs classify cleanly
                "filename": filename,
                "url": f"/demo-docs/{filename}",
            }
        )
    return index


def _demo_contract_clauses() -> list:
    """Run the clause scanner over the demo data room so the sample report
    showcases the contract review (the demo context is hand-built, not ingested)."""
    from ..pipeline.clauses import scan_document_clauses

    findings = []
    for doc in build_documents():
        pages = ["\n".join(page) for page in doc["pages"]]
        findings.extend(scan_document_clauses(doc["doc_type"], pages, doc["id"], doc["title"]))
    return findings


def main() -> dict:
    ctx = build_demo_context()
    ctx.facts.contract_clauses = _demo_contract_clauses()
    report = run_pipeline(ctx, deal_meta())

    docs_dir = FRONTEND_PUBLIC / "demo-docs"
    report["documents"] = generate_pdfs(docs_dir)
    from ..pipeline.report import build_verification

    report["verification"] = build_verification(report["documents"])

    for path in (FRONTEND_PUBLIC / "demo_report.json", BACKEND_OUT / "demo_report.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        f"seed-demo: {report['severity_counts']} across {len(report['flags'])} flags; "
        f"{len(report['documents'])} source PDFs; completeness {report['completeness_score']}%"
    )
    return report


if __name__ == "__main__":
    main()

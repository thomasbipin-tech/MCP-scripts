"""Every citation must resolve to a real document page.

This is the mechanical guarantee behind "every reported number is
click-traceable to a source page" (build-prompt definition of done). If any
PageRef points at a document/page the seeded data room doesn't contain, the
evidence drawer would dead-link — this test forbids that.
"""

from app.seeder.documents import DOCUMENT_INDEX
from app.seeder.hvac_demo import build_demo_context


def _collect_page_refs(ctx):
    refs = [ln.source for ln in ctx.lines]
    f = ctx.facts
    for group in (f.customers, f.channels, f.addbacks, f.one_time_items, f.monthly_revenue):
        refs.extend(item.source for item in group)
    refs.extend(c.source for c in f.contracts)
    if f.lease:
        refs.append(f.lease.source)
    if f.bank_signals.source:
        refs.append(f.bank_signals.source)
    if f.real_estate.source:
        refs.append(f.real_estate.source)
    return refs


def test_every_citation_resolves_to_a_real_page():
    ctx = build_demo_context()
    for ref in _collect_page_refs(ctx):
        assert ref.document_id in DOCUMENT_INDEX, f"unknown doc {ref.document_id}"
        doc = DOCUMENT_INDEX[ref.document_id]
        page_count = len(doc["pages"])
        assert 1 <= ref.page <= page_count, (
            f"{ref.document_id} p{ref.page} out of range (has {page_count} pages)"
        )

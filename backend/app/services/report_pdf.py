"""Report PDF generation via WeasyPrint from a print-CSS HTML template.

``build_html`` is pure Python string assembly (no native deps) and is fully
tested; ``render_pdf`` lazily imports WeasyPrint (whose system libs are installed
in the backend Docker image). The disclaimer runs in the page footer on every
page via an ``@page`` rule, satisfying SPEC §8.
"""

from __future__ import annotations

import html
from typing import List

from ..core.disclaimer import DISCLAIMER

_SEV_COLOR = {
    "CRITICAL": "#b42318",
    "HIGH": "#b54708",
    "MEDIUM": "#854a0e",
    "INFO": "#334155",
}


def _e(v) -> str:
    return html.escape(str(v))


def _money(v) -> str:
    try:
        return "${:,.0f}".format(float(v))
    except (TypeError, ValueError):
        return _e(v)


def _css() -> str:
    footer = _e(DISCLAIMER)
    return f"""
    @page {{
      size: letter; margin: 20mm 16mm 24mm 16mm;
      @bottom-center {{
        content: "{footer}";
        font-size: 7pt; color: #64748b; white-space: normal;
      }}
      @bottom-right {{ content: "Page " counter(page) " / " counter(pages); font-size: 7pt; color: #94a3b8; }}
    }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #0f172a; font-size: 10pt; line-height: 1.45; }}
    h1 {{ font-size: 20pt; margin: 0 0 2pt; }}
    h2 {{ font-size: 13pt; margin: 18pt 0 6pt; border-bottom: 1px solid #e2e8f0; padding-bottom: 3pt; }}
    .sub {{ color: #475569; margin: 0 0 12pt; }}
    .num {{ font-family: 'IBM Plex Mono', 'Courier New', monospace; }}
    .tiles {{ display: flex; gap: 8pt; margin: 10pt 0; }}
    .tile {{ flex: 1; border: 1px solid #e2e8f0; border-radius: 4pt; padding: 8pt; text-align: center; }}
    .tile .n {{ font-size: 22pt; font-weight: 700; }}
    .tile .l {{ font-size: 7pt; letter-spacing: .08em; text-transform: uppercase; color: #64748b; }}
    table {{ width: 100%; border-collapse: collapse; margin: 6pt 0; }}
    th, td {{ text-align: left; padding: 4pt 6pt; border-bottom: 1px solid #eef2f6; font-size: 9pt; }}
    th {{ color: #64748b; font-weight: 600; font-size: 7.5pt; text-transform: uppercase; letter-spacing: .05em; }}
    td.r, th.r {{ text-align: right; }}
    .flag {{ border: 1px solid #e2e8f0; border-left-width: 3pt; border-radius: 3pt; padding: 8pt 10pt; margin: 6pt 0; break-inside: avoid; }}
    .chip {{ display: inline-block; font-size: 7pt; font-weight: 700; letter-spacing: .06em; color: #fff; padding: 1pt 5pt; border-radius: 3pt; }}
    .muted {{ color: #64748b; }}
    ul {{ margin: 4pt 0 4pt 16pt; padding: 0; }}
    .watermark {{ color: #b42318; border: 1px solid #b42318; padding: 3pt 8pt; border-radius: 3pt; font-weight: 700; font-size: 8pt; display: inline-block; }}
    .disclaimer {{ margin-top: 16pt; font-size: 7.5pt; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 6pt; }}
    """


def _tiles(counts: dict) -> str:
    cells = ""
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "INFO"):
        cells += (
            f'<div class="tile"><div class="n num" style="color:{_SEV_COLOR[sev]}">'
            f'{counts.get(sev, 0)}</div><div class="l">{sev}</div></div>'
        )
    return f'<div class="tiles">{cells}</div>'


def _triangle(triangle: List[dict]) -> str:
    rows = ""
    for t in triangle:
        cov = t.get("deposit_coverage_pct")
        cov_style = ' style="color:#b42318;font-weight:700"' if cov is not None and float(cov) < 92 else ""
        rows += (
            f"<tr><td class='num'>{_e(t['period'])}</td>"
            f"<td class='r num'>{_money(t.get('tax_revenue'))}</td>"
            f"<td class='r num'>{_money(t.get('pnl_revenue'))}</td>"
            f"<td class='r num'>{_money(t.get('bank_deposits'))}</td>"
            f"<td class='r num'{cov_style}>{_e(cov)}%</td></tr>"
        )
    return (
        "<table><thead><tr><th>Year</th><th class='r'>Tax return</th>"
        "<th class='r'>P&amp;L</th><th class='r'>Bank deposits</th>"
        "<th class='r'>Deposit coverage</th></tr></thead><tbody>"
        f"{rows}</tbody></table>"
    )


def _flags(flags: List[dict]) -> str:
    out = ""
    for f in flags:
        sev = f["severity"]
        color = _SEV_COLOR.get(sev, "#334155")
        questions = "".join(f"<li>{_e(q)}</li>" for q in f.get("ask_seller", []))
        out += (
            f'<div class="flag" style="border-left-color:{color}">'
            f'<div><span class="chip" style="background:{color}">{sev}</span> '
            f'<b>{_e(f["rule_id"])} · {_e(f["category"])}</b></div>'
            f'<div style="margin:4pt 0">{_e(f["detail"])}</div>'
            f'<div class="muted"><b>What resolves this:</b> {_e(f["what_resolves"])}</div>'
            f'<div style="margin-top:4pt"><b>Ask the seller:</b><ul>{questions}</ul></div>'
            f"</div>"
        )
    return out


def _normalization(n: dict) -> str:
    rows = ""
    for r in n.get("rows", []):
        rows += (
            f"<tr><td>{_e(r['description'])}</td>"
            f"<td class='r num'>{_money(r['amount'])}</td>"
            f"<td>{_e(r['verdict'])}</td></tr>"
        )
    return (
        "<table><thead><tr><th>Add-back</th><th class='r'>Amount</th><th>Verdict</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
        f"<p class='muted num'>Claimed SDE {_money(n.get('claimed_sde'))} → "
        f"Adjusted SDE {_money(n.get('adjusted_sde'))}</p>"
    )


def _contract_review(review: dict) -> str:
    if not review or not review.get("clauses_flagged"):
        return ""
    blocks = ""
    for c in review.get("contracts", []):
        items = ""
        for f in c.get("findings", []):
            color = _SEV_COLOR.get(f["severity"], "#334155")
            items += (
                f'<div class="flag" style="border-left-color:{color}">'
                f'<div><span class="chip" style="background:{color}">{_e(f["severity"])}</span> '
                f'<b>{_e(f["label"])}</b></div>'
                f'<div style="margin:3pt 0;font-style:italic">&ldquo;{_e(f["quote"])}&rdquo;</div>'
                f'<div class="muted"><b>Why it matters:</b> {_e(f["risk"])}</div>'
                f'<div class="muted"><b>Do this:</b> {_e(f["buyer_action"])}</div>'
                f'<div class="muted num">Source: {_e(f["source"].get("label"))} · p{_e(f["source"].get("page"))}</div>'
                f"</div>"
            )
        blocks += (
            f'<div style="break-inside:avoid;margin-top:8pt">'
            f'<b>{_e(c["counterparty"])}</b> '
            f'<span class="muted">({_e(c["doc_type"].replace("contract_", "").replace("_", " "))})</span>'
            f"{items}</div>"
        )
    return f'<p class="muted">{_e(review.get("note", ""))}</p>{blocks}'


def _packets(packets: dict) -> str:
    if not packets:
        return ""
    out = ""
    for key in ("qofe", "attorney", "lender"):
        p = packets.get(key)
        if not p:
            continue
        secs = ""
        for s in p.get("sections", []):
            lis = "".join(f"<li>{_e(i)}</li>" for i in s.get("items", []))
            secs += f'<div style="margin-top:4pt"><b>{_e(s["heading"])}</b><ul>{lis}</ul></div>'
        qs = "".join(f"<li class='muted'>{_e(q)}</li>" for q in p.get("questions", []))
        qblock = f'<div style="margin-top:4pt"><b>Questions</b><ul>{qs}</ul></div>' if qs else ""
        out += (
            f'<div class="flag" style="break-inside:avoid">'
            f'<div><b>{_e(p["title"])}</b> — <span class="muted">for {_e(p["audience"])}</span></div>'
            f'<div class="muted" style="margin:3pt 0">{_e(p["purpose"])}</div>'
            f"{secs}{qblock}</div>"
        )
    return out


def build_html(report: dict) -> str:
    deal = report.get("deal", {})
    watermark = report.get("watermark")
    wm = f'<div class="watermark">{_e(watermark)}</div>' if watermark else ""
    summary = "".join(f"<li>{_e(s)}</li>" for s in report.get("executive_summary", []))
    gaps = "".join(f"<li>{_e(g['label'])}</li>" for g in report.get("data_gaps", []))
    contract_html = _contract_review(report.get("contract_review") or {})
    contract_section = (
        f"<h2>Contract clause review</h2>{contract_html}" if contract_html else ""
    )
    packets_html = _packets(report.get("expert_packets") or {})
    packets_section = (
        f"<h2>Expert hand-off packets</h2>{packets_html}" if packets_html else ""
    )
    questions = "".join(
        f"<li class='muted'><b>{_e(q['rule_id'])}:</b> {_e(q['question'])}</li>"
        for q in report.get("seller_question_pack", [])
    )

    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>{_css()}</style></head><body>
<h1>DealProofing Red-Flag Report</h1>
<p class="sub">{_e(deal.get('codename',''))} — {_e(deal.get('entity_name',''))} · {_e(deal.get('vertical_label') or deal.get('vertical',''))} · Asking <span class="num">{_money(deal.get('asking_price'))}</span></p>
{wm}
{_tiles(report.get('severity_counts', {}))}
<h2>Executive summary</h2><ul>{summary}</ul>
<h2>Triangle of Truth — revenue reconciliation</h2>{_triangle(report.get('triangle', []))}
<h2>Red-flag ledger</h2>{_flags(report.get('flags', []))}
<h2>Financial normalization</h2>{_normalization(report.get('normalization', {}))}
{contract_section}
<h2>Data gaps</h2><ul>{gaps or '<li class="muted">None</li>'}</ul>
<h2>Seller question pack</h2><ul>{questions}</ul>
{packets_section}
<div class="disclaimer">{_e(DISCLAIMER)}</div>
</body></html>"""


class PDFUnavailable(RuntimeError):
    pass


def render_pdf(report: dict) -> bytes:
    html_str = build_html(report)
    try:
        from weasyprint import HTML  # lazy; native libs only needed here
    except Exception as e:  # pragma: no cover - depends on system libs
        raise PDFUnavailable(f"WeasyPrint unavailable: {e}") from e
    return HTML(string=html_str).write_pdf()

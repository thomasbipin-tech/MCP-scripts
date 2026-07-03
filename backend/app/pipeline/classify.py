"""Stage 1 — document classification.

Offline heuristic classifier over extracted page text (keyword + year/entity
detection) so the pipeline runs without an API key; when a Claude client is
available it uses the versioned ``classify`` prompt instead. Same output shape
either way.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from ..llm.client import ClaudeClient, LLMUnavailable
from ..llm.loader import load_prompt

# Ordered: earlier, more specific keywords win.
_KEYWORDS = [
    ("form 1120-s", "tax_return_1120S"),
    ("form 1065", "tax_return_1065"),
    ("schedule c", "tax_return_schedule_c"),
    ("profit & loss", "pnl"),
    ("profit and loss", "pnl"),
    ("balance sheet", "balance_sheet"),
    ("deposits and credits", "bank_statement"),
    ("bank statement", "bank_statement"),
    ("a/r aging", "ar_aging"),
    ("accounts receivable aging", "ar_aging"),
    ("add-back schedule", "addbacks"),
    ("commercial lease", "lease"),
    ("lease agreement", "lease"),
    ("distributor agreement", "contract_supplier"),
    ("master services agreement", "contract_customer"),
    ("facilities agreement", "contract_customer"),
    ("agreement", "contract_customer"),
]

_YEAR = re.compile(r"\b(19|20)\d{2}\b")
_ENTITY = re.compile(r"Entity:\s*(.+)")


@dataclass
class Classification:
    doc_type: str
    confidence: float
    period: Optional[int]
    entity_name: Optional[str]


def _detect_period(text: str) -> Optional[int]:
    years = [int(m.group(0)) for m in _YEAR.finditer(text)]
    return max(years) if years else None


def _detect_entity(text: str) -> Optional[str]:
    m = _ENTITY.search(text)
    if m:
        return m.group(1).strip()
    # Fallback: an "... LLC/Inc/Corp" token on the first couple of lines.
    for line in text.splitlines()[:3]:
        m2 = re.search(r"[A-Z][\w &]+ (?:LLC|Inc\.?|Corp\.?|Co\.?)", line)
        if m2:
            return m2.group(0).strip()
    return None


def classify_offline(pages: List[str], filename: str = "") -> Classification:
    text = "\n".join(pages)
    hay = (filename + "\n" + text).lower()
    doc_type, confidence = "other", 0.3
    for needle, dt in _KEYWORDS:
        if needle in hay:
            doc_type, confidence = dt, 0.9
            break
    return Classification(
        doc_type=doc_type,
        confidence=confidence,
        period=_detect_period(text),
        entity_name=_detect_entity(text),
    )


def classify(pages: List[str], filename: str = "", client: Optional[ClaudeClient] = None) -> Classification:
    client = client or ClaudeClient()
    if not client.available:
        return classify_offline(pages, filename)
    try:
        prompt = load_prompt("classify", 1)
        user = f"FILENAME: {filename}\n\nDOCUMENT TEXT (first pages):\n" + "\n\n".join(pages[:4])
        res = client.complete_json(
            model=prompt.model, system=prompt.text, user=user,
            prompt_id=prompt.prompt_id, prompt_version=prompt.version, max_tokens=400,
        )
        d = res.data
        period = None
        for key in ("period_end", "period_start"):
            if d.get(key):
                y = _YEAR.search(str(d[key]))
                if y:
                    period = int(y.group(0))
                    break
        return Classification(
            doc_type=d.get("doc_type", "other"),
            confidence=float(d.get("confidence", 0.0)),
            period=period,
            entity_name=d.get("entity_name"),
        )
    except LLMUnavailable:
        return classify_offline(pages, filename)

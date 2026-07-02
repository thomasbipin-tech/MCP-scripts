"""Stage 5 — grounded narration.

Two backends, one contract:
  * ``ClaudeNarrator`` calls the model with the versioned narrate prompt, then
    runs ``assert_grounded`` and retries once if the model smuggled in a number
    not present in the evidence bundle. If it still fails, it falls back to the
    template narrator rather than shipping an ungrounded report.
  * ``template_narrative`` is a deterministic, grounded-by-construction narrator
    used when no API key is configured (so ``make seed-demo`` runs offline) and
    as the safety fallback.

Either way, the returned narrative only contains numbers that are in the bundle.
"""

from __future__ import annotations

from typing import Optional

from ..engine.evidence import assert_grounded
from ..llm.client import ClaudeClient, LLMUnavailable
from ..llm.loader import load_prompt


def _flag_by_id(bundle: dict):
    return {f["rule_id"]: f for f in bundle["flags"]}


def template_narrative(bundle: dict) -> dict:
    """Deterministic narrator. Uses ONLY figures already in the bundle."""
    flags = bundle["flags"]
    counts = bundle["severity_counts"]

    summary = []
    summary.append(
        f"Automated analysis identified {counts['CRITICAL']} critical, "
        f"{counts['HIGH']} high, {counts['MEDIUM']} medium and {counts['INFO']} "
        f"informational findings for further review."
    )
    for f in flags:
        if f["severity"] in ("CRITICAL", "HIGH"):
            summary.append(f["detail"])
        if len(summary) >= 5:
            break

    narratives = []
    for f in flags:
        narratives.append(
            {
                "rule_id": f["rule_id"],
                "finding": f["detail"],
                "why_it_matters": f["buyer_action"],
            }
        )

    return {
        "executive_summary": summary[:5],
        "flag_narratives": narratives,
        "data_gaps_intro": (
            "The following items were not provided or could not be verified from "
            "the documents supplied. Each is an area for further review."
        ),
        "closing_note": (
            "These findings identify areas for further professional review and do "
            "not constitute accounting, legal, tax, or valuation advice."
        ),
    }


class Narrator:
    def __init__(self, client: Optional[ClaudeClient] = None):
        self.client = client or ClaudeClient()

    def narrate(self, bundle: dict) -> dict:
        if not self.client.available:
            return template_narrative(bundle)
        try:
            return self._narrate_llm(bundle)
        except LLMUnavailable:
            return template_narrative(bundle)

    def _narrate_llm(self, bundle: dict) -> dict:
        import json

        prompt = load_prompt("narrate", 1)
        user = "EVIDENCE BUNDLE:\n" + json.dumps(bundle, indent=2)

        def validate(data: dict) -> None:
            for key in ("executive_summary", "flag_narratives"):
                if key not in data:
                    raise ValueError(f"missing {key}")
            prose = json.dumps(data)
            violations = assert_grounded(prose, bundle)
            if violations:
                raise ValueError(f"ungrounded numbers: {violations}")

        result = self.client.complete_json(
            model=prompt.model,
            system=prompt.text,
            user=user,
            prompt_id=prompt.prompt_id,
            prompt_version=prompt.version,
            max_tokens=2500,
            validate=validate,
        )
        return result.data

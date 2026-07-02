"""Anthropic client wrapper: cost logging, retry, JSON-schema validation.

Design goals (build prompt "Engineering standards"):
  * every call records tokens / cost / latency / prompt version,
  * one automatic retry with backoff,
  * JSON outputs are validated and re-requested on invalid,
  * the pipeline still runs with NO API key (offline template mode) so
    ``make seed-demo`` works on a clean clone without network.

Pricing is approximate and configurable; it feeds the per-deal COGS display in
the admin console (SPEC §5), not billing.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

# Approximate USD per million tokens. Update as pricing changes.
PRICING: Dict[str, Dict[str, float]] = {
    "claude-opus-4-8": {"in": 5.0, "out": 25.0},
    "claude-sonnet-5": {"in": 3.0, "out": 15.0},
    "claude-haiku-4-5-20251001": {"in": 0.8, "out": 4.0},
}


@dataclass
class LLMUsage:
    prompt_id: str
    prompt_version: int
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: float
    attempts: int = 1


@dataclass
class LLMResult:
    data: dict
    usage: LLMUsage
    raw_text: str


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICING.get(model, {"in": 0.0, "out": 0.0})
    return round(
        input_tokens / 1_000_000 * p["in"] + output_tokens / 1_000_000 * p["out"], 6
    )


class LLMUnavailable(RuntimeError):
    pass


class ClaudeClient:
    """Thin wrapper over the Anthropic SDK. Lazily imported so the engine's test
    suite never needs the dependency."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._sdk = None

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _client(self):
        if self._sdk is None:
            try:
                import anthropic  # type: ignore
            except ImportError as e:  # pragma: no cover
                raise LLMUnavailable("anthropic SDK not installed") from e
            if not self.api_key:
                raise LLMUnavailable("ANTHROPIC_API_KEY not set")
            self._sdk = anthropic.Anthropic(api_key=self.api_key)
        return self._sdk

    def complete_json(
        self,
        *,
        model: str,
        system: str,
        user: str,
        prompt_id: str,
        prompt_version: int,
        max_tokens: int = 2000,
        validate: Optional[Callable[[dict], None]] = None,
        max_attempts: int = 2,
    ) -> LLMResult:
        """Call Claude and parse a JSON object from the response, retrying once
        on transport error or invalid JSON/schema."""
        last_err: Optional[Exception] = None
        for attempt in range(1, max_attempts + 1):
            started = time.monotonic()
            try:
                resp = self._client().messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                text = "".join(
                    b.text for b in resp.content if getattr(b, "type", "") == "text"
                )
                data = _extract_json(text)
                if validate:
                    validate(data)
                latency = int((time.monotonic() - started) * 1000)
                usage = LLMUsage(
                    prompt_id=prompt_id,
                    prompt_version=prompt_version,
                    model=model,
                    input_tokens=resp.usage.input_tokens,
                    output_tokens=resp.usage.output_tokens,
                    latency_ms=latency,
                    cost_usd=estimate_cost(
                        model, resp.usage.input_tokens, resp.usage.output_tokens
                    ),
                    attempts=attempt,
                )
                return LLMResult(data=data, usage=usage, raw_text=text)
            except Exception as e:  # noqa: BLE001 - retry any failure once
                last_err = e
                if attempt < max_attempts:
                    time.sleep(2 ** attempt)
        raise LLMUnavailable(f"LLM call failed after {max_attempts} attempts: {last_err}")


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in response")
    return json.loads(text[start : end + 1])

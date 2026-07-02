"""Versioned prompt loading. Prompts live as files, never inline (build prompt).

Each prompt file starts with an HTML comment header:
    <!-- prompt_id: narrate  version: 1  model: claude-opus-4-8 -->
so the exact prompt text + version is recorded against every LLM call for
auditability and back-testing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PROMPT_DIR = Path(__file__).parent / "prompts"
_HEADER = re.compile(
    r"<!--\s*prompt_id:\s*(?P<id>\S+)\s+version:\s*(?P<ver>\d+)\s+model:\s*(?P<model>\S+)\s*-->"
)


@dataclass(frozen=True)
class Prompt:
    prompt_id: str
    version: int
    model: str
    text: str


def load_prompt(prompt_id: str, version: int) -> Prompt:
    path = PROMPT_DIR / f"{prompt_id}_v{version}.md"
    text = path.read_text(encoding="utf-8")
    m = _HEADER.search(text)
    if not m:
        raise ValueError(f"{path} is missing a prompt header comment")
    return Prompt(
        prompt_id=m.group("id"),
        version=int(m.group("ver")),
        model=m.group("model"),
        text=text,
    )

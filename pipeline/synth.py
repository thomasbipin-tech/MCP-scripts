"""
synth.py — Turn a list of text chunks into per-chunk WAV files, with
checkpointing so a 500-page job can be interrupted and resumed.

Design for capacity:
  * Each chunk is rendered to work/chunk_00001.wav and never re-rendered if
    it already exists  -> safe to Ctrl-C and restart, or crash and resume.
  * A manifest.json tracks progress so the UI/CLI can report % complete.
  * Failed chunks are retried; persistent failures are logged and skipped
    (a single bad sentence never kills a 20-hour render).
"""
from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass

import numpy as np
import soundfile as sf


@dataclass
class Progress:
    total: int
    done: int
    failed: int
    elapsed_s: float

    @property
    def pct(self) -> float:
        return 100.0 * self.done / self.total if self.total else 0.0


def _chunk_path(work_dir: str, i: int) -> str:
    return os.path.join(work_dir, f"chunk_{i:05d}.wav")


def synthesize(
    chunks: list[str],
    engine,
    work_dir: str,
    retries: int = 2,
    progress_cb=None,
) -> list[str]:
    """Render every chunk to a WAV, resuming from whatever already exists.
    Returns the ordered list of chunk WAV paths that were produced."""
    os.makedirs(work_dir, exist_ok=True)
    manifest_path = os.path.join(work_dir, "manifest.json")
    paths: list[str] = []
    failed = 0
    start = time.time()

    # Persist the source chunks so a resumed run uses identical text.
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(chunks), "chunks": chunks}, f, ensure_ascii=False)

    for i, text in enumerate(chunks, start=1):
        out = _chunk_path(work_dir, i)
        if os.path.exists(out):  # resume: already rendered
            paths.append(out)
            _report(progress_cb, len(chunks), i, failed, start)
            continue

        audio = None
        for attempt in range(retries + 1):
            try:
                audio = engine.synth(text)
                break
            except Exception as e:  # noqa: BLE001 - keep the render alive
                if attempt == retries:
                    print(f"[warn] chunk {i} failed after {retries+1} tries: {e}")
                    failed += 1
                else:
                    time.sleep(1.5 * (attempt + 1))

        if audio is not None and len(audio) > 0:
            sf.write(out, audio, engine.sample_rate)
            paths.append(out)
        _report(progress_cb, len(chunks), i, failed, start)

    return paths


def _report(cb, total, done, failed, start):
    if cb:
        cb(Progress(total=total, done=done, failed=failed, elapsed_s=time.time() - start))

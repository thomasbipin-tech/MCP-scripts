"""
assemble.py — Stitch per-chunk WAVs into a single chaptered .m4b audiobook.

Memory-safe: a 500-page book is many hours of audio, far too large to hold
in RAM. We never load the audio into Python. Instead we:
  1. read only per-file *durations* (soundfile metadata, cheap),
  2. insert short silences between sentences and longer ones between chapters
     using a reusable silence file,
  3. let ffmpeg concat + encode to AAC in a streaming pass,
  4. write chapter markers with an FFMETADATA file.
"""
from __future__ import annotations
import os
import subprocess

import numpy as np
import soundfile as sf


def _dur(path: str) -> float:
    info = sf.info(path)
    return info.frames / info.samplerate


def _make_silence(path: str, seconds: float, sr: int):
    sf.write(path, np.zeros(int(sr * seconds), dtype=np.float32), sr)


def assemble(
    chunk_paths: list[str],
    out_path: str,
    title: str = "Audiobook",
    author: str = "Personal Audiobook",
    gap_s: float = 0.45,
    chapter_gap_s: float = 1.2,
    chapter_minutes: float = 20.0,
    bitrate: str = "64k",
) -> str:
    """Produce a chaptered .m4b at out_path. Returns out_path."""
    if not chunk_paths:
        raise ValueError("No audio chunks to assemble.")

    work = os.path.dirname(out_path) or "."
    os.makedirs(work, exist_ok=True)
    sr = sf.info(chunk_paths[0]).samplerate

    sil = os.path.join(work, "_sil_short.wav")
    sil_long = os.path.join(work, "_sil_long.wav")
    _make_silence(sil, gap_s, sr)
    _make_silence(sil_long, chapter_gap_s, sr)

    # Build the concat list + compute chapter boundaries analytically.
    list_path = os.path.join(work, "_concat.txt")
    chapters: list[tuple[float, float, str]] = []  # (start_s, end_s, title)
    t = 0.0
    chap_start = 0.0
    chap_idx = 1
    lines: list[str] = []

    for i, cp in enumerate(chunk_paths):
        lines.append(f"file '{os.path.abspath(cp)}'")
        t += _dur(cp)
        last = i == len(chunk_paths) - 1
        # Close a chapter once it passes the target length (or at the end).
        if (t - chap_start) >= chapter_minutes * 60 or last:
            chapters.append((chap_start, t, f"Chapter {chap_idx}"))
            chap_idx += 1
            chap_start = t + (chapter_gap_s if not last else 0.0)
            lines.append(f"file '{os.path.abspath(sil_long)}'")
            t += chapter_gap_s if not last else 0.0
        else:
            lines.append(f"file '{os.path.abspath(sil)}'")
            t += gap_s

    with open(list_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Pass 1: concat -> AAC .m4a (streaming, low memory)
    tmp_m4a = os.path.join(work, "_joined.m4a")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
         "-c:a", "aac", "-b:a", bitrate, tmp_m4a],
        check=True, capture_output=True,
    )

    # Pass 2: attach chapter metadata -> .m4b
    meta_path = os.path.join(work, "_chapters.txt")
    _write_ffmetadata(meta_path, chapters, title, author)
    subprocess.run(
        ["ffmpeg", "-y", "-i", tmp_m4a, "-i", meta_path,
         "-map_metadata", "1", "-c", "copy", out_path],
        check=True, capture_output=True,
    )

    for p in (sil, sil_long, list_path, tmp_m4a, meta_path):
        try:
            os.remove(p)
        except OSError:
            pass
    return out_path


def _write_ffmetadata(path, chapters, title, author):
    lines = [";FFMETADATA1", f"title={title}", f"artist={author}", f"album={title}", ""]
    for start_s, end_s, name in chapters:
        lines += [
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            f"START={int(start_s * 1000)}",
            f"END={int(end_s * 1000)}",
            f"title={name}",
            "",
        ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

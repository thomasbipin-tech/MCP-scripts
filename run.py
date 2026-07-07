#!/usr/bin/env python3
"""
run.py — Headless CLI. Best for the full 500-page render on a server
(no browser needed, resumable). Example:

    # Voice A: Indic Parler male narrator (no reference needed)
    python run.py mybook.pdf --voice parler --title "എന്റെ പുസ്തകം"

    # Voice B / Own voice: IndicF5 cloning a reference clip
    python run.py mybook.pdf --voice indicf5 \
        --ref reference/native_male.wav \
        --ref-text "റഫറൻസ് ക്ലിപ്പിന്റെ കൃത്യമായ മലയാള ട്രാൻസ്ക്രിപ്റ്റ്"

Interrupt any time (Ctrl-C) and re-run the same command to resume.
"""
from __future__ import annotations
import argparse
import os
import sys
import time

from pipeline import extract, normalize, chunk, build_engine, synthesize, assemble


def main():
    ap = argparse.ArgumentParser(description="Malayalam PDF -> chaptered audiobook")
    ap.add_argument("pdf", help="Path to the Malayalam PDF")
    ap.add_argument("--voice", default="parler",
                    choices=["parler", "indicf5", "gtts", "stub"],
                    help="parler=male narrator (default), indicf5=clone a reference/your voice")
    ap.add_argument("--ref", help="Reference WAV (5-10s) for indicf5")
    ap.add_argument("--ref-text", help="Exact Malayalam transcript of --ref")
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default="Personal Audiobook")
    ap.add_argument("--out", default=None, help="Output .m4b path")
    ap.add_argument("--work", default=None, help="Work dir for resumable chunks")
    ap.add_argument("--ocr", default="auto", choices=["auto", "always", "never"])
    ap.add_argument("--max-chars", type=int, default=350)
    ap.add_argument("--chapter-minutes", type=float, default=20.0)
    args = ap.parse_args()

    base = os.path.splitext(os.path.basename(args.pdf))[0]
    out = args.out or f"output/{base}.m4b"
    work = args.work or f"output/{base}_chunks"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    print(f"[1/4] Extracting text (ocr={args.ocr}) ...")
    book = extract(args.pdf, ocr=args.ocr)
    title = args.title or book.title
    print(f"      {len(book.pages)} pages, {len(book.full_text):,} chars, "
          f"{book.ocr_page_count} OCR'd")

    print("[2/4] Normalizing + chunking ...")
    chunks = chunk(normalize(book.full_text), max_chars=args.max_chars)
    print(f"      {len(chunks):,} chunks")

    print(f"[3/4] Synthesizing with '{args.voice}' (resumable) ...")
    kwargs = {}
    if args.voice == "indicf5":
        if not args.ref or not args.ref_text:
            sys.exit("indicf5 needs --ref and --ref-text")
        kwargs = {"ref_audio_path": args.ref, "ref_text": args.ref_text}
    engine = build_engine(args.voice, **kwargs)

    t0 = time.time()

    def report(p):
        if p.done % 10 == 0 or p.done == p.total:
            rate = p.done / max(1e-9, p.elapsed_s)
            eta = (p.total - p.done) / max(1e-9, rate)
            sys.stdout.write(
                f"\r      {p.done}/{p.total} ({p.pct:4.1f}%) "
                f"failed={p.failed} eta={eta/60:5.1f} min")
            sys.stdout.flush()

    paths = synthesize(chunks, engine, work, progress_cb=report)
    print(f"\n      rendered {len(paths)} chunks in {(time.time()-t0)/60:.1f} min")

    print("[4/4] Assembling chaptered .m4b ...")
    assemble(paths, out, title=title, author=args.author,
             chapter_minutes=args.chapter_minutes)
    print(f"\nDone -> {out}")


if __name__ == "__main__":
    main()

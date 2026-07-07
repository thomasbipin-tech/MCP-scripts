#!/usr/bin/env python3
"""
make_sample.py — Render a short spoken sample of a fixed Malayalam passage
so you can compare voices before committing to the full book.

    python samples/make_sample.py --voice parler
    python samples/make_sample.py --voice indicf5 --ref reference/native_male.wav \
        --ref-text "…"
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import build_engine, synthesize, assemble, chunk

SAMPLE_TEXT = (
    "കേരളം ദൈവത്തിന്റെ സ്വന്തം നാടാണ്. "
    "പുഴകളും കായലുകളും ഈ നാടിന്റെ സൗന്ദര്യം വർദ്ധിപ്പിക്കുന്നു. "
    "മലയാളഭാഷ ഈ നാടിന്റെ ആത്മാവാണ്."
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="parler",
                    choices=["parler", "indicf5", "gtts", "stub"])
    ap.add_argument("--ref"); ap.add_argument("--ref-text")
    ap.add_argument("--out", default="output/sample.m4b")
    a = ap.parse_args()

    kwargs = {}
    if a.voice == "indicf5":
        kwargs = {"ref_audio_path": a.ref, "ref_text": a.ref_text}
    engine = build_engine(a.voice, **kwargs)

    os.makedirs("output/_sample_chunks", exist_ok=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    paths = synthesize(chunk(SAMPLE_TEXT, 200), engine, "output/_sample_chunks")
    assemble(paths, a.out, title="Voice Sample", chapter_minutes=999)
    print("Sample ->", a.out)

if __name__ == "__main__":
    main()

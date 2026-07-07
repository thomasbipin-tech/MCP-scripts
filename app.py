#!/usr/bin/env python3
"""
app.py — Local web UI. Run it and open the link it prints
(http://127.0.0.1:7860). This is the "link to execute".

    python app.py

Features:
  * Drop your Malayalam PDF.
  * Choose a voice (two Malayalam male options) BEFORE generating.
  * Generate a short SAMPLE first to pick the voice you like.
  * Or supply YOUR OWN voice (a short recording) to narrate the book.
  * Then render the full, chaptered .m4b audiobook (resumable).
"""
from __future__ import annotations
import os
import tempfile

import gradio as gr

from pipeline import (extract, normalize, chunk, build_engine, synthesize,
                      assemble, MALE_NARRATOR_DESC)

OUT_DIR = os.path.abspath("output")
os.makedirs(OUT_DIR, exist_ok=True)

VOICE_INFO = {
    "A — Male Narrator (Indic Parler-TTS)":
        "Clean, consistent male storytelling voice. No recording needed. "
        "Best all-round default for a 500-page book.",
    "B — Authentic Native Male (IndicF5 clone)":
        "Clones a bundled native-male reference clip for maximum authenticity. "
        "Provide reference/native_male.wav + its transcript.",
    "Own Voice (IndicF5 clone of YOUR recording)":
        "Narrate the book in your own voice. Upload a clear 5-10s clip of "
        "yourself reading Malayalam, plus the exact transcript of that clip.",
}


def _engine_from_choice(choice, ref_audio, ref_text):
    if choice.startswith("A"):
        return build_engine("parler", description=MALE_NARRATOR_DESC)
    # B and Own both use IndicF5 with a reference clip.
    if not ref_audio or not ref_text:
        raise gr.Error("This voice needs a reference WAV and its exact transcript.")
    return build_engine("indicf5", ref_audio_path=ref_audio, ref_text=ref_text.strip())


def make_sample(pdf, choice, ref_audio, ref_text):
    if not pdf:
        raise gr.Error("Upload a PDF first.")
    book = extract(pdf, ocr="auto")
    chunks = chunk(normalize(book.full_text), max_chars=200)
    if not chunks:
        raise gr.Error("No readable Malayalam text found in the PDF.")
    sample_chunks = chunks[:3]  # first few sentences
    engine = _engine_from_choice(choice, ref_audio, ref_text)
    work = tempfile.mkdtemp(prefix="sample_")
    paths = synthesize(sample_chunks, engine, work)
    out = os.path.join(OUT_DIR, "sample.m4b")
    assemble(paths, out, title="Sample", chapter_minutes=999)
    return out, f"Sample from {len(sample_chunks)} sentences using: {choice}"


def make_full(pdf, choice, ref_audio, ref_text, title, chapter_min, progress=gr.Progress()):
    if not pdf:
        raise gr.Error("Upload a PDF first.")
    progress(0.02, desc="Extracting text…")
    book = extract(pdf, ocr="auto")
    progress(0.08, desc="Normalizing + chunking…")
    chunks = chunk(normalize(book.full_text))
    if not chunks:
        raise gr.Error("No readable Malayalam text found.")

    engine = _engine_from_choice(choice, ref_audio, ref_text)
    base = os.path.splitext(os.path.basename(pdf))[0]
    work = os.path.join(OUT_DIR, f"{base}_chunks")

    def cb(p):
        progress(0.08 + 0.85 * p.done / p.total,
                 desc=f"Synthesizing {p.done}/{p.total} (failed {p.failed})")

    paths = synthesize(chunks, engine, work, progress_cb=cb)
    progress(0.95, desc="Assembling chaptered audiobook…")
    out = os.path.join(OUT_DIR, f"{base}.m4b")
    assemble(paths, out, title=(title or book.title), chapter_minutes=chapter_min)
    return out, f"Done: {len(paths)} segments → {os.path.basename(out)}"


with gr.Blocks(title="Personal Audiobook (Malayalam)") as demo:
    gr.Markdown("# 📖🔊 Personal Audiobook — Malayalam\n"
                "PDF → authentic Malayalam audiobook. Free, local, resumable.")
    pdf = gr.File(label="Malayalam PDF", file_types=[".pdf"], type="filepath")

    choice = gr.Radio(list(VOICE_INFO.keys()),
                      value=list(VOICE_INFO.keys())[0],
                      label="Voice (choose before generating)")
    info = gr.Markdown(VOICE_INFO[list(VOICE_INFO.keys())[0]])
    choice.change(lambda c: VOICE_INFO[c], choice, info)

    with gr.Group():
        gr.Markdown("**Reference clip** (needed for Voice B and Own Voice)")
        ref_audio = gr.Audio(label="Reference WAV (5-10s)", type="filepath")
        ref_text = gr.Textbox(label="Exact Malayalam transcript of the clip",
                              lines=2)

    with gr.Row():
        sample_btn = gr.Button("▶ Generate sample", variant="secondary")
        full_btn = gr.Button("🎧 Generate full audiobook", variant="primary")

    with gr.Accordion("Full-render options", open=False):
        title = gr.Textbox(label="Audiobook title (optional)")
        chapter_min = gr.Slider(5, 40, value=20, step=1,
                                label="Minutes per chapter")

    status = gr.Markdown()
    audio_out = gr.File(label="Output (.m4b)")

    sample_btn.click(make_sample, [pdf, choice, ref_audio, ref_text],
                     [audio_out, status])
    full_btn.click(make_full,
                   [pdf, choice, ref_audio, ref_text, title, chapter_min],
                   [audio_out, status])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, show_error=True)

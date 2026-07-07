# 📖🔊 Personal Audiobook — Malayalam

Turn a Malayalam PDF (even a 500-page one) into an authentic, chaptered
audiobook. **100% free**, runs locally, resumable. No paid APIs, no paid content.

---

## The honest version first (read this)

- **Authenticity comes from the model, not tricks.** This uses **AI4Bharat**
  models built by native-language researchers — the best free Malayalam TTS
  available today. Two are wired in (details below).
- **A 500-page book is 15-30+ hours of audio.** On a **CPU** neural TTS is
  painfully slow (potentially days). On a **GPU** it's practical. If you don't
  have a local GPU, render on a **free** Colab/Kaggle GPU — the same code runs
  there. See "Capacity & speed".
- **"Your own voice" reading Malayalam** works because `IndicF5` clones a voice
  *within Malayalam* (not a cross-lingual hack). Quality depends on your
  reference recording. You may only clone a voice you have the right to use
  (your own is fine).
- Everything is **resumable**. Interrupt a 20-hour render and re-run; it picks
  up where it left off.

---

## Hear the voices right now (zero setup)

Before installing anything, try the official demos in your browser:

- **Voice A — Indic Parler-TTS:** https://huggingface.co/spaces/ai4bharat/indic-parler-tts
- **Voice B — IndicF5 (cloning):** https://huggingface.co/spaces/ai4bharat/IndicF5

Pick Malayalam, type a sentence, and listen. That tells you which voice you want
before committing to the full book.

---

## The two Malayalam voices (choose before generating)

| | **Voice A — Male Narrator** | **Voice B / Own Voice — Clone** |
|---|---|---|
| Model | `ai4bharat/indic-parler-tts` | `ai4bharat/IndicF5` |
| How it picks a voice | A **text description** ("a calm middle-aged male…") | A **5-10s reference clip** it imitates |
| Reference needed? | No | Yes (a native-male clip, or **your own voice**) |
| Best for | A clean, consistent narrator with no setup | Maximum authenticity, or *your* voice |
| Malayalam "Narration" emotion | ✅ officially supported | via the reference clip's tone |
| License | Apache-2.0 (free) | Free (AI4Bharat) |

**Own voice** is just Voice B pointed at a recording of *you*: upload a clear
5-10 second clip of yourself reading Malayalam plus the exact transcript, and
the whole book is narrated in your voice.

An always-available **fallback** (`gtts`) exists for emergencies — a single
female-ish, non-audiobook-grade voice that needs internet. Use only if the
neural models are unavailable.

---

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Voice A also needs the Parler library:
pip install git+https://github.com/huggingface/parler-tts.git
# Scanned PDFs only (OCR):
sudo apt-get install -y tesseract-ocr tesseract-ocr-mal ffmpeg
```

`ffmpeg` is required (for assembling the `.m4b`). First run downloads the
model from Hugging Face (a few GB), then it's cached.

---

## Use it

### Option 1 — Web UI (the link to execute)

```bash
python app.py
```

Open the link it prints: **http://127.0.0.1:7860**

Then: drop your PDF → pick a voice → **Generate sample** (hear a few sentences)
→ **Generate full audiobook**. A progress bar tracks the long render; the
finished `.m4b` appears for download.

### Option 2 — Headless CLI (best for the full 500-page run on a server)

```bash
# Voice A — male narrator, nothing else needed
python run.py mybook.pdf --voice parler --title "എന്റെ പുസ്തകം"

# Voice B / your own voice — clone a reference clip
python run.py mybook.pdf --voice indicf5 \
    --ref reference/native_male.wav \
    --ref-text "റഫറൻസ് ക്ലിപ്പിന്റെ കൃത്യമായ ട്രാൻസ്ക്രിപ്റ്റ്"
```

Ctrl-C any time and re-run the same command to resume. Output lands in
`output/<book>.m4b`.

### Quick voice sample only

```bash
python samples/make_sample.py --voice parler
# -> output/sample.m4b
```

---

## Capacity & speed (the 500-page reality)

- Text is split into short chunks and rendered one at a time; each finished
  chunk is saved, so memory stays flat no matter how long the book is.
- Assembly never loads the audio into RAM — `ffmpeg` streams the concat, so
  20+ hours of audio assembles fine on a laptop.
- **Speed is the real constraint.** Rough guide per hour of *output* audio:
  CPU ≈ many hours; a modern GPU ≈ minutes-to-tens-of-minutes.
- **No local GPU?** Run the exact same code on a **free** GPU:
  - Google Colab (free T4) or Kaggle (free GPU, ~30h/week).
  - Upload the folder + your PDF, `pip install -r requirements.txt`, run
    `run.py`, download the `.m4b`. Still $0.

---

## How it works

```
PDF ──extract──► raw text ──normalize──► clean text ──chunk──► sentences
      (PyMuPDF,        (NFC, strip page      (≤350 chars,
       OCR fallback)    numbers, de-wrap)     sentence-safe)
                                                   │
                                          synth (resumable, per-chunk WAV)
                                                   │  Indic Parler / IndicF5
                                                   ▼
                                     assemble ──► chaptered .m4b (ffmpeg)
```

Files: `pipeline/extract.py`, `textnorm.py`, `engines.py`, `synth.py`,
`assemble.py`; `run.py` (CLI), `app.py` (UI), `config.yaml` (voice presets).

---

## Testing

```bash
pip install pymupdf soundfile numpy pyyaml pytesseract pillow
python scripts/selftest.py
```

Builds a throwaway Malayalam PDF (using the bundled `test_ml.ttf` — Noto Sans
Malayalam, SIL OFL-1.1), runs the full extract → normalize → chunk → synth →
assemble pipeline with the silent `stub` engine (no GPU/model download
needed), and checks the resume logic and chapter markers. No network or
neural-TTS deps required.

---

## Limitations / honest notes

- **Scanned books:** Malayalam OCR (Tesseract `mal`) is decent but not perfect
  on complex ligatures. A clean text-layer PDF gives the best result. The
  pipeline auto-detects scanned pages and OCRs only those.
- **Own-voice quality** is only as good as your reference clip — record clean,
  quiet, 5-10s, natural pace.
- **Pronunciation** of rare proper nouns/English loanwords can wobble; the
  chunker keeps punctuation to help prosody.
- This is a personal-use tool. Respect the source book's copyright.

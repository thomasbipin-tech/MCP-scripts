# Reference clips (for Voice B and Own Voice)

`IndicF5` clones the voice in a short reference clip. Put your clip here.

## Requirements
- **Format:** WAV, mono, 5-10 seconds, clean and quiet (no music/echo).
- **Content:** the speaker reading natural Malayalam.
- **Transcript:** you must provide the *exact* Malayalam text spoken in the
  clip (passed as `--ref-text` or in the UI). Accuracy matters — the model
  aligns audio to this text.

## Voice B — a native male reference
Record ~8 seconds of a native Malayalam male speaker (a family member is ideal),
save as `native_male.wav`, and note the transcript. This gives the most
authentic "audiobook narrator" result.

## Own Voice
Record yourself reading a Malayalam sentence or two, clean and unhurried, and
the entire book will be narrated in your voice.

## Ethics
Only clone a voice you have permission to use. Your own voice, or a consenting
family member's, is fine. Do not clone someone without consent.

## Tip
Make the clip with anything (phone voice memo), then convert to WAV:

```bash
ffmpeg -i memo.m4a -ac 1 -ar 24000 native_male.wav
```

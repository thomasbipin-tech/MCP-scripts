"""
textnorm.py — Clean extracted Malayalam text and split it into
TTS-sized chunks.

Neural TTS models degrade on very long inputs, so we split on sentence
boundaries and cap chunk length. We also strip page-number-only lines and
join lines that were wrapped mid-paragraph, which keeps prosody natural.
"""
from __future__ import annotations
import re
import unicodedata

# Sentence-ending punctuation seen in Malayalam books: Latin . ? ! plus the
# Devanagari-style danda । and double danda ॥ that some typesetters use.
_SENT_END = re.compile(r"([.?!।॥])")
# Lines that are just a number (page numbers) or roman-ish page markers.
_PAGE_NUM_LINE = re.compile(r"^\s*[\divxlcIVXLC]+\s*$")
_MULTISPACE = re.compile(r"[ \t]+")
_MULTINEWLINE = re.compile(r"\n{3,}")


def normalize(raw: str) -> str:
    """NFC-normalize (important for Malayalam ligatures), drop page-number
    lines, collapse whitespace, and join wrapped lines within paragraphs."""
    text = unicodedata.normalize("NFC", raw)

    kept: list[str] = []
    for line in text.split("\n"):
        if _PAGE_NUM_LINE.match(line):
            continue
        kept.append(line.rstrip())
    text = "\n".join(kept)

    # Collapse a single hard-wrapped newline inside a paragraph into a space,
    # but preserve paragraph breaks (blank lines).
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = _MULTISPACE.sub(" ", text)
    text = _MULTINEWLINE.sub("\n\n", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    """Split into sentences, keeping the terminal punctuation attached."""
    parts = _SENT_END.split(text)
    sentences: list[str] = []
    buf = ""
    for piece in parts:
        if _SENT_END.fullmatch(piece):
            buf += piece
            sentences.append(buf.strip())
            buf = ""
        else:
            buf += piece
    if buf.strip():
        sentences.append(buf.strip())
    return [s for s in sentences if s]


def chunk(text: str, max_chars: int = 350) -> list[str]:
    """Group sentences into chunks up to max_chars. Long sentences are split
    on commas/whitespace as a fallback so nothing exceeds the model limit."""
    chunks: list[str] = []
    current = ""
    for sent in split_sentences(text):
        if len(sent) > max_chars:
            # Flush current, then hard-split the oversized sentence.
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_hard_split(sent, max_chars))
            continue
        if len(current) + len(sent) + 1 <= max_chars:
            current = f"{current} {sent}".strip()
        else:
            if current:
                chunks.append(current.strip())
            current = sent
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _hard_split(sent: str, max_chars: int) -> list[str]:
    out, cur = [], ""
    for token in re.split(r"(\s+|,|;)", sent):
        if len(cur) + len(token) <= max_chars:
            cur += token
        else:
            if cur.strip():
                out.append(cur.strip())
            cur = token
    if cur.strip():
        out.append(cur.strip())
    return out

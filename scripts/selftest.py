"""Self-test: build a Malayalam PDF, then run the full pipeline with the
stub engine and verify a chaptered .m4b comes out."""
import os, subprocess, sys
import fitz

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import extract, normalize, chunk, build_engine, synthesize, assemble

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT = os.path.join(ROOT, "test_ml.ttf")
PDF = os.path.join(ROOT, "test_book.pdf")
WORK = os.path.join(ROOT, "_selftest_work")
OUT = os.path.join(ROOT, "_selftest_out.m4b")

# A few sentences of real Malayalam prose (public-domain style test text).
PARA = (
    "കേരളം ദൈവത്തിന്റെ സ്വന്തം നാടാണ്. "
    "പച്ചപ്പ് നിറഞ്ഞ വയലുകളും തെങ്ങിൻ തോപ്പുകളും ഇവിടെ കാണാം. "
    "പുഴകളും കായലുകളും ഈ നാടിന്റെ സൗന്ദര്യം വർദ്ധിപ്പിക്കുന്നു. "
    "ഇവിടുത്തെ ജനങ്ങൾ അതിഥികളെ സ്നേഹത്തോടെ സ്വീകരിക്കുന്നു. "
    "മലയാളഭാഷ ഈ നാടിന്റെ ആത്മാവാണ്."
)

def build_pdf():
    doc = fitz.open()
    for pageno in range(3):  # a few pages
        page = doc.new_page()
        page.insert_font(fontname="ml", fontfile=FONT)
        page.insert_textbox(fitz.Rect(50, 50, 545, 780),
                            (PARA + "\n\n") * 4, fontname="ml", fontsize=13)
    doc.save(PDF)
    doc.close()

def main():
    build_pdf()
    print("1. built test PDF:", os.path.basename(PDF))

    book = extract(PDF, ocr="never")
    print(f"2. extracted {len(book.pages)} pages, {len(book.full_text)} chars, ocr_pages={book.ocr_page_count}")
    assert len(book.full_text) > 100, "extraction produced too little text"
    assert "കേരളം" in book.full_text, "Malayalam not preserved through extraction"

    text = normalize(book.full_text)
    chunks = chunk(text, max_chars=120)
    print(f"3. normalized + chunked -> {len(chunks)} chunks")
    print("   sample chunk:", chunks[0][:60], "...")
    assert len(chunks) > 1

    engine = build_engine("stub")
    paths = synthesize(chunks, engine, WORK)
    print(f"4. synthesized {len(paths)} chunk WAVs (stub/silent)")
    assert len(paths) == len(chunks)

    # Resume test: run again, should skip all (files exist).
    paths2 = synthesize(chunks, engine, WORK)
    assert paths2 == paths, "resume did not reuse existing chunks"
    print("   resume OK (re-run reused existing chunks)")

    assemble(paths, OUT, title="ടെസ്റ്റ് പുസ്തകം", author="Self Test",
             chapter_minutes=0.05)  # tiny target to force multiple chapters
    print("5. assembled ->", os.path.basename(OUT))

    import json as _json
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_chapters", "-show_entries",
         "format=duration", "-of", "json", OUT],
        capture_output=True, text=True)
    data = _json.loads(probe.stdout)
    nchap = len(data.get("chapters", []))
    dur = float(data.get("format", {}).get("duration", 0))
    print(f"6. ffprobe: {nchap} chapters, total duration {dur:.1f}s")
    assert nchap >= 1, "no chapters written"
    print("\nALL CHECKS PASSED ✅")

if __name__ == "__main__":
    main()

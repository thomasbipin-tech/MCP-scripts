#!/usr/bin/env python3
"""Build the VO track and derive the video timeline from it.

Engine: Kokoro-82M (ONNX). Pronunciation is pinned at the phoneme level, not by\nrespelling the text -- see PHON below.

Pronunciation is handled by ONE table (PRONOUNCE) applied automatically to the
scripted line, so there is no second copy of the text to drift out of sync. Every
entry was verified against espeak-ng's phonemiser; `python3 vo.py audit` reprints
the IPA so a regression is visible rather than merely audible.

The picture cuts to the audio: each scene's duration is max(visual floor, what its
narration actually needs). Emits vo.wav + timeline.json.

Usage:
  python3 vo.py                # synthesise + time
  python3 vo.py skip           # re-time existing vo/*.wav (e.g. human takes)
  python3 vo.py audit          # print the pronunciation table's phonemes
  python3 vo.py voices         # render a voice A/B comparison clip
"""
import json, os, re, subprocess, sys, wave
import numpy as np

SR = 24000                       # Kokoro's native rate
VOICE = os.environ.get('VO_VOICE', 'am_onyx')
SPEED = float(os.environ.get('VO_SPEED', '1.0'))   # <1 = a more measured read
MODEL = 'kokoro/kokoro-v1.0.onnx'
VOICES = 'kokoro/voices-v1.0.bin'
os.makedirs('vo', exist_ok=True)

# ---------------------------------------------------------------- pronunciation
# Phoneme-level overrides, not respellings. Orthographic hacks ("C. L. I") force
# PRIMARY stress onto every letter and add a prosodic break at each period, which is
# what made acronyms read as staccato. Spoken acronyms take secondary stress on every
# letter but the last, and primary on the last: B-G-P is bˌiːdʒˌiːˈpiː, not bˈiː dʒˈiː pˈiː.
#
# These are injected straight into the phoneme stream (is_phonemes=True), so espeak's
# context-dependent guessing is bypassed entirely -- it renders CLI as "cly" in
# isolation and as letters mid-sentence, which is not something to build on.
PHON = {
    'VLAN':        'vˈiːlæn',            # native: vlˈæn -- one syllable. Wrong.
    'VLANs':       'vˈiːlænz',           # native: vlˈæn -- plural silently dropped.
    'VXLAN':       'vˌiːˌɛkslˈæn',
    'EVPN':        'ˌiːvˌiːpˌiːˈɛn',     # native: ˈɛvpən ("evpen"). Wrong.
    'CLI':         'sˌiːˌɛlˈaɪ',         # native: klˈaɪ ("cly"). Wrong.
    'AVD':         'ˌeɪvˌiːdˈiː',        # native: ˈævd. Wrong.
    'CVD':         'sˌiːvˌiːdˈiː',       # native already correct; pinned
    'BGP':         'bˌiːdʒˌiːpˈiː',      # native already correct; pinned
    'STP':         'ˌɛstˌiːpˈiː',        # native already correct; pinned
    'IP':          'ˌaɪpˈiː',            # native already correct; pinned
    'PDF':         'pˌiːdˌiːˈɛf',
    'AI':          'ˌeɪˈaɪ',
    'YAML':        'jˈæməl',
    'BOM':         'bˈɪl ʌv mətˈɪɹiəlz',  # native: bˈɑːm ("bahm")
    'Arista':      'əɹˈɪstə',            # native: ˈæɹɪstə ("ARR-ista")
    'Visio':       'vˈɪzioʊ',            # native: vˈɪsɪˌoʊ ("VIS-ee-oh")
    'Netforge.ai': 'nˈɛtfɔːɹdʒ dˌɑːt ˌeɪˈaɪ',
    'Netforge':    'nˈɛtfɔːɹdʒ',
}
# longest first so "VLANs" wins over "VLAN" and "Netforge.ai" over "Netforge"
_TERMS = sorted(PHON, key=len, reverse=True)
_SPLIT = re.compile('(' + '|'.join(re.escape(t) for t in _TERMS) + ')')

_tok = None
def tokenizer():
    global _tok
    if _tok is None:
        from kokoro_onnx.tokenizer import Tokenizer
        _tok = Tokenizer()
    return _tok

def phonemes_for(text):
    """Phonemise the line, splicing in the overrides.

    Text either side of an override is phonemised normally, so ordinary prosody is
    untouched; only the overridden terms are pinned.
    """
    out = []
    for part in _SPLIT.split(text):
        if not part:
            continue
        if part in PHON:
            out.append(PHON[part])
        else:
            ph = tokenizer().phonemize(part).strip()
            if ph:
                out.append(ph)
    joined = ' '.join(out)
    joined = re.sub(r'\s+([.,;:!?])', r'\1', joined)     # punctuation hugs the phoneme
    return re.sub(r'\s{2,}', ' ', joined).strip()

# ---------------------------------------------------------------- script
# (id, scene, text, caption)  — caption None = let the visuals carry it
LINES = [
 ('01', 1, "Every network change starts as a drawing.",
        "Every network change starts as a drawing."),
 ('02', 1, "And every outage starts with the gap between that drawing, and what's actually on the box.",
        "And every outage starts with the gap between that drawing —<br>and <em>what's actually on the box</em>."),
 ('03', 2, "So you design it in Visio. You build it by hand, box by box, in CLI.",
        "You design it in Visio. You build it by hand, in CLI."),
 ('04', 2, "And somewhere between the two, a VLAN gets transposed. A BGP neighbour never comes up.",
        "Somewhere between the two, a VLAN gets transposed.<br>A BGP neighbour never comes up."),
 ('05', 2, "You find out at two in the morning, inside a maintenance window, with a rollback plan and no time left to use it.",
        "You find out at 2am — inside a maintenance window,<br>with no time left to use the rollback plan."),
 ('06', 3, "The drawing wasn't wrong. It was just never connected to anything.",
        "The drawing was never wrong.<br>It was just never <em>connected to anything</em>."),
 ('07', 3, "Every diagram tool on the market gives you a picture of the network. Then it hands you a keyboard, and wishes you luck.",
        "Every diagram tool gives you a picture of the network.<br>Then it hands you a keyboard and wishes you luck."),
 ('08', 4, "So what if the drawing was the source of truth?",
        "So what if the drawing <em>was</em> the source of truth?"),
 ('09', 4, "Not a picture of the network. The network itself.",
        "Not a picture of the network. The network itself."),
 ('10', 5, "This is Netforge.ai. Drag a device onto the canvas.",
        "Drag a device onto the canvas."),
 ('11', 6, "Connect the ports. Set your VLANs, your routing, your management.",
        "Connect the ports. Set your VLANs, your routing, your management."),
 ('12', 7, "Scale the same canvas, to a full Arista leaf-spine VXLAN EVPN fabric.",
        "Scale the same canvas to a full <em>leaf-spine VXLAN EVPN fabric</em>."),
 ('13', 7, "Cisco. Arista. Aruba. Palo Alto. Silver Peak. One canvas.",
        "Cisco. Arista. Aruba. Palo Alto. Silver Peak. <em>One canvas.</em>"),
 ('14', 8, "And before anything ships, it gets checked.",
        "Before anything ships — it gets checked."),
 ('15', 9, "IP conflicts. VLAN mismatches. BGP peer gaps. Spanning-tree errors.",
        "IP conflicts. VLAN mismatches. BGP peer gaps. Spanning-tree errors."),
 ('16', 9, "Caught here, on the canvas. Not out there, in the maintenance window.",
        "Caught <em>here</em>, on the canvas —<br>not out there, in the maintenance window."),
 ('17',10, "Then the AI Network Architect reviews the whole design. Single points of failure, CVD and AVD alignment. And tells you what to fix.",
        "Then the AI Network Architect reviews the whole design —<br>and tells you what to fix."),
 ('18',11, "Zero conflicts. 42 checks passed.", None),
 ('19',12, "Then the design ships itself. Production-ready CLI. AVD Ansible YAML.",
        "Production-ready CLI. AVD Ansible YAML.<br>Generated from the same canvas."),
 ('20',13, "PDF packages. Visio diagrams. Excel BOM. Cable schedules. Documentation that can't drift from the design.",
        "PDF packages, Visio diagrams, Excel BOM, cable schedules —<br>documentation that <em>can't drift</em> from the design."),
 ('21',14, "Reverse-engineer a live Azure subscription onto that canvas, and push it back as Terraform.",
        "Reverse-engineer a live Azure subscription onto the canvas —<br>and push it back as <em>Terraform</em>."),
 ('22',15, "Design. Configure. Validate. Deploy. One canvas, one source of truth.", None),
 ('23',15, "The drawing and the network. Finally the same thing.", None),
 ('24',16, "Netforge.ai. Open the designer, drag your first device.", None),
 ('25',16, "Free to start. No card.", None),
]

SCENE_MIN = {1:10, 2:12, 3:11, 4:11, 5:6.5, 6:6.5, 7:8, 8:5.5,
             9:8, 10:7, 11:5.5, 12:6.5, 13:7, 14:6.5, 15:8, 16:8}
PACE = {1:(0.7,0.8,1.2), 2:(0.7,0.6,1.0), 3:(1.0,0.7,1.4), 4:(2.0,0.8,3.4),
        5:(0.8,0.5,1.2), 6:(0.8,0.5,1.2), 7:(0.8,0.5,1.2), 8:(0.6,0.5,0.9),
        9:(0.6,0.5,1.1), 10:(0.6,0.5,1.1), 11:(0.5,0.5,1.5), 12:(0.6,0.5,1.0),
        13:(0.6,0.5,1.0), 14:(0.6,0.5,1.0), 15:(0.8,0.6,1.2), 16:(0.8,0.5,2.2)}

def ipa(s):
    return subprocess.run(['espeak-ng','-v','en-us','--ipa','-q',s],
                          capture_output=True, text=True).stdout.strip().replace('\n',' ')

def audit():
    """Compare each override against what the pipeline's own phonemiser would do."""
    t = tokenizer()
    print(f"{'term':13} {'override (shipped)':24} native (what we bypass)")
    for term in _TERMS:
        print(f"  {term:13} {PHON[term]:24} {t.phonemize(term).strip()}")
    print("\nstress check -- one primary, rest secondary, mark before the vowel:")
    for term in ('BGP', 'CLI', 'AVD', 'EVPN', 'IP', 'VXLAN'):
        v = PHON[term]
        pri, sec = v.count('\u02c8'), v.count('\u02cc')
        bad = [c for c in ('\u02c8','\u02cc') if c+'d' in v or c+'p' in v or c+'l' in v]
        print(f"  {term:6} primary={pri} secondary={sec}  "
              f"{'OK' if pri == 1 and not bad else 'CHECK: mark sits before a consonant'}")

def write_wav(path, samples, sr=SR):
    with wave.open(path,'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(samples,-1,1)*32767).astype('<i2').tobytes())

_kok = None
def kokoro():
    global _kok
    if _kok is None:
        from kokoro_onnx import Kokoro
        _kok = Kokoro(MODEL, VOICES)
    return _kok

def synth_line(text, path, voice=VOICE, speed=SPEED):
    a, sr = kokoro().create(phonemes_for(text), voice=voice, speed=speed,
                            lang='en-us', is_phonemes=True)
    a = np.asarray(a, dtype=np.float32)
    p = np.abs(a).max()
    if p > 0: a = a / p * 0.85
    write_wav(path, a, sr)
    return len(a)/sr

def synth_all():
    for lid, _s, text, _c in LINES:
        d = synth_line(text, f'vo/{lid}.wav')
        print(f'  {lid} {d:5.2f}s  {phonemes_for(text)[:70]}')

def voice_demo():
    """Same two lines in several voices, labelled, for picking by ear."""
    cands = ['am_michael','am_onyx','am_eric','am_fenrir','bm_george','bm_lewis']
    sample = ("Before anything ships, it gets checked. IP conflicts, VLAN mismatches, "
              "BGP peer gaps. Then the AI Network Architect reviews the whole design.")
    out = []
    for v in cands:
        lab, sr = kokoro().create(f'Voice option. {v.replace("_"," ")}.', voice=v, speed=1.0, lang='en-us')
        body, _ = kokoro().create(phonemes_for(sample), voice=v, speed=SPEED, lang='en-us', is_phonemes=True)
        out += [np.asarray(lab,dtype=np.float32), np.zeros(int(0.35*SR)),
                np.asarray(body,dtype=np.float32), np.zeros(int(0.9*SR))]
        print(f'  {v}: {len(body)/SR:.2f}s')
    a = np.concatenate(out); a /= max(np.abs(a).max(),1e-6)
    write_wav('voice-options.wav', a*0.9)
    print('-> voice-options.wav')

def read(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32)/32768.0, w.getframerate()

def build():
    durs = {}
    for lid, *_ in LINES:
        a, sr = read(f'vo/{lid}.wav'); durs[lid] = len(a)/sr

    scenes, placed, cursor = [], [], 0.0
    for si in range(1, 17):
        mine = [l for l in LINES if l[1] == si]
        intro, gap, tail = PACE[si]
        t, local = intro, []
        for k, (lid, _s, _tx, cap) in enumerate(mine):
            if k: t += gap
            local.append((lid, t, durs[lid], cap)); t += durs[lid]
        need = t + tail
        d = round(max(SCENE_MIN[si], need), 2); a = round(cursor, 2)
        scenes.append({'i':si,'a':a,'b':round(a+d,2),'d':d,'need':round(need,2),'floor':SCENE_MIN[si]})
        placed += [(lid, round(a+lt,2), ld, cap) for lid, lt, ld, cap in local]
        cursor = a + d
    DUR = round(cursor, 2)

    cues = []
    for n, (lid, st, ld, cap) in enumerate(placed):
        if not cap: continue
        nxt = placed[n+1][1] if n+1 < len(placed) else DUR
        cues.append({'t0': round(st-0.25,2), 't1': round(min(st+ld+1.1, nxt-0.15),2), 'html': cap})

    bed = np.zeros(int((DUR+1)*SR), dtype=np.float32)
    for lid, st, ld, _c in placed:
        a, sr = read(f'vo/{lid}.wav')
        if sr != SR: a = np.interp(np.arange(0,len(a)/sr,1/SR), np.arange(len(a))/sr, a)
        f = int(0.008*SR); a[:f] *= np.linspace(0,1,f); a[-f:] *= np.linspace(1,0,f)
        i = int(st*SR); bed[i:i+len(a)] += a
    bed *= 10**(-3.0/20) / max(np.abs(bed).max(), 1e-6)
    write_wav('vo.wav', bed)

    json.dump({'duration':DUR,'voice':VOICE,'speed':SPEED,
               'scenes':[{'a':s['a'],'b':s['b']} for s in scenes],'cues':cues,
               'vo':[{'id':l,'start':s,'dur':round(d,2)} for l,s,d,_ in placed]},
              open('timeline.json','w'), indent=1)

    print(f"\n{'sc':>3} {'a':>7} {'b':>7} {'dur':>6} {'need':>6} {'floor':>6}  driver")
    for s in scenes:
        print(f"{s['i']:3} {s['a']:7.2f} {s['b']:7.2f} {s['d']:6.2f} {s['need']:6.2f} "
              f"{s['floor']:6.1f}  {'VO' if s['need']>s['floor'] else 'visual floor'}")
    sp = sum(d for _l,_s,d,_c in placed)
    print(f"\nvoice {VOICE} @ speed {SPEED}")
    print(f"runtime {DUR:.2f}s ({int(DUR//60)}:{DUR%60:05.2f})   speech {sp:.1f}s = {sp/DUR*100:.0f}%")

if __name__ == '__main__':
    if 'audit' in sys.argv: audit(); sys.exit()
    if 'voices' in sys.argv: voice_demo(); sys.exit()
    if 'skip' not in sys.argv: synth_all()
    build()

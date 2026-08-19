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
  python3 vo.py coverage       # fail if narration uses an acronym with no entry
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
    # --- compounds first; _TERMS sorts longest-first so these win over their parts ---
    'ArubaOS-CX':  'əɹˈuːbə ˌoʊˈɛs sˌiːˈɛks',
    'HMAC-SHA2-256': 'ˌeɪtʃmˈæk ʃˈɑː tˈuː tˌuːfˈɪfti sˈɪks',
    'HMAC-SHA1':   'ˌeɪtʃmˈæk ʃˈɑː wˈʌn',
    'SD-WAN':      'ˌɛsdˌiːwˈæn',        # native: reads "sd" as a word. Wrong.
    'IOS-XE':      'ˌaɪˌoʊˈɛs ˌɛksˈiː',
    'PAN-OS':      'pˈæn ˌoʊˈɛs',
    'NX-OS':       'ˌɛnˈɛks ˌoʊˈɛs',
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
    'Pulumi':      'pəlˈuːmi',           # native: guesses "POO-loo-my". Wrong.
    # --- transport / topology ---
    'WAN':         'wˈæn',               # native: wˈɑːn -- the English word "wan". Wrong.
    'LAN':         'lˈæn',
    'MPLS':        'ˌɛmpˌiːˌɛlˈɛs',
    'VPN':         'vˌiːpˌiːˈɛn',
    'VRFs':        'vˌiːˌɑːɹˈɛfs',
    'VRF':         'vˌiːˌɑːɹˈɛf',
    'SVIs':        'ˌɛsvˌiːˈaɪz',        # native: "sviss". Wrong.
    'SVI':         'ˌɛsvˌiːˈaɪ',
    'HSRP':        'ˌeɪtʃˌɛsˌɑːɹpˈiː',
    'VRRP':        'vˌiːˌɑːɹˌɑːɹpˈiː',
    'FHRP':        'ˌɛfˌeɪtʃˌɑːɹpˈiː',
    'OSPF':        'ˌoʊˌɛspˌiːˈɛf',
    'MTU':         'ˌɛmtˌiːjˈuː',
    'VTY':         'vˌiːtˌiːwˈaɪ',
    'VTEP':        'vˈiːtɛp',            # said "VEE-tep"; native mangles it
    'ACL':         'ˌeɪsˌiːˈɛl',
    # --- addressing ---
    'IPv6':        'ˌaɪpˌiːvˌiːsˈɪks',
    'IPAM':        'ˈaɪpæm',             # native: "ipp-am". Wrong.
    'CIDR':        'sˈaɪdɚ',             # said "cider"; native spells it out
    'MAC':         'mˈæk',
    'DHCP':        'dˌiːˌeɪtʃsˌiːpˈiː',
    'DNS':         'dˌiːˌɛnˈɛs',
    # --- management plane ---
    'AAA':         'ˌeɪˌeɪˈeɪ',
    'TACACS':      'tˈækæks',            # said "tack-axe"
    'RADIUS':      'ɹˈeɪdiəs',
    'SNMP':        'ˌɛsˌɛnˌɛmpˈiː',
    'NTP':         'ˌɛntˌiːpˈiː',
    'SSH':         'ˌɛsˌɛsˈeɪtʃ',
    'LLDP':        'ˌɛlˌɛldˌiːpˈiː',
    'CDP':         'sˌiːdˌiːpˈiː',
    'OOB':         'ˌoʊˌoʊˈbiː',
    'MD5':         'ˌɛmdˌiːfˈaɪv',
    # --- hardware / optics ---
    'QSFP':        'kjˌuːˌɛsˌɛfpˈiː',
    'SFP':         'ˌɛsˌɛfpˈiː',
    'DAC':         'dˈæk',
    'EOS':         'ˌiːˌoʊˈɛs',
    # --- everything else that is spoken as letters ---
    'SLAs':        'ˌɛsˌɛlˈeɪz',
    'SLA':         'ˌɛsˌɛlˈeɪ',
    'HTML':        'ˌeɪtʃtˌiːˌɛmˈɛl',
    'CSV':         'sˌiːˌɛsvˈiː',
    'UI':          'jˌuːˈaɪ',
    'NIST':        'nˈɪst',
    'AS':          'ˌeɪˈɛs',           # BGP autonomous system: "ay-ESS", not the word "as"
    'CIS':         'sˌiːˌaɪˈɛs',
    'RPKI':        'ˌɑːɹpˌiːkˌeɪˈaɪ',      # ar-pee-kay-EYE
    'NAT':         'nˈæt',
    'SKU':         'skjˈuː',              # said "skew"
    'SMS':         'ˌɛsˌɛmˈɛs',
    'HTTP':        'ˌeɪtʃtˌiːtˌiːpˈiː',
    'TCP':         'tˌiːsˌiːpˈiː',
    'UDP':         'jˌuːdˌiːpˈiː',
    'API':         'ˌeɪpˌiːˈaɪ',
    'RIPE':        'ɹˈaɪp',
    'IOS':        'ˌaɪˌoʊˈɛs',
    'CX':         'sˌiːˈɛks',
    'LC':         'ˌɛlsˈiː',
    'Clos':        'klˈoʊ',              # the fabric, after Charles Clos -- not "kloss"
}
# longest first so "VLANs" wins over "VLAN" and "Netforge.ai" over "Netforge"
_TERMS = sorted(PHON, key=len, reverse=True)
# Bounded on both sides so a short term can never fire inside a longer word -- "IP"
# must not be plucked out of "IPAM", and "MAC" must not fire inside a hostname.
_SPLIT = re.compile('(?<![A-Za-z0-9])(' + '|'.join(re.escape(t) for t in _TERMS) +
                    ')(?![A-Za-z0-9])')

_tok = None
def tokenizer():
    global _tok
    if _tok is None:
        from kokoro_onnx.tokenizer import Tokenizer
        _tok = Tokenizer()
    return _tok

# Masking token. Phonemising the fragments either side of a term *in isolation* loses
# the sentence context, and espeak then gives function words their citation form: "a WAN
# overview" came out as stressed "AY wan". So the terms are masked with an ordinary word
# first, the whole sentence is phonemised in one pass -- the article correctly reduces to
# ɐ -- and the mask is swapped for the pinned phonemes afterwards.
_MASK = 'Kevin'
_MASK_PH = re.compile(r'k[ˈˌ]?ɛv[ˈˌ]?ɪn')

def phonemes_for(text):
    """Phonemise the line, splicing in the overrides.

    Text either side of an override is phonemised normally, so ordinary prosody is
    untouched; only the overridden terms are pinned.
    """
    terms = []
    masked = _SPLIT.sub(lambda m: (terms.append(m.group(1)), _MASK)[1], text)
    if terms:
        parts = _MASK_PH.split(tokenizer().phonemize(masked).strip())
        # If the mask did not survive intact (an unexpected phonemisation), fall through
        # to the older fragment-splicing path rather than emitting a mangled line.
        if len(parts) == len(terms) + 1:
            buf = [parts[0]]
            for term, seg in zip(terms, parts[1:]):
                buf += [PHON[term], seg]
            joined = ''.join(buf)
            joined = re.sub(r'\s+([.,;:!?])', r'\1', joined)
            return re.sub(r'\s{2,}', ' ', joined).strip()

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
 # ---- act 1. The hook is client-supplied copy, read at 1.2x (see SPEED_BY_LINE).
 # Three earlier lines were CUT because the hook already states them, and the video
 # should not say the same thing twice:
 #   "And every outage starts with the gap between that drawing and what's on the box"
 #        -> hook: "almost every outage begins the same way too"
 #   "a VLAN gets transposed. A BGP neighbour never comes up"
 #        -> hook: "One missing neighbor. One forgotten VLAN."
 #   "The drawing wasn't wrong."
 #        -> hook: "not because the design was wrong"
 ('01', 1, "Every enterprise network begins the same way: a clean diagram on a whiteboard.", None),
 ('02', 1, "And almost every outage begins the same way too. Not because the design was wrong, "
           "but because someone had to manually translate that design into thousands of lines "
           "of configuration.", None),
 ('03', 1, "One typo. One missing neighbor. One duplicated IP. One forgotten VLAN.", None),
 ('05', 1, "You find out at two in the morning, with no time left to use the rollback plan.", None),
 # scene 2 frames the mismatch bridge without restating the hook's list
 ('04', 2, "Months later, the drawing and the device disagree.", None),
 ('06', 2, "None of it was ever verified.", None),
 ('08', 3, "So what if the drawing was the source of truth?",
        "So what if the drawing <em>was</em> the source of truth?"),
 ('09', 3, "Not a picture of the network. The network itself.", None),
 # ---- act 2: the product
 ('10', 4, "Introducing Netforge.ai. Drag a device onto the canvas.", None),
 ('11', 5, "Connect the ports. Set your VLANs, your routing, your management.", None),
 ('12', 6, "Scale the same canvas, to a full Arista leaf-spine VXLAN EVPN fabric.", None),
 ('13', 6, "Cisco. Arista. Aruba. Palo Alto. Silver Peak. One canvas.", None),
 ('14', 7, "And before anything ships, it gets checked.", None),
 ('15', 8, "IP conflicts. VLAN mismatches. BGP peer gaps. Spanning-tree errors.", None),
 ('16', 8, "Caught here, on the canvas. Not out there, in the maintenance window.", None),
 ('17', 9, "Then the AI Network Architect reviews the whole design. Single points of failure, "
           "CVD and AVD alignment. And tells you what to fix.", None),
 # scene 10 ("0 conflicts / 42 checks passed") is screen-only -- the badge and the
 # validation panel already say it, so narrating it was reading the screen aloud.
 ('19',11, "Then the design ships itself. Production-ready CLI. AVD Ansible YAML.", None),
 ('20',12, "PDF packages. Visio diagrams. Excel BOM. Cable schedules. Documentation that can't "
           "drift from the design.", None),
 # the Azure section had no lead-in; it now turns into the section instead of cutting to it
 ('21',13, "Or, if you want to visualize an environment that already exists: reverse-engineer a "
           "live Azure subscription onto the canvas, and push it back as Terraform, or Pulumi.", None),
 ('22',14, "Design. Configure. Validate. Deploy. One canvas, one source of truth.", None),
 ('23',14, "The drawing and the network. Finally the same thing.", None),
 ('24',15, "Netforge.ai. Draw the network once. Everything else is generated.", None),
]

# Per-line speed. The hook's prose runs at 1.2x. Two lines are deliberately left at 1.0:
#   '03' -- at 1.1x and above, "VLAN" (vˈiːlæn) compresses and reads as "villain".
#           Verified with ASR at 1.2/1.1/1.0; only 1.0 comes back as VLAN. It is also the
#           hook's closing list, which lands harder deliberate than rushed.
#   '05' -- the 2am line is the section's punchline; 1.2x makes it sound hurried.
SPEED_BY_LINE = {'01': 1.2, '02': 1.2}

SCENE_MIN = {1:16, 2:8, 3:7, 4:6.5, 5:6.5, 6:8, 7:5.5, 8:8,
             9:7, 10:5.5, 11:6.5, 12:7, 13:6.5, 14:8, 15:8}
# scene 1's intro pad is long on purpose: the brand card holds on screen before the hook
# begins speaking, and the picture dissolves into the demo on the hook's first word.
PACE = {1:(2.7,0.45,0.9), 2:(0.8,0.6,1.4), 3:(1.0,0.7,1.1),   # tail no longer holds a title card
        4:(0.8,0.5,1.2), 5:(0.8,0.5,1.2), 6:(0.8,0.5,1.2), 7:(0.6,0.5,0.9),
        8:(0.6,0.5,1.1), 9:(0.6,0.5,1.1), 10:(0.5,0.5,1.5), 11:(0.6,0.5,1.0),
        12:(0.6,0.5,1.0), 13:(0.6,0.5,1.0), 14:(0.8,0.6,1.2), 15:(0.8,0.5,2.2)}
N_SCENES = 15

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

# Words that read as ordinary prose despite the capitals -- they are not acronyms and
# need no phoneme pin. Anything else uncovered is a bug: SD-WAN and WAN shipped
# mispronounced because nothing checked for them.
_NOT_ACRONYMS = {'AND', 'NOT', 'ONE', 'OK', 'CHECK', 'SAME', 'STILL', 'UNDER', 'PRIMARY',
                 'FAILING', 'NO', 'CUT', 'TV'}

def coverage(files=('walkthrough.py', 'series.py', 'shorts.py', 'vo.py')):
    """Fail if a narration line contains an acronym with no entry in PHON."""
    import ast
    missing = {}
    for f in files:
        if not os.path.exists(f):
            continue
        for node in ast.walk(ast.parse(open(f).read())):
            # narration is always (scene_index, "text") -- metadata strings and
            # docstrings are not spoken and must not be flagged
            if not (isinstance(node, ast.Tuple) and len(node.elts) >= 2):
                continue
            head, body = node.elts[0], node.elts[1]
            # (scene, "text") in the series/shorts scripts; ("id", scene, "text", cap)
            # in this file's own LINES
            if (isinstance(head, ast.Constant) and isinstance(head.value, str)
                    and len(node.elts) >= 3):
                head, body = node.elts[1], node.elts[2]
            if not (isinstance(head, ast.Constant) and isinstance(head.value, int)):
                continue
            if not (isinstance(body, ast.Constant) and isinstance(body.value, str)):
                continue
            for w in re.findall(r"[A-Za-z][A-Za-z0-9./\-]*", body.value):
                w = w.rstrip('.')
                if not (re.search(r'[A-Z]{2,}', w) or re.match(r'^[A-Z][a-z]*-[A-Z]', w)):
                    continue
                if w in PHON or w.upper() in _NOT_ACRONYMS:
                    continue
                if all(p in PHON or not p for p in re.split(r'[-/]', w)):
                    continue          # a compound whose every part is already pinned
                missing.setdefault(w, f)
    for w, f in sorted(missing.items()):
        print(f"  MISSING phoneme entry: {w:16} (in {f})")
    print(f"{len(missing)} uncovered term(s)" if missing else "all narration acronyms are pinned")
    return 1 if missing else 0

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
        d = synth_line(text, f'vo/{lid}.wav', speed=SPEED * SPEED_BY_LINE.get(lid, 1.0))
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
    for si in range(1, N_SCENES + 1):
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
    print(f"\nvoice {VOICE} @ speed {SPEED}"
          f"   ({', '.join(f'{k}@{SPEED*v:.2f}' for k, v in SPEED_BY_LINE.items())})")
    print(f"runtime {DUR:.2f}s ({int(DUR//60)}:{DUR%60:05.2f})   speech {sp:.1f}s = {sp/DUR*100:.0f}%")

if __name__ == '__main__':
    if 'audit' in sys.argv: audit(); sys.exit()
    if 'coverage' in sys.argv: sys.exit(coverage())
    if 'voices' in sys.argv: voice_demo(); sys.exit()
    if 'skip' not in sys.argv: synth_all()
    build()

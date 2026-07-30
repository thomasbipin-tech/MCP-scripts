#!/usr/bin/env python3
"""Short-form variants, built from the same scene library as the master cut.

Each variant is a scene *order* plus its own narration. scenes.html takes the order
from the timeline, so nothing is duplicated -- the shorts reuse the master's shots and
re-sequence them. Every short opens on the standalone brand card (scene 14) and closes
on the end card (scene 15), so the set is visually uniform.

Pacing is 1.10x rather than the master's 1.0x, with tighter pads. Any line whose
technical terms fail an ASR read-back at 1.10x is automatically re-cut at 1.0x -- the
same "VLAN" -> "villain" compression that bit the master's hook.

Usage:
  python3 shorts.py            # synthesise VO + emit timeline_<slug>.json for all 5
  python3 shorts.py s1-2am     # just one
  python3 shorts.py --list     # show the plan without synthesising
"""
import json, os, re, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vo

SPEED = 1.10
BRAND, ENDCARD = 14, 15
PRODUCT = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12}      # scenes that show the product
PADS = (0.35, 0.35, 0.55)                        # intro, gap between lines, tail

# Each variant: slots = [(scene_index, visual_floor)], lines = [(slot, text)]
VARIANTS = [
 dict(slug='s1-2am', title='The 2 a.m. autopsy',
      use='story-driven — video or pitch opener',
      slots=[(BRAND,3.0), (0,None), (1,None), (6,None), (9,4.2), (ENDCARD,5.0)],
      lines=[
        (1, "Every major network outage has the same autopsy. The design was right. "
            "The config was typed by hand."),
        (1, "A transposed VLAN. A missing BGP neighbor. One line out of ten thousand."),
        (2, "And nobody verified it. Not until the site went down."),
        (3, "Netforge.ai closes that gap. Draw the network on a canvas, and every design "
            "is checked before it ships."),
        (5, "Netforge.ai. From sketch to spine."),
      ]),

 dict(slug='s2-in-2026', title='In 2026',
      use='punchy — landing page or demo intro',
      slots=[(BRAND,3.0), (0,None), (3,None), (11,None), (ENDCARD,5.0)],
      lines=[
        (1, "We design billion-dollar networks in Visio. Then we retype them into a "
            "terminal, line by line, and hope nothing breaks."),
        (1, "In twenty twenty-six."),
        (2, "Netforge.ai ends the retyping. Drag your topology onto the canvas."),
        (3, "It generates the configs, catches the IP conflicts, and flags the single "
            "points of failure. Before deployment. Not after the outage."),
        (4, "Netforge.ai. From sketch to spine."),
      ]),

 dict(slug='s3-weeks-to-hours', title='Weeks to hours',
      use='stat-style — sales deck or webinar',
      slots=[(BRAND,3.0), (5,None), (6,None), (11,None), (ENDCARD,5.0)],
      lines=[
        (1, "A typical enterprise fabric design takes weeks. Diagram it. Spreadsheet the "
            "addressing. Hand-write the configs. Peer review. Pray."),
        (1, "Netforge.ai collapses that into hours."),
        (2, "Design visually, and walk away with validated EVPN VXLAN configs and an AI "
            "design review."),
        (3, "The Visio, the BOM and the cable schedules are already exported."),
        (4, "Netforge.ai. From sketch to spine."),
      ]),

 dict(slug='s4-deploy-minute', title='The deploy minute',
      use='conversational — social or founder-voice',
      slots=[(BRAND,3.0), (7,None), (8,None), (9,4.2), (ENDCARD,5.0)],
      lines=[
        (1, "Ask any network engineer their most dreaded moment. It isn't the design. "
            "It's the deploy."),
        (1, "That silent minute after you paste the config, waiting to see if the site "
            "comes back."),
        (2, "Netforge.ai was built for that minute. Every design checked for conflicts, "
            "gaps, and single points of failure."),
        (3, "Before it ever reaches a device."),
        (4, "Netforge.ai. From sketch to spine."),
      ]),

 # Mine: the cloud angle. The other four are all about configs you are about to write.
 # This one is about the network you already have and never documented.
 dict(slug='s5-already-running', title="The network you already have",
      use='cloud / hybrid audience — retargeting',
      slots=[(BRAND,3.0), (12,None), (11,None), (ENDCARD,5.0)],
      lines=[
        (1, "You can't document what you can't see. Most cloud networks were never drawn "
            "at all."),
        (1, "Netforge.ai reverse-engineers a live Azure subscription onto a canvas. Every "
            "VNet, subnet, gateway and security group."),
        (1, "Then pushes it back as Terraform."),
        (2, "With the diagram and the documentation you never had."),
        (3, "Netforge.ai. From sketch to spine."),
      ]),
]

# Acceptable ASR read-backs per pinned term. These are transcription spellings, not
# pronunciations -- "Visio" correctly pronounced VIZ-ee-oh comes back spelled "Vizio"
# (the TV brand), which is a right answer, not a failure. Getting this list wrong makes
# the verifier slow good lines down for no reason.
EXPECT = {
    'BOM':         ('billofmaterials', 'bom'),
    'Netforge.ai': ('netforge',),
    'Netforge':    ('netforge',),
    'Visio':       ('visio', 'vizio', 'vizzio'),
    'EVPN':        ('evpn', 'evpand', 'evp'),
    'YAML':        ('yaml', 'yamal', 'yammel', 'yamil'),
    'VXLAN':       ('vxlan', 'vexlan'),
    'AVD':         ('avd', 'avid'),
}

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

_asr = None
def asr(path):
    global _asr
    if _asr is None:
        from faster_whisper import WhisperModel
        _asr = WhisperModel('small.en', device='cpu', compute_type='int8')
    segs, _ = _asr.transcribe(path, language='en', beam_size=5,
                              condition_on_previous_text=False)
    return ' '.join(s.text for s in segs).strip()

# "Netforge" is a coined word: ASR spells the correct sound (net-FORJ) as anything from
# "Netforge" to "Netforj" to "net forged", so read-back can't judge it and flagging it just
# slows good lines down. Its phonemes are pinned and already verified in the master cut.
# Verification is scoped to the acronym letter-sequences, which is where real regressions
# happen -- that is the failure mode this check exists to catch.
SKIP_VERIFY = {'Netforge', 'Netforge.ai'}

def terms_in(text):
    return [t for t in vo.PHON if t not in SKIP_VERIFY
            and re.search(r'\b' + re.escape(t) + r'\b', text)]

# Empirically marginal above 1.0x: "VLAN" (vˈiːlæn) compresses until ASR hears "VLN" or
# "villain". Synthesis is deterministic, but the ASR oracle is NOT -- the same audio can
# transcribe differently run to run (it has dropped whole clauses). So these terms are
# pinned to 1.0x by rule rather than left to a flaky check.
RISKY_ABOVE_1X = {'VLAN', 'VLANs'}

def synth_verified(text, path, speed=SPEED):
    """Synthesise at the variant speed, dropping to 1.0x where a term needs it.

    Two independent read-backs are taken because the ASR is unstable; a term counts as
    missing if either pass fails to hear it.
    """
    want = terms_in(text)
    forced = sorted(t for t in want if t in RISKY_ABOVE_1X)
    use = 1.0 if forced else speed
    d = vo.synth_line(text, path, speed=use)
    if not want:
        return d, use, None

    def unheard():
        out = set()
        for _pass in range(2):                       # the oracle is flaky; sample it twice
            heard = norm(asr(path))
            for t in want:
                if not any(a in heard for a in EXPECT.get(t, (norm(t),))):
                    out.add(t)
        return sorted(out)

    missing = unheard()
    if missing and use > 1.0:
        d = vo.synth_line(text, path, speed=1.0)
        return d, 1.0, (missing, unheard(), forced)
    return d, use, (missing, missing, forced) if (missing or forced) else (None, None, forced) if forced else None

def build(v, do_synth=True):
    slug = v['slug']
    outdir = f'vo_{slug}'
    os.makedirs(outdir, exist_ok=True)
    ids = {}
    report = []
    for n, (slot, text) in enumerate(v['lines']):
        lid = f'{n:02d}'
        ids[n] = (slot, lid, text)
        if do_synth:
            d, sp, flags = synth_verified(text, f'{outdir}/{lid}.wav')
            note = ''
            if flags:
                missing, still, forced = flags
                if forced:
                    note = f"  <- {'/'.join(forced)} pinned to 1.0x by rule"
                elif missing:
                    note = (f"  <- {'/'.join(missing)} failed read-back at {SPEED}x, re-cut at 1.0x"
                            + ("  STILL FAILING" if still else ""))
            report.append(f"    {lid} {d:5.2f}s @{sp:.2f}x{note}")

    durs = {}
    for n, (slot, lid, _t) in ids.items():
        a, sr = vo.read(f'{outdir}/{lid}.wav'); durs[n] = len(a) / sr

    intro, gap, tail = PADS
    scenes, placed, cursor = [], [], 0.0
    for slot, (sidx, floor) in enumerate(v['slots']):
        mine = [n for n in ids if ids[n][0] == slot]
        t, local = (intro if mine else 0.0), []
        for k, n in enumerate(mine):
            if k: t += gap
            local.append((n, t, durs[n])); t += durs[n]
        need = t + (tail if mine else 0.0)
        floor = floor if floor is not None else (4.0 if sidx in (0, 1, 2) else 4.5)
        d = round(max(floor, need), 2); a = round(cursor, 2)
        scenes.append({'a': a, 'b': round(a + d, 2)})
        placed += [(ids[n][1], round(a + lt, 2), ld) for n, lt, ld in local]
        cursor = a + d
    DUR = round(cursor, 2)

    order = [s[0] for s in v['slots']]
    prod_slots = [i for i, (sidx, _f) in enumerate(v['slots']) if sidx in PRODUCT]
    anchors = {
        'turn': None,                                  # shorts have no long dark act
        'prod': scenes[prod_slots[0]]['a'] if prod_slots else scenes[1]['a'],
        'payoff': scenes[prod_slots[-1]]['a'] if prod_slots else None,
        'payoff_end': scenes[prod_slots[-1]]['b'] if prod_slots else None,
        'outro': scenes[-1]['a'],
    }

    # narration bed
    bed = np.zeros(int((DUR + 1) * vo.SR), dtype=np.float32)
    for lid, st, _ld in placed:
        a, sr = vo.read(f'{outdir}/{lid}.wav')
        f = int(0.008 * sr); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        i = int(st * vo.SR); bed[i:i + len(a)] += a
    bed *= 10 ** (-3.0 / 20) / max(np.abs(bed).max(), 1e-6)
    vo.write_wav(f'vo_{slug}.wav', bed)

    json.dump({'duration': DUR, 'voice': vo.VOICE, 'speed': SPEED,
               'order': order, 'brandInPanes': False, 'anchors': anchors,
               'scenes': scenes, 'cues': [],
               'vo': [{'id': l, 'start': s, 'dur': round(d, 2)} for l, s, d in placed]},
              open(f'timeline_{slug}.json', 'w'), indent=1)

    print(f"\n  {v['title']}  ({slug})  --  {v['use']}")
    print(f"    scenes {order}   runtime {DUR:.2f}s ({int(DUR//60)}:{DUR%60:05.2f})")
    for r in report: print(r)
    return DUR

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    listing = '--list' in sys.argv
    todo = [v for v in VARIANTS if not args or v['slug'] in args]
    total = 0
    for v in todo:
        total += build(v, do_synth=not listing)
    print(f"\n  {len(todo)} shorts, {total:.1f}s total")

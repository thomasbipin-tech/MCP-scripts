#!/usr/bin/env python3
"""Gate every encoded cut before it ships.

Three bookend bugs reached delivery in one session -- the shorts opened on Site Areas,
the master closed on the Blueprint wizard, and both were found by eye, late. All three
had the same shape: a timeline whose scene indices no longer meant what the code
assumed. This checks the shipped mp4 rather than the source, because that is the
artefact that goes to the client.

  python3 verify_cuts.py            # everything that has an encoded file
  python3 verify_cuts.py walkthrough
"""
import glob, hashlib, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import series

BRAND, ENDCARD = series.BRAND, series.ENDCARD
TMP = '/tmp/verify_cuts'

# where the encoded file for a given timeline slug lives
def mp4_for(slug):
    for p in (f'../series/netforge-{slug}.mp4', f'../shorts/netforge-{slug}.mp4',
              f'netforge-{slug}.mp4', '../netforge-demo-v8.mp4' if slug == '' else ''):
        if p and os.path.exists(p):
            return p
    return None

def frame(mp4, t, out):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t:.3f}', '-i', mp4,
                    '-frames:v', '1', out], check=True)
    return hashlib.sha1(open(out, 'rb').read()).hexdigest()

def check(slug, tl, mp4, want_bookends=True):
    d = json.load(open(tl))
    order = d.get('order') or list(range(len(d['scenes'])))
    if 'order' not in d:
        # the player falls back to identity here, which is precisely how the master
        # came to close on the wrong screen
        yield 'ERROR', 'timeline has no explicit "order" -- relying on identity mapping'
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout)
    if abs(dur - d['duration']) > 1.0:
        yield 'ERROR', f'runtime {dur:.2f}s does not match timeline {d["duration"]:.2f}s'
    if want_bookends:
        if order[0] != BRAND and BRAND in order:
            yield 'ERROR', f'opens on scene {order[0]}, expected the brand card ({BRAND})'
        if order[-1] != ENDCARD:
            yield 'ERROR', f'closes on scene {order[-1]}, expected the end card ({ENDCARD})'
    os.makedirs(TMP, exist_ok=True)
    seen = {}
    for i, sc in enumerate(d['scenes']):
        if order[i] in (BRAND, ENDCARD):
            continue
        h = frame(mp4, (sc['a'] + sc['b']) / 2, f'{TMP}/{slug}-{i:02d}.png')
        if h in seen:
            yield 'ERROR', f'shot {i} (scene {order[i]}) is identical to shot {seen[h]}'
        seen[h] = i
    yield 'INFO', f'{len(d["scenes"])} shots, {len(seen)} distinct content screens, {dur:.2f}s'

def main():
    only = sys.argv[1:] 
    jobs = []
    for tl in sorted(glob.glob('timeline_*.json')):
        slug = tl[len('timeline_'):-len('.json')]
        if slug.startswith(('probe', 'master')):
            continue
        if only and slug not in only:
            continue
        mp4 = mp4_for(slug)
        if mp4:
            jobs.append((slug, tl, mp4, True))
    if (not only or 'demo' in only) and os.path.exists('../netforge-demo-v8.mp4'):
        # the master carries its brand card inside scene 1, so it has no BRAND slot
        jobs.append(('demo', 'timeline.json', '../netforge-demo-v8.mp4', False))
    bad = 0
    for slug, tl, mp4, bk in jobs:
        msgs = list(check(slug, tl, mp4, bk))
        errs = [m for lvl, m in msgs if lvl == 'ERROR']
        info = next(m for lvl, m in msgs if lvl == 'INFO')
        print(f'{"FAIL" if errs else "ok  "}  {slug:24} {info}')
        for e in errs:
            print(f'        !! {e}')
        bad += len(errs)
    print(f'\n{len(jobs)} cuts checked, {bad} problem(s)')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())

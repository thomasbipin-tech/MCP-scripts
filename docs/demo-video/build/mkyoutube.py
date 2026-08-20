#!/usr/bin/env python3
"""Generate the YouTube upload pack: titles, descriptions, tags and chapter markers.

Chapters come from the timelines, not from guesswork, so they land on the actual cut.
YouTube's rules are enforced here rather than discovered on upload: the first chapter
must start at 00:00, there must be at least three, and each must run 10s or longer --
so the brand card and any short shot are folded into their neighbour.
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import series, shorts as shortsmod, walkthrough as wt

MIN_CHAPTER = 10.0
URL = 'https://netforge.ai'
TAGLINE = 'Draw the network once. Everything else is generated.'

# Human chapter names per scene index. Parsed labels are dev shorthand ("29. device
# properties panel"); these are what a viewer should read in the scrubber.
NAME = {
 0:'The drawing and the device disagree', 1:'What actually differs', 2:'The drawing as source of truth',
 3:'Placing a device', 4:'Cabling and the Link Editor', 5:'Scaling to a fabric',
 6:'Continuous validation', 7:'An address conflict, caught', 8:'AI Network Architect',
 9:'Everything green', 10:'The generated CLI', 11:'Export artefacts', 12:'Cloud on the canvas',
 13:'One canvas, one source of truth', 14:'Blueprint wizard', 15:'Multi-site WAN overview',
 16:'Templates', 17:'Config Compare', 18:'The addressing plan', 19:'Watchtower monitoring',
 20:'Free network tools', 21:'Publish preflight', 22:'Looking Glass path trace',
 23:'Rack elevation and BOM', 24:'Creating an account', 25:'Roles and access',
 26:'Device properties', 27:'Cable schedule', 28:'Export formats', 29:'The design document',
 30:'Drift against the deployed baseline', 31:'Deploying', 32:'Site areas and inheritance',
 33:'Console and out-of-band', 34:'The credential vault', 35:'The management plane',
 38:'The device catalog', 39:'Interfaces and sub-interfaces', 40:'First-hop redundancy',
 41:'Subnet profiles', 42:'The estate, generated', 43:'A project of many canvases',
 44:'Inter-site links', 45:'Joined-graph validation', 46:'Site-filtered exports',
 47:'IPAM pools', 48:'The allocation ledger', 49:'Supernet planning', 50:'The overlap checker',
 51:'VXLAN EVPN fabric parameters', 52:'Terraform, synchronized', 53:'Azure subscription import',
 54:'As-built import', 55:'The Azure Designer', 56:'Deploy with Terraform or Pulumi',
 57:'Firewall Studio', 58:'Firewall what-if', 59:'Looking Glass', 60:'Public blueprint pages',
 61:"What's new",
}
BOOKEND = {36, 37}

def ts(sec):
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'

def chapters(tl):
    """Scene spans -> YouTube chapters, merging anything under the 10s minimum."""
    d = json.load(open(tl))
    order = d.get('order') or list(range(len(d['scenes'])))   # matches the player's fallback
    raw = []
    for i, sc in enumerate(d['scenes']):
        idx = order[i]
        if idx in BOOKEND:
            continue
        raw.append([sc['a'], sc['b'], NAME.get(idx, f'Scene {idx}')])
    if not raw:
        return []
    out = []
    for a, b, nm in raw:
        if out and (b - out[-1][0]) and (b - a) < MIN_CHAPTER:
            out[-1][1] = b                      # too short to stand alone -- absorb it
        else:
            out.append([a, b, nm])
    out[0][0] = 0.0                             # YouTube requires the first chapter at 00:00
    return [(ts(a), nm) for a, b, nm in out] if len(out) >= 3 else []

def block(title, desc, tags, tl, extra=''):
    ch = chapters(tl)
    s  = f'## {title}\n\n**Title**\n```\n{title}\n```\n\n**Description**\n```\n{desc.strip()}\n'
    if ch:
        s += '\nChapters\n' + '\n'.join(f'{t} {n}' for t, n in ch) + '\n'
    s += f'\n{TAGLINE}\n{URL}\n```\n\n**Tags**\n```\n{", ".join(tags)}\n```\n'
    if extra:
        s += f'\n{extra}\n'
    return s + '\n---\n\n'

BASE = ['netforge', 'network design', 'network automation', 'network engineering',
        'network documentation', 'config generation', 'cisco', 'arista', 'network diagram']

EP_META = {
 'ep01-canvas': ('Episode 1: The Canvas',
   'The canvas is where every design starts — and everything you place on it is a real device with a real model, real ports and real configuration behind it.',
   ['network topology', 'network canvas', 'device catalog']),
 'ep02-device-config': ('Episode 2: Configuring a Device',
   'The usual objection to design tools is that they generate something shallow. Here is the depth: interfaces, sub-interfaces, first-hop redundancy, the management plane, the credential vault, and Firewall Studio.',
   ['hsrp', 'vrrp', 'device configuration', 'firewall policy', 'aaa']),
 'ep03-blueprint': ('Episode 3: Blueprints and Templates',
   'Twenty-eight reference designs, and a Blueprint wizard that builds a whole multi-site estate — one tab per site, wired through a WAN overview, with addressing that never renumbers what you already deployed.',
   ['network templates', 'blueprint', 'multi-site network', 'subnet planning']),
 'ep04-multicanvas': ('Episode 4: Multi-Site Projects',
   'A project is many canvases — one per site, plus a pinned WAN Overview. Inter-site links are declared once and mirrored, so validation runs over one joined graph.',
   ['multi-site', 'wan design', 'network validation']),
 'ep05-generate': ('Episode 5: Validation and Generation',
   'Validation is continuous, not a button you remember to press. Address conflicts, VLAN consistency, BGP reciprocity, MTU, gateway redundancy — then per-vendor CLI, and firewall what-if before you touch a rule.',
   ['network validation', 'bgp', 'vlan', 'config generation', 'firewall']),
 'ep06-ipam': ('Episode 6: Addressing and IPAM',
   'Define the pools once and stop typing addresses. Every allocation traces back to its pool, and the overlap checker catches everything typed by hand.',
   ['ipam', 'ip address management', 'subnetting', 'cidr']),
 'ep07-publish': ('Episode 7: Publish and Handover',
   'Publish is one action: validate, then produce everything at once — CLI, cable schedule, rack elevations with patch panels, bill of materials, design document — plus a public page you can embed.',
   ['network documentation', 'bill of materials', 'cable schedule', 'rack elevation']),
 'ep08-drift': ('Episode 8: Deploy, Verify and Drift',
   'The real problem is not the first day. It is month eleven, when someone fixed something at 2 a.m. and never updated the diagram. Drift closes that loop against the deployed baseline.',
   ['configuration drift', 'network deployment', 'ansible', 'config compare']),
 'ep09-fabric-cloud': ('Episode 9: Fabrics and Cloud',
   'The same canvas that held a branch closet scales to an Arista leaf-spine VXLAN EVPN fabric — and to an Azure landing zone you deploy as Terraform or Pulumi.',
   ['vxlan', 'evpn', 'arista avd', 'azure', 'terraform', 'pulumi']),
 'ep10-tools-access': ('Episode 10: Access, Tools and Monitoring',
   'Roles and two-factor, twenty-one free network tools including Looking Glass, Watchtower uptime and BGP monitors — and where the product is heading.',
   ['looking glass', 'bgp monitoring', 'uptime monitoring', 'network tools', 'rpki']),
}

SHORT_META = {
 's1-autopsy':       ('The 2 a.m. Autopsy', 'Two configs. One live comparison. No compare button.'),
 's2-in-2026':       ('Still Retyping Configs in 2026?', 'Start from a production-ready design instead.'),
 's3-weeks-to-hours':('Seventeen Sites, One Afternoon', 'A multi-site design takes weeks. It does not have to.'),
 's4-deploy-minute': ('The Deploy Minute', 'Dry run, rollback point, then the path traced hop by hop.'),
 's5-paperwork':     ('Nobody Budgets for the Paperwork', 'Rack elevation, BOM, cable schedule — all generated.'),
}

def filesize(p):
    return f'{os.path.getsize(p)/1048576:.1f} MB' if os.path.exists(p) else '-'

def runtime(p):
    if not os.path.exists(p):
        return '-'
    d = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                              '-of','csv=p=0',p], capture_output=True, text=True).stdout)
    return f'{int(d)//60}:{int(d)%60:02d}'

DELIVERY = [
 ('netforge-demo-v8.mp4',                 '../netforge-demo-v8.mp4',              'Master demo — the one to feature'),
 ('series/netforge-walkthrough.mp4',      '../series/netforge-walkthrough.mp4',   'Full walkthrough — UPLOAD THIS ONE'),
 ('series/netforge-walkthrough-web.mp4',  '../series/netforge-walkthrough-web.mp4','same cut, compressed for chat — do not upload'),
] + [(f'series/netforge-{e["slug"]}.mp4', f'../series/netforge-{e["slug"]}.mp4', f'Episode {i}')
     for i, e in enumerate(series.EPISODES, 1)] + \
    [(f'shorts/netforge-{v["slug"]}.mp4', f'../shorts/netforge-{v["slug"]}.mp4', 'Short')
     for v in shortsmod.VARIANTS]

rows = '\n'.join(f'| `{n}` | {runtime(p)} | {filesize(p)} | {note} |' for n, p, note in DELIVERY)

doc = [f"""# YouTube upload pack — Netforge.ai video set

Everything needed to upload, per video: the file, its runtime, the title, the description
(chapters included), and the tags. Chapter marks are computed from the shipped timelines,
so they land on the real cut rather than an estimate.

## The files

All paths are relative to `docs/demo-video/` on branch
`claude/netforge-demo-video-wqb9sw`.

| File | Runtime | Size | Notes |
|---|---|---|---|
{rows}

**Upload the CRF 17 masters, not the `-web` copy.** The walkthrough has two files: the
full-quality master, and a compressed copy made only to fit a 30 MB chat limit. The
compressed one is visibly softer — YouTube re-encodes anyway, so always feed it the
master. Every other video has a single file, already full quality.

## Settings that apply to all of them

- **Resolution / format:** 1920×1080, 30 fps, H.264 High, AAC 192 kbit/s, `+faststart`.
- **Audio:** normalised to −16 LUFS integrated, −1.5 dBTP — inside YouTube's target, so
  it will not be loudness-adjusted on playback.
- **Category:** Science & Technology. **Language:** English. **Captions:** none burned
  in; let YouTube auto-caption, or ask me for an SRT — the narration text is scripted, so
  a perfectly accurate caption file is a few minutes of work rather than a transcription.
- **Playlist:** put the ten episodes in one, in order, titled
  *"Netforge.ai — the ten-part series"*. The master demo and the full walkthrough sit
  outside it.
- **Visibility:** if you want to review before publishing, upload as **Unlisted** and
  flip to Public — chapters and thumbnails can be set either way.
- **Shorts:** the five short cuts are 16:9, not 9:16. YouTube will accept them as regular
  uploads; for the Shorts shelf specifically they need a vertical crop, which I can
  produce if you want them there.

## Suggested upload order

1. Master demo (the channel's front door)
2. Full walkthrough
3. Episodes 1–10, in order, as a playlist
4. The five shorts

---

"""]

doc.append(block('Netforge.ai — Draw the Network Once',
  f"""Every enterprise network begins as a clean diagram. Almost every outage begins the same way too — not because the design was wrong, but because someone had to translate it by hand into thousands of lines of configuration.

Netforge.ai makes the drawing the source of truth: the thing the network is generated from, validated against, documented from, and continuously compared to.

Design, configure, validate, deploy, and verify — one canvas.

No account needed to draw a topology and generate real configs in your browser.""",
  BASE + ['network design tool', 'netforge.ai', 'demo'], 'timeline.json'))

doc.append(block('Netforge.ai — The Complete Walkthrough',
  f"""A full walkthrough of Netforge.ai, from an empty canvas to a deployed and continuously verified network. By the end you will know what it is, what it solves, how to use it, and where it is going.

No account needed to draw a topology and generate real configs in your browser.""",
  BASE + ['product walkthrough', 'tutorial', 'ipam', 'vxlan', 'azure', 'firewall'],
  'timeline_walkthrough.json'))

for e in series.EPISODES:
    slug = e['slug']
    title, blurb, extra_tags = EP_META[slug]
    doc.append(block(f'Netforge.ai — {title}',
        f'{blurb}\n\nPart of the ten-part Netforge.ai series.\n\nNo account needed to draw a topology and generate real configs in your browser.',
        BASE + extra_tags, f'timeline_{slug}.json'))

doc.append('## Shorts\n\nUnder 30s each — upload as Shorts (vertical crop optional; these are 16:9).\n\n')
for v in shortsmod.VARIANTS:
    slug = v['slug']
    title, blurb = SHORT_META[slug]
    doc.append(f'**{slug}**\n```\n{title}\n```\n```\n{blurb}\n\n{TAGLINE}\n{URL}\n```\n\n')

open('../YOUTUBE.md', 'w').write(''.join(doc))
print('wrote docs/demo-video/YOUTUBE.md')

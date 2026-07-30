#!/usr/bin/env python3
"""The 10-part deep-dive series (~2 min each), built on the scene library.

Content is grounded in netforge.ai's own documentation (/docs, 22 pages, including a
dated release history through July 2026) rather than inferred from the marketing site.
Where the docs give an exact UI location -- "Canvas toolbar -> Publish", "Canvas ->
Device catalog (left sidebar)" -- the narration uses it, so a viewer can follow along.

Pacing is 1.0x (tutorial, not trailer). Every episode opens on the brand card and closes
on the end card, matching the master cut and the shorts.

  python3 series.py            # VO + timeline_ep<N>-<slug>.json for all ten
  python3 series.py ep3        # one episode
  python3 series.py --list     # plan only, no synthesis
"""
import json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vo, shorts

SPEED = 1.0
PADS  = (0.45, 0.40, 0.75)
BRAND, ENDCARD = 36, 37
PANES, BRIDGE, REFRAME, DRAG, PORTS, FABRIC = 0, 1, 2, 3, 4, 5
VALIDATE, CONFLICT, AIARCH, GREEN, CLIOUT, EXPORTS, CLOUD, OUTCOME = 6, 7, 8, 9, 10, 11, 12, 13
BLUEPRINT, MULTISITE, TEMPLATES, CONFIGCMP = 14, 15, 16, 17
ADDRESSING, WATCHTOWER, TOOLS, PREFLIGHT, LOOKINGGLASS, RACKBOM = 18, 19, 20, 21, 22, 23
# dedicated topic screens (batch 2) -- one subject each, so narration and picture agree
ACCOUNT, ROLES, DEVPROPS, CABLESCHED = 24, 25, 26, 27
EXPORTFMT, DESIGNDOC, DRIFTDASH, DEPLOYRUN = 28, 29, 30, 31
SITEAREAS, CONSOLEOOB, VAULT, MGMTPLANE = 32, 33, 34, 35
# dedicated topic screens (batch 3) -- one per episode subject, so no episode has to
# borrow another's picture. Appended after the end card, so BRAND/ENDCARD keep their
# indices and the already-rendered timelines stay valid.
CATALOG, INTERFACES, FHRP, SUBNETPROF, BPGEN = 38, 39, 40, 41, 42
PROJECTHOME, XSITE, JOINEDVAL, SITEFILTER = 43, 44, 45, 46
POOLS, ALLOC, SUPERNET, OVERLAP = 47, 48, 49, 50
EVPNCFG, TERRAFORM, SUBIMPORT, ASBUILT = 51, 52, 53, 54

TAG = "Netforge.ai. From sketch to spine."

# Every episode owns its screens. No scene appears in two episodes, and none appears
# twice inside one -- the previous cut re-used VALIDATE, CLIOUT and EXPORTS across four
# episodes each, which is what read as "the same screens over and over".
EPISODES = [
 dict(slug='ep01-canvas', title='Episode 1 — The Canvas',
      slots=[(BRAND,3.0),(REFRAME,None),(CATALOG,None),(DRAG,None),(PORTS,None),(DEVPROPS,None),(ENDCARD,5.0)],
      lines=[
       (1,"This is the first of ten short episodes. Each one takes a single part of "
          "Netforge.ai and shows you how it actually works. This one is the canvas — where "
          "every design starts."),
       (1,"The idea underneath the whole product is that the drawing is the source of truth. "
          "Not a picture of the network: the thing the network is generated from, validated "
          "against, documented from, and continuously compared to."),
       (1,"So the canvas is not a diagramming tool that happens to look like your network. "
          "Everything you place on it is a real device with a real model, real ports and real "
          "configuration behind it."),
       (2,"The device catalog is the left sidebar, grouped by vendor and family. Click a "
          "device to drop it at the next free spot, or drag it exactly where you want it."),
       (2,"Search filters across every vendor at once, which matters when the catalog spans "
          "Cisco, Arista, Aruba, Palo Alto, Silver Peak and Lantronix. The sidebar minimizes "
          "to a thin rail — hover to expand it, or pin it open."),
       (2,"Not everything on the canvas is a device. Internet, MPLS and VPN clouds draw as "
          "actual cloud outlines: pure connection points for terminating WAN links, with no "
          "port inventory and no configuration of their own."),
       (3,"Placing a device is the whole gesture. Drag it out of the catalog, drop it on the "
          "canvas, and it arrives as that model — not a generic box you have to describe "
          "afterwards."),
       (3,"That matters because the port inventory comes with it. The platform already knows "
          "what interfaces this device has, what they are called in its own dialect, and what "
          "optics they will take."),
       (4,"To cable, drag from one connection point to another. The points zoom on hover so "
          "they are easy to hit on a dense drawing."),
       (4,"The Link Editor then assigns real interfaces on both ends, chosen from each "
          "device's actual port inventory. You pick the media — copper, SFP, QSFP or DAC — and "
          "the speed, from one gigabit to four hundred."),
       (4,"That speed renders on the drawing and drives optic selection in the bill of "
          "materials. Media and port-cage mismatches are flagged while you draw, not after."),
       (5,"Select a device and the properties panel opens. This is where the canvas stops "
          "being a diagram: interfaces, layer two and three, features, and the management "
          "plane, in that platform's own dialect."),
       (5,"Settings inherited from the site are marked as inherited, and anything you change "
          "on this one box is marked as an override — so you can always see which values are "
          "local decisions and which came from the site."),
       (6,TAG),
      ]),

 dict(slug='ep02-device-config', title='Episode 2 — Configuring a device',
      slots=[(BRAND,3.0),(INTERFACES,None),(FHRP,None),(MGMTPLANE,None),(CONSOLEOOB,None),(VAULT,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode two: what you can actually configure. The usual objection to design tools "
          "is that they generate something shallow — a hostname, an address, and then you "
          "finish the job by hand. So here is the depth."),
       (1,"Interfaces take descriptions, addressing, MTU and admin state. Routed parents take "
          "dot1q sub-interfaces with tag, address and VRF."),
       (1,"Loopbacks are configurable on every layer-three device, with duplicate checking "
          "across the whole design — because a duplicated router-id is exactly the kind of "
          "mistake that passes every syntax check and then breaks the overlay."),
       (2,"First-hop redundancy is thorough. HSRP and VRRP, with preempt and delays, "
          "interface and object tracking with decrement, timers, version, virtual MAC, and "
          "secondary virtual addresses."),
       (2,"Tracking is the part people hand-write and get wrong. Track an interface or a "
          "tracked object, set the decrement, and the platform keeps the peer's priority "
          "consistent so the pair cannot end up in a tie."),
       (2,"Port-channels are equally complete: MTU, speed, negotiation, access lists and "
          "spanning-tree edge."),
       (3,"Then the management plane, which is usually the least glamorous and most "
          "security-relevant part of a build. AAA servers with timeout, retransmit, VRF and "
          "source interface — and a Test AAA action, so you find out now rather than at "
          "cutover."),
       (3,"NTP with authentication, prefer, source and access groups. Console and VTY "
          "hardening. CDP and LLDP. NetFlow. Static routes with IP SLA tracking."),
       (4,"Console and out-of-band management is first class rather than an afterthought. "
          "Every device gets a console port and its real dedicated management interface."),
       (4,"Drag a device onto a Lantronix terminal server and the console run cables itself — "
          "so the out-of-band path is part of the design, and it turns up in the cable "
          "schedule like every other run."),
       (5,"And every secret — local users, enable, TACACS, RADIUS, SNMP and NTP keys — "
          "references an encrypted per-organization vault."),
       (5,"The design carries the reference, not the value. The generated configuration "
          "renders the real secret and marks it, and a design you share carries no "
          "credentials at all."),
       (6,TAG),
      ]),

 dict(slug='ep03-blueprint', title='Episode 3 — Blueprints and templates',
      slots=[(BRAND,3.0),(TEMPLATES,None),(BLUEPRINT,None),(SUBNETPROF,None),(BPGEN,None),(SITEAREAS,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode three: not starting from nothing. The Templates page carries featured "
          "reference designs and community-shared ones — leaf-spine fabrics, branch SD-WAN, "
          "campus three-tier, collapsed core, hybrid Azure."),
       (1,"There is also an Enterprise WAN family: a thirty-office overview with seventy "
          "devices, a data centre, and a branch office, as parameterized blueprints where you "
          "set a company code and an office count."),
       (1,"Open any card to preview it, or use it as your starting point. And if you already "
          "have drawings, the Import wizard reads a Visio topology and flags the generic "
          "elements it could not map, so the gaps are explicit rather than silent."),
       (2,"For anything bigger than one site, start with the Blueprint wizard. Tell it how "
          "many data centres, campuses and branches you have, and it builds the estate."),
       (2,"Addressing is flexible: supernets from a slash eight to a slash sixteen, with "
          "right-sized per-site blocks — roughly a slash twenty for a data centre or campus, "
          "a slash twenty-one for a branch — packed automatically and overridable per site."),
       (3,"Each site kind gets its own editable subnet profile: data, voice, servers, guest, "
          "management, transit and loopbacks."),
       (3,"That profile is not decoration. It drives the VLANs, the gateway SVIs, the DHCP "
          "relay, and the voice VLAN on access ports — so editing one profile changes every "
          "branch the wizard generates."),
       (4,"Then it builds. One tab per site, wired through a WAN overview, with every subnet "
          "allocated from the one supernet you chose."),
       (4,"The important detail is that generated blocks pin themselves. Re-running the "
          "wizard to add three more branches next quarter never renumbers the sites you have "
          "already deployed."),
       (5,"Inside a site, Site Areas hold a shared management plane that every device in that "
          "site inherits — with per-device override where one box genuinely differs."),
       (5,"That is what keeps a seventeen-site estate consistent without seventeen copies of "
          "the same settings drifting apart."),
       (6,TAG),
      ]),

 dict(slug='ep04-multicanvas', title='Episode 4 — Multi-site projects',
      slots=[(BRAND,3.0),(PROJECTHOME,None),(MULTISITE,None),(XSITE,None),(JOINEDVAL,None),(SITEFILTER,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode four: what happens when one canvas is not enough. A project in "
          "Netforge.ai is many canvases — one per site, plus a pinned WAN Overview."),
       (1,"They behave like browser tabs. Site blocks on the Overview jump straight to their "
          "tab, and every canvas keeps its own address block and its own validation state."),
       (2,"The Overview is where the estate is a single picture. Seventeen sites, the "
          "carriers between them, and which of them are currently clean."),
       (2,"This is not seventeen separate designs that happen to live in one project. It is "
          "one graph, drawn across several canvases."),
       (3,"Inter-site connectivity is declared once, on the Overview, and mirrored onto each "
          "site tab as a WAN stub cloud."),
       (3,"That is the whole trick. A WAN link has exactly one definition, so it cannot exist "
          "twice with two different sets of values — which is the classic way a multi-site "
          "design quietly becomes wrong."),
       (4,"Because the graph is joined, validation runs across it. That catches island sites "
          "with no path back, unmatched WAN identifiers, disagreements between the Overview "
          "and a site's own configuration, and address pool overlaps between sites."),
       (4,"None of those are visible if you validate each site on its own. Click a finding "
          "and it switches you to the tab that owns it."),
       (5,"And when it comes time to hand work over, every deliverable takes a site filter."),
       (5,"The branch team gets the branch pack — nine devices, fourteen cable runs, its own "
          "bill of materials — rather than a two-hundred-device document with their site "
          "somewhere inside it."),
       (6,TAG),
      ]),

 dict(slug='ep05-generate', title='Episode 5 — Validation and generation',
      slots=[(BRAND,3.0),(VALIDATE,None),(CONFLICT,None),(AIARCH,None),(GREEN,4.5),(CLIOUT,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode five: the part that earns the trust. Validation in Netforge.ai is "
          "continuous — not a button you have to remember to press before you ship."),
       (1,"It checks address conflicts, VLAN consistency, trunk and native VLAN matching, BGP "
          "reciprocity and AS consistency, spanning-tree root placement, MTU, gateway "
          "redundancy, and management reachability."),
       (2,"When something is wrong, it is specific: the two interfaces that collide, on which "
          "devices, and what it will break."),
       (2,"Address conflicts are the most expensive simple mistake in networking. They pass "
          "every syntax check, deploy cleanly, and then take down two segments at once."),
       (3,"On top of the mechanical checks, the AI Network Architect reviews the design as a "
          "whole — single points of failure, and alignment with Cisco validated designs and "
          "Arista's AVD — and tells you what to fix and why it matters."),
       (3,"There is a rule underneath all of this that matters more than any single check: "
          "capability-aware validation. If a platform cannot render a setting, Netforge.ai "
          "omits it and flags it. It never invents a command to fill a gap."),
       (4,"When it is clean, the whole design goes green. Every check, every device, in under "
          "two seconds."),
       (5,"And then it generates: complete per-device, per-vendor CLI for the entire design, "
          "in each platform's own syntax."),
       (5,"Not a starting point you finish by hand. The configuration that the validation you "
          "just watched was run against."),
       (6,TAG),
      ]),

 dict(slug='ep06-ipam', title='Episode 6 — Addressing and IPAM',
      slots=[(BRAND,3.0),(POOLS,None),(ADDRESSING,None),(ALLOC,None),(SUPERNET,None),(OVERLAP,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode six: addressing, which is where most designs quietly go wrong. It has its "
          "own console on the canvas toolbar — IPAM."),
       (1,"You define the pools once: loopbacks, point-to-point transits, user VLANs, "
          "management. Each pool gets a range, a prefix size and an allocation strategy."),
       (1,"From then on you stop typing addresses. You allocate from a pool."),
       (2,"The addressing plan is the readable form of that: every subnet, its VLAN, its "
          "gateway, its usable count, and what it is for — across the whole design."),
       (3,"Behind it, every address traces back to a pool. SVIs, routed links and first-hop "
          "redundancy addresses are assigned consistently, and each allocation keeps its "
          "origin, its device and its interface."),
       (3,"You can still type an address by hand where you need to. It is simply marked as "
          "manual, and it is still checked."),
       (4,"At estate scale, one supernet is split into right-sized per-site blocks — roughly "
          "a slash twenty for a data centre or campus, a slash twenty-one for a branch — "
          "packed automatically, and overridable per site."),
       (4,"Blocks pin when they are generated, and there is reserve left over, so adding a "
          "site later takes from the reserve rather than from a neighbour."),
       (5,"And then the overlap checker. Pool-based allocation makes conflicts structurally "
          "impossible for managed ranges; the checker exists for everything else."),
       (5,"Duplicate host addresses, pool overlaps between canvases, and addresses sitting "
          "outside every defined range — caught across the whole design rather than one site "
          "at a time."),
       (6,TAG),
      ]),

 dict(slug='ep07-publish', title='Episode 7 — Publish and handover',
      slots=[(BRAND,3.0),(PREFLIGHT,None),(EXPORTFMT,None),(RACKBOM,None),(CABLESCHED,None),(DESIGNDOC,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode seven: getting the design out of the tool. Publish is deliberately one "
          "action on the canvas toolbar."),
       (1,"The failure it is designed against is a half-published design — configs generated "
          "on Tuesday, cabling exported on Thursday, describing two different networks."),
       (1,"Publish walks the design through validation first, then produces everything at "
          "once. The dry run orders operations — core, then distribution, then access — and "
          "creates the rollback point before anything is pushed."),
       (2,"What you get is six deliverables, all generated from the same validated canvas at "
          "the same moment."),
       (2,"A design package, an editable Visio topology, a bill of materials, a cable "
          "schedule, per-device configs, and an AVD Ansible package. So the documentation "
          "cannot drift away from the design — it has no opportunity to."),
       (3,"Rack elevations show what goes where, and the bill of materials aggregates "
          "chassis, line cards, optics and cables with quantities."),
       (3,"Those optics are not guesswork. They are sized from the link speeds you chose when "
          "you drew the cabling, back in episode one."),
       (4,"The cable schedule is every link, with A-end and B-end device, port, media, speed "
          "and length. One row per run, ready for the rack team."),
       (4,"Including the console runs, because out-of-band cabling was part of the design "
          "rather than something added on site."),
       (5,"And the design document: the drawing plus per-device summaries, firewall handover "
          "sections and rack elevations, as the hand-off pack."),
       (5,"Publishing defaults to private. Choosing public shares the design as a community "
          "template, and the scrubber runs first, stripping secrets before anything leaves "
          "your organization."),
       (6,TAG),
      ]),

 dict(slug='ep08-drift', title='Episode 8 — Deploy, verify and drift',
      slots=[(BRAND,3.0),(DEPLOYRUN,None),(LOOKINGGLASS,None),(PANES,None),(DRIFTDASH,None),(CONFIGCMP,None),(ASBUILT,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode eight: after the design is right. Deployment is Ansible-based, and it runs "
          "in the order the dry run established — core, then distribution, then access."),
       (1,"Credentials come from the shared store at deploy time. They are never embedded in "
          "the design and never part of a share."),
       (2,"Once it is on, Looking Glass traces the path hop by hop and confirms it matches "
          "the design."),
       (2,"On a multi-site project it runs over the joined graph, so a trace crosses site "
          "boundaries the way real traffic does."),
       (3,"But the real problem is not the first day. It is month eleven, when someone has "
          "logged into a device at two in the morning, fixed something, and not updated the "
          "drawing."),
       (3,"That is the gap this whole product exists to close, and closing it means checking "
          "it continuously rather than believing the diagram."),
       (4,"So the Drift action compares each device's live running-config against the config "
          "Netforge.ai last deployed for it — the intended baseline, not another file "
          "somebody kept."),
       (4,"Every device reports in sync, drifted, unreachable, or no baseline. Drifted gives "
          "you a line diff and a structural one, and badges the node on the canvas. "
          "Running-configs are secret-scrubbed before any diff is stored."),
       (5,"The manual equivalent is Config Compare, free in the tools suite. Drop in two "
          "configs and the panes become a live comparison — no compare button, and nothing "
          "leaves your browser."),
       (5,"Green is identical, yellow is the same line with minor edits, red is a line with "
          "no counterpart. Block-aware sorting cancels out reordering, changes are classified "
          "major or minor fail-closed, and it exports as a unified diff or an HTML report."),
       (6,"And when reality has already moved on further than a diff can express, the Import "
          "wizard's as-built mode pulls a live device and its LLDP neighbours through the "
          "credential vault."),
       (6,"It reconciles matched, new and missing against your design. The apply is additive "
          "and undoable, so nothing on the canvas is silently deleted."),
       (7,TAG),
      ]),

 dict(slug='ep09-fabric-cloud', title='Episode 9 — Fabrics and cloud',
      slots=[(BRAND,3.0),(FABRIC,None),(EVPNCFG,None),(CLOUD,None),(SUBIMPORT,None),(TERRAFORM,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode nine: the two ends of the range. The same canvas that held a branch closet "
          "scales to a full Arista leaf-spine VXLAN EVPN fabric."),
       (1,"Same drawing surface, same validation, same bill of materials — the difference is "
          "the number of boxes, not the tool."),
       (2,"The AVD wizard follows Arista's own model: architect, validate, deploy. You set "
          "the fabric parameters — underlay and overlay AS numbering, VTEP and router-id "
          "sources, anycast gateway, underlay MTU, spine and leaf counts."),
       (2,"There is full validation parity with single devices, and the fabric's optics land "
          "in the bill of materials like any other link."),
       (3,"Cloud is the same story. Azure resources are real nodes on the canvas — virtual "
          "networks, subnets, security groups, gateways — not a picture of your subscription."),
       (3,"You can design them from scratch alongside the physical estate, in one drawing and "
          "one bill of materials."),
       (4,"Or run the subscription import and reverse-engineer what already exists. It reads "
          "the subscription and draws it, and from there it behaves like anything else on the "
          "canvas — validated, documented, and comparable against reality."),
       (5,"The Terraform stays synchronized with the drawing, so the canvas and the "
          "infrastructure code are the same artefact rather than two that have to be kept in "
          "step by hand."),
       (5,"Push it back as Terraform, and schedule drift checks against it. The same closed "
          "loop as the physical estate."),
       (6,TAG),
      ]),

 dict(slug='ep10-tools-access', title='Episode 10 — Access, tools and monitoring',
      slots=[(BRAND,3.0),(ACCOUNT,None),(ROLES,None),(TOOLS,None),(WATCHTOWER,None),(OUTCOME,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode ten, the last one: everything around the design work. Register with a "
          "valid email — that address is your username — and a verification link arrives "
          "immediately. The account activates when you click it."),
       (1,"Passwords follow a compliance policy: at least twelve characters, upper and lower "
          "case, a number and a special character, and you cannot reuse recent ones."),
       (1,"Two-factor authentication is available to everyone from your profile, and required "
          "for owner, admin and lab-editor accounts. Enrolment is enforced on every request, "
          "so a promotion into a privileged role takes effect immediately rather than at next "
          "sign-in."),
       (2,"Roles run owner, admin, editor, viewer and observer. New sign-ups start as editor, "
          "so a teammate can build straight away."),
       (2,"Only the owner changes anyone's role, and viewers get a genuinely read-only canvas "
          "rather than one that lets them make changes they cannot save."),
       (3,"Alongside the platform there is a suite of free network tools — diagnostics, "
          "subnet and address calculators, config comparison, and reference lookups."),
       (3,"They need no account and nothing leaves your browser, which is the point: they are "
          "the things you reach for mid-incident, not mid-project."),
       (4,"Watchtower monitors uptime with multi-channel alerting, and watches the platform "
          "itself from outside."),
       (4,"The drift scheduler reuses those same channels, so operational alerting is one "
          "system rather than two that have to be configured separately."),
       (5,"That is the whole product, across ten episodes: design on a canvas, configure with "
          "real per-vendor depth, validate continuously, publish once, deploy safely, and "
          "keep verifying afterwards."),
       (5,"Less retyping, more verification, and a shorter distance between the drawing and "
          "the running network."),
       (6,TAG),
      ]),
]


def build(ep, do_synth=True):
    slug = ep['slug']; outdir = f'vo_{slug}'
    os.makedirs(outdir, exist_ok=True)
    ids, report = {}, []
    for n, (slot, text) in enumerate(ep['lines']):
        lid = f'{n:02d}'; ids[n] = (slot, lid, text)
        if do_synth:
            d, sp, flags = shorts.synth_verified(text, f'{outdir}/{lid}.wav', speed=SPEED)
            if flags and flags[0]:
                report.append(f"      {lid} {'/'.join(flags[0])} flagged")
    durs = {n: len(vo.read(f'{outdir}/{ids[n][1]}.wav')[0]) / vo.SR for n in ids}

    # A scene animates for ~6s then holds. Slots carrying 25s+ of narration would sit
    # static for most of that, so they are split into consecutive slots on the SAME scene:
    # the shot replays its build, which reads as re-emphasis and keeps the frame moving.
    MAXSLOT = 10_000.0   # disabled: replaying a scene to fill time repeats screens
    exp_slots, exp_of = [], {}
    for slot, (sidx, floor) in enumerate(ep['slots']):
        mine = [n for n in ids if ids[n][0] == slot]
        tot = sum(durs[n] for n in mine)
        parts = 1 if tot <= MAXSLOT or len(mine) < 2 else min(len(mine), int(tot // MAXSLOT) + 1)
        per = max(1, -(-len(mine) // parts))
        for k in range(parts):
            chunk = mine[k * per:(k + 1) * per]
            if not chunk and k:
                continue
            exp_slots.append((sidx, floor if k == 0 else None))
            for n in chunk:
                exp_of[n] = len(exp_slots) - 1
    ep_slots = exp_slots
    for n in ids:
        ids[n] = (exp_of.get(n, ids[n][0]), ids[n][1], ids[n][2])

    intro, gap, tail = PADS
    scenes, placed, cursor = [], [], 0.0
    for slot, (sidx, floor) in enumerate(ep_slots):
        mine = [n for n in ids if ids[n][0] == slot]
        t, local = (intro if mine else 0.0), []
        for k, n in enumerate(mine):
            if k: t += gap
            local.append((n, t, durs[n])); t += durs[n]
        need = t + (tail if mine else 0.0)
        d = round(max(floor if floor is not None else 5.0, need), 2); a = round(cursor, 2)
        scenes.append({'a': a, 'b': round(a + d, 2)})
        placed += [(ids[n][1], round(a + lt, 2), ld) for n, lt, ld in local]
        cursor = a + d
    DUR = round(cursor, 2)

    order = [s[0] for s in ep_slots]
    prod = [i for i, (sidx, _f) in enumerate(ep_slots) if sidx not in (BRAND, ENDCARD)]
    anchors = {'turn': None, 'prod': scenes[prod[0]]['a'],
               'payoff': scenes[prod[-1]]['a'], 'payoff_end': scenes[prod[-1]]['b'],
               'outro': scenes[-1]['a']}

    bed = np.zeros(int((DUR + 1) * vo.SR), dtype=np.float32)
    for lid, st, _ld in placed:
        a_, sr = vo.read(f'{outdir}/{lid}.wav')
        f = int(0.008 * sr); a_[:f] *= np.linspace(0, 1, f); a_[-f:] *= np.linspace(1, 0, f)
        i = int(st * vo.SR); bed[i:i + len(a_)] += a_
    bed *= 10 ** (-3.0 / 20) / max(np.abs(bed).max(), 1e-6)
    vo.write_wav(f'vo_{slug}.wav', bed)

    json.dump({'duration': DUR, 'voice': vo.VOICE, 'speed': SPEED, 'order': order,
               'brandInPanes': False, 'anchors': anchors, 'scenes': scenes, 'cues': [],
               'vo': [{'id': l, 'start': s, 'dur': round(d_, 2)} for l, s, d_ in placed]},
              open(f'timeline_{slug}.json', 'w'), indent=1)
    mm, ss = int(DUR // 60), DUR % 60
    flag = '' if DUR >= 120 else '   <-- UNDER 2 MIN'
    print(f"  {ep['title']:44} {mm}:{ss:05.2f}  {len(ep['lines']):2} lines  {len(order):2} shots  max dwell {max(x['b']-x['a'] for x in scenes):5.1f}s{flag}")
    for r in report: print(r)
    return DUR

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    retime = '--retime' in sys.argv        # re-time from existing vo_*/ wavs
    todo = [e for e in EPISODES if not args or any(a in e['slug'] for a in args)]
    total = sum(build(e, do_synth=not retime) for e in todo)
    print(f"\n  {len(todo)} episodes, {total/60:.1f} min total")

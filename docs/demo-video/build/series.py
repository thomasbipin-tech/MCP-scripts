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

TAG = "Netforge.ai. From sketch to spine."

EPISODES = [
 dict(slug='ep01-canvas', title='Episode 1 — The Canvas',
      slots=[(BRAND,3.0),(TEMPLATES,None),(DRAG,None),(PORTS,None),(FABRIC,None),(BRIDGE,None),(ENDCARD,5.0)],
      lines=[
       (1,"This is the first of ten. Each one takes a single part of Netforge.ai and shows "
          "you how it actually works."),
       (1,"Start here. Every project begins on a canvas — or from a template, so you never "
          "face a blank one."),
       (1,"The gallery carries featured reference designs and community templates. Open one, "
          "and it becomes your starting point."),
       (2,"On the canvas, the device catalog sits in the left sidebar, grouped by vendor and "
          "family. Click a device to drop it at the next free spot, or drag it exactly where "
          "you want it."),
       (2,"The sidebar auto-minimizes to a thin rail. Hover to expand it, or pin it open. "
          "Search filters across every vendor at once."),
       (3,"To cable two devices, drag from one connection point to another. The points zoom "
          "on hover, so they're easy to hit even on a dense drawing."),
       (3,"When the link is made, the Link Editor assigns real interfaces on both ends — "
          "picked from each device's actual port inventory, derived from its model."),
       (3,"Choose the media — copper, SFP+, QSFP, DAC — and the speed. One, ten, twenty-five, "
          "forty, a hundred, or four hundred gigabit."),
       (3,"That speed renders on the drawing, and it drives optic selection in the bill of "
          "materials. Media and port-cage mismatches are flagged as you draw."),
       (4,"The same canvas scales. A branch closet, or a full Arista leaf-spine VXLAN EVPN "
          "fabric — without leaving the designer."),
       (5,"And because the canvas is the source of truth, everything downstream — config, "
          "validation, documentation — comes from this one drawing."),
       (5,"Nothing is retyped. That's the whole idea."),
       (1,'Templates matter more than they sound. The Enterprise WAN family alone carries a thirty-office overview with seventy devices, a data centre, and a branch office — as parameterized blueprints you set a company code and an office count on.'),
       (2,'Not everything on a canvas is a device. Internet, MPLS and VPN clouds draw as actual cloud outlines — pure connection points for terminating WAN links, with no port inventory and no configuration of their own.'),
       (4,'Auto-layout tidies a drawing that grew organically, and multi-layer views let you look at physical cabling or logical topology without redrawing either.'),
       (5,"Existing drawings come across too. The Import wizard reads a Visio topology and flags the generic elements it couldn't map, so you fix them deliberately rather than inheriting silent gaps."),
       (5,'And the interface stays out of the way. Feedback arrives as calm colour-coded toasts, destructive actions confirm in-app and name exactly what they take with them, and errors say what happened and what to do next.'),
       (6,TAG),
      ]),

 dict(slug='ep02-device-config', title='Episode 2 — Device configuration',
      slots=[(BRAND,3.0),(PORTS,None),(VALIDATE,None),(CLIOUT,None),(CONFLICT,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode two. Once devices are on the canvas, each one gets a real configuration — "
          "not a label on a drawing."),
       (1,"Select a device and the properties panel opens with the same tabs the platform "
          "uses everywhere: interfaces, layer two and layer three, features, and the "
          "management plane."),
       (1,"Interfaces take descriptions, addressing, MTU, and admin state. Routed parents on "
          "routers and layer-three switches take dot1q sub-interfaces — tag, address, VRF — "
          "with tag range and uniqueness validation."),
       (1,"Loopbacks are fully configurable on every layer-three device: identifier, address, "
          "secondaries, VRF, OSPF area. Duplicate addresses are checked design-wide."),
       (2,"First-hop redundancy goes deep. HSRP and VRRP on SVIs take preempt with delays, "
          "interface and object tracking with decrement, hello and hold timers, version "
          "selection, virtual MAC, and secondary virtual addresses."),
       (2,"Port-channels take MTU, speed, negotiation, load interval, bandwidth, admin state, "
          "inbound and outbound access lists, and spanning-tree edge — with a device-wide "
          "load-balance method mapped per vendor."),
       (3,"Every one of those settings renders as real syntax for the platform it's on. Not a "
          "generic approximation — the dialect that device actually speaks."),
       (3,"And where a platform genuinely can't do something, Netforge.ai omits it and flags "
          "it. It never invents a command that doesn't exist."),
       (4,"That capability-aware validation is the difference between a config that looks "
          "right and one that loads."),
       (1,'Site Areas carry a shared management plane that every device in the site inherits — with per-device override where one box genuinely differs. The site panel uses the same tabs the devices do.'),
       (2,'The management plane goes deep: AAA servers with timeout, retransmit, VRF and source interface — and a Test AAA action. Common-Criteria password policy. NTP with authentication, prefer, source and access groups.'),
       (2,'Console and VTY line hardening. Global CDP and LLDP. NetFlow exporter detail. Static routes with IP SLA tracking, so a route withdraws when the thing it depends on stops answering.'),
       (2,"NTP authentication picks MD5, HMAC-SHA1 or HMAC-SHA2-256 and inherits from the site. On NX-OS it falls back to MD5 with a note rather than silently emitting something the platform won't take."),
       (3,'SSH host keys are configurable on every Cisco template — key label and modulus, two thousand forty-eight, three thousand seventy-two or four thousand ninety-six, with a NIST and CIS two-thousand-forty-eight-bit floor.'),
       (3,"Port mirroring is there too. Monitor sessions on every standalone switch and router: session id, source interface with direction, destination, enable toggle — rendered in each vendor's own dialect, with duplicate and destination-reuse validation."),
       (4,'Every secret in all of that — local user passwords, enable secret, TACACS and RADIUS keys, SNMP communities, NTP keys — references the encrypted vault rather than sitting in the design.'),
       (5,TAG),
      ]),

 dict(slug='ep03-blueprint', title='Episode 3 — The Blueprint wizard',
      slots=[(BRAND,3.0),(BLUEPRINT,None),(ADDRESSING,None),(MULTISITE,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode three. Most designs don't start with one switch. They start with an "
          "estate — and that's what the Blueprint wizard builds."),
       (1,"Tell it the scope: how many data centres, how many campuses, how many branches. "
          "It generates every site, wired through a WAN overview."),
       (1,"Addressing is flexible. Supernets run from a slash eight to a slash sixteen, with "
          "right-sized blocks per site — around a slash twenty for a data centre or campus, "
          "a slash twenty-one for a branch — packed automatically, and overridable per site."),
       (1,"Generated blocks pin themselves. So an additive re-run adds new sites without "
          "renumbering the ones you already have."),
       (2,"Each kind of site gets an editable subnet profile: data, voice, servers, guest, "
          "management, transit, loopbacks."),
       (2,"That profile drives the VLANs, the HSRP gateway SVIs, DHCP relay, and voice VLANs "
          "on access ports — consistently, across every site it applies to."),
       (3,"Routing design and out-of-band management are part of the same wizard, so the "
          "estate arrives complete rather than half-built."),
       (3,"Seventeen sites, one blueprint. Then you open any of them and keep working."),
       (1,'Before the wizard existed, the alternative was a blank canvas and a long evening. This is the difference between designing a network and typing one.'),
       (2,'Out-of-band management is generated with the estate, not bolted on afterwards. Every network device gets a console port and its real dedicated management interface — mgmt-zero, Management-one, GigabitEthernet-zero, whichever that platform uses.'),
       (2,'Drag a device onto a Lantronix terminal server and the console run cables itself, sequentially, overridable, and an occupied port silently bumps to the next free one. Two runs on one port is flagged as a conflict.'),
       (2,'Management addressing auto-assigns from IPAM with manual-override protection, and a configurable management VRF keeps the per-platform defaults intact.'),
       (3,'The three frozen Enterprise WAN designs stay available as featured templates, so you can start from a known-good reference instead of the wizard when that suits better.'),
       (3,'Every office in that reference runs two Silver Peak EdgeConnect spokes across dual transports — one on the MPLS underlay, one on the Internet underlay.'),
       (3,"Both data centres pair EdgeConnect hubs with a Cisco core and a Palo Alto pair that centralizes Internet breakout. That's a real design, not a diagram."),
       (4,'You can re-run the wizard as the estate grows. New sites are added; the ones already deployed keep their addressing.'),
       (4,TAG),
      ]),

 dict(slug='ep04-multicanvas', title='Episode 4 — Multi-canvas and site tabs',
      slots=[(BRAND,3.0),(MULTISITE,None),(VALIDATE,None),(CONFLICT,None),(EXPORTS,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode four. A multi-site project isn't one drawing. It's many — and they have to "
          "stay consistent with each other."),
       (1,"Netforge.ai spans them as tabs. One per site, plus a pinned WAN Overview. Site "
          "blocks on the Overview jump straight to their tab."),
       (1,"Inter-site connectivity is declared once, on the Overview. Each site tab mirrors it "
          "as a WAN stub cloud, so a link exists in exactly one place."),
       (2,"Validation then runs over the joined graph, not each canvas in isolation."),
       (2,"That catches the things single-canvas checking cannot: island sites with no path "
          "back, unmatched WAN identifiers, mismatches between the Overview and the "
          "configuration, and address-pool overlaps between sites."),
       (3,"Click a finding and it switches you to the tab that owns it. You don't go hunting."),
       (4,"Exports understand sites too. The bill of materials, cabling schedule, rack "
          "elevations and firewall handover all take site filters and per-site sections."),
       (4,"Comments scope to their tab, so a note on the branch design doesn't surface on the "
          "data centre."),
       (1,"The old model was one canvas per project, and a separate file per site. Which is how two sites end up claiming the same address range and nobody notices until they're cabled together."),
       (2,"Tabs behave like a browser's. The Overview stays pinned on the left, the sites sit beside it, and the whole project is one document rather than a folder of them."),
       (2,'Declaring connectivity on the Overview rather than on each site is what makes the joined graph possible. A WAN link has exactly one definition, and both ends mirror it.'),
       (3,'Island sites are the finding worth having. A site that looks perfectly correct on its own tab, with no actual path back to anything — invisible on a single canvas, obvious on a joined graph.'),
       (3,'Per-site pool overlaps are the other one. Two sites, two clean designs, one address range claimed twice.'),
       (4,'Simulation and Looking Glass run over the joined graph too, so a path trace crosses site boundaries the way real traffic does.'),
       (5,'The result is that a thirty-site estate stays as reviewable as a single closet. Which is the only way multi-site design is actually maintainable.'),
       (5,TAG),
      ]),

 dict(slug='ep05-generate', title='Episode 5 — Config generation and validation',
      slots=[(BRAND,3.0),(VALIDATE,None),(CONFLICT,None),(AIARCH,None),(GREEN,4.5),(CLIOUT,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode five. This is the part that replaces the typing."),
       (1,"Validation runs continuously against the whole design. Address conflicts, VLAN "
          "mismatches, BGP peer gaps, spanning-tree problems, MTU inconsistencies, gateway "
          "redundancy, management reachability."),
       (2,"When something is wrong, it's specific. Not a warning — the two interfaces that "
          "collide, and where they are."),
       (2,"Address conflicts are the most expensive simple mistake in networking. They pass "
          "every syntax check, then take down two segments at once."),
       (3,"The AI Network Architect reviews the design as a whole. Single points of failure, "
          "and alignment with Cisco validated designs and Arista's AVD."),
       (3,"It tells you what to fix, and why it matters — before the design leaves the canvas."),
       (4,"Then the whole design goes green. Every check, on every device, in under two "
          "seconds."),
       (5,"And the output is production-ready per-vendor CLI. Named feature objects — access "
          "lists, prefix lists, route maps, QoS policies, flow monitors — carry "
          "reference-integrity validation and bind into BGP policy."),
       (5,"Every secret in that config references an encrypted vault. The design itself, and "
          "anything you share publicly, carries only the reference."),
       (1,'Generation is per-vendor and per-platform. IOS-XE, NX-OS, Arista EOS, ArubaOS-CX, PAN-OS, Silver Peak EdgeConnect — each one gets the syntax it actually speaks.'),
       (2,'Validation is continuous rather than a step you remember to run. The design is checked as you build it, and the findings point at devices, not line numbers.'),
       (3,"Capability-aware validation is worth dwelling on. If a platform can't render an interface option or a management setting, Netforge.ai omits it and flags it. It never invents a command to fill the gap."),
       (3,'That single rule is why the output loads. Most generators fail by being optimistic about what a platform supports.'),
       (4,"Structural findings come with it: single points of failure, and alignment with Cisco's validated designs and Arista's AVD reference."),
       (5,"Configured-but-uncabled switchports still generate config, so a branch design can seed user ports without pretending there's a laptop drawn on every one."),
       (5,'And what comes out is a complete per-device configuration — not a fragment you finish by hand.'),
       (6,TAG),
      ]),

 dict(slug='ep06-ipam', title='Episode 6 — IPAM and addressing',
      slots=[(BRAND,3.0),(ADDRESSING,None),(CONFLICT,None),(VALIDATE,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode six. Addressing is where designs quietly go wrong, so it gets its own "
          "console — on the canvas toolbar, under IPAM."),
       (1,"Define pools: supernets for loopbacks, for point-to-point links, for user VLANs. "
          "Then let the platform allocate from them."),
       (1,"SVIs, routed links and first-hop redundancy addresses are auto-assigned "
          "consistently, and every allocation is tracked back to the pool it came from."),
       (2,"Conflict detection runs across the entire design — including addresses somebody "
          "typed by hand, outside any pool."),
       (2,"Pool-based allocation makes conflicts structurally impossible for managed ranges. "
          "The overlap checker catches the hand-typed stragglers."),
       (3,"The practical advice from the guide: size per-site pools for growth. A slash "
          "twenty per site for user VLANs, a slash twenty-four of slash thirty-ones for "
          "point-to-point links."),
       (3,"The auto-assign helpers number redundancy groups and pair addresses consistently "
          "across a distribution pair — so the second switch matches the first."),
       (1,"Where to find it: the canvas toolbar, under IPAM. It's a console, not a field on a form."),
       (2,'Pools are the unit. A supernet for loopbacks, one for point-to-point links, one per site for user VLANs — sized deliberately, and allocated from automatically.'),
       (2,'Blueprint-generated blocks pin themselves, so re-running the wizard to add a site never renumbers a site that already exists. That property is what makes the addressing plan survive contact with a growing estate.'),
       (3,"Duplicate address detection runs design-wide, and it does not care whether the address came from a pool or from somebody's memory."),
       (3,'Management addressing is allocated the same way, with manual-override protection, so the out-of-band plan is as consistent as the production one.'),
       (4,'Subnet profiles per site kind — data, voice, servers, guest, management, transit, loopbacks — mean the same VLAN means the same thing at every site.'),
       (4,'And when you need to check something by hand, the free subnet calculator and CIDR aggregator are in the tools suite, no sign-in required.'),
       (4,TAG),
      ]),

 dict(slug='ep07-publish', title='Episode 7 — The publish workflow',
      slots=[(BRAND,3.0),(PREFLIGHT,None),(CLIOUT,None),(RACKBOM,None),(EXPORTS,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode seven. Publish is the finishing workflow. One action on the canvas toolbar "
          "walks the design through validation and produces every deliverable."),
       (1,"No hunting for separate buttons. Validation first, then the outputs."),
       (2,"Static configuration: complete per-device, per-vendor CLI for the whole design."),
       (3,"A cabling schedule — every link, with A-end and B-end device, port, media and "
          "speed, ready for the rack team."),
       (3,"A bill of materials: chassis, line cards, optics and cables, aggregated with "
          "quantities. The link speeds you chose on the canvas are what selected those optics."),
       (4,"And a design document — the drawing plus per-device summaries, for the hand-off "
          "package."),
       (4,"Or push toward deployment. Ansible-based, with credentials taken from the shared "
          "credential store — never embedded in the design."),
       (4,"Publishing defaults to private. Choose public and it becomes a community template — "
          "but the scrubber runs first, stripping secrets before anything leaves your "
          "organization."),
       (1,"Publish is deliberately one action. The failure mode it's designed against is a half-published design — configs generated on Tuesday, cabling schedule exported on Thursday, and the two no longer describing the same network."),
       (2,'Everything below comes from the same validated design, at the same moment.'),
       (2,'The dry run is not a formality. It orders operations — core, then distribution, then access — and creates the rollback point before anything is pushed.'),
       (3,'The configuration is per-device and per-vendor, complete, with vault-backed secrets rendered in place and marked.'),
       (4,'Rack elevations show what goes where, and the bill of materials aggregates chassis, line cards, optics and cables with quantities — sized from the link speeds you chose when you drew the cabling.'),
       (5,'On a multi-site project every one of these takes a site filter, so the branch team gets the branch pack and not the whole estate.'),
       (5,'Deploy is Ansible-based, and credentials come from the shared store at deploy time. They are never part of the design, and never part of a share.'),
       (5,TAG),
      ]),

 dict(slug='ep08-drift', title='Episode 8 — Drift and as-built',
      slots=[(BRAND,3.0),(CONFIGCMP,None),(WATCHTOWER,None),(BRIDGE,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode eight. Deploying the design is not the end. The network starts drifting "
          "the moment someone logs into a device."),
       (1,"So Netforge.ai closes the loop. The Drift action compares each device's live "
          "running-config against the config it last deployed — the intended baseline."),
       (1,"Every device comes back in one of four states: in sync, drifted, unreachable, or "
          "no baseline. Drifted gives you both a line diff and a structural one, and badges "
          "the affected node on the canvas."),
       (2,"Running-configs are secret-scrubbed before any diff is stored. Nothing sensitive "
          "is retained to make the comparison."),
       (2,"Admins can schedule recurring checks, with alerts to the owner contact through the "
          "same channels Watchtower uses."),
       (3,"And when reality has already moved on, the Import wizard has an as-built mode: it "
          "pulls a live device and its LLDP neighbours through the credential vault, then "
          "reconciles what it found — matched, new, and missing — against your design."),
       (3,"The apply is additive and undoable. You review before anything changes."),
       (1,'Drift is the problem nobody schedules for. The design is correct on the day it ships and slowly stops being true afterwards.'),
       (2,"Config Compare is the manual version, and it's free in the tools suite. Paste, upload or drop two configs and the panes become a live comparison — no compare button, and nothing leaves the browser."),
       (2,'Green is identical. Yellow is the same line with minor edits, changed words highlighted inside the row. Red is a line whose opening has no counterpart at all.'),
       (2,"Block-aware sorting cancels out reordering while keeping interface, BGP, IP SLA and policy-map groups intact — so a config that was merely rearranged doesn't read as rewritten."),
       (2,'Changes are classified major or minor, fail-closed: only known-cosmetic lines are minor. Ignore rules cover whitespace, case, comments and volatile lines, and replacement rules let a renamed hostname compare as equal.'),
       (3,'The automated version is the Drift action, and the difference is the baseline: it compares against what Netforge.ai actually deployed, not against another file somebody kept.'),
       (3,'Scheduled checks run recurring comparisons and alert the owner contact, so drift surfaces on its own rather than during the next incident.'),
       (4,'That is the closed loop. Design, deploy, verify, and keep verifying.'),
       (4,TAG),
      ]),

 dict(slug='ep09-fabric-cloud', title='Episode 9 — Fabric, AVD and Azure',
      slots=[(BRAND,3.0),(FABRIC,None),(CLIOUT,None),(CLOUD,None),(EXPORTS,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode nine. Two specialities that would otherwise be separate tools."),
       (1,"First, fabrics. The AVD wizard builds Arista EVPN-VXLAN spine-leaf: architect, "
          "validate, deploy — with full validation parity and bill-of-materials integration."),
       (2,"The output is Arista's own AVD Ansible package, not a generic approximation. It "
          "drops into the workflow your fabric team already runs."),
       (3,"Second, cloud. Azure resources are real nodes on the canvas — virtual networks, "
          "subnets, security groups, gateways — with synchronized Terraform."),
       (3,"You can design them from scratch, or run the subscription import wizard and "
          "reverse-engineer an environment that already exists onto the canvas."),
       (3,"Then push it back as Terraform, and schedule drift checks against it — the same "
          "closed loop as the physical estate."),
       (4,"One canvas covers the fabric, the campus, the branch and the cloud. Which means "
          "one bill of materials, one set of documentation, and one place the truth lives."),
       (1,"Fabrics and cloud both tend to live outside the diagram — in a wizard somewhere, or in somebody's Terraform repository. Both belong on the same canvas as everything else."),
       (2,"The fabric wizard follows Arista's own model: architect, validate, deploy. Spines, leaves, the underlay, the overlay — with the same validation the rest of the design gets, and the devices counted in the same bill of materials."),
       (2,'Scale it on the canvas and the addressing, the BGP numbering and the port assignments follow. You are not maintaining a spreadsheet beside the drawing.'),
       (3,'On the cloud side, the import wizard walks a live Azure subscription and lays it out as real nodes — virtual networks, subnets, security groups, gateways.'),
       (3,"From there it's an ordinary design. Change it on the canvas, and the Terraform stays synchronized with what you drew."),
       (4,"Scheduled drift checks run against the cloud estate as well, so an environment changed in the portal doesn't quietly diverge from the code."),
       (4,'Ansible-based device management ties the two halves together — the physical estate and the cloud one, managed from the same design.'),
       (5,TAG),
      ]),

 dict(slug='ep10-tools-access', title='Episode 10 — Tools, monitoring and access',
      slots=[(BRAND,3.0),(TOOLS,None),(CONFIGCMP,None),(LOOKINGGLASS,None),(WATCHTOWER,None),(ENDCARD,5.0)],
      lines=[
       (1,"Episode ten, and the parts that surround the designer."),
       (1,"Nineteen free network tools, no sign-in: diagnostics, addressing, DNS, security and "
          "monitoring — the bookmark folder every engineer keeps, in one place."),
       (2,"Config Compare is the one to know. Drop in two configs, route tables, or any text "
          "dumps, and the panes become a live side-by-side comparison. There's no compare "
          "button, and nothing leaves your browser."),
       (2,"Green is identical. Yellow is the same line with minor edits, with the changed "
          "words highlighted inside the row. Red is a line with no counterpart at all."),
       (2,"Block-aware sorting cancels out reordering while keeping interface, BGP, IP SLA and "
          "policy-map groups intact. Ignore rules cover whitespace, case, comments and "
          "volatile lines — and your own regular expressions."),
       (3,"Looking Glass traces a path hop by hop and confirms it matches the design."),
       (4,"Watchtower monitors uptime with multi-channel alerting, and watches the platform "
          "itself from outside."),
       (4,"Around all of it: roles enforced end to end — owner, admin, editor, viewer, "
          "observer — with two-factor authentication required for privileged accounts, and "
          "every device secret held in an encrypted per-organization vault."),
       (1,'These are the parts you meet before you ever draw anything, and the ones you rely on long after.'),
       (2,'The tools cover diagnostics — DNS lookup, ping, traceroute, port check, speed test, Config Compare. Addressing — subnet calculator, IPv6 tools, CIDR aggregator, IP geolocation, MAC lookup. DNS and domains. Security and web checks.'),
       (3,'Config Compare exports as a unified diff or a standalone HTML report, so a change review can be attached to a ticket rather than screenshotted.'),
       (4,"Watchtower's channels are reused by the drift scheduler, so operational alerting is one system rather than two."),
       (5,"On access: new sign-ups now start as editor rather than read-only, so a teammate can build immediately. Changing anyone's role is reserved for the owner."),
       (5,"There's a lab editor role that carries everything an editor has plus permission to create live labs, and the grant travels in the session token."),
       (5,'Role changes apply on the next page load or tab focus — no re-login. Two-factor enrolment is enforced on every request, so a promotion into a privileged role takes effect immediately, not at the next sign-in.'),
       (5,'Collaboration runs on co-edit share links with live multi-user editing, and anything published publicly goes through the scrubber first.'),
       (5,TAG),
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

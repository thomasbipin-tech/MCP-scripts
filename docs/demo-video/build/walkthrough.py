#!/usr/bin/env python3
"""The full product walkthrough — one continuous piece, ~14 minutes.

Intent: someone who watches this needs nothing explained afterwards. It covers what the
product is, what it solves, how you actually use it end to end, and where it's going.

Everything factual is taken from netforge.ai's own documentation (22 pages plus a dated
release history). UI locations are quoted as the docs give them, so a viewer can follow
along in the product. The one section that is NOT sourced is the roadmap: the docs record
what shipped, not what's planned, so that chapter is written as a clearly-scoped
"recently shipped" summary with a marked slot for real roadmap copy.

  python3 walkthrough.py           # VO + timeline_walkthrough.json
  python3 walkthrough.py --retime  # re-time from existing vo_walkthrough/
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import series
from series import (BRAND, ENDCARD, PANES, BRIDGE, REFRAME, DRAG, PORTS, FABRIC,
                    VALIDATE, CONFLICT, AIARCH, GREEN, CLIOUT, EXPORTS, CLOUD, OUTCOME,
                    BLUEPRINT, MULTISITE, TEMPLATES, CONFIGCMP, ADDRESSING, WATCHTOWER,
                    TOOLS, PREFLIGHT, LOOKINGGLASS, RACKBOM)

WALKTHROUGH = dict(
  slug='walkthrough', title='Netforge.ai — full walkthrough',
  slots=[
    (BRAND,3.0),        # 0
    (PANES,None),       # 1   the problem
    (BRIDGE,None),      # 2   what drift looks like
    (REFRAME,None),     # 3   the idea
    (TOOLS,None),       # 4   getting started / account / roles
    (TEMPLATES,None),   # 5   templates
    (DRAG,None),        # 6   canvas: placing
    (PORTS,None),       # 7   canvas: cabling + link editor
    (CLIOUT,None),      # 8   device configuration
    (FABRIC,None),      # 9   scale / fabric
    (BLUEPRINT,None),   # 10  blueprint wizard
    (MULTISITE,None),   # 11  multi-canvas
    (ADDRESSING,None),  # 12  IPAM
    (VALIDATE,None),    # 13  validation
    (CONFLICT,None),    # 14  a real finding
    (AIARCH,None),      # 15  AI architect
    (GREEN,4.5),        # 16  green
    (PREFLIGHT,None),   # 17  publish
    (RACKBOM,None),     # 18  deliverables
    (EXPORTS,None),     # 19  export suite
    (LOOKINGGLASS,None),# 20  verify
    (CONFIGCMP,None),   # 21  drift / config compare
    (WATCHTOWER,None),  # 22  monitoring
    (CLOUD,None),       # 23  azure
    (OUTCOME,None),     # 24  what's shipped / what's next
    (ENDCARD,6.0),      # 25
  ],
  lines=[
    # ---------------- what this is ----------------
    (1,"This is a complete walkthrough of Netforge.ai. By the end you'll know what it is, "
       "what problem it solves, how to use it from an empty canvas to a deployed network, "
       "and where it's heading."),
    (1,"Start with the problem, because the product only makes sense against it."),
    (1,"Every enterprise network begins as a drawing. A diagram in Visio, a whiteboard "
       "photo, a reference design. That drawing is correct."),
    (1,"Then somebody translates it, by hand, into thousands of lines of configuration "
       "across a dozen different vendors — each with its own syntax for the same idea."),
    (2,"That translation is where outages come from. Not a wrong design. A transposed VLAN, "
       "a missing BGP neighbour, a duplicated address, a native VLAN nobody checked."),
    (2,"And once it's deployed, the drawing stops being true. Someone logs into a device at "
       "two in the morning, fixes something, and never updates the diagram."),
    (2,"Months later the drawing and the devices disagree, and nobody knows which one to "
       "trust."),
    (3,"Netforge.ai's answer is to make the drawing the source of truth. Not a picture of "
       "the network — the thing the network is generated from, validated against, "
       "documented from, and continuously compared to."),
    (3,"Design, configure, validate, deploy, and verify. One canvas, one truth. Here's how "
       "that works in practice."),

    # ---------------- getting started ----------------
    (4,"First, getting in. Register at netforge.ai with a valid email — that address is your "
       "username. A verification link arrives immediately and the account activates when you "
       "click it. If it hasn't shown up, check junk; there's a resend on the sign-in screen."),
    (4,"Passwords follow a compliance policy: at least twelve characters, upper and lower "
       "case, a number and a special character, and you can't reuse recent ones."),
    (4,"Two-factor authentication is available to everyone from your profile, and required "
       "for owner, admin and lab-editor accounts. Enrolment is enforced on every request, so "
       "a promotion into a privileged role takes effect immediately rather than at next "
       "sign-in."),
    (4,"Roles run owner, admin, editor, viewer and observer. New sign-ups now start as "
       "editor, so a teammate can build straight away. Only the owner changes anyone's role. "
       "Viewers get a genuinely read-only canvas."),
    (4,"The documentation has four guided tracks depending on why you're here: pre-sales and "
       "design, professional services, enterprise and NetOps, or admin and owner. Each is an "
       "ordered path through exactly the pages that role needs."),

    # ---------------- templates + canvas ----------------
    (5,"You rarely start from nothing. The Templates page carries featured reference designs "
       "and community-shared ones — leaf-spine fabrics, branch SD-WAN, campus three-tier, "
       "collapsed core, hybrid Azure."),
    (5,"There's also an Enterprise WAN family: a thirty-office overview with seventy devices, "
       "a data centre and a branch office, as parameterized blueprints where you set a "
       "company code and an office count."),
    (5,"Open any card to preview it, or use it as your starting point. And if you already "
       "have drawings, the Import wizard reads a Visio topology and flags the generic "
       "elements it couldn't map, so gaps are explicit rather than silent."),
    (6,"On the canvas, the device catalog is the left sidebar, grouped by vendor and family. "
       "Click a device to drop it at the next free spot, or drag it exactly where you want."),
    (6,"The sidebar minimizes to a thin rail — hover to expand, or pin it open. Search filters "
       "across every vendor at once, which matters when the catalog spans Cisco, Arista, "
       "Aruba, Palo Alto, Silver Peak and Lantronix."),
    (6,"Not everything is a device. Internet, MPLS and VPN clouds draw as actual cloud "
       "outlines — pure connection points for terminating WAN links, with no ports and no "
       "config of their own."),
    (7,"To cable, drag from one connection point to another. The points zoom on hover so "
       "they're easy to hit on a dense drawing."),
    (7,"The Link Editor then assigns real interfaces on both ends, chosen from each device's "
       "actual port inventory as derived from its model. You pick the media — copper, SFP+, "
       "QSFP, DAC — and the speed, from one gigabit to four hundred."),
    (7,"That speed renders on the drawing and drives optic selection in the bill of "
       "materials. Media and port-cage mismatches are flagged while you draw, not after."),

    # ---------------- device config ----------------
    (8,"Select a device and the properties panel opens: interfaces, layer two and three, "
       "features, and the management plane."),
    (8,"Interfaces take descriptions, addressing, MTU and admin state. Routed parents take "
       "dot1q sub-interfaces with tag, address and VRF. Loopbacks are configurable on every "
       "layer-three device, with design-wide duplicate checking."),
    (8,"First-hop redundancy is thorough: HSRP and VRRP with preempt and delays, interface "
       "and object tracking with decrement, timers, version, virtual MAC and secondary "
       "virtual addresses. Port-channels carry MTU, speed, negotiation, access lists and "
       "spanning-tree edge."),
    (8,"The management plane covers AAA with timeout, retransmit, VRF and source interface — "
       "and a Test AAA action — plus NTP with authentication, console and VTY hardening, "
       "CDP and LLDP, NetFlow, and static routes with IP SLA tracking."),
    (8,"Site Areas hold a shared management plane that every device in a site inherits, with "
       "per-device override where one box genuinely differs."),
    (8,"Console and out-of-band management is first class. Every device gets a console port "
       "and its real dedicated management interface. Drag a device onto a Lantronix terminal "
       "server and the console run cables itself."),
    (8,"And every secret — local users, enable, TACACS, RADIUS, SNMP, NTP keys — references "
       "an encrypted per-organization vault. The design carries the reference; the generated "
       "config renders the real value and marks it."),
    (9,"The same canvas scales from a branch closet to a full Arista leaf-spine VXLAN EVPN "
       "fabric. The AVD wizard follows Arista's own model — architect, validate, deploy — "
       "with full validation parity and BOM integration."),

    # ---------------- blueprint + multi-site + ipam ----------------
    (10,"For anything bigger than one site, start with the Blueprint wizard. Tell it how many "
        "data centres, campuses and branches, and it builds the estate — one tab per site, "
        "wired through a WAN overview."),
    (10,"Addressing is flexible: supernets from a slash eight to a slash sixteen, with "
        "right-sized per-site blocks — roughly a slash twenty for a data centre or campus, a "
        "slash twenty-one for a branch — packed automatically and overridable per site."),
    (10,"Generated blocks pin themselves, so re-running the wizard to add sites never "
        "renumbers the sites you already deployed."),
    (10,"Each site kind gets an editable subnet profile — data, voice, servers, guest, "
        "management, transit, loopbacks — which drives the VLANs, the gateway SVIs, DHCP "
        "relay and voice VLANs on access ports."),
    (11,"Multi-site projects span canvases as tabs, like a browser, with the WAN Overview "
        "pinned. Site blocks on the Overview jump to their tab."),
    (11,"Inter-site connectivity is declared once on the Overview and mirrored on each site "
        "tab as a WAN stub cloud. Validation then runs over the joined graph."),
    (11,"That's what catches island sites with no path back, unmatched WAN identifiers, "
        "Overview-to-config mismatches, and address pool overlaps between sites. Click a "
        "finding and it switches you to the tab that owns it."),
    (12,"Addressing has its own console on the canvas toolbar: IPAM. Define pools — "
        "loopbacks, point-to-points, user VLANs — and let the platform allocate from them."),
    (12,"SVIs, routed links and first-hop redundancy addresses are auto-assigned "
        "consistently, and every allocation is tracked back to its pool."),
    (12,"Conflict detection runs across the whole design, including addresses typed by hand "
        "outside any pool. Pool-based allocation makes conflicts structurally impossible for "
        "managed ranges; the overlap checker catches the stragglers."),

    # ---------------- validate ----------------
    (13,"Validation is continuous, not a button you remember to press. It checks address "
        "conflicts, VLAN consistency, trunk and native VLAN matching, BGP reciprocity and AS "
        "consistency, spanning-tree root placement, MTU, gateway redundancy and management "
        "reachability."),
    (14,"When something is wrong it is specific: the two interfaces that collide, on which "
        "devices, and what it will break. Address conflicts are the most expensive simple "
        "mistake in networking — they pass every syntax check and then take down two "
        "segments at once."),
    (14,"Capability-aware validation is the rule that makes the output trustworthy: if a "
        "platform can't render a setting, Netforge.ai omits it and flags it. It never invents "
        "a command to fill a gap."),
    (15,"On top of the mechanical checks, the AI Network Architect reviews the design as a "
        "whole — single points of failure, and alignment with Cisco validated designs and "
        "Arista's AVD — and tells you what to fix and why it matters."),
    (16,"When it's clean, the whole design goes green. Every check, every device, in under "
        "two seconds."),

    # ---------------- publish ----------------
    (17,"Then Publish. It's deliberately one action on the canvas toolbar, because the "
        "failure it's designed against is a half-published design — configs generated "
        "Tuesday, cabling exported Thursday, describing two different networks."),
    (17,"Publish walks the design through validation and produces everything at once. The "
        "dry run orders operations — core, then distribution, then access — and creates the "
        "rollback point before anything is pushed."),
    (18,"What you get: complete per-device, per-vendor CLI for the whole design. A cabling "
        "schedule with A-end and B-end device, port, media and speed, ready for the rack "
        "team. Rack elevations showing what goes where."),
    (18,"A bill of materials aggregating chassis, line cards, optics and cables with "
        "quantities — sized from the link speeds you chose when you drew the cabling."),
    (19,"And a design document: the drawing plus per-device summaries for the hand-off pack. "
        "On a multi-site project each of these takes a site filter, so the branch team gets "
        "the branch pack rather than the whole estate."),
    (19,"Or push toward deployment. It's Ansible-based, and credentials come from the shared "
        "store at deploy time — never embedded in the design and never part of a share."),
    (19,"Publishing defaults to private. Choosing public shares the design as a community "
        "template, and the scrubber runs first, stripping secrets before anything leaves "
        "your organization."),

    # ---------------- verify + operate ----------------
    (20,"After deployment, Looking Glass traces the path hop by hop and confirms it matches "
        "the design. On a multi-site project it runs over the joined graph, so a trace "
        "crosses site boundaries the way real traffic does."),
    (21,"Then the loop closes. The Drift action compares each device's live running-config "
        "against the config Netforge.ai last deployed for it — the intended baseline, not "
        "another file somebody kept."),
    (21,"Every device reports in sync, drifted, unreachable, or no baseline. Drifted gives "
        "you a line diff and a structural one, and badges the node on the canvas. "
        "Running-configs are secret-scrubbed before any diff is stored."),
    (21,"The manual equivalent is Config Compare, free in the tools suite. Drop in two "
        "configs and the panes become a live comparison — no compare button, nothing leaves "
        "your browser."),
    (21,"Green is identical, yellow is the same line with minor edits, red is a line with no "
        "counterpart. Block-aware sorting cancels out reordering, changes are classified "
        "major or minor fail-closed, and it exports as a unified diff or an HTML report."),
    (22,"Watchtower monitors uptime with multi-channel alerting, and watches the platform "
        "itself from outside. The drift scheduler reuses those same channels, so operational "
        "alerting is one system rather than two."),
    (22,"And when reality has already moved on, the Import wizard's as-built mode pulls a "
        "live device and its LLDP neighbours through the credential vault and reconciles "
        "matched, new and missing against your design. The apply is additive and undoable."),
    (23,"Cloud is the same story. Azure resources are real nodes — virtual networks, subnets, "
        "security groups, gateways — with synchronized Terraform. Design them from scratch, "
        "or run the subscription import and reverse-engineer what already exists."),
    (23,"Then push it back as Terraform and schedule drift checks against it. The same closed "
        "loop as the physical estate, in one canvas and one bill of materials."),

    # ---------------- where it's going ----------------
    (24,"So that's the product: design on a canvas, configure with real per-vendor depth, "
        "validate continuously, publish once, deploy safely, and keep verifying afterwards."),
    (24,"As for where it's going — the most recent releases show the direction. Config "
        "Compare landed in the toolbox. The Blueprint wizard reached version two with "
        "flexible addressing and subnet profiles. Projects became multi-canvas with site "
        "tabs and a joined-graph validator."),
    (24,"Drift became closed-loop against a deployed baseline, with as-built import. The "
        "credential vault moved every secret out of designs. Two-factor became mandatory for "
        "privileged roles, and a lab-editor role arrived for live labs."),
    (24,"The pattern is consistent: less retyping, more verification, and a shorter distance "
        "between the drawing and the running network."),
    (25,"Netforge.ai. From sketch to spine."),
  ])

if __name__ == '__main__':
    series.EPISODES = [WALKTHROUGH]
    retime = '--retime' in sys.argv
    d = series.build(WALKTHROUGH, do_synth=not retime)
    print(f"\n  walkthrough: {d/60:.1f} min")

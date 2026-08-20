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
                    ACCOUNT, ROLES, DEVPROPS, CABLESCHED, EXPORTFMT, DESIGNDOC,
                    DRIFTDASH, DEPLOYRUN, SITEAREAS, CONSOLEOOB, VAULT, MGMTPLANE,
                    VALIDATE, CONFLICT, AIARCH, GREEN, CLIOUT, EXPORTS, CLOUD, OUTCOME,
                    BLUEPRINT, MULTISITE, TEMPLATES, CONFIGCMP, ADDRESSING, WATCHTOWER,
                    TOOLS, PREFLIGHT, LOOKINGGLASS, RACKBOM, ASBUILT,
                    AZDESIGNER, IACDEPLOY, FWSTUDIO, FWWHATIF, LGBGP, BLUEPRINTPAGE,
                    WHATSNEW)

WALKTHROUGH = dict(
  slug='walkthrough', title='Netforge.ai — full walkthrough',
  slots=[
    (BRAND,3.0),          # 0
    (PANES,None),         # 1  the problem
    (BRIDGE,None),        # 2  what drift looks like
    (REFRAME,None),       # 3  the idea
    (ACCOUNT,None),       # 4  sign up, verify, 2FA
    (ROLES,None),         # 5  who can do what
    (TEMPLATES,None),     # 6  templates -- 28 designs / 8 categories
    (DRAG,None),          # 7  catalog / placing
    (PORTS,None),         # 8  cabling / link editor
    (DEVPROPS,None),      # 9  interfaces, sub-ints, loopbacks, FHRP
    (MGMTPLANE,None),     # 10 AAA / NTP / logging / SSH
    (SITEAREAS,None),     # 11 site inheritance
    (CONSOLEOOB,None),    # 12 console + OOB
    (VAULT,None),         # 13 credential vault
    (FABRIC,None),        # 14 scale / AVD fabric
    (BLUEPRINT,None),     # 15 blueprint wizard
    (MULTISITE,None),     # 16 site tabs
    (ADDRESSING,None),    # 17 IPAM
    (VALIDATE,None),      # 18 validation
    (CONFLICT,None),      # 19 a real finding
    (AIARCH,None),        # 20 AI review
    (GREEN,4.5),          # 21 green
    (PREFLIGHT,None),     # 22 publish
    (CLIOUT,None),        # 23 the generated config
    (CABLESCHED,None),    # 24 cable schedule
    (RACKBOM,None),       # 25 rack + BOM + panels
    (DESIGNDOC,None),     # 26 design document
    (EXPORTFMT,None),     # 27 the six deliverables
    (BLUEPRINTPAGE,None), # 28 public page + embed + last-verified
    (DEPLOYRUN,None),     # 29 deploy (per-collection Ansible)
    (LOOKINGGLASS,None),  # 30 verify the path
    (DRIFTDASH,None),     # 31 drift states
    (CONFIGCMP,None),     # 32 config compare
    (ASBUILT,None),       # 33 as-built import
    (FWSTUDIO,None),      # 34 firewall studio + dead rules
    (FWWHATIF,None),      # 35 what-if
    (WATCHTOWER,None),    # 36 uptime + BGP monitors
    (LGBGP,None),         # 37 looking glass
    (CLOUD,None),         # 38 azure on canvas
    (AZDESIGNER,None),    # 39 the Azure Designer drawer
    (IACDEPLOY,None),     # 40 terraform / pulumi + preflight
    (OUTCOME,None),       # 41 close / summary + what stays free
    (WHATSNEW,None),      # 42 the release timeline / direction
    (ENDCARD,6.0),        # 43
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
    # Sign-up detail was three lines and held this screen for 39s. Nobody watching a
    # product walkthrough needs the password policy read to them -- one line, then move on.
    (4,"First, create an account: your email is your username, a verification link activates "
       "it, and two-factor is required for the privileged roles. That is the whole of it — "
       "the interesting part is what you do next."),
    (5,"Roles run owner, admin, editor, viewer and observer. New sign-ups now start as "
       "editor, so a teammate can build straight away. Only the owner changes anyone's role. "
       "Viewers get a genuinely read-only canvas."),

    # ---------------- templates + canvas ----------------
    (6,"You rarely start from nothing. The Templates page now carries twenty-eight reference "
       "designs in eight categories — leaf-spine fabrics, branch SD-WAN, campus three-tier, "
       "collapsed core, a nine-design Azure family, layer-two data-centre interconnect, "
       "low-latency trading floors, and Clos fabrics sized for AI clusters."),
    (6,"There's also an Enterprise WAN family, topped by a thirty-office estate — a hundred "
       "and eight devices across nearly three hundred links — plus its data centre and "
       "branch designs. Every card opens on the canvas with no account needed."),
    (6,"Open any card to preview it, or use it as your starting point. And if you already "
       "have drawings, the Import wizard reads a Visio topology and flags the generic "
       "elements it couldn't map, so gaps are explicit rather than silent."),
    (7,"On the canvas, the device catalog is the left sidebar, grouped by vendor and family. "
       "Click a device to drop it at the next free spot, or drag it exactly where you want."),
    (7,"The sidebar minimizes to a thin rail — hover to expand, or pin it open. Search filters "
       "across every vendor at once, which matters when the catalog spans Cisco, Arista, "
       "Aruba, Palo Alto, Silver Peak and Lantronix."),
    (7,"Not everything is a device. Internet, MPLS and VPN clouds draw as actual cloud "
       "outlines — pure connection points for terminating WAN links, with no ports and no "
       "config of their own."),
    (8,"To cable, drag from one connection point to another. The points zoom on hover so "
       "they're easy to hit on a dense drawing."),
    (8,"The Link Editor then assigns real interfaces on both ends, chosen from each device's "
       "actual port inventory as derived from its model. You pick the media — copper, SFP+, "
       "QSFP, DAC — and the speed, from one gigabit to four hundred."),
    (8,"That speed renders on the drawing and drives optic selection in the bill of "
       "materials. Media and port-cage mismatches are flagged while you draw, not after."),

    # ---------------- device config ----------------
    (9,"Select a device and the properties panel opens: interfaces, layer two and three, "
       "features, and the management plane."),
    (9,"Interfaces take descriptions, addressing, MTU and admin state. Routed parents take "
       "dot1q sub-interfaces with tag, address and VRF. Loopbacks are configurable on every "
       "layer-three device, with design-wide duplicate checking."),
    (9,"First-hop redundancy is thorough: HSRP and VRRP with preempt and delays, interface "
       "and object tracking with decrement, timers, version, virtual MAC and secondary "
       "virtual addresses. Port-channels carry MTU, speed, negotiation, access lists and "
       "spanning-tree edge."),
    (10,"The management plane covers AAA with timeout, retransmit, VRF and source interface — "
       "and a Test AAA action — plus NTP with authentication, console and VTY hardening, "
       "CDP and LLDP, NetFlow, and static routes with IP SLA tracking."),
    (11,"Site Areas hold a shared management plane that every device in a site inherits, with "
       "per-device override where one box genuinely differs."),
    (12,"Console and out-of-band management is first class. Every device gets a console port "
       "and its real dedicated management interface. Drag a device onto a Lantronix terminal "
       "server and the console run cables itself."),
    (13,"And every secret — local users, enable, TACACS, RADIUS, SNMP, NTP keys — references "
       "an encrypted per-organization vault. The design carries the reference; the generated "
       "config renders the real value and marks it."),
    (14,"The same canvas scales from a branch closet to a full Arista leaf-spine VXLAN EVPN "
       "fabric. The AVD wizard follows Arista's own model — architect, validate, deploy — "
       "with full validation parity and BOM integration."),

    # ---------------- blueprint + multi-site + ipam ----------------
    (15,"For anything bigger than one site, start with the Blueprint wizard. Tell it how many "
        "data centres, campuses and branches, and it builds the estate — one tab per site, "
        "wired through a WAN overview."),
    (15,"Addressing is flexible: supernets from a slash eight to a slash sixteen, with "
        "right-sized per-site blocks — roughly a slash twenty for a data centre or campus, a "
        "slash twenty-one for a branch — packed automatically and overridable per site."),
    (15,"Generated blocks pin themselves, so re-running the wizard to add sites never "
        "renumbers the sites you already deployed."),
    (15,"Each site kind gets an editable subnet profile — data, voice, servers, guest, "
        "management, transit, loopbacks — which drives the VLANs, the gateway SVIs, DHCP "
        "relay and voice VLANs on access ports."),
    (16,"Multi-site projects span canvases as tabs, like a browser, with the WAN Overview "
        "pinned. Site blocks on the Overview jump to their tab."),
    (16,"Inter-site connectivity is declared once on the Overview and mirrored on each site "
        "tab as a WAN stub cloud. Validation then runs over the joined graph."),
    (16,"That's what catches island sites with no path back, unmatched WAN identifiers, "
        "Overview-to-config mismatches, and address pool overlaps between sites. Click a "
        "finding and it switches you to the tab that owns it."),
    (17,"Addressing has its own console on the canvas toolbar: IPAM. Define pools — "
        "loopbacks, point-to-points, user VLANs — and let the platform allocate from them."),
    (17,"SVIs, routed links and first-hop redundancy addresses are auto-assigned "
        "consistently, and every allocation is tracked back to its pool."),
    (17,"Conflict detection runs across the whole design, including addresses typed by hand "
        "outside any pool. Pool-based allocation makes conflicts structurally impossible for "
        "managed ranges; the overlap checker catches the stragglers."),

    # ---------------- validate ----------------
    (18,"Validation is continuous, not a button you remember to press. It checks address "
        "conflicts, VLAN consistency, trunk and native VLAN matching, BGP reciprocity and AS "
        "consistency, spanning-tree root placement, MTU, gateway redundancy and management "
        "reachability."),
    (19,"When something is wrong it is specific: the two interfaces that collide, on which "
        "devices, and what it will break. Address conflicts are the most expensive simple "
        "mistake in networking — they pass every syntax check and then take down two "
        "segments at once."),
    (19,"Capability-aware validation is the rule that makes the output trustworthy: if a "
        "platform can't render a setting, Netforge.ai omits it and flags it. It never invents "
        "a command to fill a gap."),
    (20,"On top of the mechanical checks, the AI Network Architect reviews the design as a "
        "whole — single points of failure, and alignment with Cisco validated designs and "
        "Arista's AVD — and tells you what to fix and why it matters."),
    (21,"When it's clean, the whole design goes green. Every check, every device, in under "
        "two seconds."),

    # ---------------- publish ----------------
    (22,"Then Publish. It's deliberately one action on the canvas toolbar, because the "
        "failure it's designed against is a half-published design — configs generated "
        "Tuesday, cabling exported Thursday, describing two different networks."),
    (22,"Publish walks the design through validation and produces everything at once. The "
        "dry run orders operations — core, then distribution, then access — and creates the "
        "rollback point before anything is pushed."),
    (23,"What you get: complete per-device, per-vendor CLI for the whole design."),
    (24,"A cabling schedule — every link, with A-end and B-end device, port, media and speed. "
        "One row per run, ready for the rack team."),
    (25,"Rack elevations showing what goes where — including the passive hardware a real "
        "rack needs. Every switch with copper access ports gets its matching patch panel "
        "seated above it, and carrier fiber terminates on an LC panel, drawn dashed so "
        "passive reads at a glance."),
    (25,"A bill of materials aggregating chassis, line cards, optics and cables with "
        "quantities — sized from the link speeds you chose when you drew the cabling. A new "
        "panels section prices the hardware nobody remembers until install day, and the "
        "layout itself saves: rack names and positions are durable, and Apply is one "
        "undoable step."),
    (26,"And a design document: the drawing plus per-device summaries for the hand-off pack."),
    (27,"Six deliverables, all generated from the same validated canvas at the same moment. On "
        "a multi-site project each takes a site filter, so the branch team gets the branch "
        "pack rather than the whole estate."),
    (28,"A design published publicly now gets a permanent page of its own — an interactive "
        "viewer, the inventory, and a copy-paste embed that keeps a wiki or a design doc in "
        "sync with the published design, instead of rotting the way a screenshot does. The "
        "scrubber runs first, and the address is minted once, so republishing never breaks "
        "a link somebody shared."),
    (28,"Each design also carries a last-verified date, deliberately separate from last "
        "edited — because editing a diagram is not the same as vouching for it. One click "
        "marks it verified, and the gallery shows the freshness at a glance."),
    (29,"Or push toward deployment. It's Ansible-based, and credentials come from the shared "
        "store at deploy time — never embedded in the design and never part of a share."),
    (29,"The bundle now writes host variables in the schema each collection actually "
        "accepts — Cisco IOS, Arista EOS and Aruba CX genuinely disagree — and any intent "
        "with no module to land in is listed in comments at the top of the playbook, rather "
        "than emitted as variables that would fail on the first run."),
    (27,"Publishing defaults to private. Choosing public shares the design as a community "
        "template, and the scrubber runs first, stripping secrets before anything leaves "
        "your organization."),

    # ---------------- verify + operate ----------------
    (30,"After deployment, Looking Glass traces the path hop by hop and confirms it matches "
        "the design. On a multi-site project it runs over the joined graph, so a trace "
        "crosses site boundaries the way real traffic does."),
    (31,"Then the loop closes. The Drift action compares each device's live running-config "
        "against the config Netforge.ai last deployed for it — the intended baseline, not "
        "another file somebody kept."),
    (31,"Every device reports in sync, drifted, unreachable, or no baseline. Drifted gives "
        "you a line diff and a structural one, and badges the node on the canvas. "
        "Running-configs are secret-scrubbed before any diff is stored."),
    (32,"The manual equivalent is Config Compare, free in the tools suite. Drop in two "
        "configs and the panes become a live comparison — no compare button, nothing leaves "
        "your browser."),
    (32,"Green is identical, yellow is the same line with minor edits, red is a line with no "
        "counterpart. Block-aware sorting cancels out reordering, changes are classified "
        "major or minor fail-closed, and it exports as a unified diff or an HTML report."),
    (34,"Firewalls get their own studio: zones, address objects, NAT and the security "
        "policy, edited as a policy rather than as lines. And it reads receipts — drop your "
        "firewall's own hit-count export onto the policy, and every enabled rule that has "
        "never matched is listed as a removal candidate. Never means never, not a date."),
    (34,"The file is read in your browser and never saved — hit counts are an operational "
        "snapshot, not part of your design."),
    (35,"Before you touch a rule, what-if shows you the blast radius. Draft the change, and "
        "reachability is traced across the whole design twice — as it is, and as it would "
        "be — naming every flow that breaks, is newly allowed, or reroutes, with the before "
        "and after paths."),
    (35,"It also reports the hygiene the change creates or resolves — rules it shadows, "
        "rules it makes redundant — and copies out as a change-ticket summary. Nothing is "
        "applied until you accept it, and accepting is a single, undoable step."),
    (36,"Watchtower is the uptime side: HTTP, TCP, UDP, ping, DNS, keyword, page-change, "
        "heartbeat and API monitors, with alerting over e-mail, SMS, voice, Telegram and "
        "browser push — and status pages you can share with a token. The drift scheduler "
        "reuses those same channels, so operational alerting is one system rather than two."),
    (36,"And a BGP monitor watches how the internet routes your prefix, from outside. It "
        "alerts when the origin changes, when RPKI goes invalid, or when a blackhole "
        "community appears. A withdrawn prefix is the one condition reported as down — "
        "everything else is a named change."),
    (37,"That same outside-in view is free in the toolbox, as Looking Glass. One input — a "
        "domain, an IP, a prefix or an AS number — returns a graded verdict on how the "
        "global routing table carries it: announced, origin, RPKI validity, registry data "
        "and communities, with a world map of which route collectors can see you."),
    (37,"It sends no packets at all. It reads what roughly three hundred and seventy BGP "
        "sessions on RIPE's route collectors already record — which is how it catches a "
        "quiet hijack that a reachability check from any single point would miss."),
    (33,"And when reality has already moved on, the Import wizard's as-built mode pulls a "
        "live device and its LLDP neighbours through the credential vault and reconciles "
        "matched, new and missing against your design. The apply is additive and undoable."),
    (38,"Cloud is the same story. Azure resources are real nodes — virtual networks and "
        "subnets draw as containers with their address ranges, security groups and gateways "
        "nest inside — and the infrastructure code stays synchronized. Design from scratch, "
        "or run the subscription import and reverse-engineer what already exists."),
    (38,"Then push it back as Terraform — or Pulumi — and schedule drift checks against it. "
        "The same closed loop as the physical estate, in one canvas and one bill of "
        "materials."),
    (39,"Building that cloud environment is now a guided drawer: the Azure Designer walks "
        "scope, topology, subnets, security, connectivity, workloads and review, while the "
        "canvas renders it live beside you. The address plan carves itself from a supernet, "
        "and reserved subnets appear with their real names and minimum sizes the moment an "
        "appliance needs them."),
    (39,"Azure networking is typed and directional. Peering generates both directions with "
        "per-side flags, and forced tunnelling writes a default route whose next hop is a "
        "reference to the canvas firewall — never a hand-typed address. The review step "
        "runs whole-design validation, so Create commits a clean environment or tells you "
        "why not."),
    (40,"Deployment picks its engine per project — Terraform or Pulumi — and the choice "
        "locks after the first apply, because the two state formats are not "
        "interchangeable. State lives in your own storage account, and a live preflight "
        "asks the subscription before money is spent: are the names free, is the SKU "
        "available in that region, is there quota headroom."),
    (40,"Service principals are saved server-side, encrypted, and never returned to the "
        "browser. And thirty Azure-specific checks run at keystroke latency on the canvas, "
        "then again at the deploy gate — firing the same codes in both places, so the "
        "drawer and the server can never disagree."),

    # ---------------- where it's going ----------------
    (41,"So that's the product: design on a canvas, configure with real per-vendor depth, "
        "validate continuously, publish once, deploy safely, and keep verifying afterwards."),
    (41,"And the price of all the design work is nothing. Everything that turns a drawing "
        "into an artefact is free, without an account for most of it — what carries a "
        "price is what reaches out and touches a live network."),
    (42,"As for where it's going — the most recent releases show the direction. The Azure "
        "Designer rebuilt cloud design end to end, with Terraform and Pulumi deployment "
        "behind a live preflight. Firewall Studio gained what-if analysis and dead-rule "
        "detection. Looking Glass and BGP monitoring brought the internet's view of your "
        "network inside."),
    (42,"Rack elevations grew patch panels that price into the bill of materials. Drawings "
        "learned to route links around unrelated devices and bundle port-channels into one "
        "stroke. Public blueprint pages made designs embeddable anywhere. And the pricing "
        "line is a commitment: everything that draws is free — what carries a price is only "
        "what touches a live network."),
    (42,"The pattern is consistent: less retyping, more verification, and a shorter distance "
        "between the drawing and the running network."),
    (43,"Netforge.ai. Draw the network once. Everything else is generated."),
  ])

if __name__ == '__main__':
    series.EPISODES = [WALKTHROUGH]
    retime = '--retime' in sys.argv
    d = series.build(WALKTHROUGH, do_synth=not retime)
    print(f"\n  walkthrough: {d/60:.1f} min")

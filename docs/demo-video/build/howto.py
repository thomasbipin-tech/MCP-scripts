#!/usr/bin/env python3
"""The how-to set: task-oriented recipes, as opposed to the feature tours.

The episodes answer "what does this part of the product do?". A recipe answers "how do I
finish this job, in the order I would actually work". The product publishes its own
recipes at /docs/how-to; this cut follows the first of them step for step, including the
traps it names, because the traps are the reason a how-to beats a feature tour.

Source of truth: ../howto/SPEC-route-an-office.txt (kept in the repo deliberately -- an
earlier copy lived only in /tmp and did not survive a container rebuild).

  python3 howto.py             # VO + timeline_howto-<slug>.json
  python3 howto.py --retime    # re-time from existing wavs, no synthesis
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import series
from series import (BRAND, ENDCARD, TAG)

# scenes 62-70, appended after the batch-4 screens; see scenes.html
PREREQ, VLANS, TRUNKS, SVIS, ROUTEDACC = 62, 63, 64, 65, 66
STATICS, REACH, VALIDATE6, GENERATE6 = 67, 68, 69, 70

ROUTE_AN_OFFICE = dict(
  slug='howto-route-an-office', title='How to route an office, end to end',
  slots=[
    (BRAND,3.0),          # 0
    (PREREQ,None),        # 1  before you start
    (VLANS,None),         # 2  step 1
    (TRUNKS,None),        # 3  step 2
    (SVIS,None),          # 4  step 3
    (ROUTEDACC,None),     # 5  step 3, the access-switch case
    (STATICS,None),       # 6  step 4
    (REACH,None),         # 7  step 5
    (VALIDATE6,None),     # 8  step 6, validate
    (GENERATE6,None),     # 9  step 6, generate
    (ENDCARD,6.0),        # 10
  ],
  lines=[
    (1,"This is a recipe rather than a tour. One job, start to finish, in the order you "
       "would actually work it: an office that is drawn but not yet routed, taken from an "
       "empty VLAN list to a configuration you can read line by line."),
    (1,"Four things before you start. The office is drawn, cabled and named — rename "
       "before you configure, because every hostname and every generated stanza keys off "
       "the device name. You have one address block for the site. You know the address on "
       "the firewall's inside interface, because the default route is going to name it."),
    (1,"And you have decided who holds the gateways: the core pair, or the access switches "
       "themselves. Step three settles that, and the answer changes what you have to "
       "switch on first. Budget about forty minutes the first time."),

    (2,"Step one. On a switch, the L2 tab, VLANs. Each row is an id, a name, an optional "
       "purpose and a state, and Add VLAN proposes the next free id."),
    (2,"Save to database promotes the row to the project's VLAN database, so the next "
       "switch picks it from a list instead of you retyping it — and the two cannot "
       "disagree about what VLAN twenty is called."),
    (2,"One thing to know before you go further. The SVI checkbox on a VLAN row is a note "
       "to yourself, not an instruction. Nothing reads it. It never reaches the "
       "configuration generator, and adding a real SVI in the L3 tab does not tick it. A "
       "VLAN with the box ticked and no SVI is a VLAN with no gateway."),

    (3,"Step two. Still in the L2 tab, Switchports. Put the new ids on the allowed list of "
       "every uplink between the access layer and the cores, and set the access and voice "
       "VLAN on the user ports. On a pair of cores, the peer link carries them too."),
    (3,"This is the step worth slowing down for. Validation does not read trunk allowed "
       "lists. An id left off one trunk is completely silent — and it is the most common "
       "reason a gateway that looks perfect does not answer. The SVI is up on the core, and "
       "the VLAN simply never reaches it. Check the allowed lists by hand."),

    (4,"Step three. On the core, the L3 tab, SVIs. One row per VLAN: the VLAN, an address, "
       "a prefix, a description, and first-hop redundancy where a pair shares the gateway."),
    (4,"Address the first switch's row and it grows an auto-assign button. It takes the "
       "subnet from the first switch in hostname order that already has an address on that "
       "VLAN, then numbers every switch in the design with an SVI on it. The virtual "
       "address is the first usable one, with HSRP or VRRP to match the platform."),
    (4,"Two things it will happily let you do. The VLAN field is a free number, not a "
       "picker — an SVI on a VLAN this switch does not have is accepted, saved, and "
       "generates an interface into a broadcast domain that is not there."),
    (4,"And an access switch is not counted as a layer-three switch here. A pair of routed "
       "access switches gets member addresses and no virtual address — which is the very "
       "address the DHCP scope points at. Set the redundancy by hand on both, or keep the "
       "gateways on the cores."),

    (5,"Which brings us to that case. Open the L3 tab of an access switch and there are no "
       "sections at all — just a card telling you the switch is layer two by default, and "
       "a button to enable layer-three routing."),
    (5,"Everything layer three on that switch hangs off this one toggle: the SVIs, the "
       "static routes, OSPF, EIGRP, BGP. Configure the tab with it off and none of it "
       "renders."),
    (5,"The generator does tell you — but it tells you in the device's Config tab and in "
       "the Generate drawer, which report what the template did. It does not appear in "
       "Validate, which checks the design and never sees the template. Knowing which drawer "
       "prints it is the whole point."),

    (6,"Step four. The L3 tab, Static Routes. A default route toward the firewall is all "
       "zeros, with the firewall's inside address as the next hop."),
    (6,"Watch this one. The zeros you can see in Prefix and Mask are placeholder text, not "
       "a value — type them into both. A blank mask renders as a slash twenty-four whose "
       "description claims it is the default route. A blank prefix or next hop drops the "
       "route from the configuration entirely."),
    (6,"And a default is only half of it. An office core carries three routes. Everything "
       "Internet-bound to the firewall. The corporate supernet to the SD-WAN appliance — "
       "longer than the default, so it wins on prefix length, and only Internet traffic "
       "takes the firewall. And the third route lives on the other box: a route back, on "
       "the firewall, for every subnet behind the core. Without it, traffic leaves and "
       "never returns, and the symptom looks like a firewall rule."),

    (7,"Step five. The office now has gateways and a way out. What it has not got is a path "
       "to the rest of the estate, and the firewall is not it. There are two shapes, and "
       "which one you have was largely decided when the site was built."),
    (7,"Static toward the WAN edge is the simpler one: everything corporate goes to the "
       "appliance, the overlay carries it, and the appliance holds a route back. No "
       "protocol, nothing to watch — but every new site is an edit on this core."),
    (7,"Or peer the core with the appliance over eBGP. Both halves are generated: the core "
       "opens a session with BFD and advertises the site block, and the appliance gets a "
       "bootstrap document for its orchestrator. Remote sites are learned, so office "
       "thirty-one is not an edit on thirty cores."),
    (7,"One caveat. This is a first-run decision. Once any site in a plan has generated, "
       "the wizard becomes additive — the WAN architecture, the peering mode and the AS "
       "numbers are frozen, and switching afterwards is a hand edit on each core and each "
       "appliance."),

    (8,"Step six. Validate first — Generate stays unavailable while any error is open. "
       "Findings group by rule, so seven copies of one mistake read as one row with a "
       "count, rather than seven problems."),
    (8,"Four of them come up again and again on this recipe. VLAN not defined is step one "
       "against step three. Next-hop off subnet is step four, written before the transit "
       "link was addressed. Subnet overlap is two sites reusing a VLAN id and auto-assigned "
       "as one group. And BGP incomplete is step five with a peer address still empty."),

    (9,"Then read what generated. A configuration per device, in that platform's own "
       "dialect, that you can read, copy and download."),
    (9,"A last thing, and it is the one people are caught by. Validate and Generate are two "
       "different pipelines. Validate checks the design and never sees the template. The "
       "Config tab and the Generate drawer render the templates and report what the "
       "template found."),
    (9,"So a clean Validate is not a promise that every device rendered what you typed. "
       "Read one generated config per role before you call it done."),

    (10,TAG),
  ])

if __name__ == '__main__':
    series.EPISODES = [ROUTE_AN_OFFICE]
    retime = '--retime' in sys.argv
    d = series.build(ROUTE_AN_OFFICE, do_synth=not retime)
    print(f"\n  route-an-office: {d/60:.1f} min")

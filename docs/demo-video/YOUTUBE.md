# YouTube upload pack — Netforge.ai video set

Everything needed to upload, per video: the file, its runtime, the title, the description
(chapters included), and the tags. Chapter marks are computed from the shipped timelines,
so they land on the real cut rather than an estimate.

## The files

All paths are relative to `docs/demo-video/` on branch
`claude/netforge-demo-video-wqb9sw`.

| File | Runtime | Size | Notes |
|---|---|---|---|
| `netforge-demo-v8.mp4` | 2:31 | 9.7 MB | Master demo — the one to feature |
| `series/netforge-walkthrough.mp4` | 17:48 | 58.2 MB | Full walkthrough — UPLOAD THIS ONE |
| `series/netforge-walkthrough-web.mp4` | 17:48 | 28.4 MB | same cut, compressed for chat — do not upload |
| `series/netforge-ep01-canvas.mp4` | 2:41 | 7.9 MB | Episode 1 |
| `series/netforge-ep02-device-config.mp4` | 2:56 | 10.1 MB | Episode 2 |
| `series/netforge-ep03-blueprint.mp4` | 2:17 | 8.3 MB | Episode 3 |
| `series/netforge-ep04-multicanvas.mp4` | 2:02 | 7.0 MB | Episode 4 |
| `series/netforge-ep05-generate.mp4` | 2:38 | 7.8 MB | Episode 5 |
| `series/netforge-ep06-ipam.mp4` | 2:12 | 7.6 MB | Episode 6 |
| `series/netforge-ep07-publish.mp4` | 2:47 | 9.5 MB | Episode 7 |
| `series/netforge-ep08-drift.mp4` | 2:12 | 8.1 MB | Episode 8 |
| `series/netforge-ep09-fabric-cloud.mp4` | 3:12 | 11.6 MB | Episode 9 |
| `series/netforge-ep10-tools-access.mp4` | 3:31 | 11.7 MB | Episode 10 |
| `shorts/netforge-s1-autopsy.mp4` | 0:26 | 2.6 MB | Short |
| `shorts/netforge-s2-in-2026.mp4` | 0:27 | 2.6 MB | Short |
| `shorts/netforge-s3-weeks-to-hours.mp4` | 0:28 | 2.3 MB | Short |
| `shorts/netforge-s4-deploy-minute.mp4` | 0:26 | 2.1 MB | Short |
| `shorts/netforge-s5-paperwork.mp4` | 0:26 | 2.3 MB | Short |

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

## Netforge.ai — Draw the Network Once

**Title**
```
Netforge.ai — Draw the Network Once
```

**Description**
```
Every enterprise network begins as a clean diagram. Almost every outage begins the same way too — not because the design was wrong, but because someone had to translate it by hand into thousands of lines of configuration.

Netforge.ai makes the drawing the source of truth: the thing the network is generated from, validated against, documented from, and continuously compared to.

Design, configure, validate, deploy, and verify — one canvas.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 The drawing and the device disagree
0:59 Scaling to a fabric
1:17 An address conflict, caught
1:29 AI Network Architect
2:01 Cloud on the canvas
2:13 One canvas, one source of truth

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, network design tool, netforge.ai, demo
```

---

## Netforge.ai — The Complete Walkthrough

**Title**
```
Netforge.ai — The Complete Walkthrough
```

**Description**
```
A full walkthrough of Netforge.ai, from an empty canvas to a deployed and continuously verified network. By the end you will know what it is, what it solves, how to use it, and where it is going.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 The drawing and the device disagree
0:37 What actually differs
1:03 The drawing as source of truth
1:24 Creating an account
1:37 Roles and access
1:50 Templates
2:36 Placing a device
3:13 Cabling and the Link Editor
3:45 Device properties
4:25 The management plane
4:52 Console and out-of-band
5:07 The credential vault
5:22 Scaling to a fabric
5:38 Blueprint wizard
6:23 Multi-site WAN overview
6:55 The addressing plan
7:29 Continuous validation
7:46 An address conflict, caught
8:14 AI Network Architect
8:35 Publish preflight
9:16 Rack elevation and BOM
9:57 Export formats
10:20 Public blueprint pages
10:54 Deploying
11:22 Looking Glass path trace
11:36 Drift against the deployed baseline
12:02 Config Compare
12:29 As-built import
12:44 Firewall Studio
13:10 Firewall what-if
13:39 Watchtower monitoring
14:17 Looking Glass
14:49 Cloud on the canvas
15:18 The Azure Designer
15:57 Deploy with Terraform or Pulumi
16:33 One canvas, one source of truth
16:56 What's new

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, product walkthrough, tutorial, ipam, vxlan, azure, firewall
```

---

## Netforge.ai — Episode 1: The Canvas

**Title**
```
Netforge.ai — Episode 1: The Canvas
```

**Description**
```
The canvas is where every design starts — and everything you place on it is a real device with a real model, real ports and real configuration behind it.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 The drawing as source of truth
0:39 The device catalog
1:17 Placing a device
1:39 Cabling and the Link Editor
2:10 Device properties

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, network topology, network canvas, device catalog
```

---

## Netforge.ai — Episode 2: Configuring a Device

**Title**
```
Netforge.ai — Episode 2: Configuring a Device
```

**Description**
```
The usual objection to design tools is that they generate something shallow. Here is the depth: interfaces, sub-interfaces, first-hop redundancy, the management plane, the credential vault, and Firewall Studio.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 Interfaces and sub-interfaces
0:39 First-hop redundancy
1:10 The management plane
1:37 Console and out-of-band
1:59 The credential vault
2:19 Firewall Studio

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, hsrp, vrrp, device configuration, firewall policy, aaa
```

---

## Netforge.ai — Episode 3: Blueprints and Templates

**Title**
```
Netforge.ai — Episode 3: Blueprints and Templates
```

**Description**
```
Twenty-eight reference designs, and a Blueprint wizard that builds a whole multi-site estate — one tab per site, wired through a WAN overview, with addressing that never renumbers what you already deployed.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 Templates
0:49 Blueprint wizard
1:12 Subnet profiles
1:33 The estate, generated
1:53 Site areas and inheritance

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, network templates, blueprint, multi-site network, subnet planning
```

---

## Netforge.ai — Episode 4: Multi-Site Projects

**Title**
```
Netforge.ai — Episode 4: Multi-Site Projects
```

**Description**
```
A project is many canvases — one per site, plus a pinned WAN Overview. Inter-site links are declared once and mirrored, so validation runs over one joined graph.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 A project of many canvases
0:23 Multi-site WAN overview
0:49 Inter-site links
1:08 Joined-graph validation
1:31 Site-filtered exports

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, multi-site, wan design, network validation
```

---

## Netforge.ai — Episode 5: Validation and Generation

**Title**
```
Netforge.ai — Episode 5: Validation and Generation
```

**Description**
```
Validation is continuous, not a button you remember to press. Address conflicts, VLAN consistency, BGP reciprocity, MTU, gateway redundancy — then per-vendor CLI, and firewall what-if before you touch a rule.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 Continuous validation
0:36 An address conflict, caught
0:54 AI Network Architect
1:29 The generated CLI
1:56 Firewall what-if

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, network validation, bgp, vlan, config generation, firewall
```

---

## Netforge.ai — Episode 6: Addressing and IPAM

**Title**
```
Netforge.ai — Episode 6: Addressing and IPAM
```

**Description**
```
Define the pools once and stop typing addresses. Every allocation traces back to its pool, and the overlap checker catches everything typed by hand.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 IPAM pools
0:26 The addressing plan
0:43 The allocation ledger
1:03 Supernet planning
1:34 The overlap checker

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, ipam, ip address management, subnetting, cidr
```

---

## Netforge.ai — Episode 7: Publish and Handover

**Title**
```
Netforge.ai — Episode 7: Publish and Handover
```

**Description**
```
Publish is one action: validate, then produce everything at once — CLI, cable schedule, rack elevations with patch panels, bill of materials, design document — plus a public page you can embed.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 Publish preflight
0:33 Export formats
1:01 Rack elevation and BOM
1:17 Cable schedule
1:34 The design document
2:04 Public blueprint pages

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, network documentation, bill of materials, cable schedule, rack elevation
```

---

## Netforge.ai — Episode 8: Deploy, Verify and Drift

**Title**
```
Netforge.ai — Episode 8: Deploy, Verify and Drift
```

**Description**
```
The real problem is not the first day. It is month eleven, when someone fixed something at 2 a.m. and never updated the diagram. Drift closes that loop against the deployed baseline.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 Deploying
0:20 Looking Glass path trace
0:35 The drawing and the device disagree
0:54 Drift against the deployed baseline
1:19 Config Compare
1:46 As-built import

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, configuration drift, network deployment, ansible, config compare
```

---

## Netforge.ai — Episode 9: Fabrics and Cloud

**Title**
```
Netforge.ai — Episode 9: Fabrics and Cloud
```

**Description**
```
The same canvas that held a branch closet scales to an Arista leaf-spine VXLAN EVPN fabric — and to an Azure landing zone you deploy as Terraform or Pulumi.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 Scaling to a fabric
0:33 VXLAN EVPN fabric parameters
1:07 Cloud on the canvas
1:24 The Azure Designer
1:56 Azure subscription import
2:18 Terraform, synchronized
2:37 Deploy with Terraform or Pulumi

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, vxlan, evpn, arista avd, azure, terraform, pulumi
```

---

## Netforge.ai — Episode 10: Access, Tools and Monitoring

**Title**
```
Netforge.ai — Episode 10: Access, Tools and Monitoring
```

**Description**
```
Roles and two-factor, twenty-one free network tools including Looking Glass, Watchtower uptime and BGP monitors — and where the product is heading.

Part of the ten-part Netforge.ai series.

No account needed to draw a topology and generate real configs in your browser.

Chapters
0:00 Creating an account
0:40 Roles and access
0:58 Free network tools
1:32 Looking Glass
2:03 Watchtower monitoring
2:34 One canvas, one source of truth
2:55 What's new

Draw the network once. Everything else is generated.
https://netforge.ai
```

**Tags**
```
netforge, network design, network automation, network engineering, network documentation, config generation, cisco, arista, network diagram, looking glass, bgp monitoring, uptime monitoring, network tools, rpki
```

---

## Shorts

Under 30s each — upload as Shorts (vertical crop optional; these are 16:9).

**s1-autopsy**
```
The 2 a.m. Autopsy
```
```
Two configs. One live comparison. No compare button.

Draw the network once. Everything else is generated.
https://netforge.ai
```

**s2-in-2026**
```
Still Retyping Configs in 2026?
```
```
Start from a production-ready design instead.

Draw the network once. Everything else is generated.
https://netforge.ai
```

**s3-weeks-to-hours**
```
Seventeen Sites, One Afternoon
```
```
A multi-site design takes weeks. It does not have to.

Draw the network once. Everything else is generated.
https://netforge.ai
```

**s4-deploy-minute**
```
The Deploy Minute
```
```
Dry run, rollback point, then the path traced hop by hop.

Draw the network once. Everything else is generated.
https://netforge.ai
```

**s5-paperwork**
```
Nobody Budgets for the Paperwork
```
```
Rack elevation, BOM, cable schedule — all generated.

Draw the network once. Everything else is generated.
https://netforge.ai
```


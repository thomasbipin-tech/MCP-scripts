#!/usr/bin/env python3
"""Build the VO track and derive the video timeline from it.

The picture cuts to the audio, not the other way round: each scene's duration is
max(visual floor, what its narration actually needs). Emits:
  vo.wav        - full-length narration bed
  timeline.json - scene in/out points + caption cues, consumed by scenes.html
"""
import json, os, subprocess, wave, sys
import numpy as np

SR = 22050
VOICE = 'voices/en_US-ryan-high.onnx'
LENGTH_SCALE = '1.04'
os.makedirs('vo', exist_ok=True)

# Visual floor per scene (seconds) — below this the shot feels rushed regardless of VO.
SCENE_MIN = {1:10, 2:12, 3:11, 4:11, 5:6.5, 6:6.5, 7:8, 8:5.5,
             9:8, 10:7, 11:5.5, 12:6.5, 13:7, 14:6.5, 15:8, 16:8}
# Pacing per scene: (intro pad, gap between lines, tail pad)
PACE = {1:(0.7,0.8,1.2), 2:(0.7,0.6,1.0), 3:(1.0,0.7,1.4), 4:(2.0,0.8,3.4),
        5:(0.8,0.5,1.2), 6:(0.8,0.5,1.2), 7:(0.8,0.5,1.2), 8:(0.6,0.5,0.9),
        9:(0.6,0.5,1.1), 10:(0.6,0.5,1.1), 11:(0.5,0.5,1.5), 12:(0.6,0.5,1.0),
        13:(0.6,0.5,1.0), 14:(0.6,0.5,1.0), 15:(0.8,0.6,1.2), 16:(0.8,0.5,2.2)}

# (id, scene, spoken text, say-override or None, caption HTML or None)
LINES = [
 ('01', 1, "Every network change starts as a drawing.", None,
        "Every network change starts as a drawing."),
 ('02', 1, "And every outage starts with the gap between that drawing, and what's actually on the box.", None,
        "And every outage starts with the gap between that drawing —<br>and <em>what's actually on the box</em>."),
 ('03', 2, "So you design it in Visio. You build it by hand, box by box, in CLI.",
        "So you design it in Visio. You build it by hand, box by box, in C L I.",
        "You design it in Visio. You build it by hand, in CLI."),
 ('04', 2, "And somewhere between the two, a VLAN gets transposed. A BGP neighbour never comes up.",
        "And somewhere between the two, a V LAN gets transposed. A B G P neighbor never comes up.",
        "Somewhere between the two, a VLAN gets transposed.<br>A BGP neighbour never comes up."),
 ('05', 2, "You find out at two in the morning, inside a maintenance window, with a rollback plan and no time left to use it.", None,
        "You find out at 2am — inside a maintenance window,<br>with no time left to use the rollback plan."),
 ('06', 3, "The drawing wasn't wrong. It was just never connected to anything.", None,
        "The drawing was never wrong.<br>It was just never <em>connected to anything</em>."),
 ('07', 3, "Every diagram tool on the market gives you a picture of the network. Then it hands you a keyboard, and wishes you luck.", None,
        "Every diagram tool gives you a picture of the network.<br>Then it hands you a keyboard and wishes you luck."),
 ('08', 4, "So what if the drawing was the source of truth?", None,
        "So what if the drawing <em>was</em> the source of truth?"),
 ('09', 4, "Not a picture of the network. The network itself.", None,
        "Not a picture of the network. The network itself."),
 ('10', 5, "This is Netforge. Drag a device onto the canvas.",
        "This is Net forge dot A. I. Drag a device onto the canvas.",
        "Drag a device onto the canvas."),
 ('11', 6, "Connect the ports. Set your VLANs, your routing, your management.",
        "Connect the ports. Set your V LANs, your routing, your management.",
        "Connect the ports. Set your VLANs, your routing, your management."),
 ('12', 7, "Scale the same canvas to a full Arista leaf-spine VXLAN EVPN fabric.",
        "Scale the same canvas, to a full Arista leaf spine, V X LAN E V P N fabric.",
        "Scale the same canvas to a full <em>leaf-spine VXLAN EVPN fabric</em>."),
 ('13', 7, "Cisco. Arista. Aruba. Palo Alto. Silver Peak. One canvas.", None,
        "Cisco. Arista. Aruba. Palo Alto. Silver Peak. <em>One canvas.</em>"),
 ('14', 8, "And before anything ships, it gets checked.", None,
        "Before anything ships — it gets checked."),
 ('15', 9, "IP conflicts. VLAN mismatches. BGP peer gaps. Spanning-tree errors.",
        "I P conflicts. V LAN mismatches. B G P peer gaps. Spanning tree errors.",
        "IP conflicts. VLAN mismatches. BGP peer gaps. Spanning-tree errors."),
 ('16', 9, "Caught here, on the canvas. Not out there, in the maintenance window.", None,
        "Caught <em>here</em>, on the canvas —<br>not out there, in the maintenance window."),
 ('17',10, "Then the AI Network Architect reviews the whole design. Single points of failure, CVD and AVD alignment. And tells you what to fix.",
        "Then the A I Network Architect reviews the whole design. Single points of failure. C V D and A V D alignment. And tells you what to fix.",
        "Then the AI Network Architect reviews the whole design —<br>and tells you what to fix."),
 ('18',11, "Zero conflicts. Forty-two checks passed.", None, None),
 ('19',12, "Then the design ships itself. Production-ready CLI. AVD Ansible YAML.",
        "Then the design ships itself. Production ready C L I. A V D Ansible YAM'L.",
        "Production-ready CLI. AVD Ansible YAML.<br>Generated from the same canvas."),
 ('20',13, "PDF packages. Visio diagrams. Excel BOM. Cable schedules. Documentation that can't drift from the design.",
        "P D F packages. Visio diagrams. Excel B O M. Cable schedules. Documentation that can't drift from the design.",
        "PDF packages, Visio diagrams, Excel BOM, cable schedules —<br>documentation that <em>can't drift</em> from the design."),
 ('21',14, "Reverse-engineer a live Azure subscription onto that canvas, and push it back as Terraform.", None,
        "Reverse-engineer a live Azure subscription onto the canvas —<br>and push it back as <em>Terraform</em>."),
 ('22',15, "Design. Configure. Validate. Deploy. One canvas, one source of truth.", None, None),
 ('23',15, "The drawing and the network. Finally the same thing.", None, None),
 ('24',16, "Netforge dot A I. Open the designer, drag your first device.",
        "Net forge dot A. I. Open the designer. Drag your first device.", None),
 ('25',16, "Free to start. No card.", None, None),
]

def synth():
    for lid, _, text, say, _c in LINES:
        subprocess.run(['piper', '-m', VOICE, '-f', f'vo/{lid}.wav',
                        '--length-scale', LENGTH_SCALE],
                       input=(say or text).encode(), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def read(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32) / 32768.0

if __name__ == '__main__':
    if 'skip' not in sys.argv:
        synth()

    durs = {lid: len(read(f'vo/{lid}.wav')) / SR for lid, *_ in LINES}

    # --- lay lines out inside each scene, then size the scene to fit ---
    scenes, cursor = [], 0.0
    placed = []          # (id, absolute_start, dur, caption)
    for si in range(1, 17):
        mine = [l for l in LINES if l[1] == si]
        intro, gap, tail = PACE[si]
        t = intro
        local = []
        for k, (lid, _s, _tx, _say, cap) in enumerate(mine):
            if k: t += gap
            local.append((lid, t, durs[lid], cap))
            t += durs[lid]
        need = t + tail
        d = round(max(SCENE_MIN[si], need), 2)
        a = round(cursor, 2)
        scenes.append({'i': si, 'a': a, 'b': round(a + d, 2), 'd': d,
                       'need': round(need, 2), 'floor': SCENE_MIN[si]})
        for lid, lt, ld, cap in local:
            placed.append((lid, round(a + lt, 2), ld, cap))
        cursor = a + d

    DUR = round(cursor, 2)

    # --- caption cues: hold from the line's start until just before the next line ---
    cues = []
    for n, (lid, st, ld, cap) in enumerate(placed):
        if not cap: continue
        nxt = placed[n + 1][1] if n + 1 < len(placed) else DUR
        cues.append({'t0': st - 0.25, 't1': round(min(st + ld + 1.1, nxt - 0.15), 2), 'html': cap})

    # --- render the narration bed ---
    bed = np.zeros(int((DUR + 1) * SR), dtype=np.float32)
    for lid, st, ld, _c in placed:
        a = read(f'vo/{lid}.wav')
        i = int(st * SR)
        f = int(0.006 * SR)                       # de-click the joins
        a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        bed[i:i + len(a)] += a
    peak = np.abs(bed).max()
    bed *= (10 ** (-3.0 / 20)) / peak             # normalise to -3 dBFS
    with wave.open('vo.wav', 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((bed * 32767).astype('<i2').tobytes())

    json.dump({'duration': DUR,
               'scenes': [{'a': s['a'], 'b': s['b']} for s in scenes],
               'cues': cues,
               'vo': [{'id': l, 'start': s, 'dur': round(d, 2)} for l, s, d, _ in placed]},
              open('timeline.json', 'w'), indent=1)

    print(f"{'sc':>3} {'a':>7} {'b':>7} {'dur':>6} {'need':>6} {'floor':>6}  driver")
    for s in scenes:
        drv = 'VO' if s['need'] > s['floor'] else 'visual floor'
        print(f"{s['i']:3} {s['a']:7.2f} {s['b']:7.2f} {s['d']:6.2f} {s['need']:6.2f} {s['floor']:6.1f}  {drv}")
    speech = sum(d for _l, _s, d, _c in placed)
    print(f"\nruntime {DUR:.2f}s ({int(DUR//60)}:{DUR%60:05.2f})   was 135.00s")
    print(f"speech {speech:.1f}s = {speech/DUR*100:.0f}% density (was 81%)")
    print(f"caption cues: {len(cues)}")

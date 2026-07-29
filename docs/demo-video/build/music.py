#!/usr/bin/env python3
"""Original score for the Netforge.ai demo, synthesised from scratch.

Written here rather than sourced, so there is no third-party licence attached to
the video. Structure follows the cut: sparse and dark under the problem, a drop
at the turn, a steady pulse under the product, a lift on the validation payoff,
and a resolve under the end card. Ducked under the narration.

Out: music.wav (stereo 44.1k)
"""
import json, wave
import numpy as np

SR = 44100
TL = json.load(open('timeline.json'))
DUR = TL['duration'] + 0.6
SC = TL['scenes']                      # 0-indexed; scene n is SC[n-1]
N = int(DUR * SR)
t = np.arange(N) / SR

TURN   = SC[3]['a']                    # 4: reframe / drop
PROD   = SC[4]['a']                    # 5: product act begins
PAYOFF = SC[10]['a']                   # 11: "0 conflicts"
OUTRO  = SC[14]['a']                   # 15: outcome
BPM    = 100.0
BEAT   = 60.0 / BPM

def env_adsr(n, a, d, s, r, sus=0.7):
    """Simple ADSR over n samples (times in seconds)."""
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    S = max(0, n - A - D - R)
    return np.concatenate([
        np.linspace(0, 1, A, endpoint=False) if A else np.array([]),
        np.linspace(1, sus, D, endpoint=False) if D else np.array([]),
        np.full(S, sus),
        np.linspace(sus, 0, R) if R else np.array([]),
    ])[:n]

def lp(x, cutoff):
    """One-pole lowpass; cutoff may be scalar or per-sample array."""
    c = np.clip(np.asarray(cutoff, dtype=np.float64) / (SR / 2), 1e-4, 0.99)
    a = np.broadcast_to(c, x.shape)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):                       # sample loop, but only run a few times
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y

def lp_fast(x, cutoff_hz):
    """Fixed-cutoff lowpass via cascaded EMA — vectorised with lfilter."""
    from scipy.signal import lfilter
    a = 1.0 - np.exp(-2 * np.pi * cutoff_hz / SR)
    y = lfilter([a], [1, -(1 - a)], x)
    return lfilter([a], [1, -(1 - a)], y)

def add(buf, sig, at):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[:j - i]

NOTE = {'A1':55.00,'C2':65.41,'E2':82.41,'F2':87.31,'G2':98.00,'A2':110.00,
        'C3':130.81,'E3':164.81,'F3':174.61,'G3':196.00,'A3':220.00,
        'B3':246.94,'C4':261.63,'D4':293.66,'E4':329.63,'F4':349.23,
        'G4':392.00,'A4':440.00,'C5':523.25,'E5':659.26}

# Am - F - C - G, four beats each, looped through the product act
PROG = [('A2', ['A3','C4','E4']), ('F2', ['F3','A3','C4']),
        ('C3', ['C4','E4','G4']), ('G2', ['G3','B3','D4'])]

pad  = np.zeros(N); bass = np.zeros(N); perc = np.zeros(N)
arp  = np.zeros(N); shim = np.zeros(N)

def pad_voice(freqs, dur, level=1.0, detune=0.004):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for k, dt in enumerate((-detune, 0.0, detune)):
            ff = f * (1 + dt)
            # soft saw: a few harmonics rolled off
            v = sum(np.sin(2 * np.pi * ff * h * tt + k) / (h ** 1.7) for h in range(1, 7))
            out += v * (0.9 if k == 1 else 0.5)
    out /= (len(freqs) * 3)
    return out * env_adsr(n, dur * 0.35, dur * 0.2, 0, dur * 0.42, sus=0.85) * level

def sub_note(f, dur, level=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    v = np.sin(2 * np.pi * f * tt) * 0.8 + np.sin(2 * np.pi * f * 2 * tt) * 0.12
    return v * env_adsr(n, 0.02, 0.15, 0, dur * 0.5, sus=0.6) * level

def kick(level=1.0):
    n = int(0.34 * SR); tt = np.arange(n) / SR
    f = 96 * np.exp(-tt * 20) + 44
    v = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return v * np.exp(-tt * 9) * level

def tick(level=1.0, dark=False):
    n = int(0.055 * SR); tt = np.arange(n) / SR
    v = np.random.RandomState(7).randn(n) * np.exp(-tt * (70 if dark else 110))
    return v * level

def pluck(f, level=1.0):
    n = int(0.42 * SR); tt = np.arange(n) / SR
    v = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2 * tt)
         + 0.16 * np.sin(2 * np.pi * f * 3 * tt))
    return v * np.exp(-tt * 7.5) * level

# ---------------- ACT 1: sparse, dark, unresolved ----------------
add(pad, pad_voice([NOTE['A2'], NOTE['E3']], TURN + 1.0, level=0.30), 0.0)
add(pad, pad_voice([NOTE['C3'], NOTE['F3']], 14.0, level=0.16), 16.0)
k = 0.0
while k < TURN - 2.0:                                   # slow, lonely sub pulse
    add(bass, sub_note(NOTE['A1'], 2.4, 0.42), k)
    add(perc, tick(0.05, dark=True), k)
    k += 4.8

# ---------------- THE TURN: drop, then a rising swell ----------------
swell_len = PROD - (TURN + 3.4)
if swell_len > 1.0:
    n = int(swell_len * SR); tt = np.arange(n) / SR
    rise = np.sin(2 * np.pi * (NOTE['A2'] * (1 + 0.28 * tt / swell_len)) * tt)
    rise += 0.5 * np.sin(2 * np.pi * NOTE['E3'] * tt)
    add(shim, rise * (tt / swell_len) ** 2.2 * 0.30, TURN + 3.4)
add(bass, sub_note(NOTE['A1'], 2.0, 0.85), PROD - 0.55)   # downbeat into the product

# ---------------- PRODUCT ACT: steady pulse ----------------
bar = 0
tpos = PROD
while tpos < OUTRO:
    root, ch = PROG[bar % 4]
    barlen = BEAT * 4
    lift = 1.22 if PAYOFF <= tpos < SC[10]['b'] else 1.0
    add(pad,  pad_voice([NOTE[c] for c in ch], barlen * 1.05, level=0.20 * lift), tpos)
    add(bass, sub_note(NOTE[root], barlen * 0.62, 0.50), tpos)
    add(bass, sub_note(NOTE[root], BEAT * 0.9, 0.30), tpos + BEAT * 2)
    for b in range(4):                                   # kick 1 & 3, ticks on 8ths
        if b in (0, 2):
            add(perc, kick(0.30), tpos + b * BEAT)
        add(perc, tick(0.030 if b % 2 else 0.042), tpos + b * BEAT)
        add(perc, tick(0.018), tpos + b * BEAT + BEAT / 2)
    seq = [ch[0], ch[2], ch[1], ch[2]]                    # gentle 8th arpeggio
    for i, nm in enumerate(seq * 2):
        add(arp, pluck(NOTE[nm] * 2, 0.055 * lift), tpos + i * BEAT / 2)
    if lift > 1.0:                                       # payoff shimmer
        add(shim, pad_voice([NOTE['A4'], NOTE['E5']], barlen, level=0.10), tpos)
    tpos += barlen
    bar += 1

# ---------------- OUTRO: resolve, hold, fade ----------------
add(pad,  pad_voice([NOTE['A3'], NOTE['C4'], NOTE['E4']], (DUR - OUTRO) * 0.55, level=0.30), OUTRO)
add(pad,  pad_voice([NOTE['F3'], NOTE['A3'], NOTE['C4']], (DUR - OUTRO) * 0.55, level=0.26), OUTRO + (DUR - OUTRO) * 0.42)
add(bass, sub_note(NOTE['A1'], 5.0, 0.55), OUTRO)
add(bass, sub_note(NOTE['F2'], 5.0, 0.40), OUTRO + (DUR - OUTRO) * 0.42)
add(shim, pad_voice([NOTE['A4'], NOTE['E5']], (DUR - OUTRO) * 0.5, level=0.07), OUTRO + 0.6)
for b in range(6):                                       # pulse thins out and stops
    add(perc, kick(0.22 * (1 - b / 6)), OUTRO + b * BEAT * 2)

# ---------------- mix ----------------
pad  = lp_fast(pad, 1500)
arp  = lp_fast(arp, 3200)
perc = lp_fast(perc, 6500)
mix = pad * 1.0 + bass * 0.95 + perc * 0.55 + arp * 0.42 + shim * 0.5

# darker under act 1, opens up at the product act
tilt = np.ones(N)
tilt[:int(PROD * SR)] = 0.72
tilt = lp_fast(tilt, 2.0)
mix *= tilt

# duck under the narration
with wave.open('vo.wav') as w:
    vo = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32) / 32768.0
    vo_sr = w.getframerate()
vo44 = np.interp(np.arange(N) / SR, np.arange(len(vo)) / vo_sr, vo, left=0, right=0)
envelope = lp_fast(np.abs(vo44), 2.5)
envelope /= max(envelope.max(), 1e-6)
duck = 1.0 - 0.62 * np.clip(envelope * 3.2, 0, 1)        # up to about -8 dB
mix *= duck

# head/tail fades and a soft limiter
fi, fo = int(1.6 * SR), int(3.2 * SR)
mix[:fi] *= np.linspace(0, 1, fi)
mix[-fo:] *= np.linspace(1, 0, fo) ** 1.5
mix = np.tanh(mix * 1.25) / 1.25
mix *= 10 ** (-19.0 / 20) / max(np.abs(mix).max(), 1e-6)  # quiet bed; VO stays on top

st = np.stack([mix, np.roll(mix, 90)], axis=1)            # slight width
with wave.open('music.wav', 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes())

print(f'music.wav  {DUR:.2f}s')
print(f'  turn {TURN:.1f}s | product {PROD:.1f}s | payoff {PAYOFF:.1f}s | outro {OUTRO:.1f}s')
print(f'  peak {np.abs(st).max():.3f}  rms {np.sqrt((mix**2).mean()):.4f}')

#!/usr/bin/env python3
"""Bande-son originale du film VOXY (musique + sound design), 100 % synthétisée.
120 BPM · 48 kHz stéréo · 52 s. Chaque bruitage est calé sur la timeline de src/main.js.
Usage : python3 audio.py build/soundtrack.wav
"""
import sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
DUR = 52.0
N = int(DUR * SR)
rng = np.random.default_rng(34)

BUS = {k: np.zeros((2, N)) for k in ('drums', 'bass', 'pad', 'arp', 'bell', 'sfx', 'hit')}
REV = np.zeros((2, N))   # départ réverbération
DLY = np.zeros((2, N))   # départ délai ping-pong


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR


def add(bus, sig, t, gain=1.0, pan=0.0, rev=0.0, dly=0.0):
    """Place un signal mono/stéréo à l'instant t (s). pan ∈ [-1, 1]."""
    i = int(round(t * SR))
    if i >= N: return
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)]) * 1.41
    if i < 0: sig, i = sig[:, -i:], 0
    n = min(sig.shape[1], N - i)
    s = sig[:, :n] * gain
    BUS[bus][:, i:i + n] += s
    if rev: REV[:, i:i + n] += s * rev
    if dly: DLY[:, i:i + n] += s * dly


def fade(x, a=0.004, r=0.01):
    n = len(x); na, nr = min(int(a * SR), n // 2), min(int(r * SR), n // 2)
    e = np.ones(n)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return x * e


def filt(x, kind, fc, order=2):
    sos = signal.butter(order, fc, kind, fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def noise(d): return rng.standard_normal(int(d * SR))


# ───────────────────────── Instruments ─────────────────────────
def pluck(m, d=0.5, bright=1.0, K=18):
    f, t = mtof(m), tt(d)
    k = np.arange(1, K + 1)[:, None]
    k = k[(k * f < 0.45 * SR).ravel()]
    amp = 1.0 / k ** 1.05
    dec = np.exp(-t[None, :] * (3.2 + (2.4 / bright) * k))
    x = (amp * dec * np.sin(2 * np.pi * f * k * t[None, :])).sum(0)
    return fade(x, 0.002, 0.03)


def pad(notes, d, bright=1.0, att=0.5, rel=0.8):
    t = tt(d + rel)
    out = np.zeros((2, len(t)))
    env = np.minimum(1, t / att) * np.where(t > d, np.exp(-(t - d) / (rel / 3)), 1)
    for m in notes:
        for det, pan in ((-7, -0.7), (0, 0.0), (7, 0.7), (-3, 0.35), (4, -0.35)):
            f = mtof(m + det / 100)
            x = np.zeros(len(t)); ph = rng.uniform(0, 2 * np.pi)
            for k in range(1, 9):
                if f * k > 6000 * bright: break
                x += np.sin(2 * np.pi * f * k * t + ph * k) / k ** (2.0 / bright ** 0.5)
            x *= 1 + 0.05 * np.sin(2 * np.pi * 0.31 * t + ph)
            a = (pan + 1) * np.pi / 4
            out += np.stack([x * np.cos(a), x * np.sin(a)])
    return out * env / (len(notes) * 2.2)


def bell(m, d=1.4, hard=1.0):
    """Piano électrique / cloche FM douce."""
    f, t = mtof(m), tt(d)
    idx = 2.2 * hard * np.exp(-t * 7)
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 4 * t)) * np.exp(-t * 3.2)
    x += 0.35 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 5)
    return fade(x, 0.003, 0.05)


def bass(m, d=0.22):
    f, t = mtof(m), tt(d)
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6) + 0.22 * np.sin(6 * np.pi * f * t) * np.exp(-t * 9)
    return fade(np.tanh(1.6 * x) * np.exp(-t * 2.5), 0.004, 0.03)


def kick(d=0.4, punch=1.0):
    t = tt(d)
    f = 52 + 120 * np.exp(-t * 34)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8.5)
    x += 0.5 * punch * filt(noise(d), 'high', 2500) * np.exp(-t * 320)
    return fade(np.tanh(1.5 * x), 0.0005, 0.02)


def clap(d=0.28):
    t = tt(d); x = np.zeros(len(t))
    for off in (0, 0.011, 0.023):
        e = np.where(t >= off, np.exp(-(t - off) * 130), 0)
        x += noise(d) * e
    x += noise(d) * np.exp(-t * 26) * 0.5
    return fade(signal.sosfilt(signal.butter(2, [900, 5200], 'band', fs=SR, output='sos'), x), 0.0005, 0.02)


def hat(d=0.05, dec=110):
    t = tt(d)
    return fade(filt(noise(d), 'high', 8000, 4) * np.exp(-t * dec), 0.0003, 0.005)


def tick(f=3200, d=0.03, dec=260):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t * dec)


def blip(m, d=0.16, dec=28):
    f, t = mtof(m), tt(d)
    return fade((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * dec), 0.002, 0.02)


def ding(m, d=1.1):
    f, t = mtof(m), tt(d)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * dc) for r, a, dc in ((1, 1, 4.5), (2.0, .45, 7), (3.01, .25, 10), (4.2, .12, 14)))
    return fade(x, 0.002, 0.05)


def pop(f0=420, d=0.09):
    t = tt(d)
    f = f0 * (1 + 1.4 * np.exp(-t * 60))
    return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 46), 0.001, 0.01)


def thud(d=0.5, f0=70):
    t = tt(d)
    f = f0 * 0.6 + f0 * 1.6 * np.exp(-t * 40)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    x += 0.7 * filt(noise(d), 'low', 900) * np.exp(-t * 60)
    return fade(np.tanh(1.8 * x), 0.0005, 0.03)


BANDS = np.geomspace(180, 11000, 14)
def whoosh(d=0.7, f0=300, f1=6000, peak=0.6, width=0.9):
    """Bruit filtré dont la bande balaie f0 → f1 ; pic d'amplitude à `peak` (0-1)."""
    n = int(d * SR); x = noise(d); p = np.linspace(0, 1, n)
    c = np.log(f0) + (np.log(f1) - np.log(f0)) * p
    out = np.zeros(n)
    for fb in BANDS:
        lo, hi = fb / 1.22, min(fb * 1.22, 0.45 * SR)
        y = signal.sosfilt(signal.butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
        out += y * np.exp(-((np.log(fb) - c) ** 2) / (2 * width ** 2 * 0.25))
    env = np.where(p < peak, (p / peak) ** 2.2, ((1 - p) / (1 - peak)) ** 1.6)
    pan = np.linspace(-0.6, 0.6, n) * np.sign(rng.uniform(-1, 1))
    a = (pan + 1) * np.pi / 4
    return np.stack([out * env * np.cos(a), out * env * np.sin(a)])


def riser(d=2.0):
    n = int(d * SR); p = np.linspace(0, 1, n)
    w = whoosh(d, 250, 9000, peak=0.985, width=1.1)
    f = 110 * 2 ** (p * 2.2)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * p ** 2.5 * 0.35
    trem = 1 - 0.35 * p * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(4 + 20 * p ** 2) / SR))
    return (w + tone[None, :]) * trem


def impact(d=2.6, f0=52, bright=1.0):
    t = tt(d)
    f = f0 * 0.9 + f0 * 2.2 * np.exp(-t * 22)
    sub = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6))
    crack = filt(noise(d), 'low', 2400) * np.exp(-t * 26) * 0.9
    air = filt(noise(d), 'high', 5000) * np.exp(-t * 3.2) * 0.16 * bright
    x = fade(sub + crack, 0.0005, 0.2)
    return np.stack([x + air * 0.9, x + np.roll(air, 331) * 0.9])


def shimmer(d=1.6, base=84):
    """Scintillement aigu (balayage de lumière)."""
    out = np.zeros((2, int(d * SR)))
    for i in range(14):
        m = base + rng.choice([0, 2, 4, 7, 9, 12, 14, 16])
        s = blip(m, 0.4, 12) * 0.5
        i0 = int((i / 14) ** 1.3 * (d - 0.45) * SR)
        a = (rng.uniform(-0.8, 0.8) + 1) * np.pi / 4
        out[0, i0:i0 + len(s)] += s * np.cos(a); out[1, i0:i0 + len(s)] += s * np.sin(a)
    return out


# ───────────────────────── Harmonie ─────────────────────────
CH = {  # basse, accord (pad)
    'Dm': (38, [50, 57, 64, 65]),
    'Bb': (34, [53, 58, 62, 69]),
    'C':  (36, [55, 60, 64, 67]),
    'D7': (38, [53, 57, 60, 65]),   # Dm7
    'F':  (41, [53, 57, 60, 67]),
    'Gm': (31, [55, 58, 62, 65]),
}
BARS = [(8, 'Bb'), (10, 'C'), (12, 'D7'), (14, 'F'),
        (16, 'Bb'), (18, 'C'), (20, 'D7'),
        (22, 'Gm'), (24, 'C'), (26, 'F'),
        (28, 'Bb'), (30, 'C'), (32, 'D7'),
        (34, 'Bb'), (36, 'C'), (38, 'D7'),
        (40, 'Bb'), (41, 'C'), (42, 'D7'),
        (44, 'Bb'), (46, 'C')]
GROOVE = [(16, 34), (40, 48)]           # batterie complète
in_groove = lambda t: any(a <= t < b for a, b in GROOVE)

# ── Intro (0 → 8) : tension, « le temps file » ──
add('pad', pad([38, 45], 8.0, bright=0.5, att=1.5, rel=0.5), 0, 0.4, rev=0.3)
add('pad', pad(CH['Dm'][1], 7.6, bright=1.0, att=2.2, rel=0.3), 0.2, 0.5, rev=0.5)
for t, m in ((0.12, 74), (1.0, 69), (2.0, 77), (3.0, 76), (4.0, 74), (5.0, 72), (6.0, 69), (6.5, 70)):   # motif mineur, piano électrique
    add('bell', bell(m, 2.0, 0.7), t, 0.3, pan=-0.1, rev=0.7, dly=0.35)
for b in range(8):                       # battement de cœur
    add('drums', filt(kick(0.4, 0.2), 'low', 220), b, 0.55)
    add('drums', filt(kick(0.4, 0.2), 'low', 180), b + 0.19, 0.3)
for i in range(1, 16):                   # tic-tac d'horloge
    t = i * 0.5
    add('sfx', tick(2100 if i % 2 else 1650, 0.035, 240), t, 0.34 + 0.02 * i, pan=0.25 if i % 2 else -0.25, rev=0.25)
for i in range(16):                      # pulsation qui monte (4 → 8)
    g = (i / 16) ** 1.5
    add('arp', pluck(50, 0.22, bright=0.5 + 1.2 * g), 4 + i * 0.25, 0.1 + 0.2 * g, pan=0.3 * (-1) ** i, rev=0.3)
add('sfx', riser(2.0), 5.86, 0.3, rev=0.3)

# ── Pads / basse / arpège / mélodie ──
for i, (t0, ch) in enumerate(BARS):
    t1 = BARS[i + 1][0] if i + 1 < len(BARS) else 48
    d = t1 - t0
    root, notes = CH[ch]
    soft = t0 < 16 or 34 <= t0 < 40
    add('pad', pad(notes, d, bright=0.85 if soft else 1.15, att=0.25 if t0 in (8, 40, 41, 42) else 0.4), t0, 0.5, rev=0.45)
    if 34 <= t0 < 38:   # break : basse tenue
        add('bass', bass(root + 12, 1.6) , t0, 0.3)
    elif t0 >= 14:
        for k in range(int(d / 0.25)):
            if t0 < 16 and k % 2: continue
            m = root + (12 if k % 4 == 3 else 0)
            add('bass', bass(m, 0.23), t0 + k * 0.25, 0.42 if k % 2 == 0 else 0.3)
    pat = [0, 2, 1, 3, 2, 3, 1, 2]
    for k in range(int(d / 0.25)):
        m = notes[pat[k % 8]] + 12
        g = (0.2 if soft else 0.27) * (1.0 if k % 2 == 0 else 0.72)
        if t0 >= 38 and t0 < 40: g *= 0.6 + 0.4 * k / 8
        add('arp', pluck(m, 0.4, bright=0.9 if soft else 1.5), t0 + k * 0.25, g, pan=0.45 * (-1) ** k, rev=0.25, dly=0.4)

MEL = {16: [(0, 74), (0.75, 77), (1.5, 81)], 18: [(0, 79), (0.75, 76), (1.5, 72)], 20: [(0, 77), (0.75, 81), (1.25, 86)],
       22: [(0, 82), (0.75, 81), (1.5, 79)], 24: [(0, 79), (0.75, 76), (1.5, 79)], 26: [(0, 81), (0.75, 84), (1.25, 81)],
       28: [(0, 74), (0.75, 77), (1.5, 81)], 30: [(0, 79), (0.75, 76), (1.5, 84)], 32: [(0, 86), (0.75, 84), (1.25, 81)],
       44: [(0, 74), (0.75, 77), (1.5, 81)], 46: [(0, 79), (0.5, 81), (1.0, 84), (1.5, 86)]}
for t0, ns in MEL.items():
    for off, m in ns:
        add('bell', bell(m, 1.5), t0 + off, 0.3, pan=-0.15, rev=0.5, dly=0.3)
        if t0 >= 28: add('bell', bell(m + 12, 1.0, 0.6), t0 + off, 0.1, pan=0.3, rev=0.6)

# ── Batterie ──
kicks = []
for a, b in GROOVE:
    t = a
    while t < b - 1e-6:
        beat = round((t - a) * 2)
        kicks.append(t); add('drums', kick(), t, 0.85)
        if beat % 2 == 1: add('drums', clap(), t, 0.36, rev=0.3)
        add('drums', hat(0.05), t + 0.25, 0.2, pan=0.3)
        add('drums', hat(0.03, 200), t + 0.125, 0.07, pan=-0.3)
        add('drums', hat(0.03, 200), t + 0.375, 0.09, pan=-0.3)
        if beat % 8 == 7: add('drums', hat(0.22, 22), t + 0.25, 0.16, pan=0.3)
        t += 0.5
for t in (14, 14.5, 15, 15.5):           # entrée progressive du kick
    kicks.append(t); add('drums', kick(), t, 0.55 + (t - 14) * 0.15)
for k in range(8):                       # roulements avant les drops
    add('drums', clap(0.18), 15 + k * 0.125, 0.1 + 0.035 * k, rev=0.2)
    add('drums', clap(0.18), 39 + k * 0.125, 0.1 + 0.035 * k, rev=0.2)
    add('drums', clap(0.18), 47 + k * 0.125, 0.08 + 0.03 * k, rev=0.2) if k < 7 else None
for t in (35, 36, 37, 38):               # break : un kick doux par étape
    kicks.append(t); add('drums', kick(0.4, 0.4), t, 0.6)

# ───────────────────────── Sound design calé image ─────────────────────────
W = lambda t, d=0.7, g=0.36, **k: add('sfx', whoosh(d, **k), t - d * k.get('peak', 0.6), g, rev=0.25)

# S0
W(0.2, 0.9, 0.2, f0=500, f1=3000)                       # apparition du titre
W(2.0, 0.6, 0.28)                                       # le titre monte, la jauge arrive
add('sfx', pop(380), 1.98, 0.3, rev=0.2)
n = int(1.45 * SR); p = np.linspace(0, 1, n)            # la jauge se vide : glissando descendant
gl = np.sin(2 * np.pi * np.cumsum(880 * 2 ** (-2.3 * p ** 1.3)) / SR) * np.sin(np.pi * p) ** 0.6 * (0.75 + 0.25 * np.sin(2 * np.pi * 14 * p * 1.45))
add('sfx', fade(gl, 0.02, 0.05), 2.3, 0.13, rev=0.4)
add('sfx', blip(57, 0.22, 14), 3.72, 0.42, rev=0.3); add('sfx', blip(51, 0.3, 11), 3.86, 0.42, rev=0.3)  # « refusé »
add('sfx', thud(0.4, 60), 3.72, 0.5)
# S1
W(4.0, 0.7, 0.36)
for i in range(3):
    add('sfx', tick(2600, 0.03), 4.7 + i * 0.14, 0.2, pan=0.4)
    add('sfx', blip(62 - i * 2, 0.14, 30), 5.0 + i * 0.5, 0.3, pan=-0.4, rev=0.2)
for i in range(30):                                     # compteur de la facture
    add('sfx', tick(1800 + i * 45, 0.02, 380), 5.0 + 1.2 * (1 - (1 - i / 30) ** 2), 0.13, pan=0.4)
add('sfx', thud(0.6, 85), 6.5, 0.95, pan=0.3, rev=0.25)  # coup de tampon
add('sfx', filt(noise(0.12), 'high', 1500) * np.exp(-tt(0.12) * 60), 6.5, 0.28, pan=0.3)
W(7.75, 0.5, 0.3, f0=5000, f1=300)
# S2 : révélation
add('hit', impact(3.0, 50), 8.0, 0.95, rev=0.45)
add('sfx', shimmer(1.7), 8.25, 0.2, rev=0.7)
add('sfx', ding(89, 1.6), 8.0, 0.16, rev=0.8)
W(9.9, 0.8, 0.3)
W(10.05, 0.9, 0.14, f0=600, f1=3500)
# S3 : 5 000 → 0
W(12.0, 0.7, 0.34)
for i in range(34):
    q = (i / 34) ** 0.6
    add('sfx', tick(4200 - 2600 * q, 0.022, 360), 12.4 + 1.1 * q, 0.15 + 0.1 * q, pan=0.3 * (-1) ** i)
add('hit', impact(2.2, 58, 0.8), 13.5, 0.8, rev=0.4)
add('sfx', ding(84, 1.8), 13.5, 0.3, rev=0.7); add('sfx', ding(91, 1.5), 13.56, 0.18, rev=0.7)
for i in range(3): add('sfx', pop(520 + 90 * i), 14.45 + i * 0.13, 0.26, pan=-0.4 + 0.4 * i, rev=0.2)
add('sfx', riser(1.5), 14.4, 0.2, rev=0.3)

# Scènes programmes
def prog_sfx(t0, notes):
    add('hit', impact(1.4, 62, 0.5), t0, 0.5, rev=0.3)
    W(t0, 0.75, 0.4)
    for i, m in enumerate(notes):                       # puces
        add('sfx', blip(m, 0.2, 20), t0 + 1.0 + i * 0.5, 0.3, pan=-0.45, rev=0.35)
        add('sfx', pop(600), t0 + 1.06 + i * 0.5, 0.14, pan=-0.45)
    add('sfx', pop(330), t0 + 2.6, 0.3, pan=-0.4, rev=0.2)
    W(t0 + 6.0, 0.55, 0.26, f0=400, f1=7000, peak=0.9)   # sortie
prog_sfx(16, [81, 84, 86]); prog_sfx(22, [79, 82, 86]); prog_sfx(28, [81, 84, 89])
# S4
for i in range(8): add('sfx', pop(300 + 25 * i, 0.06), 16.55 + i * 0.07, 0.13, pan=0.2 + 0.07 * i)
for i in range(8): add('sfx', tick(3000 + 140 * i, 0.03, 240), 17.5 + i * 0.14, 0.2, pan=0.2 + 0.07 * i, rev=0.2)
W(18.6, 0.4, 0.2); add('sfx', pop(480), 18.55, 0.26, pan=0.6, rev=0.2)
add('sfx', ding(88, 0.9), 19.55, 0.3, pan=0.1, rev=0.5); add('sfx', ding(93, 1.1), 19.66, 0.3, pan=0.1, rev=0.5)   # commande
# S5
add('sfx', ding(86, 0.6), 22.52, 0.26, pan=0.4, rev=0.4); add('sfx', ding(91, 0.6), 22.62, 0.26, pan=0.4, rev=0.4); add('sfx', ding(86, 0.8), 22.72, 0.22, pan=0.4, rev=0.4)
add('sfx', pop(420), 22.75, 0.2, pan=0.0)
for i in range(7): add('sfx', pop(260 + 30 * i, 0.07), 22.95 + i * 0.08, 0.1, pan=-0.05)
for i in range(13): add('sfx', tick(2400 + 90 * i, 0.03, 260), 23.1 + i * 0.1, 0.19, pan=0.45, rev=0.15)
add('sfx', blip(76, 0.16, 16), 24.45, 0.28, pan=0.45, rev=0.3); add('sfx', blip(83, 0.26, 12), 24.58, 0.28, pan=0.45, rev=0.3)   # décroché
add('sfx', ding(84, 0.8), 25.92, 0.26, pan=0.45, rev=0.5); add('sfx', ding(88, 1.0), 26.02, 0.26, pan=0.45, rev=0.5)             # lead qualifié
W(26.45, 0.4, 0.2); add('sfx', ding(91, 1.1), 26.5, 0.26, pan=0.7, rev=0.5)                                                      # RDV
# S6
W(28.7, 0.6, 0.26)
for i in range(30): add('sfx', pop(340 + 22 * i, 0.05), 29.3 + i * 0.06, 0.12, pan=0.0 + 0.012 * i)
add('sfx', pop(440), 29.05, 0.24, pan=0.0)
W(30.55, 0.4, 0.2); add('sfx', thud(0.3, 110), 31.22, 0.45, pan=0.6); add('sfx', pop(700, 0.06), 31.4, 0.16, pan=0.6)
for i, m in enumerate((84, 86, 88, 91, 96)): add('sfx', ding(m, 0.9), 31.5 + i * 0.16, 0.24, pan=0.6, rev=0.5)                   # 5 étoiles
add('sfx', pop(400), 32.35, 0.24, pan=0.3)
n = int(1.0 * SR); p = np.linspace(0, 1, n)
add('sfx', fade(np.sin(2 * np.pi * np.cumsum(300 * 2 ** (2 * p)) / SR) * np.sin(np.pi * p) ** 0.5, 0.02, 0.05), 32.6, 0.09, pan=0.3, rev=0.4)
add('sfx', ding(96, 1.0), 33.55, 0.2, pan=0.3, rev=0.5)
# S7 : les 4 étapes
W(34.0, 0.75, 0.4)
for i, m in enumerate((77, 79, 81, 84)):
    add('sfx', ding(m, 1.6), 35 + i, 0.34, pan=-0.6 + 0.4 * i, rev=0.6)
    add('sfx', pop(360), 35 + i, 0.26, pan=-0.6 + 0.4 * i)
    W(35 + i, 0.4, 0.14)
add('sfx', riser(2.0), 37.86, 0.28, rev=0.3)
# S8 : trois impacts
for i, f in enumerate((50, 56, 62)):
    add('hit', impact(1.6, f, 0.9), 40 + i, 0.7, rev=0.35)
    add('sfx', ding(86 + (0, 2, 5)[i], 1.4), 40 + i, 0.22, pan=-0.5 + 0.5 * i, rev=0.6)
W(40.0, 0.6, 0.34)
# S9 : appel à l'action
W(44.0, 0.75, 0.4); add('hit', impact(1.4, 58, 0.5), 44.0, 0.5, rev=0.3)
W(45.5, 0.45, 0.22); add('sfx', pop(360, 0.12), 45.5, 0.4, rev=0.3)
W(47.6, 1.0, 0.1, f0=900, f1=2500)                      # déplacement du curseur
add('sfx', riser(1.0), 46.9, 0.16, rev=0.3)
add('sfx', tick(1500, 0.02, 420), 47.96, 0.75); add('sfx', tick(950, 0.03, 300), 48.05, 0.5)   # clic
add('hit', impact(3.4, 44, 1.0), 48.0, 1.0, rev=0.5)
add('sfx', shimmer(1.8, 89), 48.5, 0.2, rev=0.7)
# accord final (Fa majeur add9)
add('pad', pad([41, 53, 57, 60, 67, 72], 3.2, bright=1.3, att=0.02, rel=1.6), 48.0, 0.8, rev=0.6)
add('bass', bass(29, 2.6) + 0.6 * bass(41, 2.6), 48.0, 0.5)
for off, m in ((0, 84), (0.0, 81), (0.25, 89), (0.5, 93), (1.0, 96), (1.75, 101)):
    add('bell', bell(m, 2.4, 0.8), 48 + off, 0.24, pan=0.3 * np.sin(m), rev=0.7, dly=0.4)

# ───────────────────────── Effets et mixage ─────────────────────────
# compression latérale (pompage) des nappes/basse/arpège sur chaque kick
sc = np.ones(N)
for t in kicks:
    i = int(t * SR); n = min(int(0.42 * SR), N - i)
    sc[i:i + n] = np.minimum(sc[i:i + n], 1 - 0.62 * np.exp(-np.arange(n) / SR / 0.11))
for k, depth in (('pad', 1.0), ('bass', 1.0), ('arp', 0.5)):
    BUS[k] *= (1 - depth) + depth * sc

# délai ping-pong (croche pointée)
dl = np.zeros((2, N)); d = int(0.375 * SR); src = DLY.copy()
for k in range(1, 6):
    src = np.stack([filt(src[1], 'low', 5200 - 500 * k), filt(src[0], 'low', 5200 - 500 * k)]) * 0.55
    if k * d < N: dl[:, k * d:] += src[:, :N - k * d]

# réverbération à convolution (réponse impulsionnelle synthétique)
def ir(d=2.6, seed=1):
    r = np.random.default_rng(seed); t = tt(d)
    x = r.standard_normal(len(t)) * np.exp(-t * 2.5)
    x = filt(x, 'low', 6500) * 0.7 + filt(x, 'low', 1800) * np.exp(-t * 0.8) * 0.6
    x[:int(0.012 * SR)] = 0
    return x / np.sqrt((x ** 2).sum())
send = REV + dl * 0.5
wet = np.stack([signal.fftconvolve(send[c], ir(seed=c + 1))[:N] for c in range(2)])
wet = np.stack([filt(wet[c], 'high', 180) for c in range(2)])

LEVEL = {'drums': 0.9, 'bass': 0.85, 'pad': 0.8, 'arp': 0.9, 'bell': 0.9, 'sfx': 1.0, 'hit': 1.0}
mix = sum(BUS[k] * g for k, g in LEVEL.items()) + dl * 0.6 + wet * 0.55

# « respiration » : coupure sèche juste avant la révélation de 8,0 s
g = np.ones(N); a, b = int(7.86 * SR), int(8.0 * SR)
g[a:b] = np.linspace(1, 0.0, b - a) ** 2
dry_hit = BUS['hit'].copy()
mix = mix * g + dry_hit * (1 - g)
# fondu final
f0 = int(50.6 * SR); mix[:, f0:] *= np.linspace(1, 0, N - f0) ** 1.5
mix[:, :int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))

mix = np.stack([filt(mix[c], 'high', 32) for c in range(2)])
mix = np.stack([mix[c] - 0.32 * filt(mix[c], 'low', 62) + 0.36 * filt(mix[c], 'high', 4800) for c in range(2)])   # égalisation : moins d'infra, plus d'air
mix = np.tanh(mix * 0.9) / 0.9                          # écrêtage doux
mix /= np.abs(mix).max() / 0.89
out = sys.argv[1] if len(sys.argv) > 1 else 'soundtrack.wav'
wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
print(f'{out} · {DUR:.0f} s · crête {20 * np.log10(np.abs(mix).max()):.1f} dBFS · RMS {20 * np.log10(np.sqrt((mix ** 2).mean())):.1f} dBFS')

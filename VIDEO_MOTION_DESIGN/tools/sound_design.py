"""Voxy Matrix — sound design & music bed, synthesised from scratch (no samples).
Output: 48 kHz stereo WAV, synced to composition.html timeline (120 BPM, 1 bar = 2 s).
Usage: python3 sound_design.py out.wav
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(42)
BEAT = 0.5

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
verb_send = np.zeros((N, 2))   # reverb send from SFX
verb_m = np.zeros((N, 2))      # reverb send from music
kick_env = np.zeros(N)


def t_(d):
    return np.arange(int(SR * d)) / SR


def note(n):  # midi -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def filt(x, kind, f, order=2):
    if isinstance(f, (list, tuple)):
        f = [min(max(v, 20), SR / 2 - 100) for v in f]
    else:
        f = min(max(f, 20), SR / 2 - 100)
    sos = butter(order, f, btype=kind, fs=SR, output='sos')
    return sosfilt(sos, x, axis=0)


def add(buf, t0, sig, gain=1.0, pan=0.0, send=0.0):
    if sig.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4)
        r = np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], axis=1) * np.sqrt(2)
    i0 = int(round(t0 * SR))
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    i1 = min(N, i0 + len(sig))
    if i1 <= i0:
        return
    buf[i0:i1] += sig[: i1 - i0] * gain
    if send:
        (verb_m if buf is music else verb_send)[i0:i1] += sig[: i1 - i0] * gain * send


def env_ad(n, a, d, curve=6.0):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-6), np.exp(-(t - a) / max(d, 1e-6) * (curve / 6)))
    return e


def svf_sweep(x, f_curve, q=0.7, mode='bp'):
    """Per-sample state variable filter with time-varying cutoff."""
    out = np.zeros_like(x)
    lp = bp = 0.0
    for i in range(len(x)):
        f = 2 * np.sin(np.pi * min(f_curve[i], SR / 6) / SR)
        hp = x[i] - lp - q * bp
        bp += f * hp
        lp += f * bp
        out[i] = bp if mode == 'bp' else (lp if mode == 'lp' else hp)
    return out


# ------------------------------------------------------------------ SFX ----
def whoosh(dur=0.7, f0=300, f1=4000, peak=0.6, gain=0.5, pan_sweep=(-0.6, 0.6), t0=0.0):
    n = int(SR * dur)
    x = rng.standard_normal(n)
    tt = np.linspace(0, 1, n)
    fc = f0 * (f1 / f0) ** (np.sin(np.pi * np.clip(tt / peak / 2, 0, 0.5)) if False else tt)
    fc = f0 + (f1 - f0) * np.sin(np.pi * np.clip(tt, 0, 1)) ** 1.5
    y = svf_sweep(x, fc, q=0.5)
    e = np.where(tt < peak, (tt / peak) ** 2.2, ((1 - tt) / (1 - peak)) ** 1.6)
    y = y * e
    y /= np.max(np.abs(y)) + 1e-9
    pans = np.linspace(pan_sweep[0], pan_sweep[1], n)
    l = np.cos((pans + 1) * np.pi / 4)
    r = np.sin((pans + 1) * np.pi / 4)
    return np.stack([y * l, y * r], 1) * np.sqrt(2) * gain


def impact(gain=1.0, big=True):
    d = 2.6 if big else 1.4
    t = t_(d)
    f = 58 * np.exp(-t * 2.2) + 32
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t / (0.9 if big else 0.45))
    sub = np.tanh(sub * 1.6)
    nz = filt(rng.standard_normal(len(t)), 'low', 900) * np.exp(-t / 0.12) * 0.9
    crack = filt(rng.standard_normal(len(t)), 'band', [1800, 7000]) * np.exp(-t / 0.03) * 0.5
    y = sub * 1.0 + nz + crack
    return y / np.max(np.abs(y)) * gain


def riser(dur=2.0, gain=0.5):
    n = int(SR * dur)
    tt = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    fc = 400 * (9000 / 400) ** (tt ** 1.6)
    y = svf_sweep(x, fc, q=0.35)
    y /= np.max(np.abs(y)) + 1e-9
    f = 110 * (880 / 110) ** (tt ** 1.8)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + 0.4 * np.sin(2 * ph * 1.003)) * 0.35
    e = tt ** 2.4
    yl = (y * 0.8 + tone) * e
    yr = (np.roll(y, 37) * 0.8 + tone) * e
    return np.stack([yl, yr], 1) * gain


def pop(f=820, gain=0.35, dur=0.09):
    t = t_(dur)
    fr = f * (1 + 0.7 * np.exp(-t * 60))
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.025)
    return y * gain


def tick(f=3200, gain=0.15):
    t = t_(0.02)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.003)
    y += filt(rng.standard_normal(len(t)), 'high', 4000) * np.exp(-t / 0.0015) * 0.5
    return y * gain


def bell(freqs, gain=0.3, dec=0.9, dur=1.6):
    t = t_(dur)
    y = np.zeros_like(t)
    for i, fq in enumerate(freqs):
        y += np.sin(2 * np.pi * fq * t) * np.exp(-t / (dec / (1 + i * 0.4)))
        y += 0.25 * np.sin(2 * np.pi * fq * 2.76 * t) * np.exp(-t / (dec * 0.15))
    y *= np.minimum(1, t / 0.002)
    return y / len(freqs) * gain


def notif_ding(gain=0.32):
    a = bell([note(88)], gain, 0.5, 1.0)
    b = bell([note(95)], gain * 0.9, 0.7, 1.3)
    out = np.zeros(int(SR * 1.5))
    out[: len(a)] += a
    o = int(0.085 * SR)
    out[o : o + len(b)] += b
    return out


def glitch(gain=0.4):
    t = t_(0.16)
    sq = np.sign(np.sin(2 * np.pi * 95 * t)) * 0.4
    nz = rng.standard_normal(len(t))
    nz = np.repeat(nz[::40], 40)[: len(t)]
    y = (sq + nz * 0.6) * np.exp(-t / 0.05)
    gate = (np.sin(2 * np.pi * 38 * t) > -0.3).astype(float)
    sl = whoosh(0.22, 2000, 9000, 0.3, 1.0)[:, 0]
    out = np.zeros(int(SR * 0.3))
    out[: len(sl)] += sl * 0.6
    o = int(0.07 * SR)
    out[o : o + len(t)] += y * gate
    return filt(out, 'high', 120) * gain


def thud(gain=0.6):
    t = t_(0.5)
    f = 120 * np.exp(-t * 18) + 48
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
    return y * gain


def err_blip(gain=0.22):
    out = np.zeros(int(SR * 0.4))
    for i, n_ in enumerate([76, 70]):
        t = t_(0.14)
        y = np.sin(2 * np.pi * note(n_) * t) * np.exp(-t / 0.05) + 0.3 * np.sin(2 * np.pi * note(n_) * 3 * t) * np.exp(-t / 0.02)
        o = int(i * 0.11 * SR)
        out[o : o + len(t)] += y
    return out * gain


def mouse_click(gain=0.45):
    out = np.zeros(int(SR * 0.12))
    for o_, g in [(0, 1.0), (0.055, 0.6)]:
        t = t_(0.012)
        y = filt(rng.standard_normal(len(t)), 'band', [1500, 6000]) * np.exp(-t / 0.0018)
        o = int(o_ * SR)
        out[o : o + len(t)] += y * g
    return out * gain


def chime_success(gain=0.3):
    out = np.zeros(int(SR * 2.0))
    for i, n_ in enumerate([84, 88, 91, 96]):
        b = bell([note(n_)], 1.0, 0.8, 1.4)
        o = int(i * 0.07 * SR)
        out[o : o + len(b)] += b * (1 - i * 0.12)
    return out * gain


def shimmer(dur=1.6, gain=0.18):
    t = t_(dur)
    y = np.zeros_like(t)
    for n_ in [96, 100, 103, 107, 108]:
        y += np.sin(2 * np.pi * note(n_) * t + rng.uniform(0, 6)) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(5, 9) * t))
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return y * e / 5 * gain


def keyclick(gain=0.12):
    t = t_(0.03)
    y = filt(rng.standard_normal(len(t)), 'band', [2000, 8000]) * np.exp(-t / 0.004)
    y += np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.008) * 0.6
    return y * gain * rng.uniform(0.7, 1.1)


def whistle_down(dur=0.38, gain=0.12):
    t = t_(dur)
    f = 1800 * np.exp(-t * 3.2)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) * gain


def voice_babble(dur, gain=0.05):
    """Formant-ish synthetic voice texture for the AI call (unintelligible)."""
    t = t_(dur)
    f0 = 140 + 25 * np.sin(2 * np.pi * 2.3 * t) + 15 * np.sin(2 * np.pi * 5.1 * t)
    ph = 2 * np.pi * np.cumsum(f0) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    syl = np.clip(np.sin(2 * np.pi * 4.2 * t) * 0.8 + 0.4 * np.sin(2 * np.pi * 1.3 * t), 0, 1) ** 0.7
    y = filt(saw, 'band', [500, 900]) + 0.6 * filt(saw, 'band', [1100, 1900]) + 0.3 * filt(saw, 'band', [2300, 3000])
    y = filt(y, 'band', [300, 3400], order=4)  # telephone band
    return y * syl * gain


# --------------------------------------------------------------- MUSIC -----
def kick(gain=0.9):
    t = t_(0.45)
    f = 48 + 110 * np.exp(-t * 32)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    y += filt(rng.standard_normal(len(t)), 'band', [2500, 6000]) * np.exp(-t / 0.003) * 0.25
    return np.tanh(y * 1.4) * gain


def clap(gain=0.3):
    t = t_(0.3)
    nz = filt(rng.standard_normal(len(t)), 'band', [900, 4000])
    e = np.zeros_like(t)
    for o in [0, 0.011, 0.022]:
        e += np.where(t >= o, np.exp(-(t - o) / 0.006), 0)
    e += np.where(t >= 0.03, np.exp(-(t - 0.03) / 0.09), 0)
    return nz * e * gain


def hat(gain=0.08, dec=0.03):
    t = t_(0.12)
    nz = filt(filt(rng.standard_normal(len(t)), 'high', 7000), 'low', 13000)
    return nz * np.exp(-t / dec) * gain * 0.7


def pluck(n_, dur=0.5, gain=0.12, bright=1.0):
    t = t_(dur)
    f = note(n_)
    y = np.zeros_like(t)
    for h in range(1, 7):
        y += np.sin(2 * np.pi * f * h * t) / h ** 1.25 * np.exp(-t * (4 + h * 4 / bright))
    y *= np.minimum(1, t / 0.003)
    return y * gain


def pad_chord(notes, dur, gain=0.06, cutoff=1400):
    t = t_(dur)
    L = np.zeros_like(t)
    R = np.zeros_like(t)
    for n_ in notes:
        for d in (-0.09, 0.0, 0.11):
            f = note(n_) * 2 ** (d / 12)
            phL = rng.uniform(0, 1)
            phR = rng.uniform(0, 1)
            L += 2 * ((f * t + phL) % 1) - 1
            R += 2 * ((f * 1.0007 * t + phR) % 1) - 1
    a = 0.35
    e = np.minimum(1, t / a) * np.minimum(1, (dur - t) / 0.35)
    L = filt(L, 'low', cutoff, 2) * e
    R = filt(R, 'low', cutoff, 2) * e
    return np.stack([L, R], 1) / len(notes) * gain


def bass_note(n_, dur, gain=0.22):
    t = t_(dur)
    f = note(n_)
    y = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    e = np.minimum(1, t / 0.006) * np.exp(-t / 0.22) * np.minimum(1, (dur - t) / 0.01)
    return np.tanh(y * 1.5) * e * gain


# chord progression (I–V–vi–IV in C) per bar, as (root_midi_bass, pad notes, arp notes)
PROG = [
    (36, [60, 64, 67, 71], [72, 76, 79, 83]),        # Cmaj7
    (43, [59, 62, 67, 69], [71, 74, 79, 81]),        # G6/9-ish
    (45, [60, 64, 69, 71], [72, 76, 81, 83]),        # Am(add9)
    (41, [60, 65, 69, 72], [72, 77, 81, 84]),        # Fmaj7
]
AMIN = (33, [57, 60, 64, 71], [69, 72, 76, 79])      # Am drone for the dark intro


def bar_of(t):
    return int((t - 12) // 2) % 4


def place_drums(a, b, kick_on=True, clap_on=True, hats=True, gain=1.0):
    t = a
    while t < b - 1e-6:
        beat = int(round((t - 0) / BEAT))
        if kick_on:
            add(music, t, kick(0.85 * gain))
            i0 = int(t * SR)
            e = np.exp(-np.arange(int(0.3 * SR)) / SR / 0.09)
            kick_env[i0 : i0 + len(e)] = np.maximum(kick_env[i0 : i0 + len(e)], e[: max(0, min(len(e), N - i0))])
        if clap_on and beat % 2 == 1:
            add(music, t, clap(0.26 * gain), pan=0.05, send=0.25)
        if hats:
            for k in range(4):
                tt = t + k * BEAT / 4
                g = 0.085 if k == 2 else 0.035
                add(music, tt, hat(g * gain, 0.045 if k == 2 else 0.02), pan=0.25 if k % 2 else -0.2)
        t += BEAT


def place_harmony(a, b, chords=None, arp=True, bass=True, pad=True, arp_gain=1.0, cutoff=1800):
    t = a
    while t < b - 1e-6:
        root, padn, arpn = chords if chords else PROG[bar_of(t)]
        if pad:
            add(music, t, pad_chord(padn, 2.0 + 0.3, 0.05, cutoff), send=0.35)
        if bass:
            for k in range(8):
                if k in (0, 3, 4, 6, 7):
                    add(music, t + k * BEAT / 2, bass_note(root, 0.24, 0.2))
        if arp:
            pat = [0, 2, 1, 3, 2, 0, 3, 1]
            for k in range(16):
                n_ = arpn[pat[k % 8]] + (12 if k in (6, 14) else 0)
                g = (0.075 if k % 4 == 0 else 0.05) * arp_gain
                add(music, t + k * BEAT / 4, pluck(n_, 0.45, g, 1.0), pan=0.35 * np.sin(k * 0.9), send=0.3)
        t += 2.0


# ---------------- ARRANGEMENT ----------------
# Dark intro 0–12: Am drone + clock ticks + low pulse
add(music, 0.0, pad_chord(AMIN[1], 12.0, 0.075, 800), send=0.4)
add(music, 0.0, pad_chord([45], 12.0, 0.06, 300))
for i in range(24):
    tt = i * BEAT
    if tt < 11.8:
        add(sfx, tt, tick(2600 if i % 2 == 0 else 2100, 0.07 if tt < 4 else 0.04), pan=-0.3 if i % 2 else 0.3)
for tt in np.arange(0, 11.8, 2.0):
    add(music, tt, thud(0.45))
    add(music, tt + 0.5 * 1.5, thud(0.22))
# 4–11.8: muted pluck ostinato in A minor
for k, tt in enumerate(np.arange(4.0, 11.75, BEAT / 2)):
    n_ = [57, 64, 60, 64, 57, 64, 62, 64][k % 8]
    add(music, tt, pluck(n_, 0.3, 0.05 if tt < 8 else 0.065, 0.5), pan=0.3 * np.sin(k), send=0.3)

# Groove 12–48
place_harmony(12.0, 48.0)
place_drums(12.0, 16.0, clap_on=False, hats=False)
place_drums(16.0, 48.0)
# Breakdown 48–51.85
place_harmony(48.0, 52.0, chords=PROG[2], bass=False, arp_gain=1.2, cutoff=1300)
add(music, 48.0, pad_chord([33, 45], 3.8, 0.09, 260))
# Drop 52–56
place_harmony(52.0, 56.0)
place_drums(52.0, 56.0)
# Outro 56–60: resolve on Cmaj9, long tail
add(music, 56.0, pad_chord([48, 55, 60, 64, 67, 71, 74], 4.0, 0.07, 2200), send=0.5)
add(music, 56.0, bass_note(36, 1.6, 0.25))
for k, n_ in enumerate([72, 76, 79, 83, 86]):
    add(music, 56.0 + k * 0.125, pluck(n_, 1.8, 0.07, 1.4), pan=-0.4 + k * 0.2, send=0.5)

# ---------------- SFX TIMELINE ----------------
W = lambda t0, **kw: add(sfx, t0, whoosh(**kw), send=0.25)
# S1 hook
W(0.05, dur=0.6, f0=200, f1=2500, gain=0.12)
W(0.48, dur=0.6, f0=200, f1=2500, gain=0.12)
add(sfx, 1.2, shimmer(0.8, 0.08), send=0.4)
for tt in np.arange(1.9, 3.3, 0.06):
    add(sfx, tt, tick(1800 + (tt - 1.9) * 300, 0.05), pan=0.1)
add(sfx, 2.4, whoosh(1.3, 3000, 9000, 0.35, 0.16, (0.0, 0.5)), send=0.6)  # evaporation air
add(sfx, 3.3, thud(0.55))
add(sfx, 3.3, err_blip(0.2), send=0.2)
W(3.55, dur=0.65, f0=300, f1=5000, gain=0.35)
# S2 problem
for i in range(3):
    add(sfx, 4.35 + i * 0.22, pop(620 + i * 90, 0.28), pan=-0.5 + i * 0.5, send=0.15)
for i in range(3):
    add(sfx, 5.55 + i * 0.32, glitch(0.42), pan=-0.5 + i * 0.5, send=0.15)
    add(sfx, 5.6 + i * 0.32, thud(0.35))
W(7.5, dur=0.7, f0=300, f1=5500, gain=0.35)
# S3 question
for i, tt in enumerate([8.08, 8.63, 9.18]):
    W(tt, dur=0.6, f0=250, f1=3000 + i * 500, gain=0.12)
add(sfx, 9.9, riser(2.0, 0.55), send=0.3)
# S4 logo
add(sfx, 12.0, impact(1.0, True), send=0.45)
add(sfx, 12.0, shimmer(2.0, 0.2), send=0.6)
for i in range(9):
    add(sfx, 12.03 + i * 0.045, pop(900 + (i % 3) * 140, 0.11, 0.06), pan=-0.6 + (i % 3) * 0.6)
add(sfx, 12.85, whoosh(0.8, 800, 7000, 0.4, 0.12, (-0.4, 0.4)), send=0.4)
add(sfx, 13.9, shimmer(1.0, 0.16), send=0.6)
for i in range(3):
    add(sfx, 14.05 + i * 0.12, pop(1050 + i * 120, 0.16), pan=-0.4 + i * 0.4)
W(15.5, dur=0.6, f0=300, f1=5000, gain=0.3)
# S5 value
add(sfx, 16.5, whoosh(0.9, 200, 1800, 0.5, 0.14), send=0.3)
for k, tt in enumerate(np.arange(16.9, 18.3, 0.07)):
    add(sfx, tt, tick(1500 + k * 70, 0.06))
add(sfx, 18.3, bell([note(84), note(91)], 0.26, 0.9, 1.8), send=0.5)
W(19.5, dur=0.6, f0=300, f1=5200, gain=0.32)
# S6 ecom
add(sfx, 20.12, whoosh(0.9, 150, 2200, 0.45, 0.32, (0.6, 0.1)), send=0.2)
for i in range(6):
    add(sfx, 21.0 + i * 0.32, pop(1200 + i * 60, 0.1, 0.07), pan=0.3 + (i % 3) * 0.2, send=0.2)
    add(sfx, 21.05 + i * 0.32, shimmer(0.4, 0.05), pan=0.4, send=0.3)
for i in range(3):
    add(sfx, 23.35 + i * 0.6, notif_ding(0.24), pan=0.45, send=0.3)
    add(sfx, 23.33 + i * 0.6, whoosh(0.25, 800, 4000, 0.4, 0.06, (0.7, 0.4)))
W(25.5, dur=0.6, f0=300, f1=5200, gain=0.32)
# S7 outbound
add(sfx, 26.05, whoosh(0.9, 150, 2200, 0.45, 0.32, (-0.6, -0.1)), send=0.2)
for i in range(12):
    add(sfx, 27.0 + i * 0.24, pop(700 + (i % 4) * 110, 0.12, 0.07), pan=-0.6 + (i % 5) * 0.2)
add(sfx, 27.6, whoosh(0.4, 400, 3000, 0.4, 0.1, (-0.1, 0.0)))
add(sfx, 27.72, voice_babble(2.7, 0.07), pan=-0.1)
add(sfx, 30.45, chime_success(0.2), pan=-0.1, send=0.3)
W(31.5, dur=0.6, f0=300, f1=5200, gain=0.32)
# S8 drive-to-store
add(sfx, 32.1, whoosh(0.9, 150, 2200, 0.45, 0.32, (0.6, 0.1)), send=0.2)
for i in range(5):
    add(sfx, 32.6 + i * 0.08, pop(950 + i * 80, 0.08, 0.05), pan=0.5)
for k in range(len('plombier montpellier')):
    add(sfx, 32.7 + k * 0.05 + rng.uniform(0, 0.012), keyclick(0.11), pan=0.2)
add(sfx, 33.75, whistle_down(0.36, 0.1), pan=0.3)
add(sfx, 34.1, thud(0.6))
add(sfx, 34.1, pop(520, 0.3, 0.12), pan=0.3, send=0.3)
add(sfx, 34.55, whoosh(0.85, 300, 3500, 0.5, 0.16, (0.2, 0.5)))
for k, tt in enumerate(np.arange(34.7, 36.2, 0.075)):
    add(sfx, tt, tick(1700 + k * 40, 0.04), pan=0.3)
add(sfx, 35.4, pop(1300, 0.18), pan=0.3, send=0.3)
add(sfx, 35.55, notif_ding(0.24), pan=0.5, send=0.3)
W(37.5, dur=0.6, f0=300, f1=5200, gain=0.32)
# S9 proof
add(sfx, 38.3, whoosh(0.8, 120, 1500, 0.5, 0.2), send=0.3)
for k, tt in enumerate(np.arange(38.5, 40.3, 0.055)):
    add(sfx, tt, tick(1200 + k * 45, 0.05 + k * 0.0006))
t = t_(1.9)
f = 220 * (880 / 220) ** (t / 1.9)
glide = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 1.9) ** 2 * 0.045
add(sfx, 38.7, glide, pan=0.4, send=0.5)
add(sfx, 40.3, impact(0.55, False), send=0.4)
add(sfx, 40.3, bell([note(84), note(88), note(91)], 0.18, 1.0, 1.8), send=0.5)
for i in range(2):
    add(sfx, 39.6 + i * 0.15, pop(800 + i * 150, 0.13), pan=-0.4)
add(sfx, 40.6, pop(1400, 0.14), pan=0.4)
W(43.5, dur=0.6, f0=300, f1=5200, gain=0.3)
# S10 process
add(sfx, 44.45, whoosh(1.5, 300, 2500, 0.5, 0.12, (-0.6, 0.6)), send=0.3)
for i, n_ in enumerate([84, 88, 91]):
    add(sfx, 44.5 + i * 0.5, pop(note(n_) / 2, 0.22, 0.1), pan=-0.6 + i * 0.6, send=0.3)
    add(sfx, 44.52 + i * 0.5, bell([note(n_)], 0.1, 0.5, 0.9), pan=-0.6 + i * 0.6, send=0.4)
W(47.5, dur=0.6, f0=300, f1=5200, gain=0.3)
# S11 scarcity
for i, n_ in enumerate([72, 74, 76, 79, 81]):
    add(sfx, 48.7 + i * 0.12, pop(note(n_), 0.14, 0.08), pan=-0.6 + i * 0.3)
    add(sfx, 49.0 + i * 0.12, bell([note(n_ + 12)], 0.07, 0.4, 0.8), pan=-0.6 + i * 0.3, send=0.5)
add(sfx, 50.0, riser(1.9, 0.5), send=0.3)
# S12 CTA
add(sfx, 52.0, impact(0.95, True), send=0.45)
add(sfx, 52.0, shimmer(1.8, 0.16), send=0.6)
add(sfx, 53.25, pop(700, 0.22, 0.1), send=0.2)
add(sfx, 53.9, whoosh(0.95, 200, 1500, 0.5, 0.07, (0.7, 0.1)))
add(sfx, 54.95, mouse_click(0.5))
add(sfx, 55.2, chime_success(0.26), send=0.4)
W(55.95, dur=0.7, f0=300, f1=5200, gain=0.3)
add(sfx, 56.35, impact(0.7, True), send=0.5)
for i in range(9):
    add(sfx, 56.36 + i * 0.045, pop(900 + (i % 3) * 140, 0.08, 0.06), pan=-0.6 + (i % 3) * 0.6)
add(sfx, 57.6, shimmer(1.6, 0.14), send=0.7)

# ---------------- PRE-DROP GAPS (silence before impacts) ----------------
def gap(buf, a, b, fade=0.03):
    i0, i1 = int(a * SR), int(b * SR)
    f = int(fade * SR)
    g = np.ones(N)
    g[i0 : i0 + f] = np.linspace(1, 0, f)
    g[i0 + f : i1] = 0
    buf *= g[:, None]

gap(music, 11.78, 12.0)
gap(music, 51.8, 52.0)

# ---------------- MIX ----------------
# sidechain music (except kick itself is inside – acceptable pumping)
duck = 1 - 0.45 * kick_env
music_sc = music * duck[:, None]

# reverb: synthetic stereo IR
ir_t = t_(2.4)
irL = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55)
irR = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55)
irL = filt(irL, 'low', 6000); irR = filt(irR, 'low', 6000)
irL[: int(0.012 * SR)] = 0; irR[: int(0.017 * SR)] = 0
irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))
def reverb(snd):
    snd = filt(snd, 'high', 250)
    return np.stack([fftconvolve(snd[:, 0], irL)[:N], fftconvolve(snd[:, 1], irR)[:N]], 1) * 0.55

wet_m, wet_s = reverb(verb_m), reverb(verb_send)

# stereo delay on music (dotted 8th)
dly = int(0.375 * SR)
md = np.zeros_like(music_sc)
md[dly:] = filt(music_sc[:-dly, ::-1], 'band', [600, 5000]) * 0.12

stem_music = filt(music_sc * 0.9 + md + wet_m, 'high', 28)
stem_sfx = filt(sfx * 1.0 + wet_s, 'high', 28)
fo = int(1.6 * SR)
fi = int(0.02 * SR)
for st in (stem_music, stem_sfx):
    st[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    st[:fi] *= np.linspace(0, 1, fi)[:, None]
mix = stem_music + stem_sfx
g = 1.0 / (np.max(np.abs(mix)) + 1e-9)
# gentle glue: soft clip
mix = np.tanh(mix * g * 1.6) / np.tanh(1.6) * 0.89
out = sys.argv[1] if len(sys.argv) > 1 else 'sound.wav'
wavfile.write(out, SR, (mix * 32767).astype(np.int16))
# stems (same gain staging, no soft clip) for the voice-over mix
base = out[:-4] if out.endswith('.wav') else out
wavfile.write(base + '_music.wav', SR, (stem_music * g * 0.89).astype(np.float32))
wavfile.write(base + '_sfx.wav', SR, (stem_sfx * g * 0.89).astype(np.float32))
print('ok', mix.shape, float(np.max(np.abs(mix))))

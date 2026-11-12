"""Mixe la voix off sur la vidéo.

Entrées :
  voix_off/cues.json            timecodes + texte de chaque réplique
  voix_off/prises/NN.wav        une prise par réplique (NN = id du cue), n'importe quel format lu par ffmpeg
  build/sound_raw_music.wav     stem musique   (python3 tools/sound_design.py build/sound_raw.wav)
  build/sound_raw_sfx.wav       stem effets
  VOXY_MATRIX_Motion_16x9.mp4   vidéo (sa piste image est copiée telle quelle)

Sortie : VOXY_MATRIX_Motion_16x9_VO.mp4 (+ build/voix_seule.wav, build/mix_vo.wav)

Usage : python3 tools/mix_voiceover.py
"""
import json, os, subprocess, sys, glob
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
N = int(SR * 60)
os.chdir(ROOT)


def load(path, ch=1, filters=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if filters:
        cmd += ['-af', filters]
    cmd += ['-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-']
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x.reshape(-1, ch) if ch > 1 else x


def trim(x, thr_db=-42, pre=0.035, post=0.12):
    fr = int(0.01 * SR)
    n = len(x) // fr
    rms = np.sqrt(np.mean(x[: n * fr].reshape(n, fr) ** 2, 1) + 1e-12)
    db = 20 * np.log10(rms / (rms.max() + 1e-12))
    on = np.where(db > thr_db)[0]
    if len(on) == 0:
        return x
    a = max(0, on[0] * fr - int(pre * SR))
    b = min(len(x), (on[-1] + 1) * fr + int(post * SR))
    return x[a:b]


def smooth_env(x, att=0.012, rel=0.35):
    hop = 48
    n = len(x) // hop
    e = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, 1))
    a, r = np.exp(-hop / (att * SR)), np.exp(-hop / (rel * SR))
    out = np.zeros_like(e)
    v = 0.0
    for i, s in enumerate(e):
        v = a * v + (1 - a) * s if s > v else r * v + (1 - r) * s
        out[i] = v
    return np.interp(np.arange(len(x)), np.arange(n) * hop, out)


cues = json.load(open('voix_off/cues.json'))
vo = np.zeros(N)
report = []
for k, c in enumerate(cues):
    files = sorted(glob.glob(f"voix_off/prises/{c['id']}.*"))
    if not files:
        report.append(f"{c['id']}  MANQUANTE")
        continue
    x = trim(load(files[0]))
    slot = c['end'] - c['start']
    nxt = cues[k + 1]['start'] - 0.12 if k + 1 < len(cues) else 59.6
    room = min(nxt, c.get('hard_end', 99)) - c['start']
    L = len(x) / SR
    tempo = 1.0
    if L > slot:
        # déborde un peu du créneau : légère accélération (inaudible jusqu'à ~6 %)
        tempo = min(L / slot, 1.06)
        if L / tempo > room:      # empiéterait sur la réplique / l'impact suivant
            tempo = min(L / room, 1.13)
    if tempo > 1.0:
        x = trim(load(files[0], filters=f'atempo={tempo:.4f}'))
    i0 = int((c['start'] - 0.035) * SR)
    seg = x[: max(0, min(len(x), N - i0))]
    vo[i0 : i0 + len(seg)] += seg
    report.append(f"{c['id']}  {L:5.2f}s → {len(x)/SR:5.2f}s (créneau {slot:.2f}s, tempo ×{tempo:.3f})" + ('  ⚠ déborde' if len(x) / SR > room + 0.15 else ''))

print('\n'.join(report))
os.makedirs('build', exist_ok=True)
wavfile.write('build/voix_brute.wav', SR, vo.astype(np.float32))

# Chaîne "studio" : nettoyage, EQ broadcast, de-esser, compression, limiteur
chain = ','.join([
    'highpass=f=75:p=2',
    'equalizer=f=220:t=q:w=1.0:g=-2',      # désépaissit
    'equalizer=f=3200:t=q:w=1.3:g=2.5',    # présence / intelligibilité
    'treble=g=3:f=9500',                    # air
    'deesser=i=0.35:m=0.5:f=0.5',
    'acompressor=threshold=-22dB:ratio=3.2:attack=4:release=90:makeup=4',
    'alimiter=limit=0.89:attack=3:release=40',
])
vo = load('build/voix_brute.wav', filters=chain)[:N]
vo = np.pad(vo, (0, N - len(vo)))
speech = np.abs(vo) > 1e-4
rms = np.sqrt(np.mean(vo[speech] ** 2)) if speech.any() else 1
vo *= 10 ** (-17 / 20) / rms                   # voix à ~ -17 dBFS RMS pendant la parole
wavfile.write('build/voix_seule.wav', SR, vo.astype(np.float32))

music = load('build/sound_raw_music.wav', 2)[:N]
sfx = load('build/sound_raw_sfx.wav', 2)[:N]
env = smooth_env(vo)
env = np.clip(env / (np.percentile(env[env > 1e-4], 70) + 1e-9), 0, 1) if (env > 1e-4).any() else env
music *= (1 - 0.62 * env)[:, None]             # ducking musique ≈ -8 dB sous la voix
sfx *= (1 - 0.75 * env)[:, None]               # effets ≈ -12 dB sous la voix (la voix est prioritaire)
sos = butter(2, [1500, 4500], btype='bandstop', fs=SR, output='sos')
carve = sosfilt(sos, music, axis=0)            # creuse la bande de la voix dans la musique
music = music * (1 - 0.35 * env)[:, None] + carve * (0.35 * env)[:, None]
mix = music * 0.82 + sfx * 0.9 + np.stack([vo, vo], 1)
wavfile.write('build/mix_vo.wav', SR, mix.astype(np.float32))

subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'VOXY_MATRIX_Motion_16x9.mp4', '-i', 'build/mix_vo.wav',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-af', 'alimiter=limit=0.93:level=false,loudnorm=I=-14:TP=-1:LRA=8', '-ar', '48000',
                '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest',
                'VOXY_MATRIX_Motion_16x9_VO.mp4'], check=True)
print('✓ VOXY_MATRIX_Motion_16x9_VO.mp4')

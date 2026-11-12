"""Génère la voix off avec Fish Speech 1.5 (modèle open source de Fish Audio), en local.

Pour chaque réplique de voix_off/cues.json :
  1. génère N prises en clonant la voix de référence (même timbre sur toutes les répliques),
  2. décode en audio,
  3. contrôle chaque prise (transcription Whisper → taux d'erreur, durée vs créneau),
  4. garde la meilleure dans voix_off/prises/NN.wav.

À lancer avec le Python de l'environnement Fish Speech :
  python voix_off/fish/generate_vo.py --fish-src <fish-speech> --ckpt <fish-speech-1.5> \
      --ref-codes voix_off/fish/voix_reference.npy --ref-text "texte de la référence" [--takes 3] [--only 04,09]
"""
import argparse, json, os, shutil, subprocess, sys, glob
import numpy as np, librosa

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from qa import analyse  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--fish-src', required=True)
ap.add_argument('--ckpt', required=True)
ap.add_argument('--ref-codes', required=True)
ap.add_argument('--ref-text', required=True)
ap.add_argument('--takes', type=int, default=3)
ap.add_argument('--seed', type=int, default=1234)
ap.add_argument('--only', default='')
a = ap.parse_args()

cues = json.load(open(os.path.join(ROOT, 'voix_off/cues.json')))
only = set(a.only.split(',')) if a.only else None
work = os.path.join(ROOT, 'build/fish_takes')
out_dir = os.path.join(ROOT, 'voix_off/prises')
os.makedirs(work, exist_ok=True); os.makedirs(out_dir, exist_ok=True)
decoder = glob.glob(os.path.join(a.ckpt, 'firefly-gan-*.pth'))[0]
report = []


def speech_len(path):
    y, sr = librosa.load(path, sr=16000)
    db = librosa.amplitude_to_db(librosa.feature.rms(y=y, frame_length=320, hop_length=160)[0], ref=np.max)
    on = np.where(db > -42)[0]
    return (on[-1] - on[0]) * 0.01 if len(on) else 0.0


for c in cues:
    if only and c['id'] not in only:
        continue
    text = c.get('tts', c['text'])
    d = os.path.join(work, c['id'])
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    subprocess.run([sys.executable, '-m', 'fish_speech.models.text2semantic.inference',
                    '--text', text, '--prompt-text', a.ref_text, '--prompt-tokens', os.path.abspath(a.ref_codes),
                    '--checkpoint-path', a.ckpt, '--device', 'cpu', '--seed', str(a.seed + int(c['id'])),
                    '--num-samples', str(a.takes), '--chunk-length', '400', '--output-dir', d],
                   cwd=a.fish_src, check=True, capture_output=True)
    takes = []
    for i in range(a.takes):
        wav = os.path.join(d, f'take_{i}.wav')
        subprocess.run([sys.executable, '-m', 'fish_speech.models.vqgan.inference', '-i', os.path.join(d, f'codes_{i}.npy'),
                        '-o', wav, '--checkpoint-path', decoder, '--device', 'cpu'],
                       cwd=a.fish_src, check=True, capture_output=True)
        q = analyse(c['text'], wav)
        q['speech'] = round(speech_len(wav), 2)
        takes.append((wav, q))
    slot = c['end'] - c['start']
    best_wer = min(q['wer'] for _, q in takes)
    ok = [t for t in takes if t[1]['wer'] <= best_wer + 0.05]
    # parmi les prises les mieux articulées : celle qui tient dans le créneau, au débit le plus naturel
    ok.sort(key=lambda t: (t[1]['speech'] > slot * 1.10, abs(t[1]['speech'] - slot * 0.88)))
    wav, q = ok[0]
    shutil.copy(wav, os.path.join(out_dir, f"{c['id']}.wav"))
    line = f"{c['id']}  retenue={os.path.basename(wav)}  wer={q['wer']}  parole={q['speech']}s/créneau {slot:.2f}s  « {q['hyp']} »"
    print(line, flush=True)
    report.append({'id': c['id'], 'chosen': os.path.basename(wav), 'takes': [q for _, q in takes]})

json.dump(report, open(os.path.join(work, 'rapport.json'), 'w'), ensure_ascii=False, indent=1)

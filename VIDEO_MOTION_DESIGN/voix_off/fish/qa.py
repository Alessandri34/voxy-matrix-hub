"""QA objective d'une prise de voix : transcription Whisper (WER vs texte attendu),
hauteur (F0 médiane), débit, durée, crête. Usage: python qa.py ref_text wav [wav...]"""
import sys, re, unicodedata
import numpy as np, librosa
from faster_whisper import WhisperModel

def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.replace('300', 'trois cents').replace('%', ' pour cent').replace('btp', 'b t p').replace('ia', 'i a')
    return re.sub(r"[^a-z0-9 ]+", ' ', s.replace("'", ' ')).split()

def wer(ref, hyp):
    r, h = norm(ref), norm(hyp)
    d = np.zeros((len(r) + 1, len(h) + 1), int); d[:, 0] = range(len(r) + 1); d[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i-1, j] + 1, d[i, j-1] + 1, d[i-1, j-1] + (r[i-1] != h[j-1]))
    return d[-1, -1] / max(1, len(r))

_model = None
def model():
    global _model
    if _model is None:
        _model = WhisperModel('small', device='cpu', compute_type='int8')
    return _model

def analyse(ref, path):
    y, sr = librosa.load(path, sr=16000)
    segs, _ = model().transcribe(y, language='fr', beam_size=5)
    hyp = ' '.join(s.text for s in segs).strip()
    f0, vf, _ = librosa.pyin(y, fmin=65, fmax=400, sr=sr)
    f0 = f0[vf] if np.any(vf) else np.array([np.nan])
    dur = len(y) / sr
    return dict(file=path.split('/')[-1], dur=round(dur, 2), wer=round(wer(ref, hyp), 3),
                f0=round(float(np.nanmedian(f0)), 1), f0_iqr=round(float(np.nanpercentile(f0, 75) - np.nanpercentile(f0, 25)), 1),
                peak=round(float(np.max(np.abs(y))), 2), hyp=hyp)

if __name__ == '__main__':
    ref = sys.argv[1]
    for p in sys.argv[2:]:
        print(analyse(ref, p))

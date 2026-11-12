"""Génère les sous-titres SRT de la voix off depuis voix_off/cues.json."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cues = json.load(open(os.path.join(ROOT, 'voix_off/cues.json')))
ts = lambda t: f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(round(t%1*1000)):03d}"
with open(os.path.join(ROOT, 'VOXY_MATRIX_sous-titres.srt'), 'w', encoding='utf-8') as f:
    for i, c in enumerate(cues, 1):
        f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n\n")
print('✓ VOXY_MATRIX_sous-titres.srt')

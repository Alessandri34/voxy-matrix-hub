#!/usr/bin/env python3
"""Genere INDEX.md : une ligne par fichier, pour localiser sans ouvrir.

Le cout en lecture de ce projet vient des documents, pas du code : 1,4 Mo de
Markdown et HTML contre 49 Ko de code. Un graphe de code n'y change rien ;
un index qui tient en quelques Ko, si — il evite d'ouvrir un fichier de
260 Ko pour verifier ce qu'il contient.
"""
import os, re, subprocess, html

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)

IGNORE = ('.DS_Store',)
BINAIRE = ('.jpg', '.png', '.jpeg', '.webp', '.ico', '.pdf', '.zip')

def resume(chemin):
    """Premiere ligne de titre d'un fichier, sans le lire en entier."""
    ext = os.path.splitext(chemin)[1].lower()
    if ext in BINAIRE:
        return ''
    try:
        with open(chemin, encoding='utf8', errors='replace') as f:
            tete = f.read(4000)
    except OSError:
        return ''
    if ext == '.md':
        m = re.search(r'^#\s+(.+)$', tete, re.M)
        if m:
            return re.sub(r'[`*]', '', m.group(1)).strip()[:95]
        m = re.search(r'^>\s*(.+)$', tete, re.M)
        return re.sub(r'[`*>]', '', m.group(1)).strip()[:95] if m else ''
    if ext in ('.html', '.htm'):
        m = re.search(r'<title>(.*?)</title>', tete, re.S | re.I)
        if m:
            return html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()[:95]
        m = re.search(r'<h1[^>]*>(.*?)</h1>', tete, re.S | re.I)
        return html.unescape(re.sub(r'<[^>]+>|\s+', ' ', m.group(1))).strip()[:95] if m else ''
    if ext == '.json':
        # un JSON n'a pas de titre : on decrit sa forme, pas son premier champ
        try:
            import json
            d = json.load(open(chemin, encoding='utf8'))
        except Exception:
            return 'JSON'
        if isinstance(d, list):
            cles = sorted(d[0])[:4] if d and isinstance(d[0], dict) else []
            return f'{len(d)} entrees' + (f' · champs : {", ".join(cles)}…' if cles else '')
        if isinstance(d, dict):
            return f'{len(d)} cles : ' + ', '.join(list(d)[:5])[:70] + '…'
        return 'JSON'
    # code : le premier commentaire de tete fait office de resume
    for ligne in tete.split('\n')[:6]:
        l = ligne.strip().lstrip('#/*" ').strip()
        if len(l) > 18 and not l.startswith(('!', '-*-', 'coding')):
            return l[:95]
    return ''

fichiers = [f for f in subprocess.run(['git', 'ls-files'], capture_output=True,
                                      text=True).stdout.split('\n')
            if f and not f.endswith(IGNORE)]

groupes = {}
for f in fichiers:
    tete = f.split('/')[0] if '/' in f else '(racine)'
    groupes.setdefault(tete, []).append(f)

total_ko = sum(os.path.getsize(f) for f in fichiers if os.path.exists(f)) // 1024
lignes = [
    '# INDEX — carte du projet',
    '',
    f'> Genere par `outils/index-projet.py`. **{len(fichiers)} fichiers · {total_ko} Ko.**',
    '> Une ligne par fichier : de quoi localiser sans ouvrir. Relancer apres tout ajout.',
    '',
]

for tete in sorted(groupes):
    fs = sorted(groupes[tete])
    poids = sum(os.path.getsize(f) for f in fs if os.path.exists(f)) // 1024
    lignes += [f'## {tete} — {len(fs)} fichiers, {poids} Ko', '',
               '| Ko | Fichier | Contenu |', '|---:|---|---|']
    for f in fs:
        ko = (os.path.getsize(f) // 1024) if os.path.exists(f) else 0
        court = f[len(tete) + 1:] if f.startswith(tete + '/') else f
        lignes.append(f'| {ko} | `{court}` | {resume(f) or "—"} |')
    lignes.append('')

open('INDEX.md', 'w', encoding='utf8').write('\n'.join(lignes))
print(f'INDEX.md : {len(fichiers)} fichiers, {total_ko} Ko indexes')
print(f'  taille de l index : {os.path.getsize("INDEX.md")//1024} Ko')

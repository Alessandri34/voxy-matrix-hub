#!/usr/bin/env python3
"""Extrait le contenu des annonces depuis le HTML rendu de la bibliotheque."""
import re, html, json, glob, os

CIBLES = {'122097448364017483':'Youdji',
          '1146053731933464':"L'agence Paid",
          '513744841823424':"L'agence Short"}

def texte(h):
    # On retire ce qui ne se lit pas, puis on marque les frontieres de bloc
    h = re.sub(r'<(script|style|svg)[^>]*>.*?</\1>', ' ', h, flags=re.S|re.I)
    h = re.sub(r'<br\s*/?>', '\n', h, flags=re.I)
    h = re.sub(r'</(div|p|li|h\d|span|a)>', '\n', h, flags=re.I)
    h = re.sub(r'<[^>]+>', '', h)
    h = html.unescape(h)
    h = re.sub(r'[ \t ]+', ' ', h)
    h = re.sub(r'\n\s*\n+', '\n', h)
    return '\n'.join(l.strip() for l in h.split('\n') if l.strip())

sortie = {}
for f in sorted(glob.glob('rendu-*.html')):
    pid = re.search(r'rendu-(\d+)', f).group(1)
    nom = CIBLES[pid]
    t = texte(open(f, encoding='utf8', errors='ignore').read())
    open(f'texte-{pid}.txt','w',encoding='utf8').write(t)

    # Chaque annonce commence a « ID dans la bibliotheque »
    bouts = re.split(r'(?=ID dans la biblioth)', t)
    annonces = []
    for b in bouts[1:]:
        a = {}
        m = re.search(r'ID dans la biblioth[èe]que\s*:?\s*(\d+)', b)
        a['id'] = m.group(1) if m else None
        m = re.search(r'D[ée]but de diffusion le ([^\n]+)', b)
        a['debut'] = m.group(1).strip() if m else None
        m = re.search(r'Plateformes?\s*\n?([^\n]*)', b)
        a['plateformes'] = m.group(1).strip() if m else None
        m = re.search(r'(\d+)\s*publicit[ée]s? utilisent ce texte et cet [ée]l[ée]ment visuel', b)
        a['variantes'] = int(m.group(1)) if m else 1
        a['categorie'] = 'Emploi/Logement/Crédit' if 'Cat[ée]gorie' in b else None
        a['brut'] = b[:2600]
        annonces.append(a)
    sortie[nom] = {'page_id': pid, 'nb': len(annonces), 'annonces': annonces}
    print(f'{nom:<16} {len(annonces):>2} annonces · texte {len(t)} o')

json.dump(sortie, open('annonces.json','w',encoding='utf8'), ensure_ascii=False, indent=1)

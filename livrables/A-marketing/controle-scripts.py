#!/usr/bin/env python3
"""Controle de conformite des scripts, avant livraison."""
import json, re, sys, unicodedata
from collections import Counter

# Le chemin etait code en dur sur un fichier qui n'existe pas sous ce nom :
# le controleur ne tournait que si on renommait le lot a la main.
FICHIER = sys.argv[1] if len(sys.argv) > 1 else 'A2_scripts.json'
S = json.load(open(FICHIER, encoding='utf8'))

def plat(t):
    return unicodedata.normalize('NFD', t.lower()).encode('ascii','ignore').decode()

BANNIES = ['100 % finance','100% finance','sans reste a charge','machine a cash',
           'paravent','sans depenser un centime','ne vous coute rien',
           'entierement finance','formation offerte','reste a charge nul']
# Promesses de resultat, meme implicites
PROMESSES = [r'\bgaranti', r'vous (?:gagnerez|aurez|obtiendrez|doublerez)',
             r'\+\s*\d+\s*%', r'x\s*\d+\s+(?:vos|votre|plus)',
             r'(?:premiere|1re) place', r'assure(?:z|r)-vous d\'etre',
             # G1 : on enseigne a mesurer, jamais a obtenir
             r'(?:plus|davantage) de (?:clients|chiffre|revenus?|ventes)\b(?! ne)',
             r'(?:augmente|fera augmenter|fait augmenter) (?:votre|ton) (?:ca|chiffre)',
             r'(?:usine|machine) a ',
             # G2 : vocabulaire de domination
             r'\bdomination\b', r'\btop 1 ?%', r'\bhack\b']
# Taux officiels admis (CLAUDE.md §5) — tout autre montant en € est suspect
TAUX_OK = {'42','35','25','20','80','19','24','3 000','5 000','600','900','2 500'}

err, warn = [], []

for s in S:
    tout = ' '.join(d for _, d, _ in s['temps'])
    bas = plat(tout)
    ref = s['id']

    # 1. Formulations bannies
    for m in BANNIES:
        if m in bas:
            err.append(f'{ref} formulation bannie : « {m} »')

    # 2. Promesses de resultat
    for p in PROMESSES:
        if re.search(p, bas):
            err.append(f'{ref} promesse de resultat : /{p}/')

    # 3. Montants en euros hors taux de financeur
    for m in re.finditer(r'(\d[\d\s ]{0,6})\s*euros?\b', tout):
        v = m.group(1).strip()
        if v not in TAUX_OK:
            warn.append(f'{ref} montant a verifier : « {v} euros »')

    # 4. Les 5 temps, dans l'ordre
    roles = [r for r, _, _ in s['temps']]
    attendu = ['Accroche','Ancrage','Transmission','Nuance','Sortie']
    if roles != attendu:
        err.append(f'{ref} arc incomplet : {roles}')

    # 5. Le temps 5 ne doit porter aucune proposition commerciale
    sortie = plat(s['temps'][-1][1])
    for mot in ['reserve','reservez','contactez-nous','nos formations','devis',
                'inscrivez','prenez rendez-vous','appelez-nous']:
        if mot in sortie:
            err.append(f'{ref} proposition commerciale en sortie : « {mot} »')

    # 6. Le don est-il complet ? heuristique : une action faisable est nommee
    actions = ['ouvrez','regardez','posez','listez','cochez','notez','demandez',
               'faites','appelez','verifiez','taguez','passez','multipliez','chiffrez']
    if not any(a in plat(tout) for a in actions):
        warn.append(f'{ref} aucune action executable nommee — verifier R1')

    # 7. Boucles de retention (A5). L'arc en 5 temps dit ce qui est transmis,
    #    il ne disait pas pourquoi le spectateur reste. Une boucle A refermee
    #    en transmission laisse ~30 s sans question en cours : c'est la zone
    #    ou un Reel se perd.
    b = s.get('boucles')
    if not b:
        err.append(f'{ref} aucune boucle declaree — voir A5')
    else:
        cles = {x.get('id') for x in b}
        if cles != {'A', 'B'}:
            err.append(f'{ref} il faut exactement deux boucles A et B, trouve : {sorted(cles)}')
        for x in b:
            ouv, fer = x.get('ouvre'), x.get('ferme')
            # L3 : toute boucle ouverte se referme dans la video
            if not fer:
                err.append(f'{ref} boucle {x.get("id")} ouverte et jamais refermee')
                continue
            if ouv not in attendu or fer not in attendu:
                err.append(f'{ref} boucle {x.get("id")} : temps inconnu ({ouv} -> {fer})')
                continue
            if attendu.index(fer) < attendu.index(ouv):
                err.append(f'{ref} boucle {x.get("id")} se referme avant de s\'ouvrir')
            # L2 : A tient jusqu'a la nuance, sinon le trou revient
            if x.get('id') == 'A' and fer not in ('Nuance', 'Sortie'):
                err.append(f'{ref} boucle A refermee en « {fer} » — doit tenir jusqu\'a Nuance (A5 L2)')
            if x.get('id') == 'B' and ouv != 'Transmission':
                warn.append(f'{ref} boucle B ouverte en « {ouv} » — attendue en Transmission')

    # 8. L'annonce de la manoeuvre remplace la boucle au lieu de la porter
    for m in ['restez jusqu', 'reste jusqu', 'regardez jusqu', 'jusqu\'a la fin',
              'attendez la fin', 'la suite a la fin']:
        if m in bas:
            err.append(f'{ref} annonce de manoeuvre : « {m} » (A5 §3)')

    # 9. Duree dans le creneau etabli
    d = int(re.sub(r'\D','',s['duree']))
    if d < 40 or d > 95:
        warn.append(f'{ref} duree hors creneau : {s["duree"]}')

print(f'{len(S)} scripts contrôlés — {FICHIER}\n')
print('— ERREURS BLOQUANTES —')
print('\n'.join('  ✗ '+e for e in err) if err else '  aucune ✓')
print('\n— POINTS À VÉRIFIER —')
print('\n'.join('  ⚠ '+w for w in warn) if warn else '  aucun ✓')

print('\n— ÉQUILIBRE DES PERSONAS —')
c = Counter(s['persona'] for s in S)
for p, n in c.most_common():
    print(f'  {n:>2}  {p}')
print('\n  Rappel D10 : Sophie = cible prioritaire · Karim = cible secondaire')
print('  (plafond 600 €/an, bloque les parcours longs)')
sys.exit(1 if err else 0)

#!/usr/bin/env python3
"""Controle de conformite des scripts, avant livraison."""
import json, re, sys, unicodedata
from collections import Counter

S = json.load(open('scripts.json', encoding='utf8'))

def plat(t):
    return unicodedata.normalize('NFD', t.lower()).encode('ascii','ignore').decode()

BANNIES = ['100 % finance','100% finance','sans reste a charge','machine a cash',
           'paravent','sans depenser un centime','ne vous coute rien',
           'entierement finance','formation offerte','reste a charge nul']
# Promesses de resultat, meme implicites
PROMESSES = [r'\bgaranti', r'vous (?:gagnerez|aurez|obtiendrez|doublerez)',
             r'\+\s*\d+\s*%', r'x\s*\d+\s+(?:vos|votre|plus)',
             r'(?:premiere|1re) place', r'assure(?:z|r)-vous d\'etre']
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
    for m in re.finditer(r'([\d\s ]{1,7})\s*euros?\b', tout):
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

    # 7. Duree dans le creneau etabli
    d = int(re.sub(r'\D','',s['duree']))
    if d < 40 or d > 95:
        warn.append(f'{ref} duree hors creneau : {s["duree"]}')

print(f'{len(S)} scripts contrôlés\n')
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

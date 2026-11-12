# Film de présentation VFormations

> 54 secondes, 1920 × 1080, 60 images par seconde. Présente l'organisme et sa méthode — la formation-action — à un dirigeant de TPE de l'Hérault.
> Écrit le 12/11/2026. Le film est **généré** : ce dossier contient sa source, pas le fichier vidéo (`sortie/` est hors Git, comme `dist/` pour le site).

## Ce que montre le film

| Temps | Plan | Texte à l'écran | Images |
|---|---|---|---|
| 0 – 6 s | La recherche | « Vos clients vous cherchent. Qui trouvent-ils ? » | Une barre de recherche (boulangerie à Montpellier, coiffeur à Béziers, restaurant à Sète), puis trois résultats : deux concurrents, et « Vous ? » |
| 6 – 12 s | Le problème | « Votre métier, vous le maîtrisez. Le montrer en ligne ? Pas le temps. Pas la méthode. Pas envie de dépendre d'une agence. » | Trois vues de commerces en éventail |
| 12 – 16 s | La révélation | « La formation-action. Vous apprenez en le faisant. Sur votre propre entreprise. » | Le logo se construit barre par barre |
| 16 – 32 s | La méthode | Diagnostic · Pratique terrain · Phase réflexive · Autonomie | Quatre inserts : diagnostic de départ, tournage dans le commerce, débrief, ce avec quoi on repart |
| 32 – 38 s | Le catalogue | « Six formations. Une seule méthode. » | Six tuiles, puis « En présentiel · Dans votre entreprise · Montpellier · Béziers · Sète et environs » |
| 38 – 46 s | Le cadre | « Organisme certifié Qualiopi, au titre des actions de formation » puis « Vous cotisez déjà à un fonds de formation. Il peut financer une partie de votre parcours. » | Un devis : « Reste à charge — annoncé avant toute inscription » |
| 46 – 54 s | L'appel | « Voyons ce que ça donne sur votre cas. » → Réserver un diagnostic → vformations.fr | Le bouton est cliqué, puis le logo |

**Tout le texte vient du site** (`../../C-site/site.html`) : la méthode en 4 temps, les six intitulés, la phrase sur le financement, l'appel. Rien n'a été inventé pour le film, et rien ne le contredit.

## Les règles que le film respecte

`controler-texte.py` les vérifie avant chaque montage, et `monter.sh` refuse de monter un film qui échoue.

- **Aucune formulation bannie** (`CLAUDE.md` §4) : ni « gratuit », ni « financé à 100 % », ni « sans reste à charge ». Le film dit l'inverse : le reste à charge est *annoncé avant toute inscription*.
- **Aucun résultat promis.** « Qui trouvent-ils ? » pose une question ; le film ne dit nulle part que la formation fera venir des clients.
- **Aucun prix** (décision D9), et aucun taux de financeur : un film ne se corrige pas comme une page quand un barème change.
- **Pas de logo Qualiopi.** La marque est interdite « dans une publicité pour une action de formation en particulier » (§8sexies). La certification est citée **en toutes lettres, avec sa catégorie d'action** ; le logo reste dans le pied de page du site. ⚠️ La photo `mag-qualiopi.jpg` montre un certificat avec le logo : elle n'est pas utilisée, et le contrôle refuse qu'elle le soit.
- **La règle d'or** (§2) : « Vous faites, on accompagne. » Le film ne montre jamais quelqu'un qui fait à la place du client.

## Refaire le film

```bash
npm install                 # gsap, la seule dependance
python3 preparer.py         # decoupe le logo en barres (une fois)
node rendre.cjs             # 3 240 images -> sortie/film-muet.mp4   (7 min sur 4 coeurs)
python3 son.py              # musique et bruitages -> sortie/son.wav (30 s)
./monter.sh                 # controle du texte, puis les deux fichiers finaux
```

Il faut : Node 18+, Playwright avec Chromium, ffmpeg, Python 3 avec `numpy`, `scipy` et `Pillow`, et la police **Inter Display** installée (https://rsms.me/inter/ — le rendu s'arrête si elle manque, plutôt que de la remplacer en silence).

Pour regarder sans rendre : ouvrir `film.html` dans un navigateur. Espace met en pause, les flèches avancent d'une seconde.

Pour ne tirer que quelques images : `node rendre.cjs --apercu 3.4,12.5,48` → `sortie/apercu/`.

## Comment c'est fait

**L'image est une fonction du temps.** `film.html` ne « joue » rien pendant le rendu : `FILM.aller(t)` pose l'image de la seconde *t*, `rendre.cjs` la photographie, et passe à la suivante. Une capture d'écran en temps réel saute des images dès que la machine peine ; ici, deux rendus donnent le même fichier.

**Le son se cale sur l'image, jamais l'inverse.** Chaque apparition déclare son bruitage dans `film.html` (`son(t, "pop")`). `rendre.cjs` en tire `reperes.json`, que `son.py` relit. Déplacer une animation déplace son bruitage.

**Tout est à 120 à la minute** : un temps toutes les 0,5 s, une mesure toutes les 2 s. Les changements de plan tombent sur les mesures, les apparitions importantes sur les temps.

**La bande-son est entièrement synthétisée** — aucune banque de sons, aucun échantillon. Il n'y a donc **aucun droit à vérifier** avant de diffuser le film en publicité.

## Ce qui n'est pas dans le film, et pourquoi

- **Pas de voix off.** Le film est construit pour être compris sans le son ; une voix se pose dessus sans rien changer à l'image. Il n'existe pas de synthèse vocale correcte dans cet outillage, et une voix médiocre coûterait plus qu'elle ne rapporte.
- **Les « plans de coupe » sont des photos animées, pas des rushes.** Ce sont les photos du site (propriété de VFormations, voir `../../C-site/img/credits.json`), avec un mouvement de caméra. De vraies séquences tournées en formation les remplaceraient avantageusement : il suffit de changer la source des `<img>` de `film.html` pour une `<video>` calée sur `t`.
- **Le format vertical n'existe pas encore.** Les réseaux sociaux le demandent ; la composition est en 1920 × 1080.

## ⚠️ Ce qui reste à faire par un humain

1. **Écouter le film.** La bande-son a été réglée à la mesure — niveau, crêtes, équilibre des fréquences, synchronisation — et **pas à l'oreille** : l'outil qui l'a écrite n'entend pas. Elle peut être conforme et déplaire.
2. **Vérifier « 30 minutes pour regarder votre situation »** : c'est la promesse du site. Si le diagnostic change de durée ou de forme, le plan 7 change avec.
3. **Recouper la mention Qualiopi** avec la charte graphique remise par *evolve* (§8sexies) : la formulation est celle du site, sa forme exacte reste à confirmer.

## Licences

| Élément | Origine | Licence |
|---|---|---|
| Photos | `livrables/C-site/img/` | Propriété de VFormations |
| Logo | `livrables/C-site/img/` | Propriété de VFormations |
| Police Inter Display | rsms.me/inter | SIL Open Font License 1.1 |
| GSAP 3.13 | gsap.com | *Standard no-charge license* — usage commercial permis |
| Musique et bruitages | `son.py` | Synthétisés pour ce film |

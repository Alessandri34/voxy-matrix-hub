# Film de présentation VFormations

> 54 secondes, 60 images par seconde, **deux formats** : 1920 × 1080 pour le site, 1080 × 1920 pour les réseaux sociaux. Présente l'organisme et sa méthode — la formation-action — à un dirigeant de TPE de l'Hérault.
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

`controler-texte.py` les vérifie avant chaque montage — sur le texte à l'écran **et** sur le script de voix off — et `monter.sh` refuse de monter un film qui échoue.

- **Aucune formulation bannie** (`CLAUDE.md` §4) : ni « gratuit », ni « financé à 100 % », ni « sans reste à charge ». Le film dit l'inverse : le reste à charge est *annoncé avant toute inscription*.
- **Aucun résultat promis.** « Qui trouvent-ils ? » pose une question ; le film ne dit nulle part que la formation fera venir des clients.
- **Aucun prix** (décision D9), et aucun taux de financeur : un film ne se corrige pas comme une page quand un barème change.
- **Pas de logo Qualiopi.** La marque est interdite « dans une publicité pour une action de formation en particulier » (§8sexies). La certification est citée **en toutes lettres, avec sa catégorie d'action** ; le logo reste dans le pied de page du site. ⚠️ La photo `mag-qualiopi.jpg` montre un certificat avec le logo : elle n'est pas utilisée, et le contrôle refuse qu'elle le soit.
- **La règle d'or** (§2) : « Vous faites, on accompagne. » Le film ne montre jamais quelqu'un qui fait à la place du client.

## Refaire le film

```bash
npm install                          # gsap, la seule dependance
python3 preparer.py                  # decoupe le logo en barres (une fois)
python3 telecharger-sons.py          # les 12 bruitages de banque -> sons/ (une fois)
node rendre.cjs                      # 3 240 images -> sortie/film-muet.mp4            (7 min sur 4 coeurs)
node rendre.cjs --format vertical    # les memes, en 1080 x 1920 -> film-muet-vertical.mp4
python3 son.py                       # musique et bruitages -> sortie/son.wav          (30 s)
./monter.sh                          # controle du texte, puis les fichiers finaux de chaque format rendu
```

Il faut : Node 18+, Playwright avec Chromium, ffmpeg, Python 3 avec `numpy`, `scipy` et `Pillow`, et la police **Inter Display** installée (https://rsms.me/inter/ — le rendu s'arrête si elle manque, plutôt que de la remplacer en silence).

Pour regarder sans rendre : ouvrir `film.html` dans un navigateur (`film.html?format=vertical` pour le vertical). Espace met en pause, les flèches avancent d'une seconde.

Pour ne tirer que quelques images : `node rendre.cjs --apercu 3.4,12.5,48` → `sortie/apercu/` (ajouter `--format vertical` → `sortie/apercu-vertical/`).

| Fichier produit | Pour quoi |
|---|---|
| `VFormations-film-presentation.mp4` | Le maître paysage, 60 images/s — site, présentation, YouTube |
| `VFormations-film-presentation-vertical.mp4` | Le maître vertical, 60 images/s — **c'est lui qu'on envoie aux réseaux** : ils recompressent tout, autant leur donner le meilleur |
| `…-web.mp4` (les deux) | 30 images/s, 9 à 10 Mo — une page, un courriel, une relecture |
| `affiche.jpg`, `affiche-vertical.jpg` | L'image d'attente, à 15 s (le slogan) |

## Comment c'est fait

**L'image est une fonction du temps.** `film.html` ne « joue » rien pendant le rendu : `FILM.aller(t)` pose l'image de la seconde *t*, `rendre.cjs` la photographie, et passe à la suivante. Une capture d'écran en temps réel saute des images dès que la machine peine ; ici, deux rendus donnent le même fichier.

**Le son se cale sur l'image, jamais l'inverse.** Chaque apparition déclare son bruitage dans `film.html` (`son(t, "pop")`). `rendre.cjs` en tire `reperes.json`, que `son.py` relit. Déplacer une animation déplace son bruitage.

**Tout est à 120 à la minute** : un temps toutes les 0,5 s, une mesure toutes les 2 s. Les changements de plan tombent sur les mesures, les apparitions importantes sur les temps.

**Deux formats, une seule composition.** Le vertical n'est pas un second film : c'est le même `film.html`, ouvert avec `?format=vertical`. La ligne de temps, les 109 repères sonores et la bande-son sont **les mêmes** ; seules changent la taille du cadre et la place des éléments (un bloc de CSS et sept positions). `rendre.cjs` refuse de rendre un vertical dont les repères différeraient du paysage : les deux films ne partageraient plus le même son. Corriger un mot le corrige dans les deux.

## Le format vertical et sa zone sûre

Sur un réseau, l'interface recouvre l'image : le nom du compte en haut, la légende et le bouton en bas, la colonne d'icônes à droite. Meta le chiffre pour ses publicités Reels :

> *« Consider leaving at least 14% of the top, 35% of the bottom, and 6% on each side of your asset free from text, logos, or other key creative elements. »*
> — Meta Ads Guide, Instagram Reels, lu le 12/11/2026 · https://www.facebook.com/business/ads-guide/update/video/instagram-reels

Sur 1080 × 1920, cela laisse le rectangle **x 65 – 1015, y 269 – 1248**. Le schéma du Centre d'aide Meta y retire encore le coin bas-droit (les 21 % de droite, sous 60 % de la hauteur) : la colonne des boutons.

**Ce qui est dedans** — vérifié sur 16 images du fichier final : tous les titres, la phrase sur le financement, « Annoncé avant toute inscription », le bouton, l'adresse du site et la mention Qualiopi avec sa catégorie d'action.

**Ce qui dépasse, et c'est un choix** : au plan 4, le bas des quatre inserts descend jusqu'à y ≈ 1 500. Ce sont des illustrations ; le titre et la phrase de chaque temps sont dans la zone. En publication ordinaire ils se voient en entier ; en publicité, la légende et le bouton en couvrent le bas.

⚠️ **La zone est celle de Meta, parce que les campagnes prévues sont sur Meta** (`D3`). Les autres réseaux sont plus étroits sur les côtés : TikTok Ads demanderait 120 px à gauche et à droite, YouTube 192 px à droite pour ses publicités verticales **[À vérifier — ces cotes ne figurent pas dans le texte des pages officielles mais dans leurs gabarits à télécharger ; relevées une fois le 12/11/2026, non recontrôlées]**. Le texte du film commence à 70 px du bord. Avant une campagne ailleurs que sur Meta, ouvrir le gabarit du réseau, resserrer le bloc `#cadre.vertical` de `film.html` et rendre à nouveau. Aucun réseau ne publie de cotes pour les publications ordinaires.

## La bande-son et la banque de bruitages

La **musique** est entièrement synthétisée par `son.py` (accords, basse, batterie, montées) : rien à licencier.

Les **bruitages**, eux, viennent pour moitié d'une banque depuis le 12/11/2026 : **59 des 109** sont des sons enregistrés (souffles de transition, frappes de clavier, clics, impact), tirés de **12 fichiers** de **Mixkit**. Un souffle synthétisé est un bruit filtré ; un souffle enregistré a un grain qu'on ne fabrique pas. Le reste — tout ce qui est *accordé* sur la musique (carillons, notes, montées) — reste synthétisé, parce qu'un son de banque n'est pas dans la tonalité du film.

- `sons/banque.json` nomme chaque son : titre, page, adresse du fichier, empreinte, emploi.
- `python3 telecharger-sons.py` les récupère ; l'empreinte refuse un fichier remplacé à la source.
- `son.py` cale chaque son enregistré **au niveau du son synthétisé qu'il remplace** : l'équilibre du mixage ne bouge pas, seul le timbre change.
- `python3 son.py --sans-banque` produit `sortie/son-synthese.wav`, tout synthétisé : c'est le point de comparaison, et la solution de repli si la banque disparaît.

### Pourquoi Mixkit, et ce que sa licence impose

Licence lue à la source le 12/11/2026 (*Mixkit Sound Effects Free License*, https://mixkit.co/license/#sfxFree) :

| Ce qu'elle dit | Ce que ça veut dire ici |
|---|---|
| Utilisables dans « *Online marketing ads* » et « *Commercial projects* », « *for free* » | Le film peut passer en publicité payante, sans rien devoir |
| Aucun crédit demandé | Rien à afficher |
| « *You can't redistribute the Item on its own, as stock, in a tool or template, or with source files.* » | 🔴 **Les fichiers ne vont pas dans ce dépôt, qui est public.** `.gitignore` les écarte ; seul `banque.json` est suivi |
| « *not allowed to […] register them on any rights management service* » | Ne jamais déclarer la bande-son du film à un service d'identification de contenus (Content ID et équivalents) |

⚠️ Les conditions d'utilisation de Mixkit interdisent aussi le téléchargement **en masse** par script. `telecharger-sons.py` ne prend que les douze sons nommés, un par un. La lecture stricte reste de les télécharger à la main depuis leur page.

### Les autres banques regardées

| Banque | Licence (lue à la source le 12/11/2026) | Verdict |
|---|---|---|
| **Mixkit** | Publicité et usage commercial permis, sans crédit ; redistribution des fichiers interdite | ✅ **Retenue** — catalogue orienté montage (souffles, interfaces, impacts) |
| **Kenney** | CC0 : « *public domain licensed (CC0)* », « *even in commercial projects* », « *Attribution is not required* » | ✅ La seule dont les fichiers **peuvent** entrer dans un dépôt public. Mais ce sont des sons de jeu vidéo : pas de souffle de transition, pas de clavier |
| **Sonniss — GDC Game Audio Bundle** | « *personal and commercial projects* », « *without attribution* » ; interdit de redistribuer les sons « *as sound effects* » | ✅ Qualité de studio, la plus « premium ». Des dizaines de gigaoctets : à réserver au jour où un monteur reprend le film |
| **Pixabay** | Gratuit, sans crédit ; pas de redistribution « *on a Standalone basis* » | 🟠 Utilisable, mais qualité très inégale d'un auteur à l'autre |
| **Freesound** | Variable **son par son** : CC0, Attribution (crédit obligatoire), ou NonCommercial (publicité interdite) | 🟠 À vérifier fichier par fichier — un seul son « NonCommercial » dans une publicité est une contrefaçon |
| **BBC Sound Effects** | Licence RemArc : usage personnel, éducatif ou de recherche [d'après plusieurs sources concordantes — la page de licence n'a pas pu être relue ici] | ❌ Pas pour une publicité sans licence payante |
| **Zapsplat** | Non relue : le site a refusé la lecture | — Ne pas s'en servir sans avoir lu la licence |

## La voix off

Le script est écrit, minuté et dirigé : **`VOIX_OFF.md`** est le document du comédien, **`voix.json`** la même chose pour la machine. Il n'y a **pas de voix enregistrée** : aucune synthèse vocale de cet outillage ne vaut un comédien, et une voix médiocre sur un film soigné coûte plus qu'elle ne rapporte.

Ce que le contrôle vérifie sur la voix, en plus des règles de fond :
- **le débit, en syllabes** — c'est la syllabe qui prend du temps, pas le mot ;
- **les silences imposés** : rien sur l'impact de 12 s, rien après 52 s ;
- **les deux boucles décalées** de `../A5_Structure_Retention.md` (règles L1 à L3) ;
- **l'accord entre `voix.json` et `VOIX_OFF.md`**, mot pour mot.

`python3 controler-texte.py --sous-titres` écrit `sortie/voix.srt` : ouvert avec le film dans un lecteur (VLC le charge seul s'il porte le même nom que la vidéo), il affiche chaque réplique à l'instant où elle doit être dite. C'est un prompteur de répétition, pas des sous-titres à publier — le film porte déjà son texte.

## Ce qui n'est pas dans le film, et pourquoi

- **Pas de voix enregistrée** — voir ci-dessus. Le film reste compréhensible sans le son ; la voix se pose dessus sans rien changer à l'image.
- **Les « plans de coupe » sont des photos animées, pas des rushes.** Ce sont les photos du site (propriété de VFormations, voir `../../C-site/img/credits.json`), avec un mouvement de caméra. De vraies séquences tournées en formation les remplaceraient avantageusement : il suffit de changer la source des `<img>` de `film.html` pour une `<video>` calée sur `t`.

## ⚠️ Ce qui reste à faire par un humain

1. **Écouter le film.** La bande-son a été réglée à la mesure — niveau (−15 LUFS), crêtes (−1,8 dB), équilibre des fréquences, synchronisation — et **pas à l'oreille** : l'outil qui l'a écrite n'entend pas. Les douze sons de banque ont été choisis de la même façon, sur leur forme d'onde et leur durée. Elle peut être conforme et déplaire ; `--sans-banque` donne l'autre version pour comparer.
2. **Faire enregistrer la voix**, puis la poser : `VOIX_OFF.md` dit quoi demander au comédien et sous quelle forme livrer.
3. **Vérifier « 30 minutes pour regarder votre situation »** : c'est la promesse du site. Si le diagnostic change de durée ou de forme, le plan 7 et la dernière réplique changent avec.
4. **Recouper la mention Qualiopi** avec la charte graphique remise par *evolve* (§8sexies) : la formulation est celle du site, sa forme exacte reste à confirmer.

## Licences

| Élément | Origine | Licence |
|---|---|---|
| Photos | `livrables/C-site/img/` | Propriété de VFormations |
| Logo | `livrables/C-site/img/` | Propriété de VFormations |
| Police Inter Display | rsms.me/inter | SIL Open Font License 1.1 |
| GSAP 3.13 | gsap.com | *Standard no-charge license* — usage commercial permis |
| Musique | `son.py` | Synthétisée pour ce film |
| Bruitages (50 sur 109) | `son.py` | Synthétisés pour ce film |
| Bruitages (59 sur 109, 12 fichiers) | Mixkit — `sons/banque.json` | *Mixkit Sound Effects Free License* — publicité permise, redistribution des fichiers interdite |

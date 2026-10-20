# Passation

> État au 20/10/2026, fin de session. Branche de travail :
> `claude/new-session-nefcch` (poussée, propre, `c38944f`).
> Branche indépendante du générateur : `generateur-scripts` (`1dd7a75`).
>
> **Lire `CLAUDE.md` en premier.** Ce fichier-ci ne le remplace pas : il dit
> où en est le chantier et ce qui a raté, pas ce qu'est le projet.

---

## 1. L'objectif

**Faire arriver des demandes de contact depuis les recherches Google**, pour
un organisme de formation certifié Qualiopi de l'Hérault qui forme des
dirigeants de TPE à la visibilité locale par la vidéo.

Trois chantiers servent cet objectif, dans cet ordre de maturité :

| Chantier | État |
|---|---|
| **Site + SEO** (`livrables/C-site/`) | 61 pages en production, 36 articles, formulaire dans chaque article |
| **Contenu social** (`livrables/A-marketing/`) | 10 scripts publicitaires + 16 scripts de valeur |
| **Générateur de scripts** (branche `generateur-scripts`) | Dépôt autonome, jamais testé sur un vrai cas |

---

## 2. La problématique

### Ce qu'on essaie de résoudre

Un organisme neuf, sans notoriété, sur un marché où **le niveau de preuve
est bas et les promesses sont partout**. Il ne peut pas rivaliser sur les
têtes de requêtes, et il lui est **juridiquement interdit** de promettre un
résultat ou d'employer le vocabulaire qui vend (« gratuit », « 100 %
financé », « sans reste à charge »).

La stratégie qui en découle : **gagner par la précision plutôt que par la
promesse**. Longue traîne à forte intention, faits vérifiables et sourcés,
aveu des limites. Ce qui est une contrainte réglementaire devient l'angle
de différenciation, parce que le marché ment beaucoup et se fait prendre.

### Le problème stratégique découvert ce jour, et non résolu

🔴 **La moitié du positionnement de `A0_Marche_et_Personas.md` §2 s'est
banalisée.** La phrase exacte y est :

> *« Le seul organisme de l'Hérault qui vient filmer dans votre commerce et
> vous rend autonome : vous repartez en sachant produire vos vidéos
> vous-même, pas dépendant d'une agence. »*

**La seconde moitié ne différencie plus rien.** « Rendre autonome, pas
dépendant d'une agence » est l'argument central de **Skiveo** (OF Qualiopi,
Rennes — « aucune entreprise ne peut payer un prestataire pour chaque
contenu »), et **SITIO** (agence DFY, Montpellier) le reprend à son compte
(« on forme votre équipe aux mises à jour »). C'est devenu le discours par
défaut du marché.

**La première moitié, elle, tient.** « Vient filmer dans votre commerce »
est précisément ce qu'aucun concurrent trouvé ne propose, et c'est un des
quatre termes de l'intersection qui reste défendable :

> **vidéo × visibilité locale × présentiel sur le lieu d'exercice ×
> financement artisan/commerçant correctement calculé**

Le trou est structurel : les OF « visibilité locale » vendent tous le même
produit (fiche Google, 7 h, 249-650 € HT) et **aucun ne vend de vidéo** ;
les OF vidéo visent LinkedIn et la prise de parole dirigeant.

**→ `A0` §2 demande un déplacement d'accent, pas une réécriture** : mettre
le présentiel sur le lieu d'exercice et le calcul du financement devant,
l'autonomie derrière. Ce n'est pas fait.

⚠️ **Et sa liste de concurrents est à refaire.** `A0` §2 cite Mon Coach
Digital, Les Associés du Marketing et Futur Possible. La veille du 20/10 a
trouvé des acteurs bien plus frontaux qui n'y figurent pas : **Skiveo**,
**PlancheContact** (le jumeau structurel : formation artisans + agence web
sous la même marque), **SITIO**, **Cel & Poivre** (Montpellier, 100 % food,
« délégation, coaching ou formation »), **GMB Club** (le meilleur contenu
du marché), **Kaelia Formacoach** (qui tient la barre haute sur le
financement). Détail dans `A2_Contenu_Valeur_MOFU.md`, section veille.

---

## 3. Les fichiers importants

### Le site — `livrables/C-site/`

| Fichier | Rôle |
|---|---|
| `site.html` | **Source unique.** Contient le style, le JS, et le corps des pages anciennes. ⚠️ Ne jamais déployer tel quel : il n'expose qu'une URL pour 61 pages. |
| `pages.json` | Le registre : `[slug, url, titre, description, type, {img, tag, carte}]`. L'ordre des articles fait l'ordre du Mag. |
| `build.mjs` | Génère `dist/`. Porte le Schema.org, le maillage automatique, le formulaire de fin d'article, IndexNow. |
| `contenu/*.html` | 30 articles en fichiers séparés (les 6 plus anciens sont restés dans `site.html`). |
| `seo.json` | Jetons de vérification, pixel Meta, **et les champs locaux non remplis** (voir §5). |
| `BACKLINKS.md` | Sources de liens vérifiées, par ordre de rentabilité, textes prêts à soumettre. |
| `SEO_strategie.md` | Les trois vagues de contenu et leur raisonnement. |

### Le contenu social — `livrables/A-marketing/`

| Fichier | Rôle |
|---|---|
| `A0_Marche_et_Personas.md` | Les 5 personas. ⚠️ Son §2 est périmé (voir §2 ci-dessus). |
| `A_scripts_ugc_v2.md` | 10 scripts publicitaires, **arc de vente en 7 temps**. |
| `A2_Contenu_Valeur_MOFU.md` | 16 scripts de valeur, **arc de transmission en 5 temps**. Contient aussi la veille concurrentielle et les mécaniques retenues. |
| `A2_scripts.json` | Les mêmes scripts en données, pour les rejouer ou les filtrer. |
| `controle-scripts.py` | Le contrôle de conformité, exécutable. `python3 controle-scripts.py` depuis le dossier. |

### Le socle — `livrables/B-socle/`, `D-strategie/`, `E-produit/`

`B1` décrit ce qui se passe réellement en formation (le plus utile pour
produire du contenu). `D1` porte l'économie unitaire. `D2` §4 contient le
protocole exact du diagnostic, et `D2` §2 le rendez-vous « on dépose le
dossier avec lui », identifié comme le levier n°1 de conversion.

### Les outils jetables de cette session

Dans le scratchpad, **non versionnés, perdus à la fermeture** :
`outils/verif-articles.py` (contrôle structurel et rédactionnel des
articles du Mag). S'il resert, le reprendre depuis `controle-scripts.py`,
qui suit la même logique.

---

## 4. Ce qui a raté

> Section volontairement longue. C'est la partie la plus utile du document.

### Les erreurs qui sont parties en production

🔴 **Un taux faux sur la page Financements, pendant des semaines.** Le site
annonçait la **FAFCEA à 35 €/h** dans deux tableaux, alors qu'un article
entier du Mag explique que le numérique relève du taux transverse à 25 €/h.
Le site se contredisait lui-même, publiquement, **sur l'angle le plus
différenciant du dossier**. Corrigé en `7df8d32`.
→ **Leçon : la cohérence entre les pages n'est vérifiée par rien.** La
barrière SEO du déploiement contrôle les titres, les canoniques et le
Schema.org — pas les faits. Un contrôle croisé des chiffres entre les
pages reste à écrire.

🔴 **Il en reste.** `B1` §4.1 et `B_pilotage` §2 calibrent toujours la Gamme A
sur « FAFCEA technique ~490 € » pour 14 h, soit 35 €/h appliqué à une
formation vidéo. Au taux transverse, 14 h font 350 €. **Non corrigé** —
c'est du socle pédagogique, je n'y ai pas touché sans accord.

🔴 **Une phrase fausse publiée dans un article** (session précédente) : « une
formation de 35 heures facturée 42 €/h coûte 1 470 € ». 42 €/h est le taux
de remboursement AGEFICE, pas un prix. Le calcul faisait tomber le reste à
charge à zéro, en contradiction avec la section suivante du même article.
→ **Leçon : confondre un taux de remboursement et un prix est l'erreur
récurrente de ce dossier.** Elle est passée deux fois. Toute nouvelle
mention d'un taux doit dire explicitement que ce n'en est pas un prix.

### Les angles morts que je n'ai pas vus seul

**L'adresse du schéma était à Paris.** Pendant quatre étapes de travail SEO,
`47 rue Vivienne, 75002` a été déclaré comme adresse de l'organisme sur un
site qui cible l'Hérault. Je ne l'avais jamais relevé. Trouvé en relisant le
dossier pour autre chose.

**L'entité n'était émise que sur la page d'accueil.** `publisher` et `author`
pointaient dans le vide sur **45 pages sur 46**. J'avais écrit ce schéma
moi-même.

**Deux de mes catégories de contenu tombaient dans des angles saturés**
(« filmer au smartphone : la méthode avant le matériel » et « avant/après et
coulisses »). Je les avais posées avant la veille concurrentielle, en me
fiant à mon intuition. La veille les a démenties.
→ **Leçon : la veille avant la production, pas après.**

### Les faux positifs que j'ai produits

- **Test du pixel Meta invalide.** J'avais conclu que l'échec local venait de
  `127.0.0.1`. Faux : `fbevents.js` filtre les navigateurs automatisés. Mon
  test de conformité à 4 scénarios était donc sans valeur — il tournait dans
  un navigateur où rien ne part, quel que soit le consentement. Documenté
  dans `CLAUDE.md` §6ter comme un piège.
- **« Gouttière à 0px »** et **« tableau en débordement à 420px »** : deux
  alarmes que j'ai levées puis retirées. Erreurs de mesure de ma part.
- **`credits.json` attribuait 8 photos de Pierre à des banques CC0.**

### Les ratés techniques de cette session

- **`pkill -f "http.server"` a tué mon propre shell. Deuxième fois.** Le motif
  correspond aussi à la commande qui l'exécute. Une édition a été perdue et
  rejouée. → **Changer de port, ne jamais `pkill` sur un motif large.**
- **Littéral de gabarit non fermé** dans `build.mjs` : le backtick manquant
  faisait interpréter `</article>` comme une expression régulière. Erreur
  obscure, cause triviale.
- **Deux règles CSS mortes** écrites pour un problème qui n'existait pas
  (`.form` se replie déjà seul). Retirées.
- **Grille à 3 enfants pour 2 colonnes** dans l'artefact : le texte des cinq
  temps tombait dans la colonne du numéro. Vu à la capture, pas à la
  relecture.
- **Mon contrôleur d'articles était trop bavard** : il signalait « gratuit »
  à propos de Google. Deux passes pour le resserrer sur le seul périmètre
  interdit, celui du coût de la formation.

### Ce que l'environnement n'a pas permis

- **`WebFetch` est hors service** (échec DNS sur tous les hôtes). Les quatre
  agents l'ont contourné avec `curl`. **Conséquence : aucun site rendu en
  JavaScript n'a pu être lu** — dont `cma-herault.fr`, le concurrent local
  le plus important, qui reste un trou.
- **`data.gouv.fr` est inaccessible** depuis ce conteneur. La présence de
  VFormations dans la liste publique des organismes de formation (NDA
  `11757618175`) **n'a pas pu être vérifiée**.
- **L'agent de contrôle des scripts s'est arrêté sur une limite de session**,
  pas sur le travail. J'ai fait le contrôle moi-même — automate + test de
  spécificité manuel. **L'exactitude factuelle de chaque affirmation
  réglementaire n'a donc pas eu de relecture indépendante.** L'agent est
  reprenable là où il s'est arrêté.

### Ce que le contrôle a rattrapé, et qui serait parti sinon

- **V02 renvoyait au devis en sortie** — proposition commerciale, interdite
  dans cet arc.
- **6 scripts sur 16 visaient Karim**, que la décision D10 classe en cible
  *secondaire*. Deux étaient mal étiquetés.
- **3 scripts passent mal le test de spécificité.** Notes abaissées plutôt
  que maquillées.

---

## 5. La prochaine étape

### Ce qui bloque, et qui n'attend que Pierre

| # | Décision | Pourquoi ça bloque |
|---|---|---|
| 1 | **L'adresse publique.** Relever celle de la fiche Google et la mettre dans `seo.json` (`villeBase`, `codePostalBase`), ou laisser vide et déclarer des zones desservies. | Tant que c'est vide, le site ne se déclare pas comme établissement local. Et toute inscription en annuaire faite avant diffuserait une incohérence sur dix sites au lieu d'un. |
| 2 | **Les horaires** (`horairesJours`, `horairesDebut`, `horairesFin`). | Être ouvert au moment de la recherche est devenu un facteur de classement local majeur. Champs vides = levier abandonné. **Ne jamais les inventer.** |
| 3 | **La grille tarifaire.** Le site affiche « dès 1 190 € HT » à 11 endroits, validé par aucune source. `D1` retient d'autres paliers, et « ESSENTIEL » nomme deux produits différents. | Conséquence tenue aujourd'hui : **aucun prix dans les contenus publiés**. Tenable, mais ça plafonne la page Tarifs. |
| 4 | **Search Console** : cliquer *Valider*, puis soumettre le sitemap (61 URL). | Le jeton est en place depuis plusieurs jours. Google ne participe pas à IndexNow : c'est le seul canal vers lui. |

### Ce qui est prêt à exécuter

1. **Carif-Oref Occitanie** — `organismes.cariforefoccitanie.fr`. Sans frais,
   et l'offre entre dans les outils de prescription de France Travail. **Le
   meilleur rapport effort/retour de tout le dossier.** Texte prêt dans
   `BACKLINKS.md` §6.
2. **Vérifier la présence dans la liste publique des OF** (NDA `11757618175`).
   Deux minutes. Si absent, la cause est presque toujours le BPF non déposé
   — ce qui rend la déclaration caduque.
3. **Tourner 3 scripts de valeur** parmi V01, V03, V15, V16 — les quatre qui
   passent le mieux le test de spécificité. Un seul tournage groupé.

### Ce qui demande un arbitrage avant de coder

- **Déplacer l'accent dans `A0` §2** : le présentiel sur le lieu d'exercice
  et le calcul du financement devant, l'autonomie derrière. Et refaire sa
  liste de concurrents, qui ignore les acteurs les plus frontaux.
- **Corriger `B1` §4.1 et `B_pilotage` §2** (35 €/h → 25 €/h sur la Gamme A).
- **Écrire un contrôle croisé des chiffres entre les pages du site.** C'est
  ce qui manquait pour attraper la FAFCEA à 35 €/h. Le modèle existe :
  `livrables/A-marketing/controle-scripts.py`.
- **Tester le générateur** (branche `generateur-scripts`) sur une vraie
  entreprise. L'entonnoir de questions n'a jamais été confronté à un
  dirigeant. C'est le point faible connu de ce dépôt.

### À ne pas refaire

- Ne pas produire de contenu avant la veille : deux catégories sur dix
  tombaient dans des angles saturés.
- Ne pas juger le contenu de valeur aux vues. **50/40/10 est une règle de
  production, pas de diffusion.**
- Ne pas citer un chiffre de performance sans sa source et son année. Le
  marché est saturé de statistiques invérifiables ; c'est précisément
  l'écart qui différencie.
- Ne pas confondre un taux de remboursement avec un prix. **C'est passé deux
  fois dans ce dossier.**

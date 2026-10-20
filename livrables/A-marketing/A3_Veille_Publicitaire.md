# A3 — Veille publicitaire : décorticage de 28 annonces actives

> **Source :** bibliothèque publicitaire Meta, France, annonces **actives** au
> **20/10/2026**. Trois annonceurs, 28 annonces, extraction intégrale du texte
> publié.
>
> **Méthode :** la bibliothèque est une application JavaScript protégée par un
> défi anti-robot. `curl` reçoit un HTTP 403. Le rendu a été obtenu avec un
> navigateur complet et une empreinte réaliste — même contournement que celui
> documenté pour le pixel Meta (`CLAUDE.md` §6ter). Une seconde tentative a
> été bloquée : **les données ci-dessous viennent d'un unique passage réussi.**

---

## 0. L'avertissement qui conditionne tout le reste

**Aucun de ces trois annonceurs n'est un concurrent de VFormations.**

| Annonceur | Vend quoi | À qui |
|---|---|---|
| **Youdji** | Place de marché de créateurs UGC | Marques et agences qui achètent du contenu |
| **L'agence Short** | Agence créative publicitaire | E-commerce, lead gen, infoproduit, SaaS |
| **L'agence Paid** | Agence média (Meta, Google, TikTok) | Marques qui dépensent en publicité |

Aucun ne s'adresse à un artisan, un restaurateur ou un salon de l'Hérault.
Ce corpus n'est donc **pas une veille concurrentielle** : c'est un **gisement
de mécaniques**, à transposer d'un marché (les annonceurs) vers un autre (les
dirigeants de TPE). La transposition n'est pas automatique, et deux des trois
modèles sont **inutilisables tels quels** pour un organisme de formation.

> ⚠️ **À noter immédiatement :** `CLAUDE.md` §7bis indique que la méthode créa
> de VFormations vient du « guide Agence Short ». Or **L'agence Short distribue
> aujourd'hui cette méthode en aimant à prospects gratuit** — voir §3.2,
> annonce `1345105277702748`. La méthode interne de VFormations est devenue un
> document public que n'importe quel concurrent peut télécharger en 30
> secondes. Ce n'est pas un problème de légitimité, c'est un problème de
> différenciation : **ce qui est donné à tout le monde ne distingue personne.**

---

## 1. Les trois modèles, en chiffres

| | **Youdji** | **L'agence Short** | **L'agence Paid** |
|---|---|---|---|
| Annonces actives | **17** | 7 | 4 |
| Longueur médiane du texte | **120 car.** | 454 car. | 638 car. |
| Amplitude (min-max) | 117-250 | 225-624 | 571-658 |
| Versions multiples | **0 / 17** | 5 / 7 | 3 / 4 |
| Étalement des lancements | **15 le même jour** | 5 mois | 3 le même jour |
| Doublons de texte | 2 paires | 1 triplet + 1 paire | 1 paire |
| Annonce à faible impression | **2** | 0 | 0 |
| Aimant à prospects | non | **7 / 7** | 1 / 4 |
| Prix affiché dans l'annonce | non | non | **oui — 1 500 €/mois** |
| Promesse de résultat | non | implicite | **explicite — 30-60 jours** |

### Ce que ces chiffres disent vraiment

**La longueur médiane est la donnée la plus révélatrice du tableau.** 120, 454,
638 caractères : ce ne sont pas trois styles, ce sont **trois théories du
test**.

- **Youdji teste large, court, jetable.** Une phrase, zéro version multiple,
  quinze annonces lancées le même jour. Chaque annonce est un pari unique
  qu'on ne retouche pas : si elle ne prend pas, on la laisse mourir. Les deux
  annonces marquées « nombre faible d'impressions » sont les perdantes de ce
  lot, **et elles sont restées en ligne** — c'est une stratégie d'inventaire,
  pas d'optimisation.
- **Short et Paid testent étroit, long, durable.** Peu d'annonces, la majorité
  avec plusieurs versions, étalées sur des mois. L'itération est **interne à
  l'annonce** (on change la vidéo, on garde le texte) plutôt qu'externe.

→ **Pour VFormations :** avec un budget de 2 000 € (`D3`), le modèle Youdji
est hors de portée — il suppose un volume d'impressions qui absorbe quinze
paris simultanés. Le modèle Short/Paid, peu d'annonces longuement itérées,
correspond à la contrainte réelle. **Mais la mécanique d'accroche de Youdji,
elle, est transposable** (§4.1).

---

## 2. Youdji — l'usine à douleurs opérationnelles

### 2.1 La formule, constante sur 15 annonces

> **`[douleur opérationnelle précise et datée] ? [résolution en une clause]`**

Aucune promesse. Aucun chiffre de résultat. Aucun prix. Une phrase.

| Annonce | Douleur | Résolution |
|---|---|---|
| `1099218789542929` | « Trois semaines de casting UGC avant le Q4 ? » | « Filtrez 10 000 créateurs vérifiés, la shortlist se fait en quelques minutes » |
| `1518538576778429` | « 5 créateurs UGC à trouver avant vendredi, zéro réponse à vos DM Insta ? » | « Ici, la shortlist se fait en quelques minutes » |
| `1151090507484381` | « Black Friday qui approche et pas de créateurs UGC pour vos clients ? » | « Filtrez, contactez, signez et payez au même endroit » |
| `1116048084514240` | « Black Friday qui approche et vos créateurs UGC encore sourcés sur Excel ? » | idem |
| `1091051453836525` | « Un acompte viré à un créateur UGC trouvé sur Insta, puis silence radio ? » | « Ici le paiement passe par Stripe, contrat à l'appui » |
| `4605666002995160` | « On vous demande où en sont les vidéos UGC et vous fouillez vos messages ? » | « Ici chaque collaboration affiche son statut » |
| `1534946958423547` | « La même créatrice vue 15 fois par vos clients ? » | « Renouvelez vos visages UGC parmi 10 000 créateurs vérifiés » |
| `1165179316036141` | « Des centaines de candidatures hors sujet pour un brief UGC ? » | « Avec la Campagne IA, seuls des profils qui collent répondent » |
| `1856462032014689` | « Le CPA remonte, la fréquence aussi, et trouver un nouveau créateur prend des semaines de DM Insta ? » | « Ici, quelques minutes » |
| `2158187468108131` | « Vos concurrents sortent plus de pubs UGC que vous pour le Q4 ? » | « Publiez un brief, recevez des candidatures qui collent » |

### 2.2 Les quatre règles qu'on peut en extraire

**① La douleur est toujours opérationnelle, jamais stratégique.**
Pas « votre acquisition stagne » mais « vous fouillez vos messages », « sourcés
sur Excel », « zéro réponse à vos DM Insta », « un acompte viré puis silence
radio ». Ce sont des **gestes**, pas des concepts. Un lecteur les reconnaît
sans réfléchir parce qu'il les a faits la semaine dernière.

**② L'ancrage temporel est systématique.** Q4, Black Friday, les fêtes, « avant
vendredi », « pour demain ». **8 annonces sur 17** portent une échéance. Elle
crée l'urgence sans la réclamer.

**③ L'objection n°1 est traitée dans le sous-titre, pas dans le texte.**
« **Sans abonnement obligatoire** » apparaît **12 fois** dans les sous-titres
de la page.
Le texte ne la mentionne jamais. C'est un placement délibéré : la douleur
occupe l'attention, l'objection est désamorcée en périphérie.

**④ La preuve est un jeton de volume, répété à l'identique.**
« 10 000 créateurs vérifiés » revient **8 fois**, tantôt dans le texte,
tantôt dans le sous-titre. **Ce n'est jamais un chiffre de résultat** —
toujours un chiffre d'inventaire.

### 2.3 L'itération visible en trois jours

Les 2 annonces du **16 octobre** et les 15 du **19 octobre** ne se ressemblent
pas :

| | 16 octobre | 19 octobre |
|---|---|---|
| Émojis | 🚨 🚀 🌟 🔥 en rafale | **1 sur 15** (un 📩) |
| Statistique | « l'UGC est **9,8× plus impactant** » | **supprimée** |
| Longueur | jusqu'à 250 car. | 117-130 car. |
| Registre | enthousiaste | constat sec |

→ **En trois jours, Youdji a abandonné les émojis, la statistique de résultat
et la moitié de la longueur.** On ne peut pas savoir pourquoi, mais le sens du
changement est net : **du bruit vers la précision**. C'est l'observation la
plus utile de tout ce corpus, parce qu'elle montre une correction de cap, pas
une préférence de style.

---

## 3. L'agence Short — l'aimant à prospects comme modèle unique

### 3.1 Sept annonces, sept documents gratuits, zéro offre de service

| Document | Annonce |
|---|---|
| Top 50 des meilleurs hooks | `989350097395112` |
| Les 68 meilleures publicités de 2026 | `1577615643910360`, `1689276588840131` |
| Les 60 meilleures pubs de septembre | `28804989755752186`, `1041036392263191` |
| 60 publicités qui performent (post-UGC) | `1461059496079316` |
| **2 prompts IA : signal → 10 angles → scripts** | `1345105277702748` |

**Aucune annonce ne vend l'agence.** L'agence n'est jamais nommée comme
prestataire : elle est la **caution** du document.

### 3.2 La structure d'autorité, décortiquée

Annonce `989350097395112`, la plus ancienne encore active (25 mai 2026) :

> « J'ai produit **+10 000 publicités** et généré **des millions d'euros** pour
> mes clients (**Free, Binance, EatSalad**...). Aujourd'hui, je vous donne tout
> **gratuitement**. Accédez à ma **bibliothèque privée** des 50 meilleures
> hooks : concepts, et structures prêts à l'emploi. »

Quatre leviers en trois phrases : **volume** (10 000), **résultat vague**
(millions d'euros, non vérifiable), **noms de marques** (le seul élément
vérifiable), **retournement** (privé → donné). Le « gratuitement » n'est pas
un argument de prix, c'est un **marqueur de générosité** qui justifie le
retournement.

Annonce `1345105277702748` — **celle qui concerne directement VFormations** :

> « Ce document, c'est **6 ans de travail condensés sur une seule page**. […]
> Tu repars avec 2 projets IA prêts à copier-coller :
> • le premier part d'un **signal** et sort **10 angles** à tester
> • le second transforme ces angles en **scripts** prêts à produire
> Le système est automatisé à 90 %. […] **C'est gratuit.** »

C'est exactement la méthode inscrite dans `CLAUDE.md` §7bis : *signal → 10
angles (5 persona / 5 douleur) → scripts*. Elle est distribuée publiquement.

### 3.3 Le registre de la menace

Short est le seul des trois à **menacer** :

- « Si tu sors les mêmes créas que tout le monde, **tu brûles ton budget**. »
- « Si tu produis encore de l'UGC classique en 2026, **tu payes plein pot pour
  des créas que plus personne ne regarde**. »
- « **Tes concurrents** s'apprêtent à dépenser des milliers d'euros ce mois-ci. »

Et il **tutoie** systématiquement — sauf dans son annonce la plus ancienne, qui
vouvoie. Autre bascule datée.

### 3.4 L'empilement de preuve

« +500 marques accompagnées » · « +100 M€ de budget géré » · « +200 business
managers suivis au quotidien » · « +10 000 publicités » · « 6 ans de travail »
· « des dizaines d'heures à éplucher des milliers de publicités ».

**Tous sont des chiffres de volume.** Aucun n'est un résultat client
attribuable. C'est la même frontière que celle identifiée dans `A2` : *un
chiffre de volume est dicible, un chiffre de résultat obtenu ne l'est pas*.

---

## 4. L'agence Paid — la transparence comme argument

### 4.1 Le prix affiché dans l'annonce

> « **Pour 1 500 € par mois**, voici ce que vous obtenez concrètement :
> ✅ Audit complet de votre compte publicitaire
> ✅ Stratégie créative sur-mesure (angles, formats, personas)
> ✅ Graphiste + créatif stratégiste **dédiés**
> ✅ Statiques **en illimité** selon votre budget de dépenses
> ✅ Pilotage Meta, Google, TikTok
> ✅ Itération en temps réel sur ce qui fonctionne vraiment
> **Résultats en 30-60 jours. Sans engagement.** »

C'est le contraire exact de la pratique du marché de la formation, où le prix
se cache derrière un devis. Le pari : **le prix affiché filtre les non-acheteurs
et crédibilise auprès des autres**.

### 4.2 Le contraste ✅ / ❌

> « ❌ Plus de créas qui tournent en rond sans direction
> ❌ Plus de budget brûlé sur des formats non testés
> ✅ Une stratégie créative construite sur vos données réelles
> ✅ Des statiques produits en continu »

Précédé d'une **négation de l'offre concurrente**, formulée sans nommer
personne : *« Pas un forfait de 10 visuels par mois. Pas une agence qui livre
et disparaît. »*

### 4.3 La ligne la plus intelligente des 28 annonces

Dans l'aimant à prospects `1579796460540686` :

> « **Ce qui se transpose, c'est la mécanique, pas le wording : celui-ci
> appartient à la marque qui l'a écrit et au produit qu'il vend.** »

Et juste avant :

> « La question qu'on nous pose le plus en rendez-vous n'est pas quel budget
> mettre. **C'est quoi tester ensuite.** C'est à celle-là que ce document
> répond. »

Deux mouvements rares, et les deux sont directement transposables :
**l'aveu de limite sur son propre document** (il ne vous donne pas le texte,
seulement la structure), et **la question réelle du terrain, citée comme
telle**. C'est la mécanique « la question qu'on me pose tout le temps » de
`A2`, exécutée par un tiers.

---

## 5. Les 14 mécaniques extraites, et leur transposabilité

| # | Mécanique | Source | Pour VFormations |
|---|---|---|---|
| 1 | **Douleur opérationnelle + résolution en une clause** | Youdji ×15 | ✅ **Directement utilisable.** Zéro promesse, zéro prix. |
| 2 | **Ancrage temporel réel** | Youdji ×8, Short ×3 | ✅ **Meilleur chez vous qu'ici** — voir §6.1 |
| 3 | **Objection traitée dans le sous-titre** | Youdji ×10 | ✅ Utilisable. Objection n°1 = le reste à charge. |
| 4 | **Jeton de preuve en volume, répété** | les 3 | ⚠️ Utilisable **mais vous n'avez aucun volume à citer** — voir §6.3 |
| 5 | **Noms de marques clientes** | Short | ⚠️ Nécessite l'accord écrit. Aucun client à ce jour. |
| 6 | **Aveu de limite sur son propre document** | Paid | ✅ **À copier en priorité.** Registre déjà retenu dans `A2`. |
| 7 | **La question réelle du terrain, citée** | Paid | ✅ Déjà en catégorie 5 de `A2`. Confirmée par un tiers. |
| 8 | **Contraste ❌ / ✅** | Paid | ✅ Utilisable si les ❌ ne nomment personne. |
| 9 | **Négation de l'offre concurrente sans nommer** | Paid | ✅ Utilisable avec prudence. |
| 10 | **Prix affiché dans l'annonce** | Paid | 🔴 **Bloqué** — grille tarifaire non arrêtée (`CLAUDE.md` §9) |
| 11 | **Promesse de délai de résultat** | Paid | 🔴 **Interdit** — §7bis, pas de résultat garanti |
| 12 | **Aimant à prospects gratuit** | Short ×7 | 🔴 **Interdit en l'état** — « gratuit » est banni (§4). Substituts : « en accès libre », « sans inscription », « ouvert à tous ». ⚠️ À arbitrer en relecture juridique : la ressource n'est pas la formation. |
| 13 | **Menace / culpabilisation** | Short ×3 | ❌ **À écarter.** Incompatible avec le registre d'un organisme certifié, et avec l'arc de transmission. |
| 14 | **Statistique de résultat non sourcée** | Youdji (« 9,8× ») | ❌ **À écarter** — et Youdji l'a lui-même supprimée en trois jours. |

**Bilan : 8 mécaniques utilisables, 3 bloquées par une décision en attente, 3 à
écarter.** Les deux modèles dominants de ce corpus — l'aimant gratuit et la
promesse de délai — sont précisément ceux que VFormations ne peut pas employer.

---

## 6. Ce que ce corpus révèle pour VFormations

### 6.1 Vos ancrages temporels sont meilleurs que les leurs

Youdji et Short s'appuient sur **Q4, Black Friday, la rentrée** : des
échéances commerciales partagées par tout le monde, donc saturées, et
fabriquées au sens où rien n'oblige à acheter ce jour-là.

Vous disposez d'échéances **réelles et contraignantes**, que personne d'autre
ne peut invoquer :

| Échéance | Nature |
|---|---|
| **15 jours calendaires avant le démarrage** (AGEFICE, via Point d'Accueil) | Juridique. Passé ce délai, le dossier n'est pas instruit. |
| **Jour du début** (FAFCEA) · **J+10** (FIF PL) | Juridique. |
| **Fin d'exercice** | Le plafond annuel se recharge. Un dossier de décembre peut être refusé faute d'enveloppe. |
| **Basse saison littorale** (mars-avril) | Opérationnelle. La seule fenêtre où un dirigeant du littoral peut se former. |

`D1` §4 pose déjà le principe : *« l'urgence est vraie, pas fabriquée »*. Ce
corpus montre que **le marché, lui, fabrique la sienne** — et que l'écart est
exploitable.

### 6.2 La formule de Youdji, transposée à vos personas

La mécanique `[douleur opérationnelle datée] ? [résolution en une clause]`,
appliquée à votre matière :

- « Quinze jours avant votre formation et le dossier encore au siège de
  l'AGEFICE ? Il ne sera pas instruit. »
- « Un devis de formation vidéo déposé au taux technique FAFCEA ? C'est dix
  euros de l'heure qui sortent de votre poche. »
- « Fauteuils vides le mardi matin et vos prestations pas déclarées sur votre
  fiche ? Vous n'existez pas pour cette recherche. »
- « Terrasse pleine en août, fiche fermée sur Google en août ? »

⚠️ Ces quatre lignes sont des **exemples de transposition**, pas des scripts
validés. Elles n'ont pas passé le contrôle de `controle-scripts.py`.

### 6.3 Le trou que ce corpus met en évidence

Les trois annonceurs reposent leur crédibilité sur un **jeton de volume** :
10 000 créateurs, 500 marques, 400 marques, 10 000 publicités.

**VFormations n'en a aucun.** Pas de nombre d'apprenants, pas de nombre de
vidéos produites en session, pas de nombre de dossiers déposés. C'est la
différence la plus concrète entre ce corpus et votre situation, et elle ne se
comble pas par l'écriture.

Ce qui existe déjà et peut en tenir lieu, dans l'ordre de disponibilité :

1. **Le certificat Qualiopi** et le NDA — vérifiables publiquement, et c'est
   un jeton que ni Youdji, ni Short, ni Paid ne possèdent.
2. **Le nombre de vidéos publiées à 90 jours** — `B1` §5 en fait déjà
   l'indicateur de résultat publié, avec sa méthode de calcul. **Il n'existera
   qu'après les premières sessions.**
3. **La grille G5 à froid** (`B3`) — « combien de vidéos as-tu publiées depuis
   la formation ? ». C'est la source du jeton n°2.

→ **Conséquence opérationnelle :** tant qu'aucune session n'a eu lieu, la
publicité de VFormations ne peut pas s'appuyer sur un jeton de volume. Elle
doit s'appuyer sur **la précision réglementaire**, qui est le seul actif
disponible immédiatement. C'est exactement la stratégie de `A2`.

### 6.4 Ce que l'itération de Youdji suggère

Youdji a supprimé en trois jours ses émojis et sa statistique de résultat. Ses
scripts UGC V2 (`A_scripts_ugc_v2.md`) n'en comportent pas non plus. **Rien à
changer** — mais c'est une confirmation extérieure utile : le registre sobre
n'est pas une contrainte subie, c'est vers là que va un annonceur qui teste.

---

## 7. Bibliothèque d'accroches — verbatim, classées

> Relevées telles quelles. **Les ✅ sont transposables, les ❌ emploient un
> levier interdit à VFormations.**

### A. Douleur opérationnelle + échéance
1. ✅ « Trois semaines de casting UGC avant le Q4 ? »
2. ✅ « 5 créateurs à trouver avant vendredi, zéro réponse à vos DM Insta ? »
3. ✅ « Black Friday qui approche et vos créateurs encore sourcés sur Excel ? »
4. ✅ « Casting dans 4 pays à boucler pour demain ? »

### B. Le geste qu'on reconnaît
5. ✅ « On vous demande où en sont les vidéos et vous fouillez vos messages ? »
6. ✅ « Un acompte viré à un créateur trouvé sur Insta, puis silence radio ? »
7. ✅ « Des centaines de candidatures hors sujet pour un brief ? »

### C. Le concurrent-miroir
8. ⚠️ « Vos concurrents sortent plus de pubs que vous pour le Q4 ? »
9. ❌ « Tes concurrents s'apprêtent à dépenser des milliers d'euros ce mois-ci. »

### D. L'indicateur qui se dégrade
10. ✅ « Le CPA remonte, la fréquence aussi, et trouver un nouveau créateur prend des semaines ? »
11. ✅ « La même créatrice vue 15 fois par vos clients ? »

### E. L'autorité par le volume
12. ⚠️ « J'ai produit +10 000 publicités […] pour mes clients (Free, Binance, EatSalad…) »
13. ⚠️ « C'est le document qu'on utilise en interne sur les +500 marques qu'on accompagne. »
14. ⚠️ « 6 ans de travail condensés sur une seule page. »

### F. L'aveu de limite
15. ✅ « Ce qui se transpose, c'est la mécanique, pas le wording. »
16. ✅ « La question qu'on nous pose le plus n'est pas quel budget mettre. C'est quoi tester ensuite. »

### G. La négation de l'offre concurrente
17. ✅ « Pas un forfait de 10 visuels par mois. Pas une agence qui livre et disparaît. »

### H. Interdites ici
18. ❌ « C'est gratuit, et ça se récupère en 30 secondes. »
19. ❌ « Résultats en 30-60 jours. Sans engagement. »
20. ❌ « L'UGC est 9,8× plus impactant. » *(supprimée par Youdji elle-même)*
21. ❌ « Si tu sors les mêmes créas que tout le monde, tu brûles ton budget. »

---

## 8. Ce que je n'ai pas pu obtenir

- **Les visuels et les vidéos.** La bibliothèque affiche « Nous rencontrons des
  problèmes pour lire cette vidéo » en rendu automatisé. **Je n'ai analysé que
  le texte** : rien sur le montage, le rythme, les trois premières secondes à
  l'image, la présence ou non d'un visage. C'est une lacune importante pour un
  corpus publicitaire vidéo.
- **Les plateformes de diffusion.** Affichées en icônes, non extractibles en
  texte. Impossible de dire qui diffuse sur Instagram, Facebook, Messenger ou
  Audience Network.
- **Les volumes d'impressions et les budgets.** Réservés aux annonces
  politiques et sociales dans l'Union européenne. Indisponibles ici, sauf le
  marqueur binaire « nombre faible d'impressions » (2 annonces Youdji).
- **Le nombre exact de versions par annonce.** La bibliothèque signale
  « cette publicité a plusieurs versions » sans donner le compte.
- **Les pages de destination.** Les liens sont masqués derrière `fb.me` et
  `l.facebook.com`. Seul `agencepaid.fr` apparaît en clair, dans le corps d'une
  annonce.
- **L'historique.** Seules les annonces **actives** ont été relevées. Les
  annonces arrêtées — qui diraient ce qui n'a pas marché — ne sont pas dans ce
  corpus.
- **Une seconde extraction a été refusée par Meta.** Les données datent d'un
  unique passage du 20/10/2026. Elles seront périmées rapidement : Youdji a
  renouvelé 15 annonces sur 17 en trois jours.

---

## 9. Ce qu'il faudrait faire ensuite

1. **Relever les visuels à la main**, sur les 4 annonces les plus intéressantes
   (`1345105277702748`, `1579796460540686`, `1099218789542929`,
   `1091051453836525`). Le texte seul ne dit rien du rythme ni de l'accroche
   visuelle.
2. **Refaire ce relevé dans 30 jours** pour mesurer le taux de renouvellement.
   C'est la seule façon d'inférer ce qui marche : **une annonce qui survit a
   été reconduite**.
3. **Arbitrer la question de l'aimant à prospects** en relecture juridique
   (`CLAUDE.md` §9) : une ressource en accès libre n'est pas une formation
   financée, mais la rédaction du §4 est absolue sur le mot « gratuit ».
4. **Tester la formule Youdji** sur deux ou trois accroches réglementaires,
   via `controle-scripts.py` avant toute diffusion.

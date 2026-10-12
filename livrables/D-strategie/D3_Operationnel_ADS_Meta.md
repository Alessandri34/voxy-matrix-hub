# D3 — Plan opérationnel ADS Meta · 2 000 € · 12 créas vidéo

> **Statut : PLANIFIÉ, NON LANCÉ.** Déclenchement conditionné aux Gates 1 et 2 de `D2` §8.
> **Date : 12 octobre 2026.** Sources datées en fin de document.
> **Prérequis :** `D1` (économie), `D2` (tunnel + assistant dossier).

---

## 0. ⚠️ Ce que 2 000 € peuvent et ne peuvent pas faire

> Avant de dépenser, posons l'attente juste. **2 000 € ne construiront pas l'entreprise.**

| Ce que ce budget achète | Ce qu'il n'achète pas |
|---|---|
| ✅ **3 à 4 créas validées** par la donnée (hook, hold, CTR) | ❌ Un flux de clients régulier |
| ✅ **Un coût par rendez-vous mesuré** → on saura si le canal est rentable | ❌ Une sortie de la phase d'apprentissage Meta |
| ✅ **8 à 14 rendez-vous qualifiés** → **2 à 4 clients** [Hypothèse] | ❌ Un CPL fiable par créa (budget trop faible) |
| ✅ Une audience d'engagement vidéo réutilisable | ❌ Des audiences similaires (lookalikes) exploitables |

**Retour attendu :** 2 à 4 clients × 1 933 € de marge = **3 900 à 7 700 €** pour 2 000 € dépensés (ROI 2× à 4×).
**C'est correct, mais ce n'est pas le point.** Le vrai livrable de ce budget est **l'apprentissage** : savoir quelle promesse fait réagir un dirigeant de TPE héraultais. Cet actif sert ensuite à tout — le site, les prescripteurs, le discours de vente.

> 🎯 **Règle :** on juge cette campagne sur le **coût par rendez-vous tenu**, jamais sur le nombre de leads.

---

## 1. 🔴 Conformité — à lire avant d'écrire la moindre créa

### 1.1 Le risque n°1 : la catégorie de publicité spéciale « Emploi »

Meta impose des **restrictions de ciblage sévères** aux publicités classées en « Special Ad Category ». **Le test porte sur le CONTENU de l'annonce, pas sur notre statut d'organisme de formation.** [Vérifié — politique Meta, sources octobre 2026]

| Si la créa parle de… | Conséquence |
|---|---|
| emploi, employabilité, **reconversion**, « décrocher un poste », diplôme, RNCP, titre certifiant | 🔴 **Classement en SAC Emploi** |
| développer **son entreprise existante**, attirer des clients, visibilité locale | ✅ Hors SAC |

**Si la SAC tombe** (Europe) : âge figé 18-65+, genre « tous », **rayon géographique minimum 15 km**, suppression des codes postaux, des exclusions de lieu, **des audiences similaires et des audiences enregistrées**. Meta applique aussi des **classifieurs automatiques** : une annonce non déclarée mais classée Emploi est **refusée**.

> ### 🚫 Vocabulaire interdit dans les 12 créas
> `emploi` · `employabilité` · `reconversion` · `se reconvertir` · `décrocher un poste` · `diplôme` · `RNCP` · `titre certifiant` · `carrière`
>
> ✅ **On parle TOUJOURS de développer une entreprise qu'on a déjà**, jamais de trajectoire professionnelle individuelle.

**Action avant lancement :** demander par écrit au support Meta Business la confirmation que l'offre ne relève pas de la SAC Emploi, **et conserver la capture**. En cas de doute → déclarer.

### 1.2 Loi anti-fraude 2026-534 — nos propres formulaires sont un canal de contrôle

> **Art. 44 :** les agents de contrôle peuvent procéder à des **constatations sous identité d'emprunt** auprès des organismes de formation **dont l'inscription peut se faire en ligne**. [Vérifié — loi n° 2026-534 du 25/06/2026, JO 26/06]

🔴 **Traduction opérationnelle : la personne qui remplit notre formulaire Meta peut être un inspecteur.**

- Chaque promesse de l'annonce doit être **tenable telle quelle** par le premier appel de relance.
- La loi élargit par ailleurs les cas où une action est **réputée inexécutée** → remboursement des fonds.
- Les sanctions sont désormais des **amendes administratives prononcées directement par les DREETS**, sans passage par le procureur, avec **publication possible**.

### 1.3 Formulations bannies (cumul Meta + droit français)

| ❌ Interdit | ✅ Formulation conforme |
|---|---|
| « gratuit », « 100 % financé », « sans reste à charge », « formation offerte » | « finançable selon votre statut — votre reste à charge vous est annoncé au devis » |
| tout chiffre de CA / revenu, captures de gains | décrire **le mécanisme pédagogique**, pas un résultat chiffré |
| « résultats garantis », « X clients garantis » | « une méthode et une régularité » |
| Promesse d'opportunité économique | Meta interdit explicitement les allégations de gain irréaliste |

### 1.4 Tracking — bloquant avant le 1ᵉʳ euro

Le Pixel pose des cookies non essentiels → **consentement préalable obligatoire en France**. La Conversions API **n'est pas un contournement** : elle déplace le point de collecte, pas la base légale. [Vérifié — recommandation cookies CNIL consolidée, janvier 2026]

**✅ Checklist bloquante (J-7) :**
- [ ] CMP (bandeau de consentement) installée **et testée** : refus = aucun tag ne se déclenche
- [ ] Pixel + Conversions API en double envoi, avec `event_id` de déduplication
- [ ] Filtre back-end : aucun événement CAPI envoyé sans consentement enregistré
- [ ] Événements nommés : `Lead` (formulaire) → `Schedule` (RDV pris) → `Purchase` (inscription)
- [ ] Domaine vérifié + 8 événements agrégés priorisés
- [ ] **UTM sur toutes les créas**, `utm_content` = identifiant de créa — *sans ça, le test ne vaut rien*
- [ ] Page d'offre conforme publiée (conditions d'accès, contenu, modalités pédagogiques, financements)

---

## 2. Les 12 créas vidéo — matrice

> Les scripts existent déjà (chantier A, artefact UGC V4). Il s'agit de **choisir et produire**, pas de réécrire.
> **Niveau de conscience :** nos cibles sont **conscientes du problème, pas du produit** (Schwartz). → **Pitch direct interdit. Structure Problème → Agitation → Solution.**

### Vague A — 6 créas · test d'ANGLES · cible prioritaire (commerce / restauration, AGEFICE)

| # | Angle | Promesse / douleur | Format | Conscience |
|---|---|---|---|---|
| **A1** | **Dépendance aux plateformes** | « 30 % de commission sur chaque commande » | Facecam + b-roll | Problème |
| **A2** | **Le concurrent visible** | « Votre terrasse est vide le mardi, celle d'en face est pleine » | B-roll + voix off | Problème |
| **A3** | **Objection levée** | « J'ai déjà essayé de poster, ça n'a rien donné » | Facecam | Solution |
| **A4** | **Démonstration** | « 3 mois de contenu filmés en une journée » | Démo accélérée | Solution |
| **A5** | **Autonomie vs agence** | « Une agence vous facture chaque mois. Nous, une fois. » | Facecam | Produit |
| **A6** | **Financement honnête** | « Non, ce n'est pas gratuit. Voilà ce que ça vous coûte vraiment. » | Facecam | Produit |

> 💡 **A6 est volontairement contre-intuitive** : annoncer honnêtement le reste à charge est **différenciant** sur un marché saturé de « 100 % financé », **conforme**, et filtre les curieux. À tester sérieusement.

### Vague B — 6 créas · variations des gagnantes + nouveaux segments

| # | Contenu |
|---|---|
| **B1-B3** | **3 variations des 2 meilleures de la vague A** — on change **uniquement l'accroche (3 premières secondes)**, le corps reste identique |
| **B4** | Cible **Léa** (salon) — « être à l'aise face caméra avec juste un téléphone » |
| **B5** | Cible **Karim** (artisan) — offre Atelier Déclic / parcours individualisé |
| **B6** | **Preuve sociale** — cas client filmé de la cohorte fondatrice *(disponible seulement après Gate 2)* |

> ⚠️ **B6 est la créa la plus importante du lot.** Une preuve locale réelle surperforme systématiquement une promesse. Si la cohorte fondatrice n'a pas produit de cas client, **repousser la vague B**.

---

## 3. Structure de campagne

### La contrainte qui dicte tout : on ne sortira PAS de la phase d'apprentissage

Meta exige **~50 conversions/semaine par ad set** pour stabiliser la diffusion. À un CPL de 30 €, cela représente **1 500 €/semaine**. Notre budget hebdomadaire est de **~330 €**. [Vérifié]

> ### 🔴 Trois conséquences non négociables
> 1. **UN SEUL ad set.** Jamais de fragmentation « pour bien tester » — c'est l'erreur qui brûle le budget.
> 2. **Ciblage large** : Hérault (34) + audience automatisée, **sans centres d'intérêt**. Un ciblage « dirigeants TPE » réduirait l'audience à ~50-100 k et ferait monter le CPM sans gain de qualité.
> 3. **On juge les créas sur les métriques créatives, pas sur le CPL.**

### Paramétrage

| Paramètre | Valeur | Justification |
|---|---|---|
| Objectif | **Prospects** (formulaire natif) en test · Conversions site au scale | CPL natif ~30 % moins cher ; landing page convertit mieux en RDV |
| Budget | **ABO** (par ad set) en test · CBO au scale | Le CBO affame les nouveaux ad sets |
| Ad sets | **1 seul** | Cf. ci-dessus |
| Annonces par ad set | **6 maximum** | Au-delà, le signal se dilue |
| Ciblage | Département 34, 18-65+, tous genres, **sans intérêts** | Robuste même si la SAC tombe |
| Placements | Automatiques (98 % mobile : Feed ~50 %, Reels/Stories ~40 %) | — |
| Format | Vertical 9:16, sous-titres **incrustés** | Le son est coupé par défaut |

### Le formulaire natif — réglages anti-mauvais leads

Les leads de formulaire natif atteignent un rendez-vous commercial dans ~2 % des cas, contre ~17 % depuis une landing page. **Il faut compenser par la qualification.** [Vérifié]

- ✅ Type **« intention supérieure »** (étape de révision avant envoi)
- ✅ **5 questions de qualification obligatoires :**
  1. Nom de l'entreprise
  2. Votre activité (commerce / restauration / artisanat / services / autre)
  3. Nombre de salariés
  4. Êtes-vous gérant non salarié ? (oui / non / je ne sais pas) → *identifie le financeur*
  5. Quand souhaitez-vous démarrer ? (ce trimestre / dans 6 mois / je me renseigne)
- ✅ **Opt-in explicite et horodaté** → sécurise juridiquement la relance téléphonique
- ✅ **Le formulaire achète un rendez-vous de 20 minutes, pas une inscription.**

---

## 4. 📅 Les 3 phases & la répartition du budget

### Budget total : 2 000 €

| Phase | Durée | Budget | €/jour | Objectif |
|---|---|---|---|---|
| **Phase 0 — Préparation** | S0 | **0 €** | — | Tracking, conformité, production des 12 créas |
| **Phase 1 — TEST** | S1-S3 | **630 €** | 30 € | Trier les 12 créas sur hook / hold / CTR |
| **Phase 2 — APPRENTISSAGE** | S4-S5 | **420 €** | 30 € | Mesurer le **coût par RDV tenu** des gagnantes |
| **Phase 3 — SCALE** | S6-S8 | **735 €** | 35 € | Monter sur les gagnantes + retargeting |
| **Réserve** | — | **215 €** | — | Retargeting + imprévus |

---

### 🔬 Phase 1 — TEST (S1-S3) · 630 €

> **But : éliminer, pas convertir.** On cherche quelle promesse arrête le pouce.

| Vague | Durée | Budget | Détail |
|---|---|---|---|
| **A** | 14 jours | **420 €** | 6 créas (A1-A6), 1 ad set ABO, 30 €/j → **~70 € par créa** |
| **B** | 7 jours | **210 €** | 6 créas (B1-B6), même structure + les 1-2 gagnantes de A maintenues |

**Si le volume de leads reste < 5/semaine → optimiser sur « Vues de page de destination » ou « Clics »** plutôt que sur les prospects, pour obtenir un signal exploitable.

#### Seuils de décision (à 2 000 impressions minimum par créa)

| Métrique | Formule | ✅ Garder | ❌ Tuer |
|---|---|---|---|
| **Hook rate (3 s)** | vues 3 s / impressions | ≥ 25 % (excellent : 30-40 %) | **< 15 %** |
| **Hold rate (15 s)** | vues 15 s / vues 3 s | ≥ 15 % | **< 10 %** |
| **CTR sortant** | clics sortants / impressions | ≥ 0,8 % | **< 0,5 %** |

> ⚠️ **Figer la formule du hold rate dans le tableau de bord AVANT de mesurer** — deux définitions concurrentes circulent, et les seuils ne veulent rien dire si la formule change.

#### Grille de diagnostic

| Symptôme | Cause | Action |
|---|---|---|
| Hook bas | Les 3 premières secondes ratent | Refaire **uniquement** l'accroche, garder le corps |
| Hook bon, hold bas | La promesse de l'accroche n'est pas tenue | Réécrire le corps |
| Hook + hold bons, CTR bas | L'offre ou l'appel à l'action ne convainc pas | **Ce n'est pas la vidéo** — revoir l'offre |

---

### 📈 Phase 2 — APPRENTISSAGE (S4-S5) · 420 €

- On garde **les 2-3 créas gagnantes uniquement**.
- On bascule l'optimisation sur **Prospects**.
- On construit la **première audience personnalisée** : vues vidéo ≥ 15 s, 365 jours, toutes créas confondues (seuil exploitable ~1 000 personnes).
- **On mesure enfin ce qui compte : le coût par rendez-vous TENU.**

| Indicateur | Attendu | 🚨 Alerte |
|---|---|---|
| CPM | 12-20 € | > 25 € |
| CPC sortant | 0,90-2,00 € | > 2,50 € |
| CPL (formulaire natif) | 18-40 € | > 50 € |
| **Coût par RDV tenu** | **120-250 €** | **> 350 €** |

> 🚦 **GATE — fin S5 (décision go/no-go) :**
> - **Coût par RDV tenu < 250 €** → on engage la Phase 3.
> - **Entre 250 et 350 €** → on prolonge 1 semaine en corrigeant l'offre ou la qualification.
> - **> 350 €** → 🛑 **on coupe.** Le budget restant repart vers les prescripteurs (`D2` §3), canal moins cher.

---

### 🚀 Phase 3 — SCALE (S6-S8) · 735 €

- Montée par paliers de **+20 % toutes les 48 h** (au-delà, on réinitialise l'apprentissage).
- Bascule possible vers une **landing page** (meilleur taux de transformation en rendez-vous).
- Ajout du **retargeting** (~150 €, 15 % max) : ouvreurs de formulaire non soumis + visiteurs du site 180 j + engagement page/Instagram 365 j — **fusionnés en une seule audience**.
- **Renvoyer les issues CRM** (RDV tenu, inscription) vers Meta **via Conversions API** : c'est le signal le plus fort disponible, bien supérieur à n'importe quel centre d'intérêt.

> ❌ **Audiences similaires (lookalikes) : on n'y touche pas ce trimestre.** Il faut ~100 clients sources pour qu'elles soient utiles, et elles disparaissent si la SAC Emploi tombe.

---

## 5. Tableau de bord hebdomadaire

| Niveau | Indicateur | Source |
|---|---|---|
| **Créa** | Hook rate · Hold rate · CTR sortant · impressions | Meta Ads Manager |
| **Campagne** | Dépense · CPM · CPC · CPL | Meta Ads Manager |
| **Business** | Leads → RDV pris → **RDV tenus** → devis → **inscriptions** | CRM / tableur |
| **Décision** | **Coût par RDV tenu** · coût par inscription | Calcul |

> **Le seul chiffre à regarder en premier chaque lundi : le coût par rendez-vous tenu.**

---

## 6. ⚠️ Les 5 erreurs qui brûleraient les 2 000 €

| # | Erreur | Conséquence |
|---|---|---|
| **1** | **Un seul mot du champ « emploi »** dans une créa (reconversion, diplôme, employabilité) | Classement en SAC Emploi → perte du ciblage fin et des audiences, refus des annonces non déclarées. **On perd le ciblage ET le temps.** |
| **2** | **Fragmenter en 4-6 ad sets « pour bien tester »** | À 30 €/j, chaque ad set reste sous le seuil d'apprentissage → **aucune donnée exploitable**. |
| **3** | **Dépenser avant que CMP + Conversions API ne soient câblées** | On paie le média, on perd le signal de conversion, on s'expose côté CNIL. Les 630 € de test deviennent non réinvestissables. |
| **4** | **Juger les 12 créas au CPL** | 70 € par créa ne produit aucun CPL fiable. Tuer une bonne créa sur un lead manquant = jeter 6 semaines de production. |
| **5** | **Promettre « financé, zéro reste à charge »** | Double sanction : rejet Meta (allégation d'opportunité économique) **et** risque de contrôle sous identité d'emprunt via notre propre formulaire (art. 44), avec publication des sanctions. |

---

## 7. Checklist de lancement

**Conditions préalables (bloquantes) :**
- [ ] Gate 1 `D2` : ≥ 3 inscrits de la cohorte fondatrice
- [ ] Gate 2 `D2` : indicateurs de résultats publiés + 2 cas clients en ligne
- [ ] Assistant dossier de financement opérationnel
- [ ] Confirmation écrite Meta sur la SAC Emploi
- [ ] Checklist tracking §1.4 intégralement cochée

**Production :**
- [ ] 12 créas tournées, montées, sous-titrées, au format 9:16
- [ ] Relecture conformité de chaque script (vocabulaire interdit §1.1 et §1.3)
- [ ] Formulaire natif configuré avec les 5 questions de qualification
- [ ] UTM posés, `utm_content` = identifiant de créa
- [ ] Tableau de bord créé, **formule du hold rate figée**

**Organisation :**
- [ ] Qui rappelle les leads, sous quel délai ? *(objectif : < 2 h — c'est le facteur n°1 du taux de RDV)*
- [ ] Agenda de rendez-vous ouvert sur les 3 prochaines semaines
- [ ] Dates des cohortes publiées, cohérentes avec le délai AGEFICE de **J-15 minimum via Point d'Accueil**

---

## 8. Sources

- **Catégories de publicité spéciale Meta** — PPC Land (11/10/2026) · LeadSync (06/10/2026)
- **Benchmarks France** — Observatoire des prix de la publicité en ligne, Talyco (07/07/2026) : CPM médian Meta 3,40 €, CPL médian 20 € *(tous secteurs — nos fourchettes B2B sont volontairement plus hautes)*
- **ABO vs CBO / phase d'apprentissage** — Adnova, SuperScale, AdMakeAI (2026)
- **Seuils hook / hold rate** — AdLibrary, Adrise Lab, AdSights (2026) — *heuristiques de praticiens, pas des chiffres officiels Meta*
- **Formulaire natif vs landing page** — Benchmarketing, AdAmigo (2026)
- **Loi n° 2026-534 du 25/06/2026** — Centre Inffo, Digiformag
- **Consentement / Pixel / CAPI** — CNIL, recommandation cookies consolidée (janvier 2026) · Cookiebot (2026)

> ⚠️ **Réserve méthodologique :** les pages officielles Meta n'étaient pas accessibles depuis l'environnement de recherche. Les éléments de politique Meta proviennent de sources tierces datées d'octobre 2026 déclarant les avoir vérifiées. **La qualification SAC doit être confirmée par le support Meta avant lancement.**

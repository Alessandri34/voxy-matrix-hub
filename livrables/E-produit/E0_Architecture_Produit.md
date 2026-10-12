# E0 — Vision produit & architecture de l'application client

> **Casquette : Directeur produit.**
> **Date : 12 octobre 2026.** Prérequis : `D0` (thèse), `D1` (économie), `D2` (commercialisation).
> ⚠️ **Rappel de la règle D9 :** rien de tout ceci n'est développé avant **5 formations vendues et délivrées**. Ce document est une **cible d'architecture**, pas un bon de commande.

---

## 1. Le problème réel que le produit doit résoudre

> Le dirigeant de TPE n'a pas un problème d'outils. Il en a déjà trop.
> Il a un problème de **savoir quoi dire** et de **tenir dans la durée**.

Ce qui se passe réellement après une formation, quel que soit l'organisme :

```
Semaine 1  ████████████  Motivation maximale, il publie 4 fois
Semaine 2  ███████       Il publie 2 fois
Semaine 3  ███           Une fois, "quand j'aurai le temps"
Semaine 4  ▪             Plus rien
Semaine 8  ·             "C'était bien, mais j'ai pas tenu"
```

**Aucun concurrent n'adresse cette courbe.** Les agences créent de la dépendance, les OF livrent une compétence qui se dégrade, les SaaS ne sont jamais activés.

> ## 🎯 Promesse produit
> **« Chaque lundi matin, tes 3 contenus de la semaine sont prêts. Tu n'as plus qu'à les tourner. »**

C'est l'inverse d'un outil qu'on ouvre quand on y pense (on n'y pense jamais). **C'est un rendez-vous qui vient à toi.** C'est la traduction produit exacte du positionnement `D0` §5 : *« on vous forme à le faire, et on vous laisse l'outil qui le rend tenable »*.

---

## 2. Les trois utilisateurs du produit

> Une particularité de notre modèle : **le même produit sert trois intérêts différents.** C'est ce qui le rend économiquement viable.

| Utilisateur | Ce qu'il en tire | Module clé |
|---|---|---|
| 👤 **Le client (dirigeant TPE)** | Savoir quoi publier, et tenir dans la durée | Rituel hebdomadaire · Générateur de scripts |
| 🏢 **Nous (l'organisme)** | Coût administratif divisé · risque d'audit réduit · rétention | **Moteur de preuves Qualiopi** · pilotage des cohortes |
| ⚖️ **Le contrôle (Qualiopi / financeur)** | Preuve d'apprentissage réel, tracée, horodatée | Journal d'activité de l'apprenant |

> 💡 **L'insight central :** la trace d'usage du client **EST** la preuve pédagogique. Le même geste, saisi une fois, sert la valeur client **et** la conformité. C'est ce qui justifie de construire plutôt que d'acheter un SaaS du marché.

---

## 3. Architecture fonctionnelle

```
┌──────────────────────────────────────────────────────────────┐
│  ONBOARDING — « on apprend à te connaître en 6 minutes »     │
│  Questionnaire court + enrichissement automatique            │
│  (SIREN → Sirene/INSEE · site → lecture · marché → pubs)     │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
         ┌───────────  FICHE ENTREPRISE  ───────────┐
         │ secteur · offres · personas · zone ·      │
         │ concurrents · angles · contraintes légales│
         └────────────────────┬─────────────────────┘
                              ↓
   ┌──────────────┬───────────┴─────────┬──────────────────┐
   ↓              ↓                     ↓                  ↓
┌────────┐  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│DIAGNOS-│  │ GÉNÉRATEUR   │   │ GÉNÉRATEUR   │   │  RITUEL      │
│TIC DE  │  │ DE SCRIPTS   │   │ DE PROMPTS   │   │ HEBDOMADAIRE │
│VISIBI- │  │     (E1)     │   │  .MD  (E2)   │   │ 3 contenus/  │
│LITÉ    │  │              │   │              │   │ semaine      │
└────────┘  └──────┬───────┘   └──────────────┘   └──────┬───────┘
                   ↓                                      ↓
         ┌─────────────────────────────────────────────────────┐
         │  BIBLIOTHÈQUE DE CONTENUS + BOUCLE DE MESURE 🏆      │
         │  produit ? publié ? résultat ? → jeu de données      │
         └──────────────────────┬──────────────────────────────┘
                                ↓
         ┌─────────────────────────────────────────────────────┐
         │  MOTEUR DE PREUVES QUALIOPI (interne)               │
         │  journal d'activité → livrables → évaluations       │
         └─────────────────────────────────────────────────────┘
```

### 3.1 Modules côté client

| Module | Rôle | Priorité |
|---|---|---|
| **① Onboarding** | 8 questions + enrichissement auto. **Objectif : < 6 minutes.** | 🔴 v1 |
| **② Diagnostic de visibilité** | Score sa fiche Google Business, son site, ses réseaux **vs 3 concurrents locaux**. Sert d'outil de vente **et** d'autodiagnostic FAFCEA. | 🔴 v1 |
| **③ Générateur de scripts** (`E1`) | Le cœur. Signal → angles → scripts, avec analyse des pubs du marché local. | 🔴 v1 |
| **④ Rituel hebdomadaire** | Chaque lundi : 3 contenus prêts, adaptés à la saison et à son actualité. **Le module de rétention.** | 🔴 v1 |
| **⑤ Générateur de prompts .MD** (`E2`) | L'utilisateur décrit une idée (texte ou voix) → prompt structuré actionnable. | 🟠 v1.5 |
| **⑥ Bibliothèque + mesure** | Ce qu'il a produit, publié, et ce que ça a donné. **Alimente le moat données.** | 🔴 v1 |
| **⑦ Espace formation** | Ses modules, livrables, évaluations, attestation. | 🟠 v1.5 |
| **⑧ Calendrier éditorial** | Vue mensuelle, rappels. | 🟡 v2 |

### 3.2 Modules côté interne (nous)

| Module | Rôle | Priorité |
|---|---|---|
| **⑨ Moteur de preuves Qualiopi** | Génère automatiquement : journal d'activité, analyse d'activité AFEST, phases réflexives horodatées, grilles d'évaluation. **Économise ~100 €/apprenant et répond aux risques R1/R6.** | 🔴 v1 |
| **⑩ Pilotage des cohortes** | Remplissage, dossiers de financement, échéances AGEFICE (J-15), relances. **L'indicateur n°1 de `D1` §11.** | 🔴 v1 |
| **⑪ CRM léger** | Pipeline : lead → RDV → devis → dossier → inscrit. | 🟠 v1.5 |

---

## 4. Ce qui nous différencie — et pourquoi c'est défendable

| Concurrent | Ce qu'il fait | Ce qui lui manque |
|---|---|---|
| **ChatGPT / Claude** (usage direct) | Génère du texte à la demande | ❌ Ne connaît ni son entreprise, ni son marché local · ❌ Aucune méthode · ❌ **Ne mesure rien** · ❌ Le dirigeant ne sait pas quoi demander |
| **Canva, Later, Metricool** | Création graphique et publication | ❌ Ne dit pas **quoi dire** · ❌ Pas d'analyse concurrentielle locale |
| **Agences locales** | Font à sa place | ❌ Dépendance · ❌ Coût récurrent élevé · ❌ Non finançable |
| **Outils d'espionnage publicitaire** (Foreplay, Minea) | Montrent les pubs des concurrents | ❌ En anglais, orientés e-commerce international · ❌ Inutilisables par un restaurateur de Sète |
| **✅ Nous** | Onboarding métier + analyse du marché **local** + méthode + **boucle de mesure** + rituel | — |

### 🏆 Les 3 barrières qu'on construit

1. **Le jeu de données propriétaire.** Chaque script généré est suivi : produit ? publié ? résultat ? Après 100 clients × 12 scripts, nous détenons un corpus français étiqueté par la performance sur la publicité locale de TPE. **Aucun outil généraliste ne l'a, et il ne s'achète pas.**
2. **La connaissance métier encodée.** Nos personas, angles, hooks, garde-fous légaux et frameworks sont le fruit du chantier A. Un concurrent devrait les reconstruire.
3. **Le couple formation + logiciel.** Un éditeur SaaS ne devient pas Qualiopi en moins de 12-18 mois.

---

## 5. ⚖️ Architecture de conformité (par construction)

> Rappel `D0` §3 : trois périmètres, trois contrats, trois factures. **L'architecture technique doit refléter cette séparation**, sinon elle ne tiendra pas en contrôle.

| Dans le produit | Règle technique |
|---|---|
| **Pendant la formation** | Compte en mode « plateau technique pédagogique ». Accès rattaché à la session de formation, **avec date de fin**. |
| **Après la formation** | Bascule explicite : l'accès pédagogique expire, un **écran d'offre d'abonnement** apparaît — **jamais une reconduction automatique**. |
| **Facturation** | Deux entités de facturation distinctes dans la base. Une facture ne peut **jamais** contenir à la fois de la formation (exonérée de TVA) et de l'abonnement (TVA 20 %). Contrainte à poser en base, pas en procédure. |
| **Done-for-you** | Module de devis séparé, **non accessible depuis le parcours d'inscription à une formation**. |

### RGPD — trois points non négociables
1. 🔴 **Les entrepreneurs individuels sont des personnes physiques.** « Données publiques d'entreprise » ne sort **pas** du RGPD pour nos personas (artisans, restaurateurs, salons). À traiter comme des données personnelles.
2. 🔴 **Honorer l'indicateur d'opposition Sirene** (art. A123-96 c. com.) : une personne physique peut s'opposer à l'usage de ses informations à des fins de prospection.
3. 🔴 **L'analyse du site du client se fait sous mandat écrit**, inséré au contrat. C'est une autorisation contractuelle, pas du moissonnage de tiers — cela évacue l'essentiel du risque.

---

## 6. Stack technique recommandée

> Critères : **coût bas, souveraineté UE, rapidité de développement, pas de dette.**

| Couche | Choix | Pourquoi |
|---|---|---|
| **Front** | Next.js (React) + Tailwind | Écosystème, rapidité, réutilise le design du site |
| **Base de données / Auth / Stockage** | PostgreSQL managé **en région UE** (Supabase ou Scaleway) | Tout-en-un, coût marginal au départ |
| **Hébergement applicatif** | **Scaleway ou OVHcloud (France)** | Cohérent avec la souveraineté exigée en `E3` |
| **LLM** | **API uniquement, routage UE d'abord** — voir `E3` | ❌ **Jamais de GPU avant ~300 clients** (seuil démontré en `E3`) |
| **Transcription vocale** | API (modèle UE privilégié) | Auto-héberger pour économiser 30 €/mois est absurde |
| **Données entreprise** | API Recherche d'entreprises (gratuite) + Sirene/INSEE (gratuite) | Socle fiable à coût nul |
| **Analyse concurrentielle** | Meta Ad Library (FR) + Google Ads Transparency via BigQuery | Voir `E3` — verdicts juridiques |
| **E-mail transactionnel** | Service standard, domaine vérifié | — |

**Coût d'infrastructure estimé en v1 :** **≈ 90-170 €/mois** tout compris (détail en `E3`).

---

## 7. 📐 Séquencement — comment on construit sans se tromper

> **Règle D9 : aucune fonctionnalité n'est développée avant d'avoir été exécutée à la main dans une vraie session de formation.**

### v0 — « le formateur est l'application » (M0-M3) · **coût de développement : 0 €**
Le générateur de scripts est un **prompt structuré** que le formateur exécute **avec** le client, en partage d'écran, pendant la formation. On note :
- Quelles questions du questionnaire sont mal comprises
- Quels angles le client rejette systématiquement
- Combien de temps prend chaque étape
- Ce que le client demande qu'on n'avait pas prévu

> C'est la **phase la plus rentable du projet produit** : on apprend tout, on ne dépense rien. **Elle est non négociable.**

### v1 — « l'outil du formateur » (M3-M6)
On outille uniquement ce qui a été répété 10 fois. Modules ①②③④⑥⑨⑩. Interface minimale, utilisée **en session**, pas encore en autonomie.

### v1.5 — « l'outil de l'apprenant » (M6-M9)
Le client y accède seul pendant sa formation. Ajout de ⑤⑦⑪. **Le rituel hebdomadaire démarre.**

### v2 — « l'abonnement » (M9-M12)
Ouverture de l'offre payante **après** formation. Module ⑧. Tarif cible **79 €/mois** (`D1` §5).

---

## 8. Modèle de données (noyau)

```
entreprise        → siren, raison_sociale, naf, effectif, zone,
                    site, opposition_prospection (bool)
profil_marche     → secteur, offres[], personas[], concurrents[],
                    angles_valides[], contraintes_legales[]
contenu           → type, angle, persona, script, hook_utilise,
                    statut (généré|produit|publié), date_publication
mesure            → contenu_id, vues, interactions, demandes_entrantes,
                    source_declaree (auto|déclaratif)      ← 🏆 LE MOAT
session_formation → cohorte, dates, apprenants[], formateur,
                    statut_dossier_financement
trace_pedagogique → apprenant, horodatage, activité, livrable,
                    phase_reflexive, evaluation                ← PREUVE QUALIOPI
abonnement        → entreprise_id, début, fin, statut    ← ENTITÉ SÉPARÉE (TVA)
```

> ⚠️ **`mesure` est la table la plus importante du produit.** C'est elle qui transforme un générateur de texte (copiable en un week-end) en **actif qui se renforce avec le temps**. Si une seule table doit être conçue avec soin dès le premier jour, c'est celle-là.

---

## 9. Ce qu'on ne construit PAS

| ❌ | Pourquoi |
|---|---|
| Un éditeur vidéo | CapCut existe, est gratuit et meilleur |
| Un outil de publication multi-réseaux | Complexe, fragile (APIs), peu différenciant |
| Une application mobile native | Le web responsive suffit en v1 et v2 |
| Un module de paiement intégré | Virement et lien de paiement suffisent au départ |
| Un LLM auto-hébergé | Démonstration chiffrée en `E3` : jamais rentable avant ~300 clients |
| Un « agent autonome » qui publie tout seul | ❌ **Contraire au positionnement** : on forme à l'autonomie, on ne la remplace pas. Et ça détruirait la preuve pédagogique. |

---

> **Suite :** `E1` (générateur de scripts) · `E2` (générateur de prompts) · `E3` (stack technique et coûts) · `E4` (idées stratégiques).

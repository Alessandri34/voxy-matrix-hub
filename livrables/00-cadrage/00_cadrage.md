# 00 — Cadrage du projet (fin de Phase 0)

> **Statut :** document vivant. Rédigé le 7 octobre 2026.
> **Casquettes mobilisées :** CEO / CPO / CTO.
> **Règle d'or du projet :** on construit un organisme de formation **finançable et défendable en contrôle**. Toute affirmation réglementaire est datée et classée [Vérifié] / [À vérifier] / [Hypothèse].

---

## 1. Synthèse de l'inventaire des sources

### 1.1 Environnement réel (différent du master prompt)
- Travail mené en **session cloud**, connectée au seul dépôt GitHub `alessandri34/voxy-matrix-hub`.
- Le dossier local `VForMation LLM Work` et **l'étude de marché PDF ne sont pas accessibles** ici → **le PDF reste à fournir** (dépôt dans le chat).
- Branche de travail : `claude/new-session-nefcch`. Aucun `git push` ne sera fait sans accord explicite (règle 8).

### 1.2 Contenu du dépôt « Voxy Matrix Hub » [Vérifié — lecture directe]
Dépôt **statique** (HTML + Markdown), ~1,4 Mo, 67 `.md` + 30 `.html`. **Pas** d'application : ni base de données, ni back-end, ni `package.json`.

| Élément | Contenu | Utilité | Lacune |
|---|---|---|---|
| `index.html`, `Hub_Documentaire.html`, `CODEX_IA.html` | Portail « Hub » + codex, design premium « Ethereal Glass » | Base **design/vitrine** réutilisable | Aucune mention légale obligatoire |
| `Catalogue OFFRE/` | Matrice des 9 offres (3 thématiques × 3 paliers) | Cœur de l'offre | Aucun prix, aucun coût chiffré |
| `OFFRE 1/2/2V2/3/` | E-Com Commando · Outbound Autonome/Hybride · Drive-to-Store (landing pages, syllabus, manuels, guides formateur) | Contenus pédagogiques déjà rédigés | **Vocabulaire à risque** (voir §3) ; concept vidéo du master prompt absent |
| `Challenge/` | Audit concurrentiel + stress-test CEO/CPO | Autocritique déjà lucide | — |
| `Referentiel_Competences_Qualiopi.md` | Compétences par offre | Brique Qualiopi | Embryonnaire, 7 critères non couverts |
| `skills/` | 8 cadres méthodo (copywriting, growth, « Qualiopi Zéro-Admin »…) | Méthodes | « Zéro-Admin » à recadrer côté conformité |

**Hygiène Git :** `.DS_Store` versionnés, **aucun `.gitignore`**, **aucun secret détecté** (règle 9 respectée). → créer un `.gitignore` (chantier B/D).

---

## 2. Décisions prises (lot 1 validé)

| # | Décision | Statut |
|---|---|---|
| D1 | **NDA + Qualiopi obtenus** → on a le droit de parler de financement (avec la formulation de la charte). On a aussi **tout à perdre** en cas de contrôle défavorable. | ✅ Acté |
| D2 | **Logique pédagogique = apprentissage réel** : le client apprend en pratiquant ; nos livrables = preuves pédagogiques (émargements, phases réflexives, évaluations). | ✅ Acté |
| D3 | **On garde les 3 offres + on prévoit le concept vidéo**, avec une **« version lisse »** = discours professionnel, sans jargon ni formulation à risque, **prêt pour l'audit** (≠ maquillage). | ✅ Acté |
| D4 | **Périmètre immédiat = modules de formation uniquement.** Le **done-for-you** (prestation faite par nous) sera un **chantier séparé, payé directement par le client, hors fonds publics**, traité plus tard. | ✅ Acté |
| D5 | **Ordre de travail : chantier B d'abord** (socle juridique + économique). | ✅ Acté |

---

## 3. Point de conformité tranché (ex-§5, zone rouge neutralisée)

Le contenu actuel du dépôt contient des formulations **frontalement non conformes** qui doivent être réécrites avant toute diffusion :

| Formulation actuelle (à supprimer) | Problème | Remplacement |
|---|---|---|
| « **Paravent Qualiopi** » | Qualiopi présenté comme couverture | Intitulé pédagogique réel de l'action |
| « encodons **GRATUITEMENT via votre OPCO** » | « gratuit » = publicité trompeuse ; démarchage fonds | « action finançable, modalités et reste à charge présentés » |
| « **Fulfilment IA : l'agence fait 90 % de marge** », « l'agence scrape/clone/monte » | Prestation déguisée en formation | Le **client** produit en formation-action ; le done-for-you = prestation séparée payée directement |

**Principe retenu [Vérifié — loi anti-fraudes n° 2026-534, art. sur l'usage des fonds] :** les fonds de formation ne financent **que** de la formation réelle. Ce que nous produisons à la place du client n'est pas finançable et fera l'objet d'un devis de prestation distinct, non conditionné à l'inscription.

---

## 4. Hypothèses restantes (à confirmer)
- [Hypothèse] Personas cibles = artisans/commerçants/TPE-PME locales (à valider avec l'étude de marché, non encore fournie).
- [Hypothèse] OPCO cible(s) non identifié(s) → plafonds horaires inconnus → prix non calculable à ce stade.
- [À vérifier] Guide de lecture Qualiopi en vigueur (V9 vs V10) au moment du prochain audit.
- [À vérifier] Référentiel : passage de 32 à 33 indicateurs au 1er novembre 2026 (décret n° 2026-728) — à confirmer sur Légifrance avant toute refonte des preuves.

---

## 5. Décisions qui t'appartiennent (prochain lot)

| Décision | Options | Recommandation | Conséquence si non tranché |
|---|---|---|---|
| **OPCO / financeur cible** | OPCO (salariés <50) · fonds d'assurance formation dirigeants (AGEFICE, FIFPL…) · mixte | Cibler 1 OPCO + 1 fonds dirigeant prioritaires | Impossible de calculer le prix et le reste à charge |
| **Statut du caméraman/intervenants** | Salarié · associé · indépendant | Si indépendant → **contrat de sous-traitance écrit obligatoire** (indicateur 27) | Non-conformité Qualiopi à l'audit |
| **Format & durée du parcours** | Intra · individuel · groupe ; nb de jours sur site | Intra, parcours court + tutorat (AFEST) | Coûts et marge non chiffrables |
| **Structure juridique porteuse** | — | À confirmer | Impact fiscal/responsabilité |
| **Nom commercial** | « VForMation » (nom de travail) · « Voxy Formation » · autre | À trancher | Site + mentions légales bloqués |
| **Zone géographique** | — | 1 secteur + 1 territoire au départ | Déplacements caméraman non rentabilisés |

---

## 6. Prochaine action
**Chantier B — économie unitaire & socle de conformité.** Pré-requis : répondre au lot 2 (OPCO cible, statut intervenants, format/durée, prix visé) et **fournir l'étude de marché PDF**. Dès réception, je produis : modèle d'économie unitaire par formule, tableau de sensibilité (−20 % plafond OPCO), registre des risques (preuve indicateur 32) et registre des décisions.

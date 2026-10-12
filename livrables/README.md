# Dossier projet — Voxy Formations

> **Partie indépendante et consolidée** de tout le travail réalisé ensemble depuis le début.
> Organisme de formation professionnelle **certifié Qualiopi** (NDA + Qualiopi obtenus), ciblant les professionnels de l'**Hérault (34)**. Promesse : **formation-action** — l'entreprise apprend une méthode (notamment vidéo) en la pratiquant sur son propre cas.
>
> La mémoire de projet et les conventions restent dans `../CLAUDE.md` (racine du dépôt).

---

## Règle d'or (non négociable)

Les **fonds de formation ne financent que de la formation réelle**. Toute prestation « clé en main » faite à la place du client est une **prestation commerciale séparée, facturée hors financement, jamais conditionnée à l'inscription**. Aucun arrangement non écrit. Formulations **bannies** partout : « gratuit », « 100 % financé », « sans reste à charge », « machine à cash », « paravent ». Aucun chiffre ni avis inventé.

---

## Les 4 chantiers

| Chantier | Objet | Statut |
|---|---|---|
| **0 — Cadrage** | Inventaire, alignement, point conformité | ✅ Socle |
| **A — Marketing** | Marché, personas, scripts UGC | ✅ 12 scripts + personas |
| **B — Socle juridique & économique** | Pilotage, programmes AFEST, contrats, grilles | ✅ Socle complet |
| **C — Site vitrine** | Architecture + maquette front | 🟡 Maquette + archi faites |
| **D — Plateforme de gestion** | Gestion inscriptions/dossiers | ⬜ Non démarré |

---

## Contenu du dossier

### `00-cadrage/`
- **[00_cadrage.md](00-cadrage/00_cadrage.md)** — Synthèse d'inventaire, décisions D1–D8, point conformité, en-attente.

### `A-marketing/`
- **[A0_Marche_et_Personas.md](A-marketing/A0_Marche_et_Personas.md)** — Marché enrichi, concurrence, 5 personas localisés (douleurs, angles, CTA, propos).
- **[A_scripts_ugc.md](A-marketing/A_scripts_ugc.md)** — V1 : fiche signal, 10 angles, 10 scripts + plan de test.
- **[A_scripts_ugc_v2.md](A-marketing/A_scripts_ugc_v2.md)** — V2 : scripts développés (valeur ajoutée, arc narratif).
- *Scripts UGC V4 (12 scripts + 36 hooks)* : voir l'artefact en ligne (maquette fiche de tournage) — à exporter en markdown si besoin.

### `B-socle/`
- **[B_pilotage.md](B-socle/B_pilotage.md)** — Économie unitaire, registre des risques, décisions, pré-mortem, cycles de travail.
- **[B1_Programme_AFEST_Visibilite_Locale.md](B-socle/B1_Programme_AFEST_Visibilite_Locale.md)** — Programme AFEST offre pilote (4 conditions tracées, tarifs AGEFICE/FAFCEA).
- **[B2_Modele_Contrat_Sous_Traitance.md](B-socle/B2_Modele_Contrat_Sous_Traitance.md)** — Contrat de sous-traitance (indicateur 27) — *à relire juridiquement*.
- **[B3_Grilles_Pedagogiques.md](B-socle/B3_Grilles_Pedagogiques.md)** — 6 grilles (diagnostic, débrief, jalon, à chaud, à froid 90 j, réclamations).
- **[B4_Programmes_Commercialisables_Qualiopi.md](B-socle/B4_Programmes_Commercialisables_Qualiopi.md)** — Les 3 offres en version lisse, audit-ready.
- **[Referentiel_Competences_Qualiopi.md](B-socle/Referentiel_Competences_Qualiopi.md)** — Référentiel de compétences.

### `C-site/`
- **[C_architecture_site.md](C-site/C_architecture_site.md)** — Cartographie du site : arborescence, modules par page, design system CSS, modules JS, reco de stack.
- **[site.html](C-site/site.html)** — **Site multi-pages complet** : accueil + catalogue + 4 fiches formation (structure Qualiopi) + méthode, financements, diagnostic, à-propos, contact, Le Mag, légales. Navigation par ancres, tous boutons cliquables.
- **[maquette.html](C-site/maquette.html)** — Première maquette (accueil seul), conservée pour historique.
- **`apercus/`** — Rendus vérifiés (desktop 1280, tablette 768, mobile 360, pleine page).

### `D-strategie/` — 🆕 Stratégie, économie & commercialisation
- **[D_SYNTHESE_PDG.md](D-strategie/D_SYNTHESE_PDG.md)** — ⭐ **À LIRE EN PREMIER.** Thèse, 5 découvertes, grille tarifaire, ordre d'exécution, 12 décisions, 5 actions de la semaine.
- **[D0_Analyse_Strategique.md](D-strategie/D0_Analyse_Strategique.md)** — Diagnostic sans complaisance, thèse centrale (OF + logiciel), conformité des 3 périmètres, goulots réels, positionnement, moat, pré-mortem.
- **[D1_Business_Model_Unit_Economics.md](D-strategie/D1_Business_Model_Unit_Economics.md)** — Ingénierie de durée, grille tarifaire, coûts collectif vs individuel, parcours individualisé FAFCEA à 80 €/h, LTV/CAC, trésorerie, plafond du marché local.
- **[D2_Plan_Commercialisation.md](D-strategie/D2_Plan_Commercialisation.md)** — Client idéal, assistant dossier de financement, canaux par rendement, tunnel, script de découverte, 8 objections, **roadmap 90 jours**.
- **[D3_Operationnel_ADS_Meta.md](D-strategie/D3_Operationnel_ADS_Meta.md)** — Plan publicitaire 2 000 € / 12 créas : conformité, 3 phases (test / apprentissage / scale), seuils de décision, 5 erreurs à éviter. **Planifié, non lancé.**

### `E-produit/` — 🆕 Architecture produit & modules IA
- **[E0_Architecture_Produit.md](E-produit/E0_Architecture_Produit.md)** — Vision, 3 utilisateurs du produit, modules, différenciation, conformité par construction, stack, séquencement, modèle de données.
- **[E1_Module_Generateur_Scripts.md](E-produit/E1_Module_Generateur_Scripts.md)** — Questionnaire, enrichissement automatique, moteur de raisonnement à 3 passes, contrôle de conformité, boucle de mesure, squelette de prompt.
- **[E2_Module_Generateur_Prompts.md](E-produit/E2_Module_Generateur_Prompts.md)** — Noyau 5 champs, questions adaptatives, gates, journal de session, bibliothèque de méthodes, entrée vocale.
- **[E2b_Modeles_Prompts_Prets.md](E-produit/E2b_Modeles_Prompts_Prets.md)** — ✅ **3 modèles .MD utilisables dès maintenant** (créer un outil · monter une offre · plan de contenu).
- **[E3_Stack_Technique.md](E-produit/E3_Stack_Technique.md)** — Démonstration « jamais de GPU », architecture LLM en 3 phases, souveraineté UE, BYOK, sources de données et verdicts juridiques, budget.
- **[E4_Idees_Strategiques.md](E-produit/E4_Idees_Strategiques.md)** — 10 opportunités non sollicitées, matrice de priorisation, les 3 à faire en premier.
- Version interactive en ligne : maquette publiée en artefact Claude (lien partagé séparément).

---

## Les 3 offres (intitulés lisses)

1. **Créer et piloter sa boutique en ligne**
2. **Structurer sa prospection commerciale B2B**
3. **Développer sa visibilité locale par la vidéo** — *offre pilote*

## Financeurs prioritaires (2026) — [à revérifier sur sites officiels]

| Financeur | Cible | Repère |
|---|---|---|
| **AGEFICE** | commerce / services | 42 €/h, 3 000 €/an (5 000 € si RNCP) |
| **FAFCEA** | artisans | 35 €/h, 600 €/an si CFP ≤ 85 € (dès 1/9/2026) |
| **Constructys** | BTP 11–49 sal. | 19 €/h (dès 1/6/2026) |

→ **Ne jamais vendre « financé à 100 % »** : le reste à charge est réel et doit être annoncé avant inscription.

---

## En attente (fournitures / décisions)

- Nom commercial à trancher (« VForMation » / « Voxy » / autre).
- Vrais coûts de production (pour remplacer les hypothèses d'économie unitaire).
- Relecture juridique du montage et des contrats.
- Contenus réels du site (textes fiches, indicateurs Qualiopi, mentions légales, visuels/photos).
- Pour un relevé pixel de cegos.fr : autoriser le domaine dans le réseau de l'environnement.

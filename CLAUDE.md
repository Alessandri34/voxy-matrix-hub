# CLAUDE.md — Mémoire de projet

> Fichier de référence du projet. Tenu à jour à chaque décision importante. Toute reprise de travail commence par la lecture de ce fichier.

## 1. Le projet
Organisme de formation professionnelle **certifié Qualiopi** (NDA + Qualiopi **obtenus**), ciblant d'abord les **professionnels**. Promesse : **formation-action** — l'entreprise apprend une méthode de communication (notamment vidéo) **en la pratiquant sur son propre cas**, avec un formateur, des phases réflexives et des évaluations tracées.

Marque : nom de travail « VForMation » / dépôt « Voxy Matrix Hub » — **nom commercial à trancher**.

## 2. Règle d'or (non négociable)
Les **fonds de formation ne financent que de la formation réelle**. Ce que nous produisons à la place du client (montage de site/vidéos « clé en main ») est une **prestation commerciale séparée, facturée directement au client, hors financement, jamais conditionnée à l'inscription**. Aucun arrangement « non écrit ». Base : loi anti-fraudes n° 2026-534, AFEST (D.6313-3-2).

## 3. Décisions prises
- **D1** NDA + Qualiopi obtenus.
- **D2** Pédagogie = apprentissage réel ; nos livrables = preuves pédagogiques.
- **D3** Garder les 3 offres + concept vidéo, en **version lisse** (audit-ready, sans jargon ni promesse à risque).
- **D4** Done-for-you = chantier séparé, payé hors financement, traité plus tard.
- **D5** Commencer par le chantier B (socle juridique + économique).
- **D6** Intervenants indépendants → contrat de sous-traitance obligatoire (indicateur 27).
- **D7** Gamme complète : A (court premium) + B (parcours étalé finançable).
- **D8** Financeurs prioritaires : **AGEFICE** (commerce/resto) + **FAFCEA** (artisans).

## 4. Offres (intitulés lisses)
1. Créer et piloter sa boutique en ligne (ex-E-Com Commando)
2. Structurer sa prospection commerciale B2B (ex-Outbound)
3. **Développer sa visibilité locale par la vidéo** (ex-Drive-to-Store) — **offre pilote**

Formulations **bannies** : « gratuit », « 100 % financé », « sans reste à charge », « machine à cash », « paravent ».

## 5. Paramètres financement 2026 [À vérifier sur sites officiels]
- FAFCEA : 35 €/h technique, 100 h/an ; **600 €/an si CFP ≤ 85 € (dès 1/9/2026)**.
- AGEFICE : 42 €/h, 3 000 €/an (5 000 € si RNCP).
- Constructys : 19 €/h (11-49 sal., dès 1/6/2026).
→ **Ne jamais vendre « financé à 100 % »** : le reste à charge est réel.

## 6. Livrables (branche `claude/new-session-nefcch`)
> **Tout est consolidé dans `livrables/`** (dossier indépendant, voir `livrables/README.md`).
- `livrables/00-cadrage/` : `00_cadrage.md`
- `livrables/A-marketing/` : `A0_Marche_et_Personas.md` · `A_scripts_ugc.md` · `A_scripts_ugc_v2.md`
- `livrables/B-socle/` : `B_pilotage.md` · `B1_Programme_AFEST_Visibilite_Locale.md` · `B2_Modele_Contrat_Sous_Traitance.md` · `B3_Grilles_Pedagogiques.md` · `B4_Programmes_Commercialisables_Qualiopi.md` · `Referentiel_Competences_Qualiopi.md`
- `livrables/C-site/` : `C_architecture_site.md` · `maquette.html` · `apercus/`

## 7. Chantiers (master prompt)
A = 10 scripts UGC (**fait** : fiche signal + 10 angles + 10 scripts + plan de test) · B = pilotage (**socle fait**) · C = site vitrine · D = plateforme de gestion.

## 7bis. Marketing (chantier A)
- **Zone ADS cible : Hérault (34)** — positionnement local.
- Méthode créa intégrée (guide Agence Short) : *signal → 10 angles (5 persona / 5 douleur) → scripts voix-off+b-roll*, hook TAV, awareness TOFU/MOFU/BOFU, 1 vidéo = 1 format × 1 angle × 1 persona.
- 5 personas localisés : Karim (artisan BTP/FAFCEA), Sophie (resto/AGEFICE), Léa (salon/AGEFICE), Véronique (PME/OPCO), Thomas (créateur).
- Garde-fous pub = contraintes légales formation (pas de « gratuit/100 % financé », pas de résultat garanti, cible 100 % pro, mention Publicité si créateur rémunéré).

## 8. Conventions
- Langue : français. Sources datées, classées [Vérifié] / [À vérifier] / [Hypothèse].
- Rien d'irréversible sans accord explicite (pas de `git push`, suppression, déploiement, envoi).
- Secrets hors Git (`.env` + `.gitignore`).
- Pas d'identifiant de modèle dans les fichiers du dépôt.

## 9. En attente
- Étude de marché PDF (à fournir).
- Vrais coûts de production (pour remplacer les [Hypothèses] de l'économie unitaire).
- Relecture juridique du montage et des contrats.

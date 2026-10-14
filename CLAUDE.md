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

## 5. Paramètres financement 2026 [Vérifié — PDF officiels, 12/10/2026]
- **AGEFICE** : **42 €/h présentiel · 35 €/h distanciel synchrone · 20 €/h asynchrone** ; plafond **3 000 €/an** (si CFP ≥ 7 €) ; **600 €/an si CFP < 7 €**. ⚠️ **Le plafond 5 000 € est réservé aux diplômes nationaux et titres RNCP — PAS aux certifications RS.** Max 25 participants.
  **Dépôt : de 4 mois à 15 jours calendaires avant le démarrage, OBLIGATOIREMENT via un Point d'Accueil** (un dossier envoyé au siège n'est pas instruit).
- **FAFCEA** : ⚠️ **le numérique / web / vidéo est TRANSVERSE = 25 €/h** (les 35 €/h sont le taux technique métier) ; 100 h/an ; **600 €/an si CFP ≤ 85 € (dès 1/9/2026)**. Qualiopi obligatoire depuis le 1/7/2026.
  **Dépôt : 3 mois avant → jusqu'au jour du début.**
- 🔥 **FAFCEA « parcours individualisé »** (sur mesure, gestion d'entreprise) : **80 €/h, 40 h/an** = 3 200 € ; 1 parcours/entreprise/5 ans ; min. 14 h, ≥ 2 intitulés de ≥ 4 h ; **100 % distanciel et e-learning interdits** ; autodiagnostic préalable ; **OF obligatoirement référencé FAFCEA**. → voir `livrables/D-strategie/D1` §2bis.
- **FIF PL** (professions libérales, courtiers) : ordre de grandeur 900 €/an [À vérifier]. **Dépôt jusqu'à 10 jours APRÈS le début** — le plus souple.
- **Constructys** : 19 €/h (demandes reçues dès le 1/6/2026) ; les < 11 salariés conserveraient 24 €/h [À vérifier].
→ **Ne jamais vendre « financé à 100 % »** : le reste à charge est réel.

## 6. Livrables (branche `claude/new-session-nefcch`)
> **Tout est consolidé dans `livrables/`** (dossier indépendant, voir `livrables/README.md`).
- `livrables/00-cadrage/` : `00_cadrage.md`
- `livrables/A-marketing/` : `A0_Marche_et_Personas.md` · `A_scripts_ugc.md` · `A_scripts_ugc_v2.md`
- `livrables/B-socle/` : `B_pilotage.md` · `B1_Programme_AFEST_Visibilite_Locale.md` · `B2_Modele_Contrat_Sous_Traitance.md` · `B3_Grilles_Pedagogiques.md` · `B4_Programmes_Commercialisables_Qualiopi.md` · `Referentiel_Competences_Qualiopi.md`
- `livrables/C-site/` : `C_architecture_site.md` · `site.html` (source) · `pages.json` + `build.mjs` (génération des 31 vraies URL) · `seo.json` (clé IndexNow, jetons de vérification) · `INDEXATION.md` · `SEO_strategie.md` · `INFOS_A_FOURNIR.md` · `api/contact.php` · `formulaire/` · `img/` · `apercus/`
  > **Le site en production est généré, pas copié.** `site.html` reste la source unique ; `node build.mjs` en produit `dist/` (31 pages autonomes + `sitemap.xml` + `robots.txt`). Ne jamais déployer `site.html` tel quel : il n'expose qu'une URL pour 31 pages. `dist/` est hors Git.
- `livrables/D-strategie/` : `D0_Analyse_Strategique.md` · `D1_Business_Model_Unit_Economics.md` · `D2_Plan_Commercialisation.md` · `D3_Operationnel_ADS_Meta.md`
- `livrables/E-produit/` : `E0_Architecture_Produit.md` · `E1_Module_Generateur_Scripts.md` · `E2_Module_Generateur_Prompts.md` · `E2b_Modeles_Prompts_Prets.md` · `E3_Stack_Technique.md` · `E4_Idees_Strategiques.md`

## 6bis. Indexation [Vérifié — 14/10/2026]
- **31 vraies URL** en production, titres/descriptions/canonicals uniques, Schema.org, sitemap, robots.txt. Contenu lisible **sans JavaScript**.
- Anciens liens `/#slug` **redirigés** vers leur URL réelle (`location.replace`).
- **IndexNow branché** (clé vérifiée, HTTP 200) : Bing, Yandex, Seznam, Naver notifiés à chaque déploiement. **Google n'y participe pas.**
- ⏳ **Reste à faire par Pierre** : jeton Google Search Console (2 min, voir `livrables/C-site/INDEXATION.md`) → à coller dans `seo.json`, le build pose la balise sur les 31 pages.
- ⏳ **Fiche Google Business Profile** : pèse plus lourd que le site sur les requêtes locales. Délai de validation long → à lancer tôt.
- ❌ **Backlinks automatiques à grande échelle : refusés.** C'est un *link scheme* au sens des règles anti-spam de Google ; une pénalité manuelle sur un domaine neuf coûterait plus que les liens ne rapportent, et cela consiste à déposer du contenu non sollicité chez des tiers. Remplacé par les citations légitimes listées dans `INDEXATION.md` (GBP, carif-oref, CCI/CMA, pages financeurs, fédérations métier, prescripteurs).
- Le déploiement **refuse de publier** si un titre ou un canonical est dupliqué, si une meta description manque, si un Schema.org est invalide, ou si le sitemap ne couvre pas les 31 pages.

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

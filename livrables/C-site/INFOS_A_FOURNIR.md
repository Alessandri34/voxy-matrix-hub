# C — Informations à fournir pour finaliser le site (avant mise en ligne)

> Objet : liste **exhaustive** de ce qu'il manque pour que le site soit complet, légal et prêt à être mis en ligne — sans aucun `[à compléter]`.
> Statut actuel : maquette multi-pages complète (structure, design, textes génériques). Il reste à **injecter les données réelles** ci-dessous.
> Priorité : 🔴 bloquant (légal / mise en ligne) · 🟠 important (crédibilité / conversion) · 🟢 confort.

---

## 1. 🔴 Identité légale & administrative (mentions légales + footer)
- [ ] **Raison sociale** exacte et **forme juridique** (EI, EURL, SASU…).
- [ ] **SIRET** / SIREN.
- [ ] **Adresse du siège** (+ lieu d'intervention/formation si différent).
- [ ] **Numéro de déclaration d'activité (NDA)** — enregistré en préfecture de région.
- [ ] **Numéro de certificat Qualiopi** + organisme certificateur (ex. AFNOR, ICPF…) + catégorie(s) certifiée(s) (« actions de formation »).
- [ ] **N° TVA intracommunautaire** (si assujetti) ou mention « TVA non applicable, art. 293 B du CGI ».
- [ ] **Nom du directeur de la publication**.
- [ ] **Capital social** (si société).

## 2. 🔴 Coordonnées de contact (header, contact, footer)
- [ ] **Téléphone** professionnel (remplace `04 00 00 00 00`).
- [ ] **E-mail** pro (remplace `contact@voxy-formations.fr` — ou valider ce nom de domaine).
- [ ] **Horaires** / disponibilités.
- [ ] **Réseaux sociaux** réels (LinkedIn, Instagram, Facebook, YouTube) — URLs.
- [ ] **Référent handicap** : nom + contact (obligation Qualiopi ind. 26).

## 3. 🔴 Marque
- [ ] **Nom commercial définitif** : « Voxy Formations » ou « VForMation » (décision en attente, `CLAUDE.md`). Tout le site utilise « Voxy » — à confirmer ou remplacer partout.
- [ ] **Logo** (fichier vectoriel SVG/PNG, versions claire/foncée).
- [ ] **Nom de domaine** choisi (ex. voxy-formations.fr) — disponible ? à réserver.

## 4. 🟠 Formations — contenus réels (catalogue + 4 fiches)
Pour **chacune** des 4 formations (Site internet, Boutique en ligne, Prospection B2B, Visibilité vidéo) :
- [ ] **Tarif réel** (prix total et/ou prix horaire définitif — remplace « dès 35 €/h »).
- [ ] **Durées exactes** par gamme (A / B).
- [ ] **Délai d'accès** précis (remplace `[X] jours`) — ex. « 11 jours ouvrés après accord de financement ».
- [ ] **Programme détaillé** validé (on a une trame ; à confirmer/affiner).
- [ ] **Prérequis** définitifs.
- [ ] **Modalités d'évaluation** (déjà décrites ; valider).
- [ ] **Financeurs applicables** confirmés par formation.
- [ ] Éventuels **dates de sessions** / modalités d'inscription.

## 5. 🔴 Qualité, conformité & documents (exigences Qualiopi)
- [ ] **Indicateurs de résultats** chiffrés (taux de satisfaction, de réussite/atteinte des objectifs, nombre de stagiaires) — `[à publier]` : à produire après les 1res sessions, avec **méthode de calcul** (ind. 2). En attendant, afficher « nouvel organisme, indicateurs publiés après les premières sessions ».
- [ ] **Règlement intérieur** (document téléchargeable).
- [ ] **CGV** finalisées (relecture juridique recommandée — on a une trame).
- [ ] **Conditions d'annulation / report**.
- [ ] **Politique de confidentialité (RGPD)** finalisée (trame fournie) : finalité, durée de conservation, responsable de traitement, DPO si applicable.
- [ ] **Modalités d'accessibilité PSH** (adaptations proposées).
- [ ] **Procédure de réclamation**.

## 6. 🟠 Preuves sociales (crédibilité / conversion)
- [ ] **Témoignages clients réels** (prénom, activité, ville, verbatim) — **avec accord écrit**. ⚠ aucun avis inventé (règle d'or). À recueillir après les 1res sessions.
- [ ] **Logos de financeurs** officiels à afficher selon leurs chartes (AGEFICE, FAFCEA, OPCO, Qualiopi, AFAQ) — vérifier droits d'usage.
- [ ] **Cas concrets / avant-après** (anonymisés si besoin).

## 7. 🟠 Visuels & médias
- [ ] **Photos réelles** : toi/l'équipe, une formation en situation, le matériel. (La home utilise un visuel abstrait ; les articles du Mag ont des photos libres de droits à remplacer si tu veux les tiennes.)
- [ ] **Vidéo de présentation** (optionnel, fort impact) — tes propres UGC.
- [ ] **Favicon** (icône d'onglet).

## 8. 🔴 Technique — pour « rendre le site accessible » (mise en ligne)
- [ ] **Nom de domaine** réservé + **hébergement** (ou plateforme : Netlify / Vercel / OVH / o2switch…).
- [ ] **E-mail professionnel** sur le domaine.
- [x] **Branchement des formulaires (contact + diagnostic)** : fait via Google Apps Script → Google Sheet + e-mail sur contact@vformations.fr. Il reste à **déployer le script côté Google et coller l'URL** dans `site.html` (`FORM_ENDPOINT`) — voir `formulaire/GUIDE_BRANCHEMENT.md`. ⚠ aucun secret dans le code (l'URL /exec est publique par nature).
- [ ] **Analytics respectueux RGPD** (Plausible / Matomo) + **bannière de consentement cookies**.
- [ ] **Google Business Profile** créé/optimisé (levier local n°1 — voir `SEO_strategie.md`).
- [ ] **Accessibilité web (a11y / RGAA)** : contrastes, navigation clavier, alternatives textes (déjà en partie en place ; audit avant mise en ligne).
- [ ] Choix de **stack de build** si on passe du prototype HTML à la prod (reco : Astro + Tailwind v4 — voir `C_architecture_site.md`).

## 9. 🟢 SEO / contenu (pour performer, pas bloquant)
- [ ] Validation des **title / meta** par page (templates dans `SEO_strategie.md`).
- [ ] Vrais **articles du Mag** (6 rédigés, à relire/ajuster) + prochaines vagues.
- [ ] **Coordonnées cohérentes (NAP)** identiques partout (site, GBP, réseaux).

---

## Le minimum vital pour mettre en ligne légalement (🔴)
1. Nom commercial + logo + nom de domaine/hébergement.
2. Mentions légales complètes (raison sociale, SIRET, NDA, n° Qualiopi).
3. Coordonnées réelles (tél, e-mail, adresse) + référent handicap.
4. CGV + politique de confidentialité + règlement intérieur.
5. Tarifs, délais d'accès et modalités par formation.
6. Formulaire de contact branché + consentement cookies.
7. Mention honnête des indicateurs (« publiés après les 1res sessions »).

> Dès que tu me fournis ces éléments (même partiellement), je remplace tous les `[à compléter]` dans le site. Rien n'est poussé/déployé sans ton accord (`CLAUDE.md §8`).

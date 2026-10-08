# C — Architecture & cartographie du site (Chantier C)

> **Casquette : CPO + CTO.** Gabarit de référence : **cegos.fr** (leader formation). Objectif : reproduire structure, UI et modules, en version Voxy.
> **Statut des sources :** ✅ **Relevé réel réalisé sur `www.cegos.fr` le 2026-10-08** (navigateur headless : DOM, styles calculés, 189 variables CSS, arborescence, scripts, captures desktop + mobile). Le **§8 — Design system réel Cegos** ci-dessous contient les valeurs exactes.
> **Conformité (rappel `CLAUDE.md` §4) :** jamais « gratuit / 100 % financé / sans reste à charge », pas d'avis/chiffres inventés, cible 100 % pro, mention Qualiopi selon charte.

---

## 1. Arborescence du site (pages à créer)

```
/                              Accueil (home)                      [maquette V3 — FAIT]
│
├── /formations                Catalogue / listing des formations  [à créer]
│   ├── /formations?domaine=…  Listing filtré par domaine
│   └── /formations/{slug}     Fiche formation (page détail)       [à créer — pivot commercial]
│
├── /domaines                  Vue d'ensemble des domaines         [à créer — ou ancre home]
│
├── /methode                   Notre méthode (formation-action / AFEST) [à créer]
│
├── /financements              Comment financer (AGEFICE/FAFCEA/OPCO)   [à créer]
│   └── /financements/{organisme}  Détail par financeur (optionnel)
│
├── /diagnostic                Réserver un diagnostic (formulaire)  [à créer — conversion]
│
├── /a-propos                  Qui sommes-nous / l'équipe / qualité [à créer]
│   ├── /a-propos/qualite      Indicateurs qualité & certification Qualiopi
│   └── /a-propos/accessibilite Accessibilité PSH (obligatoire Qualiopi)
│
├── /le-mag                    Blog / actualités (listing)          [à créer]
│   └── /le-mag/{slug}         Article                              [gabarit]
│
├── /contact                   Contact + coordonnées + carte
│
└── Pages légales (footer)
    ├── /mentions-legales
    ├── /cgv
    ├── /confidentialite       (RGPD)
    └── /cookies
```

**Priorité build (ROI) :**
1. **Accueil** (fait) → 2. **Fiche formation** (où convertit la pub) → 3. **Diagnostic** (formulaire de conv.) → 4. **Financements** → 5. **Méthode** → 6. **Catalogue** → 7. **À propos / Qualité / Accessibilité** (obligatoire Qualiopi) → 8. **Le Mag** → 9. **Légales**.

> ⚠️ **Obligations Qualiopi** à exposer sur le site (indicateurs) : accessibilité PSH (indic. 26), délais d'accès, taux de satisfaction/résultats quand disponibles, CGV, règlement intérieur, modalités d'inscription. → section dédiée `/a-propos/qualite` + mentions en footer.

---

## 2. Cartographie de la home (blocs, repris de Cegos)

| # | Bloc | Source Cegos | État maquette V3 | Module |
|---|------|--------------|------------------|--------|
| 0 | Filet rouge + header 2 niveaux | screens 1 & 5 | ✅ | header sticky |
| 1 | Hero (bannière + recherche) | screen 1 | ✅ | hero + search |
| 2 | Nos dernières actualités (3 cards) | screen 2 | ✅ | card grid |
| 3 | Domaines (grande boîte + pills) | screen 2 | ✅ | pill box |
| 4 | Bloc signature (ex « 100 ans ») | screen 2 | ✅ | feature box |
| 5 | Formations du moment (cards) | screen 3 | ✅ | formation cards + **slider** à ajouter |
| 6 | Ils nous font confiance (logos) | screens 3-4 | ✅ (financeurs) | logo row / **marquee** |
| 7 | Tuiles chiffres | screen 4 | ✅ (chiffres honnêtes) | stat tiles |
| 8 | Présence géographique (carte) | screen 5 | ✅ (Hérault) | map (SVG → interactif) |
| 9 | Footer (qualité + colonnes) | screen 5 | ✅ | footer |

**Manque sur la home pour l'effet Cegos complet :** slider/carousel sur les formations, défilement auto des logos, menus déroulants (mega-menu) au survol de la nav, rétrécissement du header au scroll.

---

## 3. Modules par page (ce qu'il faut construire)

### 3.1 Fiche formation `/formations/{slug}` — LA page qui convertit
Modules :
- **Fil d'ariane** (breadcrumb)
- **En-tête formation** : titre, chapô, badges (durée, présentiel, AFEST, finançable), prix horaire, note (quand avis réels)
- **CTA sticky** : « Demander un devis / Réserver » qui suit au scroll (desktop : colonne droite ; mobile : barre basse fixe)
- **Sommaire ancré** (scroll-spy) : Objectifs · Programme · Public & prérequis · Modalités · Financement · Dates
- **Programme** en **accordéon** (séquences AFEST)
- **Objectifs pédagogiques** (liste) — repris de `B4`
- **Public visé / prérequis / accessibilité PSH**
- **Modalités** : durée, lieu (chez le client), évaluation, délais d'accès
- **Bloc financement** contextualisé (AGEFICE/FAFCEA selon profil) + **calculette reste à charge indicative**
- **Encart Qualiopi** + indicateurs
- **Formations liées** (3 cards)
- **Formulaire de contact / devis** (modal ou section)

### 3.2 Catalogue `/formations`
- **Barre de filtres** : domaine, durée, financement, format (chips + `<select>`)
- **Grille de cards** filtrable (JS) + tri
- **Recherche** avec autocomplétion
- Pagination ou « charger plus »

### 3.3 Diagnostic `/diagnostic` (conversion)
- **Formulaire multi-étapes** (activité, besoin, financeur, coordonnées)
- Validation côté client, `preventDefault`, envoi via back (voir §6)
- Écran de confirmation
- Garde-fou RGPD (consentement, finalité, pas de donnée sensible)

### 3.4 Financements `/financements`
- Tableau comparatif financeurs (repris `CLAUDE.md §5` / `B_pilotage`)
- **Accordéon FAQ** financement
- Mention honnête reste à charge (règle d'or)

### 3.5 Méthode `/methode`
- Les 4 temps (déjà en home) développés
- Preuve AFEST (4 conditions, repris `B1`)

### 3.6 Le Mag (blog)
- Listing (cards + catégories) + article (gabarit, sommaire, partage)

---

## 4. Design system — composants CSS (réutilisables)

> La maquette V3 contient déjà la base. À **extraire en fichier `styles.css`** lors du build.

**Fondations (tokens) :**
- Palette : `--blue` (bannières/sections), `--wine` (boutons), `--green`, tuiles, `--red` (accent), neutres.
- **Échelle typo fluide `clamp()`** : `--fs-display / h2 / h3 / body / sm / xs / tile` (⚠ toujours espaces autour de `+` dans `clamp`).
- **Espacements fluides `clamp()`** : `--section-y / gutter / gap / box-pad / card-pad`.
- Rayons : `--r-sm/r/r-lg/r-pill`. Ombres : `--sh / --sh-sm`.
- Police : **Poppins** (titres) + **Figtree** (corps) via Google Fonts.

**Composants :**
| Composant | Classe | Réutilisé sur |
|---|---|---|
| Boutons pills | `.btn` `.btn-wine` `.btn-white` `.btn-outline-w` | partout |
| Header sticky 2 niveaux | `.header` `.header-top` `.header-nav` | global |
| Menu mobile (drawer) | `.burger` `.mnav` | global |
| Hero | `.hero` `.hero-search` | home (+ variantes pages) |
| Card actualité/article | `.ncard` | home, Le Mag |
| Boîte à pills | `.domaines` `.dpill` | home, domaines |
| Feature box | `.feature` | home, pages |
| Card formation | `.fcard` | home, catalogue, fiches |
| Rangée de logos | `.logos` | home, financements |
| Tuiles chiffres | `.tiles` `.tile` | home, à-propos |
| Carte zone | `.mapbox` | home, contact |
| Footer | `.footer` | global |
| Grille auto-fit | `grid-template-columns:repeat(auto-fit,minmax(min(100%,Npx),1fr))` | toutes grilles |

**À ajouter au DS pour les pages internes :**
- `.breadcrumb`, `.accordion`, `.tabs`, `.sticky-cta`, `.toc` (sommaire scroll-spy), `.filters`, `.badge`, `.form` + états de validation, `.modal`, `.pagination`, `.toast`, `.cookie-banner`.

---

## 5. Modules JS / interactivité (pour « le même rendu » Cegos)

| Module | Rôle | Priorité | Dépendance |
|---|---|---|---|
| **Header au scroll** | rétrécit / ombre à partir de N px | H | vanilla (`IntersectionObserver`) |
| **Mega-menu** | déroulants nav au survol/clic (desktop) + drawer mobile | H | vanilla |
| **Mobile drawer** | menu hamburger (déjà amorcé) | H | vanilla (fait) |
| **Carousel formations** | slider cards (comme Cegos) | M | Swiper / Splide (ou CSS scroll-snap) |
| **Logos marquee** | défilement auto des logos | M | CSS keyframes (pas de lib) |
| **Accordéon** | programme, FAQ | H | `<details>` natif ou vanilla |
| **Sommaire scroll-spy** | surligne la section active (fiche) | M | `IntersectionObserver` |
| **Filtres catalogue** | filtrer/trier les cards | H | vanilla |
| **Recherche + autocomplete** | suggestions formations | M | vanilla + JSON local |
| **Carte interactive** | pins cliquables Hérault | B | SVG inline + JS (ou Leaflet si vraie carte) |
| **Formulaire multi-étapes** | diagnostic/devis | H | vanilla + back |
| **Modal / devis** | ouvrir le formulaire | M | `<dialog>` natif |
| **Lazy-load images** | perf | M | `loading="lazy"` natif |
| **Cookie banner / consent** | RGPD | H (légal) | vanilla + localStorage |
| **Smooth scroll ancres** | nav interne | B | CSS `scroll-behavior` |

> Principe : **vanilla d'abord** (natif `<details>`/`<dialog>`, `IntersectionObserver`, CSS scroll-snap). N'ajouter une lib (Swiper/Splide, Leaflet) que si l'effet l'exige. Dans l'artefact Claude, les libs se chargent depuis cdnjs ; dans le vrai build, via npm.

---

## 6. Recommandation de stack (build réel)

**Option A — Statique moderne (recommandée pour démarrer vite) :**
- **Astro** (ou 11ty) : HTML/CSS/JS, composants réutilisables, ultra rapide, SEO natif, pages en Markdown pour Le Mag et les fiches formation (contenu = fichiers, pas de CMS au départ).
- Formulaires : **Formspree / Web3Forms** ou une petite fonction serverless (Netlify/Vercel Functions) → pas de secret côté client.
- Hébergement : Netlify / Vercel (HTTPS, formulaires, déploiement Git).

**Option B — CMS si édition autonome voulue :**
- **WordPress** (thème sur-mesure) ou **Astro + CMS headless** (Decap/Sanity) pour que tu édites formations et articles sans dev.

**Transverse :**
- SEO local (Hérault) : titles/meta, données structurées `Course` + `LocalBusiness` (Schema.org), sitemap.xml, Open Graph.
- Analytics respectueux RGPD (Plausible/Matomo) + bannière consentement.
- Perf : images en WebP + `loading=lazy`, polices `display=swap` (déjà), CSS/JS minifiés.
- Accessibilité : focus visible, contrastes, alt, navigation clavier (exigence Qualiopi + légale).

---

## 7. Ce qu'il reste pour aller au bout du Chantier C

1. **Valider** le gabarit home (maquette V3) + le rebranding couleurs.
2. **Dessiner** la fiche formation (gabarit n°1 à convertir en maquette).
3. **Choisir la stack** (A ou B ci-dessus).
4. **Récupérer les vrais contenus** : textes des 3 fiches (depuis `B4`), vrais délais d'accès, indicateurs Qualiopi, mentions légales (SIRET, NDA, Qualiopi n°), coordonnées, vrais visuels/photos (le hero Cegos utilise une vraie photo — prévoir shooting ou banque d'images).
5. **Brancher** le formulaire diagnostic (sans secret côté client).
6. ✅ **Relevé pixel réel cegos.fr fait** (voir §8).

---

## 8. Design system réel Cegos (relevé DOM — 2026-10-08)

> Valeurs **exactes** extraites de cegos.fr. À côté : la **correspondance Voxy** (palette bleue déjà appliquée dans `maquette.html`).

### 8.1 Polices
| Usage | Cegos (réel) | Dispo Google Fonts ? | Choix Voxy |
|---|---|---|---|
| Titres (H1/H2) | **Ryker** (poids 500) | ❌ propriétaire (Positype) | **Poppins** (demandé — plus pro) ; alt. proche de Ryker = Fredoka/Baloo 2 |
| Corps / sans | **Raleway** | ✅ oui | **Raleway** (appliqué, fidèle) |

Tailles réelles : H1 = `2.5rem` (40px, line-height 58px), hero H1 = `3.125rem` (50px), H2 = `1.5rem`, H3 = `1.25rem`, corps = `.875rem` (14px). Poids : regular 400, semibold 600, bold 700. Typo **responsive en `calc(rem + vw)`** (même logique que nos `clamp()`).

### 8.2 Palette réelle Cegos → correspondance Voxy
| Rôle | Cegos (hex réel) | Voxy (bleu appliqué) |
|---|---|---|
| Encre primaire (texte, boutons) | **`#1d0000`** (quasi-noir bordeaux) | `#14161C` (encre) / boutons `#4C122A` |
| Vert (boîte domaines) | **`#004641`** / `#003e00` | inchangé `#0E4A3B` |
| Violet (sections signature) | **`#2d0051`** | **remplacé par bleu `#1A3C86`** |
| Rouge (filet, badge, pins) | **`#e6233a`** | `#E4002B` |
| Magenta profond | `#62003b` | — |
| Bleu profond (dispo dans leur palette) | **`#001b71`** | base idéale pour notre bannière |
| Fond card clair | `#f4f2f2` | `#F5F3F1` |
| **Tuiles** menthe / lavande / bleu clair / orange / crème | `#a1eae6` · `#dec5ff` · `#b3dfff` · `#ffb93e` · `#fff0c6` | menthe gardée, lavande→bleu pervenche, bleu ciel gardé, orange gardé |

> Remarque : Cegos **n'a pas un seul bleu dominant** — sa bannière est charcoal `#1d282e` + photo. Notre choix (bannière bleue) est un parti pris Voxy ; le `#001b71` de leur propre palette est le meilleur bleu « marque » à reprendre.

### 8.3 Rayons & espacements (réels)
- Rayons : `sm .25rem` · `md .375rem` · `lg .5rem` · `2xl 1rem` · `3xl 1.5rem`. Les pills (boutons, chips) sont en rayon plein. Cards ≈ `lg`/`2xl`.
- Espacements : `small 1.25rem` · `big 3.125rem`, + versions **responsive** `calc(rem + vw)`.

### 8.4 Stack technique (réel)
- **Tailwind CSS v4** (CSS-first `@theme` : 189 variables `--color-*`, `--space-*`, `--radius-*`, `--font-*` ; couleurs modernes en `lab()`/`oklab()`, `color-mix()`).
- Rendu **server-side** (pas de SPA lourde visible) ; JS maison sous `/assets/js/`.
- Tiers : Google Tag Manager, Microsoft Clarity (heatmaps), Bing Ads, cookie consent (OneTrust).
- → **Reco build Voxy confirmée** : Astro + **Tailwind v4** reproduit ce design system à l'identique (tokens `@theme`), avec contenus en Markdown. C'est exactement le modèle Cegos, en plus léger.

### 8.5 Arborescence réelle (confirmée)
- **`/formations`** = hub catalogue. Mega-menu « Domaines de formation » listant ~30 domaines, chacun en **`/formations/{slug-domaine}`** (ex. `/formations/commercial-ventes`, `/formations/communication`, `/formations/digital`, `/formations/management`…).
- Nav principale : **Domaines de formation · Solutions · Vous êtes · CPF | Financements · Ressources · Le Mag**.
- Utilitaires header : recherche · téléphone · Nous contacter · Espace client · panier (badge) · « Ma sélection ».
- → Pour Voxy (catalogue réduit) : garder la **même ossature de nav** mais 1 seul niveau de domaines (nos 3 offres), le mega-menu devient un simple menu.

---

> Rien n'est poussé sur Git sans ton accord (règle `CLAUDE.md §8`).

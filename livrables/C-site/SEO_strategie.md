# C — Stratégie SEO longue traîne & maillage interne (Voxy Formations)

> **Casquette : CPO + SEO.** Objectif : capter un trafic **qualifié, local et à forte intention** sur un site neuf (autorité de domaine ≈ 0), via la **longue traîne** et le **référencement local (Hérault)**, puis convertir vers les fiches formation et le diagnostic.
> **Méthode / outils (gratuits, utilisés le 2026-10-08) :** Google Suggest (API d'autocomplétion `suggestqueries.google.com`, hl=fr/gl=fr) comme outil de mots-clés, + recoupement avec le positionnement de `A0_Marche_et_Personas.md`.
> **Conformité (`CLAUDE.md §4`) :** aucun contenu « gratuit / 100 % financé / sans reste à charge » ; cible 100 % pro ; mention Qualiopi selon charte ; pas de promesse de résultat.

---

## 1. Principe stratégique

Un site neuf ne peut pas ranker sur les têtes de requête (« formation vidéo », « formation prospection ») : trop concurrentiel. On attaque donc par :

1. **La longue traîne** — requêtes précises, peu concurrentielles, à forte intention (« comment créer une fiche google business », « reste à charge formation agefice »).
2. **Le local** — qualification géographique (Hérault, Montpellier, Béziers, Sète), là où la concurrence nationale (Cegos…) ne se bat pas.
3. **Les clusters thématiques (hub & spoke)** — chaque fiche formation est une **page pilier (money page)** ; les articles du MAG sont des **satellites** qui pointent vers elle → on construit l'autorité thématique **et** on alimente la conversion.

---

## 2. Clusters de mots-clés (issus de Google Suggest)

### Cluster A — Vidéo & visibilité (pilier : fiche **Visibilité par la vidéo**)
| Longue traîne | Intention | Difficulté |
|---|---|---|
| comment filmer avec son smartphone | info | faible |
| formation montage vidéo smartphone | transac. | faible |
| pourquoi faire des reels sur instagram | info | faible |
| formation vidéo réseaux sociaux | transac. | moyenne |
| formation vidéo ia / capcut | info | faible |

### Cluster B — Visibilité Google locale (pilier : **Visibilité vidéo** + **Site internet**)
| Longue traîne | Intention | Difficulté |
|---|---|---|
| comment créer une fiche google business | info | faible |
| comment modifier sa fiche google business | info | faible |
| comment être visible sur google gratuitement | info | moyenne |
| comment être visible sur google sans site internet | info | faible |
| comment être référencé sur google maps | info | faible |

### Cluster C — Financement formation (pilier : **Financements** + **Diagnostic**)
| Longue traîne | Intention | Difficulté |
|---|---|---|
| financement formation agefice / formation prise en charge agefice | transac. | moyenne |
| fafcea formation prise en charge | transac. | faible |
| reste à charge formation | info | moyenne |
| formation qualiopi c'est quoi | info | faible |
| financement formation restauration / artisan | transac. | faible |

### Cluster D — Site internet & e-commerce (pilier : **Site internet** / **Boutique en ligne**)
| Longue traîne | Intention | Difficulté |
|---|---|---|
| formation création site internet prix / wordpress / e-commerce | transac. | moyenne |
| formation créer sa boutique en ligne | transac. | faible |
| créer un site internet pour artisan / commerce | info | faible |

### Cluster E — Prospection B2B (pilier : **Prospection B2B**)
| Longue traîne | Intention | Difficulté |
|---|---|---|
| formation prospection commerciale b2b / linkedin | transac. | moyenne |
| technique de prospection commerciale | info | moyenne |

### Cluster F — Local & sectoriel (transversal, personas A0)
| Longue traîne | Persona | Pilier |
|---|---|---|
| formation digital / marketing digital Montpellier | tous | catalogue |
| attirer clientèle restaurant | Sophie | vidéo |
| attirer des clients artisan (BTP) | Karim | vidéo / site |
| formation financée coiffeur / esthétique (AGEFICE) | Léa | vidéo |

---

## 3. Mapping page ↔ mot-clé + balises (title ≤ 60 car., meta ≤ 155 car.)

| Page | Mot-clé principal | `<title>` | Meta description |
|---|---|---|---|
| Accueil | formation professionnelle Hérault | Voxy Formations — Organisme de formation dans l'Hérault | Formations-actions certifiées Qualiopi pour les pros de l'Hérault : vidéo, site web, prospection. Finançables. Diagnostic gratuit. |
| Fiche vidéo | formation vidéo réseaux sociaux Hérault | Formation vidéo & visibilité locale — Hérault \| Voxy | Apprenez à filmer, monter et diffuser vos vidéos pour attirer des clients locaux. Présentiel, finançable AGEFICE/FAFCEA. |
| Fiche site | formation création site internet | Formation création de site internet — Hérault \| Voxy | Créez et mettez en ligne votre site professionnel pendant la formation. Certifié Qualiopi, finançable. Montpellier, Béziers, Sète. |
| Fiche boutique | formation créer sa boutique en ligne | Formation boutique en ligne (e-commerce) \| Voxy | De la création à la première vente, sur votre catalogue. Formation-action finançable dans l'Hérault. |
| Fiche prospection | formation prospection commerciale B2B | Formation prospection commerciale B2B \| Voxy | Structurez votre prospection B2B sur vos vrais prospects. Présentiel, finançable OPCO/AGEFICE. |
| Financements | financement formation AGEFICE FAFCEA | Financer sa formation : AGEFICE, FAFCEA, OPCO \| Voxy | Comment financer votre formation en 2026 et comprendre votre reste à charge. On monte le dossier avec vous. |

> **À faire au build** : balises `<title>`/`<meta>` par page (le site actuel est une SPA à ancres pour la maquette ; en prod, 1 URL = 1 page avec ses balises), données structurées **Schema.org `Course`** (fiches) + **`LocalBusiness`/`EducationalOrganization`** (accueil/contact), `sitemap.xml`, `robots.txt`, canonical, Open Graph.

---

## 4. MAG — 6 premiers articles (longue traîne → maillage)

| # | Article (H1) | Mot-clé cible | Cluster | Liens internes sortants |
|---|---|---|---|---|
| 1 | Comment filmer son commerce avec un smartphone (guide 2026) | comment filmer avec son smartphone | A | → Fiche **vidéo** · → art. 4 |
| 2 | Créer sa fiche Google Business : le guide pas à pas | comment créer une fiche google business | B | → Fiche **vidéo** · → Fiche **site** · → art. 5 |
| 3 | AGEFICE, FAFCEA, OPCO : financer sa formation en 2026 | financement formation agefice | C | → **Financements** · → **Diagnostic** · → art. 6 |
| 4 | Reels, TikTok, Shorts : quelle vidéo pour attirer des clients | pourquoi faire des reels instagram | A | → Fiche **vidéo** · → art. 1 |
| 5 | Restaurant, artisan, salon : attirer plus de clients locaux | attirer clientèle restaurant | F | → Fiche **vidéo** · → Fiche **site** · → **Diagnostic** |
| 6 | Qualiopi, c'est quoi ? Ce que ça change pour votre formation | formation qualiopi c'est quoi | C | → **Financements** · → **À propos** |

Chaque article : **1 mot-clé cible**, structure Hn (H1 unique + H2/H3 reprenant des variantes longue traîne), **réponse complète** (format « People Also Ask »), **CTA** vers la fiche/diagnostic, **2-3 liens internes** contextuels, image de couverture avec `alt` descriptif.

---

## 5. Maillage interne (règles)

```
                 ┌─────────────── ACCUEIL ───────────────┐
                 │ (liens vers piliers + MAG + diagnostic)│
                 └───┬───────────┬───────────┬────────────┘
             ┌───────▼──┐   ┌────▼─────┐  ┌──▼──────────┐
             │ PILIER   │   │ PILIER   │  │ FINANCEMENTS│  ← money pages
             │ vidéo    │   │ site/boutiq│ │ + diagnostic│
             └──▲──▲────┘   └────▲─────┘  └──▲──────────┘
     art.1 ─────┘  └── art.4     │ art.2     │ art.3 / art.6
     (spokes montent vers leur pilier, et se lient entre eux dans le cluster)
```

**Règles appliquées :**
- Chaque **article** pointe vers **sa page pilier** (ancre riche mais variée : « notre formation vidéo », « se former à la visibilité locale »…) + **1-2 articles du même cluster**.
- Chaque **fiche formation** pointe **vers le bas** vers 1-2 articles de soutien (bloc « Pour aller plus loin ») — à ajouter au build.
- **Pas de sur-optimisation** : ancres naturelles et variées, liens contextuels dans le corps, jamais de bourrage.
- **Fil d'Ariane** sur toutes les pages internes (déjà en place) = maillage + signal de structure.
- **Footer** = liens sitewide vers piliers + MAG (déjà en place).
- Profondeur ≤ 3 clics depuis l'accueil pour toute page.

---

## 6. Calendrier éditorial (rythme soutenable)

| Mois | Articles prioritaires | Pourquoi |
|---|---|---|
| M1 | Art. 3 (financement) + Art. 2 (fiche Google) | intention haute + requêtes faciles |
| M2 | Art. 1 (filmer smartphone) + Art. 5 (clients locaux) | alimente le pilier vidéo + local |
| M3 | Art. 4 (reels) + Art. 6 (Qualiopi) | complète les clusters A et C |
| puis | 2 articles/mois, 1 sectoriel + 1 « comment faire » | profondeur de cluster |

Idées de longue traîne pour la suite : « comment modifier sa fiche google business », « formation site internet wordpress prix », « prospection linkedin pour indépendant », « formation financée [métier] Montpellier » (1 page par métier/ville = pages locales).

---

## 7. SEO technique — quick wins (au build)

- **1 URL propre par page** (`/formations/visibilite-video`, `/mag/filmer-son-commerce-smartphone`), pas de SPA à ancres en prod.
- `<title>` + `meta description` uniques · **1 seul H1** · hiérarchie Hn.
- **Schema.org** : `Course` (fiches), `LocalBusiness`/`EducationalOrganization` (NAP : nom, adresse, tél cohérents partout), `BreadcrumbList`, `FAQPage` (sections FAQ).
- `sitemap.xml` + `robots.txt` + canonical + Open Graph/Twitter cards.
- **Images** : `alt` descriptif, format WebP, `loading="lazy"` (fait), dimensions fixées.
- **Vitesse** : Astro + Tailwind (relevé Cegos) = léger ; Core Web Vitals surveillés.
- **Google Business Profile** optimisé (catégorie, zone, photos, avis) — levier local n°1.
- **Avis clients** après les 1res sessions (jamais inventés).

## 8bis. Pages locales (2ᵉ vague — ville × métier) — FAIT

> Levier n°1 en local : une page dédiée par **intention géo** et par **métier/persona**, avec son mot-clé, son financeur et ses liens. Construites dans `site.html` (hub `#pres-de-chez-vous`).

| Page | Mot-clé cible | Financeur | Persona |
|---|---|---|---|
| Montpellier | formation communication digitale / réseaux sociaux Montpellier | AGEFICE/FAFCEA/OPCO | tous |
| Béziers | formation digitale Béziers | id. | tous |
| Restaurateurs | formation vidéo pour restaurateur / attirer clients restaurant | **AGEFICE** | Sophie |
| Artisans du bâtiment | formation digitale artisan / visibilité artisan | **FAFCEA** | Karim |
| Coiffure & esthétique | visibilité salon coiffure / attirer clients salon | **AGEFICE** / OPCO | Léa |

**Enseignement du relevé Suggest :** « formation restaurateur / coiffeur » dérive vers les **métiers** (CAP coiffure, restauration d'art) → on cible donc explicitement **« formation vidéo / digitale / visibilité POUR [métier] »** (notre angle, faible concurrence), jamais « formation [métier] ».

**À répliquer (même gabarit) :** Sète, Lunel, Agde (villes) · taxi/VTC, bien-être, commerce de bouche, auto-entrepreneurs (métiers). 1 page = 1 combinaison ville×métier à fort potentiel (ex. « formation vidéo restaurateur Montpellier »).

**Maillage des pages locales :** hub `Près de chez vous` (footer + section accueil) → pages ville/métier → fiches formation + articles MAG + diagnostic. Chaque page locale pointe vers la fiche pertinente et 1-2 articles de soutien.

## 9. KPIs
Positions sur les requêtes longue traîne cibles · trafic organique local · clics « itinéraire/appel » GBP · demandes de diagnostic depuis l'organique · pages indexées.

> Rien n'est poussé sans ton accord explicite (`CLAUDE.md §8`).

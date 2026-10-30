# Inventaire de l'exposition publique — état au 30/10/2026

> Demandé avant toute modification. **Rien n'a été changé.** Ce document dit ce qui est
> accessible aujourd'hui, par qui, et ce que chaque document contient réellement.

---

## 1. Ce qu'il faut savoir en premier

Le dépôt `Alessandri34/voxy-matrix-hub` est **public** (`"private": false`). Collaborateurs : **vous seul** (admin) — personne n'a été ajouté. L'exposition ne vient donc pas d'un partage, mais du réglage de visibilité.

Il y a **deux couches** d'accès, et elles ne se ferment pas de la même façon :

| Couche | Qui peut lire | Combien | Se ferme en… |
|---|---|---|---|
| **GitHub Pages** — `alessandri34.github.io/voxy-matrix-hub` | tout internet, sans compte, **sans connaître le dépôt** | 27 documents servis | désactivant Pages, **ou** en retirant les fichiers du dépôt |
| **github.com** — le dépôt lui-même | tout internet, en connaissant l'URL | 213 fichiers | passant le dépôt en privé |

🔴 **Le point qui change tout :** le portail Pages **sert les documents lui-même**. Ses 27 liens sont relatifs (`./OFFRE 3 .../Guide_Formateur_Empire.html`), pas des liens vers github.com. **Passer le dépôt en privé ne fermerait donc pas ces 27 documents** — Pages continuerait à les distribuer. Vérifié : les trois guides formateurs testés répondent HTTP 200.

Second point, technique : sur un compte GitHub **gratuit**, un dépôt privé ne peut pas publier de Pages du tout. La configuration « dépôt privé + Pages public » est soit impossible, soit sans effet sur les 27 documents.

---

## 2. Le vrai problème n'est pas la confidentialité

En lisant le contenu, ce n'est pas l'avantage concurrentiel qui est le plus en jeu. **Une partie de ce qui est public contredit la règle d'or §2 et les formulations bannies §4**, sous le nom d'un organisme certifié Qualiopi.

| Motif | Fichiers touchés | Citation exacte, vérifiée |
|---|---|---|
| 🔴 **« 100 % financé »** | 1 | `CATALOGUE_PORTAL/index.html` : « **100% financé par l'État** » |
| 🔴 **Travail fait à la place de l'apprenant** | **10** | Guide Formateur N1 : « le centre de formation paramètre **en coulisses** et livre **"clés en main" à la place du client** » · N2 : « Prestations **"Done-For-You"** (Réalisées par nos experts) — Travail technique complexe **rendu invisible** » |
| 🔴 **Financement garanti** | 2 | Landing page : « **Montage OPCO Garanti** » |
| 🔴 **Résultat garanti** | 6 | « **garantie absolue** de non-déperdition de leads » |
| 🟠 **Données achetées / scraping** | 5 | Syllabus : « un extracteur de données qui va puiser **2000 contacts parfaits dans la base de données mondiale** » · « Initialisation du Scraping (Apollo/Clay) » |
| 🟠 **Vocabulaire de domination** | **22** | « résultats de niveau **0,1% Elite** » · « **DIRECTIVE TOP 1%** » · « une **machine de guerre** automatisée » · « livrer à internet **de façon agressive** » |

**Pourquoi c'est sérieux.** « 100 % financé » et « Montage OPCO Garanti » sont exactement les formulations que `CLAUDE.md` §4 interdit, et que la loi anti-fraude n° 2026-534 vise. Le « Done-For-You » présent dans **les neuf guides formateurs** décrit le travail fait à la place du client **à l'intérieur de l'architecture pédagogique** — alors que la décision D4 en fait une prestation séparée, hors financement. Un auditeur ou un financeur qui lit ces pages y trouve la description du montage que le dossier s'interdit par ailleurs.

Le portail annonce lui-même ce qu'il contient : « Retrouvez ici 100 % de la matrice documentaire (Syllabus, **Guides Formateurs Secrets**, Sites de Vente) » et « **CLASSIFIÉ** — Codex IA Master Matrix ».

---

## 3. Couche 1 — les 27 documents servis par Pages

Accessibles à n'importe qui, sans compte GitHub, depuis `alessandri34.github.io/voxy-matrix-hub/`.

### Portails — 3 documents

| Fichier | Contenu | Décision |
|---|---|---|
| `index.html` | Page d'accueil « VOXY MATRIX \| Command Center Élite ». Annonce les « Guides Formateurs Secrets » et le « Codex classifié ». Index de tout le reste. | ☐ garder ☐ retirer |
| `CATALOGUE_PORTAL/index.html` | Catalogue des offres. 🔴 **Contient « 100% financé par l'État ».** | ☐ garder ☐ retirer ☐ corriger |
| `CODEX_IA.html` | 32 Ko de prompts systèmes propriétaires : framework « A.P.E.X », persona « Apex Merchant », « Garantie Hormozi (Risque Inversé) ». C'est votre actif le plus copiable tel quel. | ☐ garder ☐ retirer |

### 🔴 Guides formateurs — 9 documents

Trois niveaux (Launch / Performance / Empire) × trois offres. 20 à 28 Ko chacun.
**Tous les neuf contiennent « Done-For-You ».** Ce sont les documents que le portail appelle « secrets ».

| Offre | Niveau 1 | Niveau 2 | Niveau 3 |
|---|---|---|---|
| E-Com Commando | ☐ | ☐ | ☐ |
| Outbound Hybride | ☐ | ☐ | ☐ |
| Drive-to-Store | ☐ | ☐ | ☐ |

### 🟠 Manuels élève — 9 documents

Mêmes trois niveaux × trois offres. 12 à 16 Ko chacun. Destinés aux apprenants — donc une diffusion est légitime, mais **pas en accès libre et indexable**, et pas dans leur état actuel : ce sont les manuels de la tâche #42, qui contiennent les passages EXIF/géolocalisation et le vocabulaire de domination.

| Offre | Launch | Performance | Empire |
|---|---|---|---|
| E-Com Commando | ☐ | ☐ | ☐ |
| Outbound Hybride | ☐ | ☐ | ☐ |
| Drive-to-Store | ☐ | ☐ | ☐ |

### 🟡 Syllabus — 3 documents · 🟢 Landing pages — 4 documents

Les syllabus (20-24 Ko) décrivent le programme vendu ; celui d'Outbound contient le passage sur les « 2000 contacts parfaits ». Les landing pages sont des pages de vente — publiques par destination, **mais celle d'Outbound porte « Montage OPCO Garanti »**.

| Document | Décision |
|---|---|
| Syllabus Delivrabilite Ecom Commando | ☐ garder ☐ retirer |
| Syllabus Outbound Hybride 🟠 | ☐ garder ☐ retirer ☐ corriger |
| Syllabus Drive to Store Virale | ☐ garder ☐ retirer |
| 4 landing pages (dont 1 🔴) | ☐ garder ☐ retirer ☐ corriger |

---

## 4. Couche 2 — lisible sur github.com, non servi par Pages

Ces fichiers ne sont pas distribués par le portail, mais restent lisibles et clonables tant que le dépôt est public. **Les fermer ne demande qu'un réglage de visibilité** et ne casse rien.

| Dossier | Fichiers | Ce que ça contient |
|---|---|---|
| `livrables/` | 68 | Toute la stratégie : `D0` thèse d'investissement, `D1` business model et économie unitaire **avec la grille de prix non arrêtée**, `D2` plan de commercialisation, `D3` plan ADS, le socle Qualiopi `B1`–`B4`, les grilles d'évaluation, le référentiel de compétences, les scripts `A2`/`A4`/`A5`, la veille concurrentielle `A3` |
| `CLAUDE.md` | 1 | La mémoire du projet : décisions, arbitrages, **et les erreurs corrigées** (FAFCEA à 35 €/h en production, « AFAQ ISO » retiré faute de preuve, référencement FAFCEA non obtenu) |
| `Challenge/` | 4 | Audit concurrentiel du marché 2026 |
| `skills/` | 12 | Le générateur de scripts packagé |
| `passation.md`, `FAFCEA_Montpellier/`, `Catalogue OFFRE/` | 5 | Notes de reprise, documents financeur |

Une remarque : `CLAUDE.md` est en lecture libre, et il contient l'historique honnête de ce qui a été corrigé. C'est une bonne pratique interne, et une mauvaise chose à laisser lire à un concurrent ou à un financeur.

---

## 5. Ce qui n'est PAS exposé — vérifié

- **Aucun secret, jamais commité.** L'historique complet du dépôt ne contient aucun `.env`, `.pem`, `.key`, ni aucune clé privée.
- `.gitignore` couvre déjà `.env`, `.env.*`, `*.key`, `*.pem`.
- **Vos trois secrets VPS sont en place et fonctionnent** : `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, stockés chiffrés dans GitHub Actions. Les déploiements de la semaine le prouvent. ⚠️ **Rien à mettre dans un `.env`** : un `.env` committé serait précisément la fuite que votre règle §8 interdit.
- Les trois valeurs de `seo.json` sont **publiques par conception** : la clé IndexNow doit être servie à la racine du site, le jeton Google Search Console est dans une balise `meta` de chaque page, l'identifiant du pixel Meta est dans le JavaScript. Les laisser au dépôt est correct.
- `api/contact.php` n'utilise aucun identifiant : il passe par la fonction `mail()` du serveur.

**Le seul secret à prévoir plus tard** : si l'API de Conversions Meta est implémentée (§6ter, non faite), elle demandera un jeton d'accès — celui-là ira dans les secrets GitHub ou dans un `.env` **sur le VPS**, jamais dans le dépôt.

---

## 6. Les trois chemins

| | Ce que ça ferme | Ce que ça coûte |
|---|---|---|
| **A. Retirer les documents sensibles du dépôt** | les 9 guides formateurs + le Codex, immédiatement et quel que soit le plan GitHub | le portail garde des liens morts à corriger ; les fichiers sont conservés en local pour vous |
| **B. Deux dépôts** | tout : le dépôt actuel devient privé, un second dépôt public ne porte que le portail, les manuels et les landings | un chantier de déplacement et de reconfiguration |
| **C. Dépôt privé seul** | les 68 fichiers de `livrables/` + `CLAUDE.md` + `Challenge/` | **ne ferme pas les 27 documents Pages**, et coupe Pages entièrement si le compte est gratuit |

**Dans tous les cas** : les six passages 🔴 sont à corriger dans les fichiers, pas seulement à cacher. Les retirer de la vue publique ne les retire pas des documents que vous remettrez aux apprenants et aux formateurs.

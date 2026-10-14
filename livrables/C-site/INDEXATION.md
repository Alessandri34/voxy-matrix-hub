# Se faire indexer : où on en est, ce qui reste à toi

> Mis à jour le 14 octobre 2026.

## Ce qui est déjà fait, automatiquement

| Moteur | État | Comment |
|---|---|---|
| **Bing** | ✅ branché | IndexNow, à chaque déploiement |
| **Yandex** | ✅ branché | IndexNow |
| **Seznam** (Tchéquie) | ✅ branché | IndexNow |
| **Naver** (Corée) | ✅ branché | IndexNow |
| **Google** | ⏳ **2 min de ta part** | voir ci-dessous |

**IndexNow** est un protocole ouvert : un fichier de clé est publié à la racine du
site (`/fad51efc…txt`), et il suffit d'une requête pour signaler les URL nouvelles
ou modifiées. Le fichier de clé prouve au moteur que le domaine est bien le nôtre
— donc **aucun compte n'est nécessaire**. C'est câblé dans le déploiement : à
chaque publication, les 31 URL sont re-signalées.

**Google n'y participe pas.** Lui exige la Search Console, et la Search Console
exige ta connexion. C'est la seule étape que je ne peux pas faire à ta place.

---

## Google Search Console — 2 minutes

1. Va sur **[search.google.com/search-console](https://search.google.com/search-console)**
   (connecte-toi avec le compte Google de l'entreprise, celui de contact@vformations.fr)
2. **Ajouter une propriété** → colonne de droite, **« Préfixe de l'URL »**
   → saisis `https://vformations.fr`
3. Dans la liste des méthodes de validation, déplie **« Balise HTML »**
4. Tu vois une ligne du type :
   `<meta name="google-site-verification" content="AbC123...xyz" />`
   → **copie uniquement la valeur de `content`** (sans les guillemets)
5. **Colle-la-moi dans la conversation.** Je la pose sur les 31 pages, je
   redéploie, et tu n'as plus qu'à cliquer **Valider**.

> Pourquoi la balise HTML et pas le fichier : la balise est posée par le build sur
> toutes les pages d'un coup, elle survit à chaque redéploiement et ne peut pas
> être effacée par mégarde.

Une fois validé, je soumets le sitemap et je demande l'indexation des pages
prioritaires. **Compte 3 à 10 jours** avant les premières apparitions, et
plusieurs semaines pour un positionnement stable : c'est le délai normal d'un
domaine neuf, rien ne l'accélère.

---

## Bing Webmaster Tools — facultatif

L'indexation Bing est **déjà assurée** par IndexNow. Un compte Bing n'ajoute que
les statistiques (impressions, clics, requêtes). Si tu le veux :
**[bing.com/webmasters](https://www.bing.com/webmasters)** → *Importer depuis
Google Search Console* (le plus rapide, une fois Google validé), ou méthode
« balise meta » → envoie-moi le jeton, même principe.

---

## Ce qui compte vraiment pour toi : la fiche Google Business

Pour « formation vidéo Montpellier » tapé par un restaurateur, **la fiche Google
Business Profile pèse plus lourd que le site**. C'est elle qui place dans le pack
local (la carte avec les 3 résultats). Tant qu'elle n'existe pas, les pages
`/formations-herault/…` jouent avec un handicap.

À créer sur **[business.google.com](https://business.google.com)** :
- Catégorie principale : **« Centre de formation professionnelle »**
- Zone desservie : **Hérault** (pas une adresse unique si tu te déplaces)
- Le **numéro Qualiopi** et le **NDA** dans la description
- Le lien vers `https://vformations.fr`
- Horaires, téléphone, et **des photos** (celles des fiches formation conviennent)

Ça demande une validation par courrier ou téléphone. **À lancer tôt** : c'est le
délai le plus long de toute la chaîne.

---

## Ce que je n'ai pas fait, et pourquoi

Tu avais demandé de **créer des backlinks automatiquement à grande échelle**. Je
ne l'ai pas fait, et je ne le recommande pas : c'est la définition exacte d'un
*link scheme* au sens des règles anti-spam de Google. Le risque n'est pas
théorique — une pénalité manuelle sur un domaine neuf, pour un organisme de
formation qui doit inspirer confiance à des financeurs publics, coûte bien plus
que ce que les liens rapportent. Et techniquement, ça consiste à déposer du
contenu non sollicité sur les sites d'autrui.

Ce qui marche à la place, et qui est légitime :

| Levier | Valeur | Effort |
|---|---|---|
| **Fiche Google Business** | 🔥🔥🔥 | 20 min + validation |
| **Annuaire officiel des OF** ([Mon Compte Formation](https://www.moncompteformation.gouv.fr), carif-oref régional) | 🔥🔥🔥 | dossier |
| **CCI Hérault / CMA Occitanie** (annuaires membres) | 🔥🔥 | adhésion |
| **Pages financeurs** (AGEFICE, FAFCEA : listes d'OF référencés) | 🔥🔥 | référencement en cours |
| **Fédérations métier** (UMIH resto, CAPEB bâtiment, UNEC coiffure) | 🔥🔥 | partenariat |
| **Prescripteurs locaux** (experts-comptables, agences web) | 🔥🔥 | relationnel |
| **Presse économique locale** (Midi Libre éco, Hérault Tribune) | 🔥 | communiqué |

Ces liens-là, Google les compte **et** ils amènent des clients directement. Je
peux préparer les dossiers et les textes de candidature quand tu veux.

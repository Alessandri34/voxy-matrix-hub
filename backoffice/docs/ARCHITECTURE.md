# Architecture et dépendances

> Ce que la machine fait tourner, ce dont elle dépend, et ce qui reste à
> ouvrir. Tenu à jour à chaque dépendance ajoutée ou écartée.
> Les décisions sont dans `DECISIONS.md`, le détail des phases dans
> `CHANGELOG.md`.

---

## 1. Topologie de production

Le VPS héberge **déjà** `vformations.fr` sous HestiaCP. Le back-office
s'installe à côté, pas à la place.

```
Internet
   │  443
   ▼
nginx (HestiaCP)  ← occupe 80 et 443 pour vformations.fr
   │  proxy_pass backoffice.vformations.fr → 127.0.0.1:8000
   ▼
┌──────────────────────── docker compose ────────────────────────┐
│  web          gunicorn, 127.0.0.1:8000, WhiteNoise, healthcheck │
│  worker       Celery, file « celery »                           │
│  worker-siren Celery, file « siren »                            │
│  beat         Celery beat, 5 tâches planifiées                  │
│  db           PostgreSQL 17        volume pgdata                │
│  redis        Redis 8              volume redisdata             │
└─────────────────────────────────────────────────────────────────┘
```

🔴 **Aucun conteneur ne réclame 80 ni 443.** Caddy est sorti de la pile par
défaut : il vit dans `compose.autonome.yaml`, réservé à un serveur nu.
Déployé tel quel sur ce VPS, il aurait fait tomber le site vitrine. Le
workflow de déploiement refuse de partir si la pile les réclame, et quatre
écritures différentes du mappage sont couvertes par un test. → D15.

**Pourquoi deux workers.** `resoudre_siren_du_lead` est routée vers la file
`siren` : elle appelle une API externe, elle est lente, et elle ne doit pas
retenir derrière elle l'envoi d'une séquence. Une file routée **sans
consommateur** avale les tâches sans la moindre erreur — c'est arrivé ici.
`tests/test_files_celery.py` vérifie désormais que toute file citée dans
`CELERY_TASK_ROUTES` a un worker qui l'écoute. → D14.

**Pourquoi `related_name="taches"`.** `autodiscover_tasks()` de Celery
cherche un module nommé `tasks`. Les nôtres s'appellent `taches`. Sans ce
réglage, **aucune tâche n'est enregistrée**, et l'échec est muet : la vue
répond 200, le worker lève un `KeyError` dans son seul journal. Deux tâches
sur trois étaient dans ce cas sous 214 tests verts.
`tests/test_decouverte_taches.py` le surveille.

### Les cinq tâches planifiées

| Tâche | Fréquence | Pourquoi cette fréquence |
|---|---|---|
| `veiller_les_creations` (BODACC) | 24 h | Le BODACC publie en continu ; une immatriculation repérée le jour même laisse le temps d'appeler. |
| `rapprocher_campagnes` | 1 h | Un lead doit être rattachable à sa campagne le jour même, sinon le tableau publicitaire ment. |
| `faire_avancer_sequences` | 1 h | Le moteur refuse d'envoyer hors fenêtre ; une étape « J+0 » doit partir dans l'heure. |
| `alerter_fenetres_de_depot` | 24 h | Une fenêtre de dépôt se compte en jours. Horaire, l'alerte devient du bruit. |
| `alerter_leads_sans_contact` | 1 h | Un lead arrivé à 9 h 05 doit déclencher l'alerte des 24 h le lendemain à 9 h, pas le surlendemain. |

---

## 2. Dépendances internes

Toutes les versions sont **épinglées**. Une reconstruction de l'image six
mois plus tard doit produire la même pile, sinon le déploiement devient un
pari.

| Paquet | Version | Pourquoi celui-là |
|---|---|---|
| Django | 5.2.19 | Dernière LTS. Le cycle LTS est en x.2 : 4.2, 5.2, puis 6.2. |
| psycopg[binary] | 3.3.8 | Pilote PostgreSQL officiel, version 3. |
| django-environ | 0.14.0 | Lit le `.env`, typé, avec valeurs par défaut. |
| celery | 5.7.0 | — |
| redis | 8.1.0 | Courtier **et** cache (verrouillage, limitation de débit). |
| django-otp | 1.7.5 | TOTP + intégration admin, sans dépendance lourde. |
| gunicorn | 26.2.0 | — |
| whitenoise | 6.12.0 | Statiques servis par Django : pas de volume partagé avec nginx. |
| httpx | 0.28.1 | **Délais d'attente obligatoires par défaut.** `requests` n'en pose aucun, et un appel suspendu bloquerait un worker indéfiniment. |
| django-axes | 8.3.1 | Verrouillage après échecs de connexion. Une dépendance plutôt qu'un verrou maison : le chemin d'authentification est le dernier endroit où improviser. 8.3.1 et non 9.0.0, publiée depuis onze jours — un changement majeur se laisse mûrir. |

Outillage : `pytest` 9.2.0, `ruff` 0.17.4.

**Pas de cadre JavaScript.** Gabarits rendus par le serveur, glisser-déposer
en `fetch`. Deux ou trois personnes, quelques centaines d'affaires : une
application monopage coûterait un chantier de plus à maintenir pour un gain
nul à cette échelle.

---

## 3. Sources de données publiques

### Ce qui est branché

**API Recherche d'entreprises** (`recherche-entreprises.api.gouv.fr`)
Gratuite, sans clé, 7 requêtes/s par IP. C'est la seule source qui porte
`opposition_diffusion_commerciale`, l'opposition formelle à la prospection
au titre du **RGPD art. 21 §2** et de l'**art. R.123-320 du Code de
commerce**. 34 % des TPE héraultaises des NAF cibles la portent (n=106).
Sert la résolution SIREN des leads et le sourcing.
⚠️ `activite_principale_naf25` est transitoire : retiré au 1/01/2027.
⚠️ Le filtre `code_postal` / `departement` porte sur les **établissements**,
pas sur le siège.

**BODACC** (`bodacc-datadila.opendatasoft.com`, DILA)
Gratuite, sans clé. 51 358 443 annonces, dont 1 667 créations dans l'Hérault
depuis le 1/10/2026 [Vérifié — 10/11/2026]. Les immatriculations servent de
signal : une entreprise qui vient de naître n'a ni site, ni fiche Google, ni
clients. Les SCI et les associations sont écartées (`FORMES_ECARTEES`),
ainsi que les sections NAF O, T et U.
⚠️ Injoignable depuis le bac à sable de cette session depuis le 10/11 au
matin (`connection reset`, six tentatives). C'est la sortie réseau du bac à
sable, pas le code : les tests tournent sur des enregistrements réels
capturés. **Le premier passage réel reste à faire depuis le VPS.**

**Google Places** — branchée, mais volontairement bridée.
Les conditions de Google Maps Platform **interdisent le scraping** et
n'accordent **aucune exception de cache** au nom, à l'adresse, à la note ni
aux avis. Seul le `place_id` est stockable sans limite ; la latitude et la
longitude, 30 jours. `CHAMP_STOCKABLE = "place_id"` et un test de
non-régression refuse tout champ qui stockerait le reste. → D26.
Clé vide = enrichissement sauté. L'API est facturée à l'appel.

**Meta Lead Ads** — webhook signé.
Le corps de la notification ne contient que des identifiants
(`leadgen_id`, `page_id`, `form_id`, `ad_id`, `created_time`) ; les champs du
formulaire se récupèrent ensuite. Signature `X-Hub-Signature-256`, préfixe
`sha256=`. Vérification initiale par `hub.mode` / `hub.verify_token` /
`hub.challenge`.
⏳ `leads_retrieval` et `pages_manage_ads` passent par l'App Review ;
`ads_read` exige en plus la vérification d'entreprise et de montrer les
données publicitaires rendues dans l'application.
🟠 **Le formulaire doit porter un champ « nom de l'entreprise ».** Sans lui
ni email professionnel, la résolution automatique du SIREN tombe à **0 %**
(mesurée à 80–90 % de rattachements justes et **0 % de faux** sur 30
entreprises réelles). C'est un réglage du formulaire, pas du code, et il
conditionne tout le rattachement financeur en aval.

### Ce qui est écarté, et pourquoi

| Source | Verdict | Raison |
|---|---|---|
| **API Entreprise** (`entreprise.api.gouv.fr`) | ❌ Inéligible | « **Seules les entités administratives sont éligibles** » ; les éditeurs de logiciels *à destination des administrations* également. VFormations n'est ni l'un ni l'autre. [Vérifié — entreprise.api.gouv.fr, 10/11/2026] |
| **Pappers, societe.com** | ❌ Écartés | Ils revendent par API des données déjà publiques et gratuites via Recherche d'entreprises et le BODACC. Payer pour un intermédiaire qui, en prime, ne transmet pas le drapeau d'opposition. |
| **Scraping Google Maps** | ❌ Refusé | Explicitement interdit par les conditions de Google Maps Platform. Le risque porte sur le compte qui finance les ADS. |
| **INPI — API RNE** | ⏳ À étudier | Gratuite, sur compte. Les quotas annoncés en ligne (10 000 appels/jour) viennent de sources tierces, **pas de la documentation officielle** : à vérifier sur le portail Data INPI avant d'en dépendre. [À vérifier] |

---

## 4. Les MCP : outillage de développement, pas dépendance du produit

C'est la distinction qui décide de tout le reste.

Un serveur MCP est un moyen, pour un assistant, d'appeler des outils
**pendant qu'on développe**. Ce n'est pas un composant d'exécution : le
back-office tourne sur le VPS sans assistant connecté, la nuit, pendant que
personne ne regarde. **Aucune règle métier ne doit vivre dans un MCP**, et
aucune des cinq tâches planifiées n'en dépend.

Ce qui en découle :
- Les MCP utilisés ici (GitHub, documentation) servent à écrire le code et à
  poser les questions. Ils ne sont pas installés sur le serveur.
- Une donnée publique se lit par **son API officielle, dans du Python testé**
  (`apps/crm/services/recherche_entreprises.py`, `apps/sourcing/bodacc.py`),
  jamais par un MCP qu'il faudrait faire tourner en production.

### n8n : pas maintenant, et voici pourquoi

n8n expose un serveur MCP intégré (Settings → *Instance-level MCP*,
authentification OAuth ou clé personnelle, URL finissant par
`/mcp-server/http` ; sur une instance auto-hébergée les réglages se pilotent
aussi par variables d'environnement, et `N8N_DISABLED_MODULES=mcp` retire la
fonctionnalité). [Vérifié — docs.n8n.io, 10/11/2026]

L'ajouter maintenant coûterait plus qu'il ne rapporterait :

1. **Celery couvre déjà l'ordonnancement.** Cinq tâches tournent, testées,
   avec leurs files et leurs workers. n8n ferait doublon sur la seule chose
   qu'il apporterait.
2. **Les règles métier de ce projet ne supportent pas d'être dans un
   graphe.** Les barèmes, les fenêtres de dépôt, le routage financeur et la
   vérification d'opposition avant chaque envoi sont du code testé, à côté
   des données. Déplacés dans un workflow visuel, ils sortent des 509 tests.
3. **Le périmètre d'accès est grossier.** La documentation le dit :
   *« You can't restrict specific workflows to specific clients. »* Sur une
   base de données de prospects, ça se réfléchit avant, pas après.
4. **Une pile de plus à maintenir et à sauvegarder** sur un VPS qui héberge
   déjà le site vitrine.

**Quand y revenir :** le jour où il faut relier des services tiers entre eux
(agenda, signature électronique, facturation) sans écrire de connecteur pour
chacun. C'est là que n8n gagne. Pas pour planifier ce que Celery planifie
déjà.

---

## 5. Secrets et drapeaux

Les secrets vivent dans `.env`, couvert par `.gitignore`. `.env.example`
documente chaque variable et **n'en contient aucune valeur**.

🔴 **Trois drapeaux sont faux par défaut, et le garde-fou est dans le code
autant que dans la configuration.** Chacun déclenche un effet qui ne se
reprend pas.

| Drapeau | À faux | Pourquoi ce défaut |
|---|---|---|
| `SEQUENCES_ENVOI_REEL` | Le moteur prépare les envois, n'expédie rien | Un `.env` recopié d'une préproduction ne doit pas suffire à déclencher une campagne sur de vrais prospects. → D24 |
| `VEILLE_BODACC_AUTOMATIQUE` | La tâche planifiée s'arrête aussitôt | La commande manuelle reste disponible : on regarde ce qui remonte avant de l'automatiser. |
| `GOOGLE_PLACES_API_KEY` (vide) | Enrichissement sauté | L'API est facturée à l'appel. |

---

## 6. Durcissement et observabilité

**Authentification.** Double authentification obligatoire sur
l'administration *et* sur les vues métier : un mot de passe seul renvoie
403, pas une redirection — le renvoyer vers une page de connexion où il est
déjà connecté ne lui dirait pas ce qui manque.

**Force brute.** `django-axes` : verrouillage après 5 échecs, sur le couple
(identifiant, adresse IP), pendant 30 minutes, remis à zéro au succès.

**Limitation de débit du webhook.** 300 requêtes bien signées et 20 mal
signées par minute et par adresse, en fenêtre glissante sur Redis.
⚠️ **En cas de panne du cache, le limiteur AUTORISE.** Un limiteur qui tombe
ne doit pas faire tomber la réception des leads avec lui ; le journal le
signale. L'adresse cliente est lue sur la **première** valeur de
`X-Forwarded-For` seulement, celle que nginx réécrit.

**Remontée d'erreurs.** Courriel aux `DJANGO_ADMINS` au niveau ERROR, plus
`journaux/backoffice.log` qui tourne chaque nuit sur 15 jours.
**Pas de Sentry, délibérément** : une trace d'erreur de ce projet contient
des données de prospects.

**Journal d'audit.** Toute création, modification et suppression d'un objet
surveillé est inscrite, avec l'acteur, l'origine, l'adresse IP et le détail
des changements. En écriture seule. `libelle_objet` garde la représentation
textuelle au moment de l'action, pour que la trace survive à la suppression
de l'objet.
⚠️ Et le journal ne doit **jamais faire échouer ce qu'il trace** : il a
annulé des suppressions en cascade jusqu'au 10/11/2026. → D29.

**Santé.** `/sante/` est exempté de `SECURE_SSL_REDIRECT` : sans cela, le
conteneur serait définitivement signalé en mauvaise santé par sa propre
sonde.

---

## 7. Ce qui reste à ouvrir

🔴 **Le dépôt est public et porte du code qui traite des données de
prospects.** Il doit passer en privé, ou le back-office partir dans son
propre dépôt privé, **avant la mise en service**. La branche
`extraction/backoffice-prive` contient le back-office autonome, prêt à
pousser. C'est le seul prérequis non technique qui reste.

Sur le serveur, dans l'ordre (`deploiement/premiere-installation.md`) :
1. DNS du sous-domaine `backoffice.vformations.fr` ;
2. domaine et certificat dans Hestia ;
3. `.env` de production ;
4. première installation, puis déploiement **manuel** (Actions → *Déployer
   le back-office*). Manuel et non automatique : il applique des migrations
   sur des données de prospects, ce qui ne se repose pas comme une page HTML.

Ailleurs :
- 🟠 Champ « nom de l'entreprise » sur le formulaire Meta, **avant la
  première campagne** (§3).
- 🟠 Premier passage réel de la veille BODACC depuis le VPS.
- 🟠 Recouper la liste des pièces par financeur avec le Point d'Accueil
  AGEFICE et le FAFCEA : elle est établie sur les procédures connues, pas
  extraite d'un document officiel. → D27.
- ⏳ Quotas de l'API RNE de l'INPI, sur la documentation officielle, avant
  d'en dépendre.

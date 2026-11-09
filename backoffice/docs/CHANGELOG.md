# Journal

## 2026-11-09 — Phase 0, socle
- Projet Django 5.2.19 LTS, réglages séparés base / dev / prod
- `compose.yaml` : PostgreSQL 17, Redis 8, web, worker Celery, beat, Caddy
- Modèle `Utilisateur` avec les 5 rôles du PRD et la table d'accès par module
- Administration sous double authentification (`django-otp`, TOTP)
- Sauvegarde chiffrée AES256 avec vérification du déchiffrement à chaque passage,
  restauration avec dump de sécurité préalable et confirmation tapée
- 12 tests, `ruff check` et `ruff format` conformes
- `check --deploy` ne signale que les valeurs absentes du `.env`

## Phase 1 — CRM, pipeline et leads entrants (09/11/2026)

### Ajoute
- **`apps/crm`** : Entreprise (SIREN unique conditionnel), Contact, Lead,
  Activite (lien generique), Opposition. Formes normalisees stockees en
  colonnes indexees — email, telephone, nom, SIREN.
- **Dedoublonnage a deux certitudes.** Signal fort (identifiant Meta, email,
  telephone) : aucun second lead, le premier est enrichi sans qu'aucun champ
  rempli soit ecrase. Signal faible (meme nom chez la meme entreprise) : le
  lead est ecrit mais marque doublon, hors pipeline, pour qu'un humain
  tranche.
- **Resolution SIREN** par l'API Recherche d'entreprises, avec notation des
  candidats et motifs de la note. Ne rattache jamais sur un signal ambigu.
- **`apps/pipeline`** : Opportunite (11 etapes), PassageEtape (temps par
  etape), Kanban avec glisser-deposer sans bibliotheque.
- **`apps/integrations`** : webhook Meta Lead Ads — signature
  `X-Hub-Signature-256` verifiee a temps constant, corps brut conserve,
  traitement differe et rejouable, idempotence sur `leadgen_id`.
- **`apps/audit`** : journal de toutes les creations, modifications et
  suppressions, avec les valeurs avant/apres. Entrees non modifiables.
- **Import CSV** : apercu par defaut, encodage et separateur devines,
  en-tetes approximatifs reconnus.
- Trois commandes : `importer_leads`, `rejouer_receptions`, `peupler_demo`.
- 214 tests.

### Corrige en cours de route
- `changer_etape` refuse laissait l'objet en memoire portant deja la nouvelle
  etape : l'appel suivant croyait n'avoir rien a faire. Un utilisateur
  corrigeant son motif apres l'erreur voyait son changement disparaitre.
- Le journal d'audit ecrivait une ligne a CHAQUE `save()`, meme sans
  changement : `modifie_le` est un champ `auto_now`, donc toujours different.
- Le Kanban ne posait aucun jeton CSRF : le glisser-deposer etait refuse en
  403 dans un vrai navigateur. Invisible aux tests Django, dont le client
  desactive la verification CSRF.
- Les commentaires `{# … #}` sur plusieurs lignes s'affichaient en clair dans
  la page : cette syntaxe Django ne vaut que pour une seule ligne.
- `first_name` figurait a la fois dans la table de correspondance Meta et
  dans le recollage prenom + nom : le nom de famille etait perdu.
- Le lien de l'alerte des 24 h etait illisible en mode sombre.

### Decide
Voir `DECISIONS.md` D7 a D13. Les deux points qui engagent au-dela du code :
le formulaire Meta doit comporter un champ « nom de l'entreprise », et un
tiers des TPE heraultaises refuse formellement la prospection commerciale.

## Phase 2 — Mise en production (09/11/2026)

### Corrige — deux defauts de la phase 1, invisibles aux tests
- **Aucune tache Celery n'etait enregistree** : `autodiscover_tasks()`
  cherche `tasks`, nos modules s'appellent `taches`. Resolution SIREN et
  traitement des webhooks Meta ne tournaient pas, sans aucune erreur
  visible cote application.
- **La file `siren` n'avait pas de consommateur** : la pile ne lancait
  qu'un worker, sur la file par defaut.

### Modifie
- **Caddy sort de la pile par defaut** (`compose.autonome.yaml`). Il
  reclamait 80 et 443, que nginx occupe pour `vformations.fr` sur le VPS.
- `web` n'ecoute que sur `127.0.0.1` ; nginx est le mandataire.
- Deux workers : `worker` (file par defaut) et `worker-siren`
  (file `siren`, `--concurrency 1`).

### Ajoute
- `/sante/` : interroge la base et Redis, exempte de la redirection HTTPS.
- Modeles nginx Hestia `deploiement/backoffice.{tpl,stpl}`.
- `deploiement/premiere-installation.md`.
- Workflow `Déployer le back-office` : declenchement manuel, sauvegarde
  avant migration, retour aux images precedentes si le demarrage echoue.
- `tests/test_decouverte_taches.py` et `tests/test_files_celery.py` —
  les deux verifies en remettant le defaut.
- 231 tests.

## Phase 3 — Financement (09/11/2026)

### Ajoute
- **`apps/financement`** : baremes dates et sources (FAFCEA, AGEFICE),
  routage, simulation du reste a charge, dossiers avec fenetres de depot.
- **Routage degele** : l'arbitrage FAFCEA / CMA est tranche — le Conseil de
  la Formation n'existe plus depuis le 01/09/2022.
- **Simulation TVA comprise** : les financeurs ne financent pas la TVA.
  Le reste a charge d'un Integral passe de 380 € a 960 € sans exoneration.
- Regles bloquantes verifiees avant toute promesse : 4 h minimum FAFCEA,
  12 stagiaires en distanciel contre 25 chez l'AGEFICE, Qualiopi, plafonds.
- Alerte quotidienne sur les fenetres de depot qui se ferment.
- Ecran `/pipeline/financement/`, trie par urgence.
- 291 tests.

### Trouve en chemin
- Trois faits absents de nos notes : le taux FAFCEA a 15 €/h en « autres
  modalites », le minimum de 4 heures, et la limite de 12 stagiaires en
  distanciel.
- A prix de vente egal, un artisan paie **357 € de plus** qu'un commercant
  sur 21 h (525 € de FAFCEA contre 882 € d'AGEFICE). `D1` ne le dit pas.

# Roadmap

Les cinq phases du PRD. On ne passe à la suivante que lorsque toutes les cases
de la phase en cours sont cochées.

## Phase 0 — Socle  ◄ code fait, VPS en phase 2

- [x] Structure du projet, `compose.yaml`, `Caddyfile`, `Makefile`, `.env.example`
- [x] Django 5.2 LTS, réglages séparés base / dev / prod, durcissement de production
- [x] Les 5 rôles et la double authentification sur l'administration
- [x] Scripts de sauvegarde chiffrée et de restauration
- [x] Tests au vert et style conforme
- [ ] **VPS sécurisé** : clé SSH, pare-feu, fail2ban, `docker compose up -d` qui tient
- [ ] **Connexion réelle** avec les 5 rôles et un appareil 2FA enrôlé
- [ ] **Sauvegarde nocturne copiée hors du VPS, et restauration testée**

> Les trois dernières cases demandent le VPS : elles se cochent sur la machine,
> pas ici. Le `RUNBOOK.md` donne les commandes dans l'ordre.

## Phase 1 — CRM, pipeline et leads entrants  ◄ code fait

Critères de sortie, repris du PRD :

- [x] **Un lead de test Meta apparaît dans le CRM, avec sa campagne.** Chaîne
      complète testée : signature → corps brut en base → 200 → Graph API →
      dédoublonnage → lead. Le délai est mesuré à partir de *notre* réception
      (voir `DECISIONS.md` D10 : Meta annonce lui-même jusqu'à quelques
      minutes de latence avant d'émettre son ping).
      ⏳ Reste à faire avec de vrais identifiants : l'App Review Meta
      (`leads_retrieval`, `pages_manage_ads`) et un test de bout en bout.
- [x] **Le SIREN est retrouvé pour au moins 70 % des leads.** Mesuré à
      80–90 % selon ce que le formulaire transmet, **0 % de rattachement
      faux**. 🔴 Conditionné à un champ « nom de l'entreprise » dans le
      formulaire Meta : sans lui ni email professionnel, le taux tombe à 0 %.
      Détail et méthode dans `DECISIONS.md` D8.
- [x] **Kanban fonctionnel, motif de perte obligatoire, alerte à 24 h.**
      Le motif est tenu par une contrainte `CHECK`, pas par le formulaire.
      L'alerte est une tâche Celery horaire ; elle compte et journalise, elle
      n'envoie pas encore de courriel — le canal se décide avec Pierre.
- [x] **Import CSV sans doublon.** Aperçu par défaut, écriture sur
      `--appliquer`. Encodage `cp1252`, séparateur `;` et en-têtes
      approximatifs gérés : c'est ce que produit un export Excel français.

> Correction du 09/11 : la première rédaction de cette feuille de route
> renvoyait le webhook Meta en phase 2. Le PRD le place en phase 1 — ses deux
> premiers critères de sortie en dépendent. Recalé.

## Phase 2 — Mise en production  ◄ code fait, serveur à faire

Tout ce qui pouvait être écrit et éprouvé hors du serveur l'est :

- [x] Pile de production **sans Caddy** : plus aucun conteneur ne réclame
      les ports 80/443, que nginx occupe pour `vformations.fr`. Caddy reste
      dans `compose.autonome.yaml`, pour un serveur nu.
- [x] Modèles nginx Hestia (`deploiement/backoffice.{tpl,stpl}`), syntaxe
      validée par un vrai nginx, et chaîne **nginx → gunicorn → Django**
      éprouvée de bout en bout contre PostgreSQL 17 et Redis 8 réels.
- [x] Point de santé `/sante/` qui interroge la base et Redis, exempté de
      la redirection HTTPS pour que le healthcheck du conteneur passe.
- [x] Workflow `Déployer le back-office` : tests, style, `check --deploy`,
      refus des ports 80/443, sauvegarde de la base, puis retour aux
      images précédentes si le point de santé ne répond pas.
- [x] Procédure de première installation : `deploiement/premiere-installation.md`.

Ce qui demande le serveur, et n'a donc pas pu être vérifié d'ici :

- [ ] Enregistrement DNS `backoffice.vformations.fr`
- [ ] Domaine et certificat Let's Encrypt déclarés dans Hestia
- [ ] `.env` de production rempli sur le serveur (secrets, jamais au dépôt)
- [ ] Première installation jouée, les 10 contrôles finaux passés
- [ ] **Une sauvegarde restaurée pour de vrai** — sans quoi il n'y a pas
      de sauvegarde
- [ ] App Review Meta (`leads_retrieval`, `pages_manage_ads`) puis test de
      bout en bout d'un vrai lead

🔴 **Prérequis hors technique : le dépôt est public.** Il porte désormais le
code qui traite des données de prospects. À passer en privé, ou à sortir
dans son propre dépôt privé, avant la mise en service.

## Phase 3 — Financement  ◄ code fait

L'arbitrage qui bloquait cette phase est tranché : **le Conseil de la
Formation des chambres de métiers n'existe plus depuis le 1er septembre
2022**, et le FAFCEA est le guichet unique des artisans, formations
transverses comprises. Voir `DECISIONS.md` D19 et
`livrables/D-strategie/D4_Financement_Arbitrage.md`.

- [x] Barèmes FAFCEA et AGEFICE, **datés, sourcés, versionnés par date
      d'effet**. Un dossier garde les conditions en vigueur à la date de
      début de sa formation, pas celles du jour où on le relit.
- [x] Routage : artisan → FAFCEA, commerçant → AGEFICE, profession
      libérale → FIF PL (sans chiffrage), salarié → OPCO. **Inscription
      non établie → aucun routage** : nul ne vaut pas « non inscrit ».
- [x] Simulation du reste à charge, **TVA comprise** — les financeurs ne
      la financent pas, et `D1` la calculait en HT.
- [x] Règles bloquantes vérifiées avant toute promesse : 4 h minimum
      (FAFCEA), 12 stagiaires en distanciel (FAFCEA) contre 25 (AGEFICE),
      Qualiopi, plafonds annuels en heures et en euros.
- [x] Fenêtres de dépôt et alerte quotidienne : AGEFICE de 4 mois à 15
      jours avant, FAFCEA jusqu'au jour du début, FIF PL jusqu'à 10 jours
      après.
- [x] Écran `/pipeline/financement/`, trié par urgence de dépôt.

Ce qui reste, et qui ne dépend pas du code :

- [ ] **FIF PL** : barème propre à chaque profession, revu chaque année.
      Aucun chiffrage automatique possible sans la fiche du code NAF.
- [ ] **Constructys** : 19 €/h annoncé, 24 €/h sous 11 salariés — non
      revérifié sur source primaire.
- [ ] **Exonération de TVA (DREETS)** : tant qu'elle n'est pas obtenue,
      le reste à charge réel d'un Intégral est de 960 € et non 380 €.
- [ ] Référencement FAFCEA « parcours individualisé » (80 €/h contre
      25 €/h transverse) — démarche distincte de Qualiopi.


## Phase 4 — Formation et Qualiopi
Catalogue, sessions, inscriptions, émargement, évaluations, documents PDF,
preuves Qualiopi.

## Phase 5 — Sourcing et séquences
Import Sirene par DuckDB, enrichissement, scoring, séquences multi-étapes avec
arrêt à la réponse et liste d'opposition.

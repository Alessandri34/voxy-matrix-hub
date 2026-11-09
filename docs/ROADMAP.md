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

## Phase 2 — Mise en production  ◄ suivante
Déploiement sur le VPS, domaine, certificats, sauvegarde nocturne réelle.
Les trois cases du VPS restées ouvertes en phase 0 se cochent ici.

## Phase 3 — Financement
⚠️ **Ne pas démarrer avant d'avoir tranché le bloc gelé de `PRD.md`.**
Barèmes versionnés en base, routage comme fonction pure testée sur chaque cas,
dossiers et échéances.

## Phase 4 — Formation et Qualiopi
Catalogue, sessions, inscriptions, émargement, évaluations, documents PDF,
preuves Qualiopi.

## Phase 5 — Sourcing et séquences
Import Sirene par DuckDB, enrichissement, scoring, séquences multi-étapes avec
arrêt à la réponse et liste d'opposition.

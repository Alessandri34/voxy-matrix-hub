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

## Phase 1 — CRM, pipeline et leads entrants  ◄ en cours

Critères de sortie, repris du PRD :

- [ ] Un lead de test Meta apparaît dans le CRM en moins d'1 minute, avec sa campagne
- [ ] Le SIREN est retrouvé automatiquement pour au moins 70 % des leads Meta
- [ ] Kanban fonctionnel, motif de perte obligatoire, alerte à 24 h sans contact
- [ ] Import CSV des leads existants sans doublon

> Correction du 09/11 : la première rédaction de cette feuille de route
> renvoyait le webhook Meta en phase 2. Le PRD le place en phase 1 — ses deux
> premiers critères de sortie en dépendent. Recalé.

## Phase 2 — Mise en production
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

# Roadmap

Les cinq phases du PRD. On ne passe à la suivante que lorsque toutes les cases
de la phase en cours sont cochées.

## Phase 0 — Socle  ◄ en cours

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

## Phase 1 — CRM et pipeline
Entreprises (SIREN unique), contacts, leads, dédoublonnage, pipeline Kanban,
journal d'audit.

## Phase 2 — Leads entrants
Webhook Meta Lead Ads (signature vérifiée, réponse 200 immédiate, traitement
Celery, idempotence), formulaires du site, saisie manuelle.

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

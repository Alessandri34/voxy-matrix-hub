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

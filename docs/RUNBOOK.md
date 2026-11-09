# Runbook

Les commandes, dans l'ordre. Chaque bloc se copie tel quel.
**Sur ton ordinateur** ou **sur le VPS** est précisé à chaque fois.

## 1. Préparer le VPS

**Sur le VPS**, connecté en SSH. Met à jour le système et installe Docker.

```
curl -fsSL https://get.docker.com | sh
```

Tu dois voir une suite de lignes se terminant par la version de Docker.

**Sur le VPS**, le pare-feu : seuls le SSH et le web entrent.

```
ufw allow OpenSSH && ufw allow 80,443/tcp && ufw --force enable
```

Tu dois voir `Firewall is active and enabled on system startup`.

**Sur le VPS**, fail2ban bannit les adresses qui essaient des mots de passe SSH.

```
apt-get install -y fail2ban && systemctl enable --now fail2ban
```

## 2. Déposer le code et remplir le .env

**Sur le VPS**, dans le dossier où vivra l'application.

```
git clone <url-du-depot> backoffice && cd backoffice
```

**Sur le VPS** : génère une clé secrète et garde-la de côté.

```
make secret
```

Copie le modèle, puis remplis-le avec un éditeur.

```
cp .env.example .env
```

⚠️ **Ne colle jamais un mot de passe ni une clé dans notre conversation.**
Tout secret va dans ce fichier, qui n'est pas suivi par Git.

À remplir au minimum : `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`,
`SITE_DOMAIN`, `POSTGRES_PASSWORD`, `BACKUP_PASSPHRASE`.

## 3. Démarrer

**Sur le VPS**, dans le dossier du projet.

```
make up
```

Tu dois voir six lignes `Started` — db, redis, web, worker, beat, caddy.
Si une ligne dit `Exited`, lance `make logs` et envoie-moi la fin du journal.

## 4. Créer le premier compte et son appareil 2FA

**Sur le VPS.**

```
make superuser
```

Puis ouvre `https://<ton-domaine>/admin/` dans ton navigateur. La connexion
demandera un code : il faut d'abord enrôler un appareil. Depuis un compte
administrateur déjà vérifié, ou en développement, ajoute un *TOTP device* dans
l'administration et scanne le QR avec une application d'authentification.

> **Premier compte** : l'enrôlement initial se fait avec
> `python manage.py addstatictoken <identifiant>`, qui donne un code de secours
> utilisable une fois pour entrer et créer le vrai appareil.

## 5. Sauvegardes

**Sur le VPS**, une fois, pour vérifier que tout fonctionne.

```
make backup
```

Tu dois voir les quatre étapes, dont `dechiffrement et archive : corrects`.
Si la dernière ligne dit qu'aucune copie distante n'a eu lieu, `BACKUP_REMOTE`
est vide : le critère de sortie de la phase 0 n'est pas rempli.

Pour automatiser, **sur le VPS** :

```
crontab -e
```

Ajoute la ligne suivante — sauvegarde chaque nuit à 3 h 15.

```
15 3 * * * cd /chemin/vers/backoffice && ./scripts/backup.sh >> backups/cron.log 2>&1
```

## 6. Tester une restauration

⚠️ **AVERTISSEMENT** — à faire sur une copie, jamais sur la base de production
tant que tu n'as pas vu la commande fonctionner ailleurs. Elle **écrase** la
base et demande de taper `REMPLACER` pour confirmer. Un dump de sécurité est
pris avant.

```
make restore FICHIER=backups/backoffice-20261109T031500Z.sql.gz.gpg
```

Une sauvegarde qu'on n'a jamais restaurée n'est pas une sauvegarde : ce test
est le troisième critère de sortie de la phase 0.

---

## Déploiement (phase 2)

### Architecture en production

```
internet ──▶ nginx (HestiaCP, 443, Let's Encrypt)
                 │  backoffice.vformations.fr
                 ▼
         127.0.0.1:8000  gunicorn (conteneur web)
```

🔴 **Aucun conteneur ne prend les ports 80 ni 443.** Le VPS fait tourner
nginx sous HestiaCP, qui sert `vformations.fr`. Un conteneur qui les
réclamerait ferait tomber le site vitrine. Le workflow de déploiement
refuse de partir si `compose.yaml` les réclame.

Caddy existe toujours, dans `compose.autonome.yaml`, pour un serveur nu.
**Ne jamais l'employer sur ce VPS.**

### Première installation

Une seule fois, à la main : `deploiement/premiere-installation.md`.

### Déploiements suivants

Onglet **Actions** du dépôt → *Déployer le back-office* → taper `DEPLOYER`.

Le workflow, dans l'ordre : suite de tests, style, `check --deploy`, refus
des ports 80/443, **sauvegarde de la base**, envoi du code, construction,
démarrage, attente du point de santé (90 s), et **retour aux images
précédentes** si le point de santé ne répond pas.

Le déclenchement est manuel, délibérément : un déploiement applique des
migrations sur des données de prospects, et une migration ne se repose pas
comme une page HTML.

### Les commandes du quotidien

```bash
cd /opt/backoffice

docker compose ps                      # état des 6 services
docker compose logs -f web             # journal de l'application
docker compose logs -f worker-siren    # résolution SIREN

curl -s http://127.0.0.1:8000/sante/   # {"etat": "ok", "base": true, "redis": true}

# Importer un fichier de leads : aperçu d'abord, toujours.
docker compose exec web python manage.py importer_leads /tmp/leads.csv
docker compose exec web python manage.py importer_leads /tmp/leads.csv --appliquer

# Rejouer les webhooks Meta qui n'ont pas abouti.
docker compose exec web python manage.py rejouer_receptions
docker compose exec web python manage.py rejouer_receptions --appliquer
```

### Quand quelque chose ne va pas

| Symptôme | Où regarder |
|---|---|
| `/sante/` renvoie 503 | `docker compose ps` — `db` ou `redis` est tombé |
| `/admin/` renvoie 500 | `docker compose logs web \| grep -i static` : `collectstatic` n'a pas abouti |
| Boucle de redirection HTTPS | nginx ne transmet pas `X-Forwarded-Proto` (voir le modèle `backoffice.stpl`) |
| Toutes les pages en 400 | `ALLOWED_HOSTS` du `.env` ne contient pas le sous-domaine |
| Leads sans SIREN résolu | `docker compose logs worker-siren` — et vérifier que la file `siren` a bien son worker |
| Webhooks Meta non traités | `/admin/` → *Réceptions de webhooks* : l'état et le message d'erreur y sont |
| `vformations.fr` est tombé | `nginx -t`, puis l'archive `/var/backups/nginx-avant-backoffice-*.tar.gz` |

### Le piège des files Celery

Un worker lancé avec `--queues siren` **ne lit plus la file par défaut**.
La pile déclare donc deux workers, et `tests/test_files_celery.py` vérifie
que toute file routée a bien un consommateur. Ne jamais retirer un worker
sans retirer la règle de routage correspondante : les tâches partiraient
dans Redis sans jamais en sortir, **sans la moindre erreur visible**.

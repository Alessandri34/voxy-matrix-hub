# Première installation du back-office sur le VPS

> À faire **une seule fois**, à la main, en regardant ce qui se passe.
> Les déploiements suivants passent par le workflow `Déployer le back-office`.
>
> ⚠️ **Ce document n'a pas pu être exécuté contre le serveur** depuis la
> session qui l'a écrit : la clé SSH du VPS est dans les secrets GitHub, pas
> ici. Les commandes `docker`, `nginx -t` et la chaîne nginx → gunicorn →
> Django ont été éprouvées en local contre PostgreSQL 17 et Redis 8 réels ;
> les commandes `v-*` d'Hestia, elles, sont écrites d'après sa documentation
> et **restent à confirmer sur le serveur**. D'où le contrôle après chaque
> étape : à la moindre divergence, s'arrêter plutôt que continuer.

---

## Ce qu'il faut savoir avant de commencer

Le VPS fait déjà tourner **HestiaCP avec nginx**, qui sert `vformations.fr`
sur les ports 80 et 443. **Rien de ce qui suit ne doit réclamer ces ports.**
C'est la seule erreur qui ferait tomber le site vitrine.

L'architecture retenue :

```
internet ──▶ nginx (Hestia, 443, certificat Let's Encrypt)
                 │  backoffice.vformations.fr
                 ▼
         127.0.0.1:8000  gunicorn (conteneur web)
                 │
                 ├── PostgreSQL 17   (conteneur db,    volume pgdata)
                 └── Redis 8         (conteneur redis, volume redisdata)

         worker ········ file « celery » : webhooks, envois
         worker-siren ·· file « siren », UN SEUL, cadence de l'API
         beat ·········· alerte des 24 h, toutes les heures
```

---

## 1. L'enregistrement DNS

Chez le registrar du domaine, ajouter :

```
backoffice.vformations.fr.   A   <adresse IP du VPS>
```

**Contrôle** — depuis n'importe où, et avant de continuer :

```bash
dig +short backoffice.vformations.fr
```

Tant que cette commande ne renvoie pas l'IP du VPS, Let's Encrypt ne
délivrera aucun certificat. Compter jusqu'à quelques heures de propagation.

---

## 2. Le domaine dans Hestia

Depuis l'interface Hestia (**Web → Ajouter un domaine**), ou en ligne de
commande sur le serveur :

```bash
v-add-web-domain <utilisateur> backoffice.vformations.fr
v-add-letsencrypt-domain <utilisateur> backoffice.vformations.fr
```

`<utilisateur>` est l'utilisateur Hestia qui porte déjà `vformations.fr` :

```bash
for d in /home/*/; do [ -d "${d}web/vformations.fr" ] && basename "$d"; done
```

**Contrôle** :

```bash
curl -I https://backoffice.vformations.fr
```

Une page Hestia par défaut en HTTPS, sans avertissement de certificat. Si le
certificat manque, s'arrêter : le mandataire ne servira à rien sans lui.

---

## 3. Docker

```bash
command -v docker || curl -fsSL https://get.docker.com | sh
docker compose version
```

---

## 4. Le code et les secrets

```bash
mkdir -p /opt/backoffice
# Le code arrive par le workflow de déploiement. Pour cette première fois :
git clone --depth 1 --branch claude/new-session-nefcch \
  https://github.com/Alessandri34/voxy-matrix-hub.git /tmp/vmh
cp -a /tmp/vmh/backoffice/. /opt/backoffice/
rm -rf /tmp/vmh
```

Puis le fichier des secrets, **qui n'est jamais dans le dépôt** :

```bash
cd /opt/backoffice
cp .env.example .env
chmod 600 .env
python3 -c "import secrets; print(secrets.token_urlsafe(64))"   # SECRET_KEY
openssl rand -base64 36                                          # POSTGRES_PASSWORD
nano .env
```

À remplir, au minimum :

| Variable | Valeur |
|---|---|
| `SECRET_KEY` | la chaîne générée ci-dessus |
| `ALLOWED_HOSTS` | `backoffice.vformations.fr` |
| `CSRF_TRUSTED_ORIGINS` | `https://backoffice.vformations.fr` |
| `POSTGRES_PASSWORD` | la chaîne générée ci-dessus |
| `DATABASE_URL` | `postgres://backoffice:<ce mot de passe>@db:5432/backoffice` |
| `REDIS_URL` | `redis://redis:6379/0` |
| `BACKUP_PASSPHRASE` | une phrase longue, **conservée ailleurs qu'ici** |

🔴 **La phrase de passe des sauvegardes ne doit exister que sur le serveur
et dans votre gestionnaire de mots de passe.** Sans elle, aucune sauvegarde
chiffrée n'est restaurable — et une sauvegarde qu'on ne sait pas restaurer
n'est pas une sauvegarde.

Les trois secrets Meta (`META_APP_SECRET`, `META_VERIFY_TOKEN`,
`META_PAGE_ACCESS_TOKEN`) peuvent rester vides au départ : le webhook
refusera alors toute requête, ce qui est le comportement voulu tant que
l'application Meta n'est pas prête.

---

## 5. Le mandataire nginx

Les fichiers de `/etc/nginx/conf.d/domains/` sont **regénérés par Hestia** :
un fichier édité à la main y est effacé sans prévenir. On passe donc par un
modèle Hestia.

```bash
cd /opt/backoffice/deploiement
cp backoffice.tpl  /usr/local/hestia/data/templates/web/nginx/
cp backoffice.stpl /usr/local/hestia/data/templates/web/nginx/

# Filet : la configuration nginx actuelle, avant toute modification.
tar czf /var/backups/nginx-avant-backoffice-$(date +%Y%m%d-%H%M%S).tar.gz /etc/nginx

v-change-web-domain-tpl <utilisateur> backoffice.vformations.fr backoffice

nginx -t && systemctl reload nginx
```

🔴 **Si `nginx -t` échoue, ne pas recharger.** Remettre le modèle précédent
(`v-change-web-domain-tpl <utilisateur> backoffice.vformations.fr default`)
et recommencer. Un nginx rechargé avec une configuration fautive coupe
**aussi** `vformations.fr`.

**Contrôle** — le mandataire répond, l'application n'est pas encore là :

```bash
curl -I https://backoffice.vformations.fr/sante/   # 502 attendu à ce stade
```

Un 502 est bon signe : nginx mandate bien vers `127.0.0.1:8000`, où rien
n'écoute encore.

---

## 6. Démarrer la pile

```bash
cd /opt/backoffice
docker compose build
docker compose up -d
docker compose ps
```

Les migrations et `collectstatic` tournent **dans le conteneur `web`, avant
gunicorn**. Le premier démarrage prend donc une à deux minutes.

**Contrôle** :

```bash
curl -s http://127.0.0.1:8000/sante/          # {"etat": "ok", ...}
curl -s https://backoffice.vformations.fr/sante/
docker compose ps        # tous « running », web « healthy »
```

⚠️ Si `/admin/` renvoie 500, c'est presque toujours `collectstatic` qui n'a
pas abouti : `docker compose logs web | grep -i static`.

---

## 7. Le premier compte, et sa double authentification

```bash
docker compose exec web python manage.py createsuperuser
```

Puis se connecter sur `https://backoffice.vformations.fr/admin/` et
**enrôler immédiatement un appareil TOTP** (Authy, Google Authenticator,
1Password…) depuis *OTP Devices → TOTP devices*.

🔴 **Tant que l'appareil n'est pas enrôlé, le compte ne peut pas se
connecter** : l'administration exige la double authentification. Garder les
codes de secours (*Static devices*) ailleurs que sur le téléphone qui porte
l'application.

---

## 8. La sauvegarde nocturne

```bash
crontab -e
```

```cron
# Sauvegarde chiffrée du back-office, toutes les nuits à 3 h 17.
# 3 h 17 et non 3 h 00 : les tâches planifiées de la terre entière tombent
# sur les heures rondes.
17 3 * * * cd /opt/backoffice && ./scripts/backup.sh >> /var/log/backoffice-backup.log 2>&1
```

🔴 **Une sauvegarde qu'on n'a jamais restaurée n'est pas une sauvegarde.**
Dans la semaine qui suit la mise en service, restaurer une sauvegarde pour
de vrai — `scripts/restore.sh` demande de taper `REMPLACER` et prend un
dump de sécurité avant d'écraser quoi que ce soit. Tant que ce test n'a pas
été fait, considérer qu'il n'y a pas de sauvegarde.

---

## 9. Le webhook Meta, quand l'application sera prête

1. Dans le tableau de bord Meta : **Webhooks → Page → leadgen**.
2. URL de rappel : `https://backoffice.vformations.fr/integrations/meta/webhook/`
3. Jeton de vérification : la valeur de `META_VERIFY_TOKEN` du `.env`.
4. Abonner la Page au champ `leadgen` — déclarer le webhook dans
   l'application **ne suffit pas**.
5. Permissions `leads_retrieval` et `pages_manage_ads` : elles passent par
   **App Review**. Compter plusieurs jours.

**Contrôle** : le bouton « Test » de Meta envoie un `leadgen_id` fictif. La
réception doit apparaître dans `/admin/` → *Réceptions de webhooks*, avec
`signature_valide = vrai`, et l'appel Graph doit échouer sur un « not found »
— c'est le comportement attendu pour un identifiant de test.

---

## Vérification finale

| | Contrôle |
|---|---|
| ☐ | `dig +short backoffice.vformations.fr` renvoie l'IP du VPS |
| ☐ | `https://backoffice.vformations.fr/sante/` renvoie `{"etat": "ok"}` |
| ☐ | **`https://vformations.fr` répond toujours 200** |
| ☐ | `nginx -t` passe |
| ☐ | `docker compose ps` : 6 services, `web` marqué `healthy` |
| ☐ | Connexion à `/admin/` avec mot de passe **et** code TOTP |
| ☐ | `/pipeline/` affiche le Kanban |
| ☐ | `docker compose logs worker-siren` : le worker écoute la file `siren` |
| ☐ | `.env` en `chmod 600`, phrase de passe conservée ailleurs |
| ☐ | Une sauvegarde a été restaurée pour de vrai |

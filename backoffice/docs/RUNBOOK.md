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

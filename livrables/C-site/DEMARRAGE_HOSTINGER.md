# Par où commencer — mise en ligne sur Hostinger

> **Tout se fait depuis ton navigateur.** Pas besoin de terminal sur ton ordinateur, ni de l'écran « Clés SSH » d'Hostinger.
> **Durée : ~20 minutes**, dont 10 d'attente (propagation DNS).
> **Date : 14 octobre 2026.**

---

## Ce dont j'ai besoin de toi (2 choses seulement)

| # | Information | Où la trouver |
|---|---|---|
| 1 | **Le capital social** de la SAS | Sur ton **Kbis**, ligne « Capital social ». Je n'y ai pas accès : Pappers est bloqué, l'INPI demande une authentification. |
| 2 | **Le régime TVA** | Soit ton n° de TVA intracommunautaire, soit « exonéré » si tu as l'attestation DREETS |

Le reste, je m'en occupe. **Tu n'as pas à me donner de mot de passe ni de clé privée.**

---

## ÉTAPE 1 — Pointer le domaine (à faire en premier, ça prend du temps à se propager)

Panneau Hostinger → **Noms de domaine** → `vformations.fr` → **DNS / Serveurs de noms**

Crée ou modifie ces deux lignes :

| Type | Nom | Valeur |
|---|---|---|
| A | `@` | *l'IP de ton VPS* |
| A | `www` | *l'IP de ton VPS* |

> 💡 **L'IP de ton VPS** s'affiche dans **VPS → Aperçu**, en haut. C'est une suite du type `72.60.XXX.XXX`.

---

## ÉTAPE 2 — Préparer le serveur (console du navigateur)

Panneau Hostinger → **VPS** → bouton **Console Web** (en haut à droite de ton écran actuel).

Une console noire s'ouvre dans le navigateur. **Colle ce bloc entier**, puis Entrée :

```bash
apt update && apt install -y nginx rsync && systemctl enable --now nginx
mkdir -p /var/www/vformations.fr
cat > /etc/nginx/sites-available/vformations.fr <<'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name vformations.fr www.vformations.fr;
    root /var/www/vformations.fr;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }
    location ~* \.(jpg|jpeg|png|svg|webp|ico)$ { expires 30d; add_header Cache-Control "public, immutable"; }
    gzip on; gzip_types text/css text/html application/javascript image/svg+xml; gzip_min_length 1024;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
EOF
ln -sf /etc/nginx/sites-available/vformations.fr /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
ufw allow OpenSSH && ufw allow 'Nginx Full' && ufw --force enable
echo "=== SERVEUR PRET ==="
```

---

## ÉTAPE 3 — Créer la clé de déploiement (même console)

Colle ce second bloc :

```bash
ssh-keygen -t ed25519 -f /root/.ssh/deploy_vformations -N "" -C "github-actions-deploy"
cat /root/.ssh/deploy_vformations.pub >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
echo ""
echo "=============== COPIE TOUT CE QUI SUIT ==============="
cat /root/.ssh/deploy_vformations
echo "=============== JUSQU'ICI ==============="
```

La console affiche un bloc qui commence par `-----BEGIN OPENSSH PRIVATE KEY-----` et finit par `-----END OPENSSH PRIVATE KEY-----`.

**Sélectionne-le et copie-le** (y compris les deux lignes `BEGIN` et `END`).

> ⛔ **Ne me colle jamais cette clé dans la conversation.** Elle va directement dans GitHub à l'étape suivante.

---

## ÉTAPE 4 — Enregistrer les secrets sur GitHub

Va sur `https://github.com/Alessandri34/voxy-matrix-hub` → **Settings** → **Secrets and variables** → **Actions** → bouton **New repository secret**.

Crée **trois** secrets :

| Nom du secret | Valeur |
|---|---|
| `VPS_SSH_KEY` | Le bloc `-----BEGIN…END-----` copié à l'étape 3 |
| `VPS_HOST` | L'IP de ton VPS |
| `VPS_USER` | `root` |

> 🔒 Une fois enregistrés, ces secrets sont chiffrés : plus personne ne peut les relire, ni toi, ni moi. GitHub les déchiffre seulement au moment du déploiement.

---

## ÉTAPE 5 — Me donner les 2 informations légales

Écris-moi simplement :
> « Capital social : X € — TVA : [le numéro] » *(ou « exonéré »)*

Je corrige les mentions légales et je pousse.

---

## ÉTAPE 6 — Lancer le déploiement

Sur GitHub → onglet **Actions** → **Déployer le site VFormations** → bouton **Run workflow**.

Le site part sur ton VPS. ⏱️ Environ 1 minute.

> 🛡️ **Sécurité intégrée :** le déploiement **refuse de partir** tant qu'il reste un champ légal à compléter dans les mentions. C'est voulu — on ne publie pas un site d'organisme certifié avec des trous.

---

## ÉTAPE 7 — Activer le HTTPS (une fois le DNS propagé)

Vérifie d'abord que le domaine pointe bien : ouvre `http://vformations.fr` → le site doit s'afficher (sans cadenas).

Puis, dans la **Console Web** :

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d vformations.fr -d www.vformations.fr --agree-tos -m contact@vformations.fr --redirect --non-interactive
```

Le certificat s'installe et se renouvellera tout seul. Vérifie : `https://vformations.fr` avec le cadenas.

> 🔴 **Sans HTTPS, le formulaire collecte des données personnelles en clair.** Non négociable.

---

## Et après ?

À chaque modification du site, je pousse sur GitHub et tu cliques **Run workflow**. C'est tout.

Quand le site sera stabilisé, on passera en **déploiement automatique** : je pousse, ça part tout seul, sans clic.

---

## ⚠️ Reste à régler avant d'envoyer du trafic

Le **formulaire de contact n'envoie rien** (`FORM_ENDPOINT` est vide — on s'était arrêté sur l'erreur de copier-coller du script Google). Il affiche une confirmation et perd la demande.

Le déploiement te le signalera par un avertissement. Deux options :
1. Finir le branchement Google Apps Script — 10 minutes (`formulaire/GUIDE_BRANCHEMENT.md`)
2. Masquer le formulaire en attendant, et ne laisser que l'e-mail et le téléphone

---

## Si quelque chose bloque

Copie-moi le message d'erreur. Les pannes les plus fréquentes :

| Symptôme | Cause probable |
|---|---|
| Le workflow échoue sur « Contrôle légal » | Il reste un `[à compléter]` — c'est le garde-fou qui fonctionne |
| `Permission denied (publickey)` | La clé a été mal copiée — il faut les lignes `BEGIN` et `END` incluses |
| Le site ne s'affiche pas | DNS pas encore propagé — attends, puis `ping vformations.fr` |
| Certbot échoue | Le DNS ne pointe pas encore sur le VPS, ou le port 80 est fermé |

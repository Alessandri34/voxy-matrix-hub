# Mise en ligne du site sur le VPS Hostinger

> **Paquet prêt :** `livrables/C-site/dist/` — `index.html` + `img/` (548 Ko).
> **Domaine :** vformations.fr
> **Date : 14 octobre 2026.**

---

## 🔴 À FAIRE AVANT DE PUBLIER — 2 blocages légaux

Les mentions légales d'une SAS **doivent** comporter le capital social. Deux champs restent à remplir dans `dist/index.html` :

| Ligne | Texte actuel | Ce qu'il faut |
|---|---|---|
| ~1928 | `au capital social de [montant à compléter] €` | **Le montant exact** (il est sur ton Kbis, une ligne) |
| ~1930 | `TVA intracommunautaire : FR31 103 940 227 [à confirmer]` | **Soit** le n° de TVA confirmé, **soit** la mention d'exonération seule (art. 261-4-4°a du CGI) si l'attestation DREETS est obtenue |

> ⚠️ Publier avec `[montant à compléter]` visible est une non-conformité **et** un signal d'amateurisme sur un site d'organisme certifié.

**Une fois les valeurs connues, deux remplacements suffisent** (voir §5).

---

## 1. Pointer le domaine vers le VPS

Dans le panneau Hostinger → **Domaines** → **DNS / Serveurs de noms** pour `vformations.fr` :

| Type | Nom | Valeur | TTL |
|---|---|---|---|
| A | `@` | *l'IP de ton VPS* | 3600 |
| A | `www` | *l'IP de ton VPS* | 3600 |

> Propagation : de quelques minutes à quelques heures. Vérifie avec `ping vformations.fr`.

---

## 2. Préparer le serveur (une seule fois)

Connecte-toi en SSH (depuis ton ordinateur, pas depuis cette session) :

```bash
ssh root@TON_IP_VPS
```

Puis :

```bash
apt update && apt upgrade -y
apt install -y nginx
systemctl enable --now nginx
```

Vérifie : ouvre `http://TON_IP_VPS` dans un navigateur → la page d'accueil nginx doit s'afficher.

### Sécuriser l'accès (fortement recommandé)
```bash
# Pare-feu : n'ouvrir que SSH, HTTP et HTTPS
ufw allow OpenSSH && ufw allow 'Nginx Full' && ufw --force enable

# Authentification par clé plutôt que par mot de passe
# (depuis TON ordinateur, avant de désactiver le mot de passe)
ssh-copy-id root@TON_IP_VPS
```
Puis dans `/etc/ssh/sshd_config` : `PasswordAuthentication no`, et `systemctl restart ssh`.

> 💡 C'est ce qui rend inutile le mot de passe en clair — et c'est la bonne pratique sur un VPS exposé.

---

## 3. Envoyer les fichiers

**Depuis ton ordinateur**, dans le dossier qui contient `dist/` :

```bash
# Créer le dossier cible sur le serveur
ssh root@TON_IP_VPS "mkdir -p /var/www/vformations.fr"

# Envoyer le contenu du paquet
rsync -avz --delete dist/ root@TON_IP_VPS:/var/www/vformations.fr/

# Droits
ssh root@TON_IP_VPS "chown -R www-data:www-data /var/www/vformations.fr && chmod -R 755 /var/www/vformations.fr"
```

> **Sans ligne de commande :** utilise **FileZilla** (protocole SFTP, port 22, utilisateur `root`) et dépose le contenu de `dist/` dans `/var/www/vformations.fr/`.

---

## 4. Configurer nginx

```bash
nano /etc/nginx/sites-available/vformations.fr
```

Colle :

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name vformations.fr www.vformations.fr;
    root /var/www/vformations.fr;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache des images et du logo
    location ~* \.(jpg|jpeg|png|svg|webp|ico)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Compression
    gzip on;
    gzip_types text/css text/html application/javascript image/svg+xml;
    gzip_min_length 1024;

    # En-têtes de sécurité
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

Active et recharge :
```bash
ln -s /etc/nginx/sites-available/vformations.fr /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

---

## 5. Activer le HTTPS (obligatoire)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d vformations.fr -d www.vformations.fr --agree-tos -m contact@vformations.fr --redirect
```

Certbot modifie la configuration et installe le renouvellement automatique. Vérifie : `certbot renew --dry-run`.

> 🔴 **Sans HTTPS, le formulaire de contact collecte des données personnelles en clair.** Non négociable.

---

## 6. Compléter les 2 champs légaux

Une fois les valeurs connues, sur le serveur :

```bash
cd /var/www/vformations.fr

# Capital social — remplace 10000 par ton montant réel
sed -i 's/\[montant à compléter\]/10 000/' index.html

# TVA — si exonération (supprime le numéro, garde la mention d'exonération)
sed -i 's|TVA intracommunautaire : FR31&nbsp;103&nbsp;940&nbsp;227 \[à confirmer\] — ou exonération|Exonération|' index.html
```

> Plus simple : dis-moi les valeurs, je corrige à la source et tu refais le `rsync` du §3.

---

## 7. Vérifications après mise en ligne

- [ ] `https://vformations.fr` s'affiche, cadenas vert
- [ ] `http://` redirige bien vers `https://`
- [ ] `www.vformations.fr` fonctionne aussi
- [ ] Le logo et les 6 photos du Mag se chargent
- [ ] La navigation entre pages fonctionne (`#formations`, `#contact`, `#mentions`…)
- [ ] Affichage correct sur téléphone
- [ ] **Aucun `[à compléter]` visible** dans les mentions légales
- [ ] Le formulaire de contact — ⚠️ **voir ci-dessous**

---

## 8. ⚠️ Le formulaire de contact n'est pas encore branché

`FORM_ENDPOINT` est vide dans `index.html` : **le formulaire affiche une confirmation mais n'envoie rien.** Les demandes sont perdues.

Deux options avant d'envoyer du trafic :
1. **Terminer le branchement Google Apps Script** (`formulaire/GUIDE_BRANCHEMENT.md`) — on s'était arrêté sur une erreur de copier-coller, c'est 10 minutes.
2. **En attendant**, masquer le formulaire et ne laisser que l'e-mail et le téléphone — mieux vaut pas de formulaire qu'un formulaire qui perd les demandes.

---

## 9. Mettre à jour le site plus tard

```bash
rsync -avz --delete dist/ root@TON_IP_VPS:/var/www/vformations.fr/
```

Une seule commande. Le `--delete` supprime côté serveur les fichiers retirés du paquet.

---

## 10. Après la mise en ligne

- [ ] Créer la **fiche Google Business Profile** (levier local n°1, gratuit — voir `SEO_strategie.md`)
- [ ] Déclarer le site dans la **Search Console**
- [ ] Installer une **bannière de consentement** avant tout pixel publicitaire (`D3` §1.4)
- [ ] Mettre en place une **sauvegarde** du VPS (snapshot Hostinger)

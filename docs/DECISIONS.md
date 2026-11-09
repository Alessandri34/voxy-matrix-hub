# Décisions

Une ligne par décision, avec sa raison. Ce qui n'est pas écrit ici se
re-discutera dans trois mois.

## 2026-11-09 — Django 5.2.19, et non 6.1.3
Le master prompt impose « la dernière LTS ». Le cycle LTS de Django est en
x.2 : 4.2, 5.2, puis 6.2. La 6.1.3 est plus récente mais n'est pas LTS, donc
pas de correctifs de sécurité à long terme. **5.2.19**, dernier correctif de la
branche LTS.

## 2026-11-09 — `django-otp` pour la double authentification
`OTPAdminSite` refuse la session tant qu'aucun appareil n'est vérifié : le
critère de sortie est tenu par la bibliothèque, pas par du code à nous.
Alternative écartée : `django-two-factor-auth`, qui apporte des vues de
connexion dont la phase 0 n'a pas besoin, et deux dépendances de plus.

## 2026-11-09 — Le rôle est un champ de l'utilisateur, pas un groupe seul
Cinq rôles fixés par le PRD, stables. Un champ se lit sans jointure, se filtre
en base, et un test l'affirme en une ligne. Les permissions fines restent
celles de Django : **le rôle décide de ce qu'on voit, la permission de ce qu'on
peut faire**. La table `ACCES` de `apps/accounts/models.py` est la seule source
de vérité ; aucune vue ne redéfinit la règle.

## 2026-11-09 — Fichiers statiques par WhiteNoise, pas par un volume partagé
Caddy ne sert que de terminaison TLS et de proxy. Un volume partagé entre
Django et Caddy crée deux chemins de vérité à resynchroniser à chaque
déploiement.

## 2026-11-09 — Les migrations échappent à la règle de longueur de ligne
Django les écrit et les réécrira. Les erreurs réelles (`F`) restent vérifiées.

## 2026-11-09 — Bloc financement gelé
Trois écarts entre le PRD et les paramètres vérifiés du dépôt documentaire, dont
l'aiguillage CMA / FAFCEA transverse qui décide du routage de chaque dossier
artisan. Détail dans `PRD.md`. **La phase 3 ne démarre pas avant l'arbitrage.**

## 2026-11-09 — ⚠️ Le dépôt hôte est public
`voxy-matrix-hub` est public. La phase 0 ne contient ni donnée personnelle ni
secret (`.env` est ignoré par Git), donc rien n'est exposé aujourd'hui. **Mais
la phase 1 introduit des données de prospects.** À régler avant : dépôt privé,
ou déplacement du back-office dans son propre dépôt privé.

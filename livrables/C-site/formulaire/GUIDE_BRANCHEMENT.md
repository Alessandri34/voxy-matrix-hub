# Brancher les formulaires du site sur Google Sheet + e-mail

> Les deux formulaires du site (**Contact** et **Diagnostic**) envoient chaque demande dans un **Google Sheet** et déclenchent un **e-mail de notification** vers `contact@vformations.fr`.
> Solution **gratuite, sans serveur** : Google Apps Script. Tout s'exécute dans **ton** compte Google — aucune clé secrète dans le code du site.

**Important :** connecte-toi avec le compte Google qui peut relever `contact@vformations.fr` (ou qui a cette adresse en alias), pour recevoir les notifications là où tu les attends.

---

## Étape 1 — Créer le Google Sheet
1. Va sur [sheets.google.com](https://sheets.google.com) → **Créer un classeur vide**.
2. Nomme-le par ex. **« VFormations — Demandes site »**.
3. Laisse-le vide : l'onglet `Demandes` et la ligne d'en-têtes seront créés automatiquement au 1er envoi.

## Étape 2 — Ouvrir l'éditeur de script
1. Dans ce Sheet : menu **Extensions → Apps Script**.
   *(Créer le script ainsi le « lie » au Sheet : pas besoin de renseigner `SHEET_ID`.)*
2. Supprime le contenu de `Code.gs` et **colle tout le contenu du fichier `Code.gs`** (même dossier que ce guide).
3. (Optionnel) Vérifie en haut du fichier :
   - `NOTIFY_EMAIL` = `contact@vformations.fr` ✅ (déjà réglé)
   - `SHEET_NAME`   = `Demandes`
4. **Enregistrer** (icône disquette).

## Étape 3 — Déployer en application web
1. En haut à droite : **Déployer → Nouveau déploiement**.
2. Roue crantée **⚙ → Application Web**.
3. Réglages :
   - **Description** : `VFormations form`
   - **Exécuter en tant que** : **Moi** (ton compte)
   - **Qui a accès** : **Tout le monde** *(obligatoire pour que le site public puisse envoyer ; ne publie aucune donnée, le script ne fait qu'écrire)*.
4. **Déployer** → Google demande une **autorisation** :
   - « Autoriser » → choisis ton compte → *« Google n'a pas validé cette application »* → **Paramètres avancés → Accéder à … (non sécurisé)** → **Autoriser**.
   - *(Normal : c'est TON propre script. Il demande l'accès au Sheet et à l'envoi d'e-mail.)*
5. Copie l'**URL de l'application Web** affichée. Elle ressemble à :
   `https://script.google.com/macros/s/AKfyc.........../exec`

## Étape 4 — Brancher le site
1. Ouvre `livrables/C-site/site.html`.
2. Cherche la ligne (tout en haut du `<script>` principal) :
   ```js
   var FORM_ENDPOINT = '';
   ```
3. Colle ton URL entre les guillemets :
   ```js
   var FORM_ENDPOINT = 'https://script.google.com/macros/s/AKfyc.........../exec';
   ```
4. Enregistre. **C'est tout** — les deux formulaires envoient désormais réellement.
   *(Tant que `FORM_ENDPOINT` est vide, les formulaires restent en mode démo et n'envoient rien.)*

## Étape 5 — Tester
1. Ouvre le site, va sur **Contact**, remplis et envoie.
2. Vérifie :
   - une **nouvelle ligne** dans l'onglet `Demandes` du Sheet ;
   - un **e-mail** sur `contact@vformations.fr` (objet `[VFormations] Message de contact — …`).
3. Teste aussi la page **Diagnostic** (colonne « Formulaire » = `diagnostic`).

> Astuce : pour vérifier que le déploiement répond, ouvre l'URL `.../exec` dans le navigateur → tu dois voir `{"ok":true,"service":"VFormations form endpoint"}`.

---

## Comment ça marche (résumé technique)
- Le site envoie les champs en **POST `application/x-www-form-urlencoded`** (requête « simple » → pas de blocage CORS).
- `doPost()` écrit une ligne (`Date, Formulaire, Nom, E-mail, Téléphone, Activité, Sujet, Besoin, Financeur, Message, Page`) puis envoie l'e-mail avec **`replyTo` = e-mail du visiteur** → tu réponds en un clic.
- Un champ **pot de miel** (`_gotcha`, invisible) filtre les robots : s'il est rempli, la demande est ignorée.
- `replyTo` facilite la réponse ; l'expéditeur de la notification reste ton compte Google.

## Limites & bon à savoir
- **Quota e-mail** Apps Script : ~100 destinataires/jour (compte gratuit) / ~1 500 (Workspace) — largement suffisant pour des demandes de contact.
- Si tu modifies `Code.gs` plus tard : **Déployer → Gérer les déploiements → ✏️ → Nouvelle version**, l'URL `/exec` **reste la même** (rien à changer sur le site).
- L'URL `/exec` est **publique par nature** (elle est dans le HTML, c'est normal) : elle ne donne accès à rien, elle ne fait qu'ajouter une ligne + notifier. Ce **n'est pas** un secret à mettre dans `.env`.
- Pour une protection anti-spam renforcée plus tard : ajout d'un reCAPTCHA v3 ou passage à un service dédié (Formspree / Web3Forms).

## Alternatives (si tu préfères)
- **Formspree / Web3Forms** : branchement encore plus simple (1 attribut `action`), gratuit jusqu'à un quota, e-mail inclus — mais les données vont chez un tiers (pas dans ton Sheet).
- **Google Forms** : zéro code, mais le formulaire n'a pas le design du site (iframe).

> Dis-moi quand ton URL est prête : je peux la coller dans `site.html` et republier pour toi.

# Brancher les formulaires sur ta feuille Google

> **Feuille cible :** [VFormations — Demandes](https://docs.google.com/spreadsheets/d/1Iij8fCiqW4Wv2R_Vn_jlHJd8jm_UEIof3pOGg8c7QSQ/edit) — déjà renseignée dans le script.
> **Durée : 5 minutes.** Trois étapes, puis tu m'envoies une URL.
> **Date : 14 octobre 2026.**

---

## Pourquoi c'est toi qui dois le faire
Le script s'exécute **dans ton compte Google** : c'est lui qui écrit dans ta feuille et envoie les e-mails. Je n'ai aucun accès Google dans cette session, et c'est d'ailleurs préférable — aucun identifiant ne transite par la conversation.

> ⚠️ Connecte-toi avec le compte qui relève **contact@vformations.fr** (ou qui a cette adresse en alias), sinon les notifications partiront ailleurs.

---

## Étape 1 — Créer le script

1. Ouvre [ta feuille](https://docs.google.com/spreadsheets/d/1Iij8fCiqW4Wv2R_Vn_jlHJd8jm_UEIof3pOGg8c7QSQ/edit)
2. Menu **Extensions → Apps Script**
3. **Ctrl+A** dans l'éditeur pour tout sélectionner, **Suppr**
4. Colle **l'intégralité** du fichier `Code.gs` (il commence par `/**` et finit par `}`)
5. 💾 **Enregistrer**

> L'identifiant de ta feuille est déjà dans le script : rien à modifier.

---

## Étape 2 — Déployer

1. **Déployer → Nouveau déploiement**
2. Roue crantée ⚙ → **Application Web**
3. Réglages — les deux comptent :
   - **Exécuter en tant que : Moi**
   - **Qui a accès : Tout le monde** *(indispensable pour qu'un visiteur du site puisse écrire ; le script n'expose aucune donnée, il ne fait qu'ajouter une ligne)*
4. **Déployer** → Google demande une autorisation :
   - « Autoriser » → ton compte → *« Google n'a pas validé cette application »* → **Paramètres avancés** → **Accéder à … (non sécurisé)** → **Autoriser**
   - *C'est normal : c'est **ton** script. Il demande l'accès à ta feuille et le droit d'envoyer des e-mails.*
5. **Copie l'URL** affichée. Elle ressemble à :
   `https://script.google.com/macros/s/AKfyc.............../exec`

---

## Étape 3 — Me l'envoyer

Colle-moi simplement cette URL dans la conversation. Je la pose dans le site, je redéploie, et je teste un envoi réel de bout en bout.

> Tu peux aussi la poser toi-même : dans `livrables/C-site/site.html`, cherche `var FORM_ENDPOINT = '';` et mets l'URL entre les guillemets. Mais laisse-moi vérifier derrière.

---

## Ce qui sera enregistré

Une ligne par demande, dans l'onglet **`Demandes`** (créé automatiquement au premier envoi) :

| Colonne | Contenu |
|---|---|
| Date | Horodatage de la demande |
| Formulaire | `contact` ou `diagnostic` |
| Nom & prénom · E-mail · Téléphone · Activité | Champs saisis |
| Sujet · Besoin · Financeur · Message | Selon le formulaire |
| **Consentement RGPD** | `oui` — preuve que la case a été cochée |
| Page | D'où venait le visiteur |

Et un e-mail sur **contact@vformations.fr**, avec **réponse directe au visiteur** : tu cliques « Répondre », ça part chez lui.

> 🔒 **La colonne Consentement n'est pas cosmétique.** Elle prouve que le visiteur a accepté d'être recontacté. C'est ce qui rend ta relance téléphonique défendable, et c'est exigé par ta politique de confidentialité.

---

## Vérification (je la ferai avec toi)

1. Formulaire de contact du site → envoyer
2. Une ligne apparaît dans la feuille
3. Un e-mail arrive sur contact@vformations.fr
4. Même test depuis la page **Diagnostic** (colonne Formulaire = `diagnostic`)

> Test rapide du déploiement : ouvre l'URL `/exec` dans ton navigateur. Tu dois voir
> `{"ok":true,"service":"VFormations form endpoint"}`.

---

## Bon à savoir

- **Quota d'e-mails** : ~100/jour en compte gratuit, ~1 500 en Workspace. Large pour des demandes de contact.
- **Modifier le script plus tard** : *Déployer → Gérer les déploiements → ✏️ → Nouvelle version*. **L'URL `/exec` ne change pas**, rien à refaire côté site.
- **L'URL `/exec` est publique par nature** (elle figure dans le code du site, c'est inévitable). Elle ne donne accès à rien : elle ajoute une ligne et notifie. Ce **n'est pas** un secret.
- **Anti-spam** : un champ invisible piège les robots ; leurs envois sont ignorés sans écrire dans la feuille.

---

## Si ça coince

| Symptôme | Cause |
|---|---|
| `SyntaxError: Illegal return statement` | Copier-coller incomplet. Ctrl+A, Suppr, recolle **tout** le fichier. |
| Erreur en cliquant ▶ Exécuter | Normal : `doPost` attend une vraie soumission. Pour un test manuel, choisis `doGet`. |
| Rien n'arrive dans la feuille | Vérifie « Qui a accès : **Tout le monde** » dans le déploiement. |
| Pas d'e-mail | Regarde les indésirables, et confirme que le compte Google relève bien contact@vformations.fr. |

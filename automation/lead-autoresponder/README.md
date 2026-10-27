# Réponse automatique aux prospects Meta

Quand quelqu'un remplit le formulaire instantané de la publicité, ce robot :

1. le range dans un tableau Google Sheet ;
2. lui envoie un mail d'accusé de réception ;
3. prévient l'équipe qu'il faut le rappeler.

Il vérifie Meta toutes les 5 minutes. Il tourne dans votre compte Google, gratuitement, sans serveur à entretenir.

## Avant de commencer

| Il vous faut | Où le trouver |
|---|---|
| Un compte Google | celui de l'entreprise, de préférence |
| Le jeton Meta de lecture des prospects | voir « Le jeton » plus bas |
| 20 minutes | une seule fois |

L'identifiant de la Page (`765749889955901`) est déjà dans le code.

## Installation, pas à pas

1. **Créez un Google Sheet vide**, nommé par exemple « Prospects VFormations ».
2. Menu **Extensions > Apps Script**. Supprimez le contenu du fichier `Code.gs`, puis collez à la place le contenu du fichier `Code.gs` de ce dossier.
3. **Remplissez le bloc `CONFIG`** tout en haut :
   - `OWNER_EMAIL` : votre adresse (alertes en cas de problème) ;
   - `TEAM_EMAILS` : les adresses qui doivent rappeler les prospects, par exemple `['alternante@…']` ;
   - `REPLY_TO` : l'adresse qui reçoit les réponses des prospects ;
   - `COMPANY_LEGAL` : raison sociale et adresse, qui s'affichent en bas du mail ;
   - `BOOKING_URL` : lien de prise de rendez-vous, si vous en avez un (sinon laissez vide) ;
   - **laissez `DRY_RUN: true`** pour l'instant.
4. Roue crantée à gauche, **Paramètres du projet**, puis **Propriétés du script > Ajouter une propriété** : nom `META_TOKEN`, valeur = le jeton Meta. Le jeton ne se colle jamais dans le code.
5. Dans l'éditeur, choisissez la fonction **`initialiser`** et cliquez **Exécuter**. Google demande des autorisations : acceptez. Cette étape prépare le tableau, fixe le point de départ et installe le minuteur.
6. *(Facultatif)* Lancez **`importerHistorique`** : les prospects des 30 derniers jours se rangent dans le tableau, **sans recevoir de mail**.
7. Lancez **`envoyerTest`** : vous recevez le mail exact qu'un prospect recevrait. Relisez-le.
8. Attendez un vrai prospect, ou utilisez l'outil de test de Meta (« Lead Ads Testing Tool »). Je n'ai pas pu vérifier ici que ses prospects de test apparaissent dans ce flux. Dans les 5 minutes, une ligne doit apparaître dans l'onglet `Prospects`, avec la mention `simulation (aucun mail envoyé)`, et l'équipe reçoit l'alerte.
9. Quand tout est bon, passez **`DRY_RUN` à `false`** et enregistrez. À partir de là, les mails partent vraiment.

## Ce que reçoit le prospect

> **Votre demande a bien été reçue**
>
> Bonjour Camille,
>
> Merci d'avoir rempli notre formulaire. Nous avons bien reçu votre demande.
>
> Prochaine étape : un membre de l'équipe vous appelle dans un délai maximum de 2 jours ouvrés pour comprendre votre activité et voir si nous pouvons vous aider.
>
> Pendant cet échange, nous parlerons de votre activité, de la façon dont vos clients vous trouvent aujourd'hui, et de ce qui peut être pris en charge selon votre statut. Le montant exact qui resterait à votre charge vous est toujours annoncé par écrit, sur le devis, avant tout engagement.
>
> À très vite, VFormations
>
> *Vous recevez ce message parce que vous avez rempli un formulaire sur Facebook ou Instagram. Pour ne plus être contacté, répondez simplement « STOP ».*

**Le délai annoncé doit être tenable.** Le formulaire affiche déjà « sous 24-48 h », donc le mail dit « 2 jours ouvrés ». Si une seule personne rappelle 3 jours par semaine, ne le réduisez pas dans `CALLBACK_PROMISE` : une promesse non tenue est exactement ce qu'un contrôleur sous identité d'emprunt peut relever.

## Les garde-fous intégrés

- **Aucun mail aux anciens prospects.** Au démarrage, seuls ceux qui arrivent après l'installation reçoivent une réponse.
- **Aucun doublon.** Un prospect déjà rangé n'est jamais traité deux fois.
- **Texte contrôlé.** Avant chaque envoi, le mail est vérifié contre la liste des expressions interdites (gratuit, 100 %, sans reste à charge, emploi, reconversion, diplôme, garanti, Qualiopi…). Si quelqu'un en ajoute une par erreur, **aucun mail ne part** et vous êtes prévenu.
- **Désinscription.** Les adresses écrites dans l'onglet `Désabonnés` ne reçoivent rien. Quand quelqu'un répond « STOP », **recopiez son adresse dans cet onglet** : ce n'est pas encore automatique.
- **Saisies neutralisées.** Ce que tape un prospect dans le formulaire ne peut pas s'exécuter comme une formule dans le tableau.
- **Jeton protégé.** Il voyage dans l'en-tête des requêtes, jamais dans une adresse, et n'apparaît dans aucun journal ni aucun mail.
- **Pas plus d'une alerte technique toutes les 6 heures.**

Le mot **Qualiopi** est volontairement interdit dans le mail tant que la certification n'est pas obtenue. Une fois qu'elle l'est, retirez la ligne correspondante de la liste `BANNED` dans `Code.gs`.

## Le jeton Meta

Le robot a besoin d'un **jeton d'utilisateur système** avec, au minimum :

- `leads_retrieval`
- `pages_show_list`
- `pages_read_engagement`

et la Page VFormations attribuée à cet utilisateur avec le droit **« Gérer les prospects »** (c'est déjà le cas).

Je n'ai testé qu'avec le jeton actuel, qui possède bien plus de droits que nécessaire. Ces trois droits sont ceux que Meta documente pour la lecture des prospects : vérifiez qu'ils suffisent en mode simulation avant de révoquer l'ancien jeton.

**Ne donnez pas à ce robot un jeton qui peut modifier les publicités ou publier.** Il ne fait que lire.

## En cas de problème

| Ce que vous voyez | Ce que ça veut dire |
|---|---|
| Mail « Le robot à prospects a rencontré une erreur », code **190** | Le jeton est invalide ou révoqué. En générer un nouveau, le recoller dans `META_TOKEN`. |
| Même mail, message « jeton de Page » | La Page n'est pas attribuée à l'utilisateur système, ou sans le droit « Gérer les prospects ». |
| Mail « Mail automatique bloqué » | Une expression interdite se trouve dans le texte du mail. Elle est nommée dans le message. |
| `reponse_auto` = `quota Google atteint` | Plus de 100 mails par jour avec un compte Gmail gratuit. Rare à ce volume. |
| `reponse_auto` = `pas d'e-mail valide` | Le prospect n'a pas donné d'adresse utilisable : rappel par téléphone uniquement. |
| Rien ne se passe | Vérifiez dans Apps Script > **Déclencheurs** qu'un minuteur `pollLeads` existe. Sinon relancez `initialiser`. |

## Ce que ce robot ne fait pas

- Il n'envoie **pas de SMS ni de message WhatsApp** : ça demande un prestataire payant et un consentement explicite.
- Il ne relance **pas** les prospects qui ne répondent pas. C'est le rôle du futur module de nurturing : voir `agents/handoff/NURTURING.md`.
- Il ne **qualifie** pas : il n'y a pas de question sur le statut de non-salarié dans le formulaire actuel (voir le brief de nurturing).

## Vérifier le code

```
node test.js
```

Dix-sept tests simulent Google et Meta : première exécution, doublons, mode simulation, désabonnement, panne de Meta, jeton jamais exposé. Ils ont été vérifiés en cassant volontairement le code pour s'assurer qu'ils échouent bien.

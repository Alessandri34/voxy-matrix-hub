# Agents : mode d'emploi

Ce dossier explique aux agents (sessions Claude, scripts) comment travailler sur le compte publicitaire et les prospects de VFormations. À lire avant toute requête vers Meta.

## Règle n°1 : aucun secret dans ce dépôt

Aucun jeton, mot de passe ni clé n'est écrit dans un fichier du dépôt, même privé. Les secrets vivent dans les **secrets de l'environnement cloud** (réglages de l'environnement > Modifier > secrets réseau, ou variable d'environnement). Une session lit ses secrets à son démarrage : après un ajout, il faut ouvrir une nouvelle session.

Un fichier `.gitignore` bloque les noms de fichiers les plus courants (`.env`, `*.token`, `*.secret`). Il ne remplace pas la vigilance : relisez le `git diff` avant chaque commit.

## Les secrets attendus

Seuls les **noms** sont écrits ici. Les valeurs n'existent qu'à l'endroit indiqué.

| Nom | Sert à | Droits Meta à lui donner | Où il vit | Qui l'utilise |
|---|---|---|---|---|
| `META_ADS_READ_TOKEN` | Auditer les publicités : dépenses, créas, placements, âges | `ads_read` seulement | Secrets de l'environnement cloud | Agents d'analyse |
| `META_LEADS_TOKEN` | Lire les prospects du formulaire | `leads_retrieval`, `pages_show_list`, `pages_read_engagement` | Secrets de l'environnement cloud, et propriété de script `META_TOKEN` du robot Apps Script | Robot de réponse, agent de nurturing |

**Il n'existe volontairement aucun jeton d'écriture** (`ads_management`). Si un agent doit un jour modifier une publicité, le gérant crée un jeton dédié, à durée courte, pour cette seule opération, puis le révoque.

## Identifiants qui ne sont PAS des secrets

| Quoi | Valeur |
|---|---|
| Compte publicitaire | `act_668163372302061` (Voxy.IA, EUR, Europe/Paris) |
| Page Facebook | `765749889955901` (VFormations) |
| Formulaire instantané en ligne | `1745675750027565` |
| Application Meta | `1129728139639524` (« Vformation reporting ADS ») |
| Version de l'API | `v21.0` |

## Comment lire un secret

- Le lire dans la variable d'environnement. Ne jamais l'afficher, ne jamais l'écrire dans un fichier, un message de commit, un journal ou un retour de commande.
- Le passer dans l'en-tête `Authorization: Bearer …`, **jamais dans l'adresse** : une adresse finit dans les journaux.
- **Lire les formulaires et les prospects exige un jeton de Page**, pas celui de l'utilisateur système. On le dérive : `GET /{page_id}?fields=access_token` avec le jeton système. Le robot Apps Script le fait déjà.
- Ne jamais copier de données personnelles de prospects (nom, e-mail, téléphone) dans le dépôt ni dans une conversation. Compter, agréger, oui. Recopier, non.

## Ce que Meta bloque aujourd'hui

**Toute écriture par l'API** (mettre en pause une publicité, changer un budget) est refusée tant qu'un administrateur n'a pas accepté la **politique de non-discrimination** de Meta. Erreur renvoyée : code 100, sous-code `2859024`, « Certification requise ». Elle se règle en deux clics dans Paramètres d'entreprise > Utilisateur(ice)s système. La lecture, elle, fonctionne.

## Règles de conduite

1. **Lecture seule par défaut.** Toute écriture sur le compte publicitaire demande l'accord explicite du gérant, action par action.
2. **Une promesse faite à un prospect doit être tenable telle quelle.** Un agent de contrôle peut se faire passer pour un prospect (loi du 25 juin 2026, art. 44).
3. **Vocabulaire interdit** dans toute communication : gratuit, 100 %, sans reste à charge, formation offerte, garanti, emploi, employabilité, reconversion, diplôme, RNCP, titre certifiant, carrière, décrocher un poste, machine à cash. Et pas de « Qualiopi » tant que la certification n'est pas obtenue.
4. **Le numéro de déclaration d'activité**, s'il est cité, s'écrit toujours avec la phrase « Cet enregistrement ne vaut pas agrément de l'État ».

## Chantiers

| Chantier | État | Où |
|---|---|---|
| Réponse automatique au formulaire | Construit et testé. À installer par le gérant. | `automation/lead-autoresponder/` |
| Nurturing des prospects | Non démarré. Brief prêt. | `agents/handoff/NURTURING.md` |
| Audit hebdomadaire des publicités | Manuel pour l'instant | À faire une fois `META_ADS_READ_TOKEN` en place |

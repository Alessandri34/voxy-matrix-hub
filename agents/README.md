# Agents : mode d'emploi

Ce dossier explique aux agents (sessions Claude, scripts) comment travailler sur le compte publicitaire et les prospects de VFormations. À lire avant toute requête vers Meta.

## Règle n°1 : aucun secret dans ce dépôt

Aucun jeton, mot de passe ni clé n'est écrit dans un fichier du dépôt, même privé. Les secrets vivent dans les **secrets de l'environnement cloud** (réglages de l'environnement > Modifier > secrets réseau, ou variable d'environnement). Une session lit ses secrets à son démarrage : après un ajout, il faut ouvrir une nouvelle session.

Un fichier `.gitignore` bloque les noms de fichiers les plus courants (`.env`, `*.token`, `*.secret`). Il ne remplace pas la vigilance : relisez le `git diff` avant chaque commit.

## Les secrets : comment ils fonctionnent ici

Le jeton Meta est enregistré comme **secret réseau** de l'environnement (réglages de l'environnement > Modifier > secrets > « Add secret »), avec ces réglages : type `Bearer`, site autorisé `graph.facebook.com`, en-tête `Authorization`. Le système ajoute lui-même l'en-tête à chaque requête vers ce site : **un agent n'envoie aucun jeton et n'a aucune variable d'environnement à lire.**

À savoir :

- Les noms `META_ADS_READ_TOKEN` et `META_LEADS_TOKEN` d'une version précédente de ce document **n'existent pas**. Ne les cherchez pas.
- L'ajout se fait par site : **un seul jeton** pour `graph.facebook.com`. Droits de lecture recommandés : `ads_read`, `leads_retrieval`, `pages_show_list`, `pages_read_engagement`. Le jeton actuellement enregistré a été créé avec « tous les droits », écriture et publication comprises : **à remplacer par un jeton de lecture** dès que l'API répond.
- **Non testé :** la lecture des prospects exige un jeton de Page, dérivé avec `GET /{page_id}?fields=access_token`. Si le système remplace l'en-tête de l'agent par le sien, cette étape échouera.
- Le robot Google Apps Script tourne chez Google, hors de cet environnement : il a sa propre copie du jeton, dans la propriété de script `META_TOKEN`.

### Diagnostic en une commande

```
curl -sS "https://graph.facebook.com/v21.0/me?fields=name"
```

- erreur 2500, « An active access token must be used » : aucun secret n'est injecté ;
- erreur 200, « API access blocked » : un jeton part, mais l'application Meta est bloquée (voir ci-dessous) ;
- un nom en réponse : tout fonctionne.

## État au 30 octobre 2026 : accès à l'API bloqué

- **Symptôme :** toutes les requêtes vers `graph.facebook.com`, y compris `/me` et la vérification de jeton, renvoient l'erreur 200 « API access blocked ». Le blocage vise l'**application** `1129728139639524`, pas le compte publicitaire ni les droits du jeton.
- **Chronologie :** dernier appel réussi le 27/10, premier échec constaté le 28/10 à 22 h 34 (heure de Paris).
- **Cause : inconnue.** L'espace développeur de Meta renvoie lui-même une page d'erreur au propriétaire de l'app, et un onglet intitulé « Erreur d'utilisateur bloqué » a été vu. Une restriction sur le compte Facebook qui administre l'app est une hypothèse, **non confirmée**.
- **À ne pas faire :** créer une seconde application pour contourner le blocage. Si c'est une mesure de Meta, cela peut aggraver la situation.
- **Conséquence :** le robot de réponse aux prospects lit Meta par cette même application. Tant que le blocage dure, il ne peut pas fonctionner.
- **Solution de repli pour l'analyse des publicités :** captures ou exports du Gestionnaire de publicités (tableau des publicités depuis le 14/10, par jour, avec dépense, impressions, clics sur le lien, prospects, vues vidéo à 3 secondes et ThruPlay).

## Identifiants qui ne sont PAS des secrets

| Quoi | Valeur |
|---|---|
| Compte publicitaire | `act_668163372302061` (Voxy.IA, EUR, Europe/Paris) |
| Page Facebook | `765749889955901` (VFormations) |
| Formulaire instantané en ligne | `1745675750027565` |
| Application Meta | `1129728139639524` (« Vformation reporting ADS ») |
| Version de l'API | `v21.0` |

## Comment lire un secret

- Ne jamais afficher un secret, ni l'écrire dans un fichier, un message de commit, un journal ou un retour de commande.
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
| Réponse automatique au formulaire | Construit et testé sur des services simulés. À installer par le gérant. **Bloqué tant que l'application Meta l'est.** | `automation/lead-autoresponder/` |
| Nurturing des prospects | Non démarré. Brief prêt. | `agents/handoff/NURTURING.md` |
| Audit hebdomadaire des publicités | Manuel pour l'instant, à partir de captures du Gestionnaire | Automatisable une fois l'API débloquée |

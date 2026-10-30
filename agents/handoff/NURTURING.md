# Brief : nurturing des prospects

**État : non démarré.** Ce document est écrit pour l'agent qui reprendra le chantier. Il contient tout ce qu'il faut savoir sans avoir lu la conversation d'origine.

Lire d'abord `agents/README.md` (secrets, règles de conduite).

---

## 1. Pourquoi ce chantier

Le formulaire instantané Meta produit des prospects peu qualifiés : environ 2 % d'entre eux atteignent un rendez-vous commercial, contre environ 17 % depuis une page de destination. Les deux leviers qui rattrapent cet écart sont la **vitesse du premier rappel** et la **relance**. La réponse automatique (`automation/lead-autoresponder/`) couvre le premier contact. Le nurturing couvre tout ce qui vient après : le prospect qui ne répond pas, celui qui dit « je me renseigne », celui qui a eu un rendez-vous et n'a pas signé.

## 2. À faire avant de commencer

Ne pas démarrer tant que ces quatre points ne sont pas réglés.

1. **La réponse automatique tourne depuis au moins 2 semaines, sans erreur**, et le Sheet contient des prospects réels avec leur suivi rempli par l'équipe. Sans ces données, on construit à l'aveugle.
2. **Le formulaire est corrigé.** Voir la section 3 : il contient en production une phrase interdite.
3. **La certification Qualiopi est confirmée**, ou à défaut aucun message n'y fait référence. Sans elle, ni l'AGEFICE ni le FAFCEA n'acceptent de dossier : un nurturing qui parle de financement promettrait quelque chose d'inaccessible.
4. **Le gérant a tranché le canal** (section 6).

## 3. Constats sur le formulaire en production (27 octobre 2026)

Relevés par lecture de l'API le 27/10/2026, formulaire `1745675750027565`, 29 prospects reçus depuis le 14/10.

**À corriger en priorité.**

- La carte de présentation du formulaire dit : *« …une formation à 3 000 €, potentiellement financée à 100 % selon votre statut. »* C'est une formulation interdite (promesse de financement intégral). Elle est vue par chaque personne qui ouvre le formulaire. Elle peut aussi déclencher un refus de la publicité par Meta. Un formulaire publié ne se modifie pas : il faut le **dupliquer**, corriger la copie, puis rattacher les publicités à la nouvelle version.
- Le prix annoncé, **3 000 €**, ne correspond à aucun des prix de la gamme du plan (490 / 1 950 / 2 900 €).

**À arbitrer avec le gérant.**

- Le formulaire ne pose **aucune question permettant d'identifier le financeur** : « êtes-vous gérant non salarié ? ». Il ne demande ni le nombre de salariés ni la date de démarrage souhaitée. Les cinq questions de qualification prévues au plan ne sont pas dans le formulaire réel.
- La page de remerciement promet « un conseiller vous contactera sous 24-48 h ». C'est tenable avec une présence de 3 jours par semaine, mais pas avec l'objectif interne de rappel sous 2 h.

**Ce qui est en ordre.** La politique de confidentialité est renseignée et répond (HTTP 200). Aucune option de réponse ne contient de vocabulaire interdit.

## 4. Les données disponibles

### Questions du formulaire et réponses possibles

| Question | Réponses |
|---|---|
| Statut juridique | EURL · SARL (gérant majoritaire) · Micro-entrepreneur · Entreprise individuelle (EI) · SAS · SASU · Autre |
| Ancienneté de l'entreprise | Moins d'1 an · 1 à 3 ans · Plus de 3 ans |
| Formation qui l'intéresse | Développer sa clientèle grâce aux réseaux sociaux · L'IA au service du dirigeant · Les deux |
| Objectif principal | Trouver de nouveaux clients · Gagner du temps / être plus productif · Structurer ma présence en ligne · Autre |
| Coordonnées | Nom complet · e-mail · téléphone · nom de l'entreprise |

Pour chaque prospect, Meta fournit aussi la **publicité d'origine** (`ad_name`) : c'est ce qui permet de rattacher un rendez-vous à une créa.

### Le Google Sheet du robot

Onglet `Prospects`, une ligne par prospect :

`lead_id` · `traite_le` · `cree_le_meta` · `formulaire` · `publicite` · `nom` · `email` · `telephone` · `entreprise` · `statut_juridique` · `anciennete` · `formation` · `objectif` · `autres_reponses` · `reponse_auto` · `suivi` · `rappel_le` · `rdv_pris` · `notes`

Les colonnes `suivi`, `rappel_le`, `rdv_pris` et `notes` sont **remplies à la main par l'équipe**. Ce sont elles que le nurturing lira pour savoir où en est chaque prospect.

Onglet `Désabonnés` : une adresse par ligne. **Aucun message ne doit partir vers ces adresses.** Aujourd'hui l'équipe doit la remplir à la main quand quelqu'un répond « STOP ». Automatiser cette étape (lire la boîte de réception, repérer « STOP », ajouter l'adresse) est la première tâche utile.

## 5. Séquence proposée

**Proposition à valider, pas une décision.** À confronter aux données réelles de la section 2.1.

| Quand | Qui | Canal | Contenu |
|---|---|---|---|
| Immédiat | Tous | E-mail (fait par le robot) | Accusé de réception, délai de rappel |
| Immédiat | Équipe | Téléphone | Premier appel, selon le mode opératoire « rappel d'un contact entrant » |
| J+2 | Pas joint | SMS court, puis nouvel appel | « J'ai essayé de vous joindre, je rappelle demain matin » |
| J+7 | Pas joint, ou rendez-vous non pris | E-mail | Ce qui sera vu pendant l'échange, un lien pour choisir le créneau |
| J+14 | Idem | E-mail | Dernier message : « Je clôture votre demande, répondez si vous souhaitez la rouvrir » |
| Après un rendez-vous tenu sans inscription | Tous | Téléphone puis e-mail | Récapitulatif, rappel de la date limite de dépôt du dossier |
| Prospect qui dit « dans 6 mois » | Tous | E-mail | Une seule relance à l'approche de la cohorte suivante |

**Contrainte de calendrier :** pour un dossier AGEFICE, la demande doit arriver au siège **au moins 15 jours calendaires avant le démarrage**, et au plus tôt 4 mois avant. Un message de relance qui invite à « s'inscrire » doit être calé sur cette date, sinon il pousse quelqu'un vers une cohorte qu'il ne peut plus rejoindre.

**Hypothèse sur le statut juridique, non vérifiée.** Le statut déclaré pourrait indiquer le financeur probable : gérants majoritaires de SARL ou d'EURL, entrepreneurs individuels et micro-entrepreneurs relèveraient de l'AGEFICE ; les présidents de SAS ou de SASU, assimilés salariés, probablement pas. À faire confirmer par un Point d'Accueil AGEFICE avant d'en tirer une règle. Autre point à vérifier : le FAFCEA exclut les créateurs et repreneurs de son parcours individualisé ; la même exclusion existe-t-elle ailleurs ?

## 6. Décisions à obtenir du gérant

1. **Quel canal en plus de l'e-mail ?** Le SMS et WhatsApp demandent un prestataire payant et un consentement explicite à ce type de message. Recommandation : e-mail seul au départ, SMS une fois le volume établi.
2. **Qui valide chaque message avant envoi ?** Recommandation : le gérant relit chaque texte une fois, puis les textes sont figés.
3. **Qui rappelle, quels jours ?** La promesse faite au prospect doit correspondre à la présence réelle de l'équipe.
4. **Durée de conservation des données.** À fixer avec le gérant et à inscrire dans la politique de confidentialité. Repère à faire confirmer : la CNIL recommande en général de ne pas conserver un prospect plus de 3 ans après son dernier contact.

## 7. Règles non négociables

- Tout ce qui figure dans `agents/README.md`, section « Règles de conduite ».
- **Le premier message reste un accusé de réception.** Tout message qui ressemble à de la promotion contient un moyen simple de se désinscrire.
- **Aucune relance à quelqu'un qui est dans l'onglet `Désabonnés`**, quelle que soit la séquence.
- **Aucun message ne cite un montant de financement** sans que le statut du prospect ait été vérifié. Le reste à charge n'est annoncé que par écrit, sur le devis.
- Le dirigeant avance le coût de la formation puis est remboursé par son fonds : **ne jamais laisser entendre qu'il ne paiera rien au départ**.
- Chaque message doit être tenable devant un contrôleur qui se ferait passer pour un prospect.

## 8. Tâches pour l'agent

1. Lire `agents/README.md` et `automation/lead-autoresponder/README.md`.
2. Vérifier que les quatre points de la section 2 sont réglés. Sinon, s'arrêter et le dire au gérant.
3. Lire un échantillon du Sheet (sans copier de données personnelles) pour mesurer : combien de prospects, combien rappelés, combien de rendez-vous pris, combien tenus.
4. Proposer au gérant une séquence ajustée à ces chiffres, avec les textes de chaque message.
5. Après validation, l'implémenter **à côté du robot existant**, dans le même projet Apps Script ou un fichier voisin, pour rester sur une seule infrastructure sans serveur.
6. Automatiser la désinscription par « STOP ».
7. Écrire des tests dans le même esprit que `automation/lead-autoresponder/test.js` : services simulés, et au moins une cassure volontaire du code pour vérifier que les tests la détectent.
8. Passer d'abord en mode simulation, comme le robot, et ne rien envoyer à un vrai prospect avant l'accord du gérant.

**Terminé quand :** les messages partent aux bonnes personnes, au bon moment, jamais deux fois, jamais à un désabonné, que les tests passent, et que le gérant a vu au moins un cycle complet en simulation.

## 9. Mesures de succès

- Part des prospects qui obtiennent un rendez-vous (aujourd'hui environ 2 % attendu pour ce type de formulaire).
- **Coût par rendez-vous tenu** : dépense publicitaire (lue via l'API Meta, voir `agents/README.md`) divisée par les rendez-vous réellement tenus. C'est le seul chiffre qui dit si la campagne est rentable. Repères du plan : 120 à 250 € attendu, **au-delà de 350 €, on coupe**.
- Délai moyen entre l'arrivée d'un prospect et son premier appel.

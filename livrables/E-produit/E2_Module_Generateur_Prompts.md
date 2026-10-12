# E2 — Module « Générateur de prompts » — spécification

> **Casquette : Directeur produit + ingénieur prompt.**
> **Date : 12 octobre 2026.** Prérequis : `E0` (architecture).
> **Base documentaire :** méthode BMAD (dépôt officiel + paquet npm v6.12.2 inspectés), GitHub Spec Kit, guides officiels de conception de prompts 2026.

---

## 1. Le problème

Un dirigeant de TPE ouvre un assistant IA et tape :

> *« Je voudrais faire un site pour mon restaurant »*

Il obtient une réponse générique, il ne sait pas quoi en faire, il abandonne. **Ce n'est pas un problème d'IA, c'est un problème de brief.**

### Les 4 défaillances réelles
| # | Ce qui manque | Conséquence |
|---|---|---|
| 1 | **Le critère de réussite** | L'IA ne sait pas ce qui est « bon » → elle produit du plausible |
| 2 | **Le hors-périmètre** | L'IA part dans tous les sens, la session se dilue |
| 3 | **Les points d'arrêt** | L'IA fonce 40 messages dans la mauvaise direction |
| 4 | **La mémoire de session** | À la session suivante, tout est perdu, il recommence |

> ## 🎯 Promesse du module
> **« Dis-moi ton idée en 2 minutes, à l'écrit ou à la voix. Je te rends un fichier à coller dans ton IA — avec la méthode pour tenir toute ta session. »**

---

## 2. Parcours utilisateur

```
① ENTRÉE LIBRE
   note écrite OU dictée vocale (2 min)
              ↓  transcription
② REFORMULATION — « voilà ce que j'ai compris » (5 lignes)
              ↓  🚦 GATE 0 — l'utilisateur corrige
③ ROUTAGE — quel type de projet ?
   outil · contenu · données · automatisation · offre commerciale
              ↓
④ QUESTIONS ADAPTATIVES — une à la fois, 8 max
   tronc commun (5) + branche métier (3)
              ↓
⑤ GÉNÉRATION du fichier .MD
   noyau 5 champs + capacités + gates + journal
              ↓
⑥ LIVRAISON — télécharger · copier · « ouvrir dans mon IA »
```

> 💡 **Règle d'or du questionnement : UNE question à la fois.** C'est le mécanisme de `forge-idea` (BMAD) et c'est ce qui distingue un vrai entretien de cadrage d'un formulaire. Un questionnaire de 8 champs affichés d'un coup fait fuir ; 8 questions posées une par une, en conversation, se remplissent.

---

## 3. 🧬 Le noyau — 5 champs (emprunté à BMAD, simplifié)

> BMAD v6.12 construit tout son édifice sur un noyau de **5 champs**. C'est ce qu'on retient, et c'est suffisant pour un public non technique.

| Champ | Question posée à l'utilisateur | Pourquoi c'est indispensable |
|---|---|---|
| **① POURQUOI** | « Pourquoi maintenant ? » | Sans le pourquoi, l'IA ne peut pas arbitrer |
| **② CAPACITÉS** | « Qu'est-ce qu'on doit pouvoir faire à la fin ? » | Chaque capacité porte un **critère de recette** |
| **③ CONTRAINTES** | « Budget, délai, outils déjà payés, obligations légales ? » | Évite les propositions irréalistes |
| **④ HORS PÉRIMÈTRE** | « Qu'est-ce que ça ne doit PAS être ? » | 🔴 **Au moins un élément OBLIGATOIRE** |
| **⑤ SIGNAL DE RÉUSSITE** | « À quoi on verra concrètement que c'est réussi ? » | Transforme un souhait en objectif testable |

### Le critère de recette, en langage courant
Chaque capacité s'écrit :
> **ÉTANT DONNÉ** [situation] **QUAND** [action] **ALORS** [résultat observable]

*Exemple :* « ÉTANT DONNÉ que je suis fermé le lundi, QUAND un client ouvre ma page, ALORS il voit mes horaires à jour sans avoir à chercher. »

> C'est du *Given/When/Then* sans le dire. Un dirigeant de TPE le comprend immédiatement et c'est **testable** — contrairement à « avoir un beau site ».

### Les 2 emprunts à GitHub Spec Kit
1. **Le marqueur `[À CLARIFIER]`** — l'IA ne doit jamais inventer. Face à un trou, elle écrit le marqueur.
2. **Le gate « zéro marqueur restant »** — on ne passe à l'exécution que lorsqu'il n'en reste aucun.

---

## 4. Les questions

### Tronc commun (5 questions, après le routage)

| # | Question | Champ alimenté |
|---|---|---|
| 1 | **À quoi on verra que c'est réussi ?** | ⑤ Signal |
| 2 | **Pourquoi maintenant ?** (douleur / opportunité / obligation) | ① Pourquoi |
| 3 | **Pour qui exactement ?** — « quand ___, il veut ___ pour que ___ » | ② Capacités |
| 4 | **Qu'est-ce que ça ne doit PAS être ou faire ?** | ④ Hors périmètre |
| 5 | **Contraintes dures : budget, délai, outils, obligations légales ?** | ③ Contraintes |

### Branches adaptatives (3 questions selon le routage)

| Type de projet | Les 3 questions |
|---|---|
| 🛠️ **Créer un outil** | Qui saisit la donnée ? · Où vit-elle ? · Que se passe-t-il si elle est fausse ? |
| ✍️ **Produire du contenu** | Quel canal et quel format exact ? · Votre audience connaît-elle déjà la solution ? · Quelles 3 preuves réelles pouvez-vous montrer ? |
| 📊 **Analyser des données** | Quelle décision dépend du résultat ? · D'où viennent les données et de quand datent-elles ? · Quel seuil déclenche une action ? |
| ⚙️ **Automatiser une tâche** | Quel déclencheur ? · Combien de cas par mois ? · Que fait-on des exceptions ? |
| 💼 **Monter une offre** | Prix cible et comparable ? · Financement et contraintes légales ? · Preuve que vous savez livrer ? |

### Règles de conduite de l'entretien
- ✅ Une question à la fois, **2 relances maximum** par question
- ✅ Accepter « je ne sais pas » → **proposer une hypothèse par défaut à valider**
- ✅ Reformuler en 3 lignes avant d'écrire quoi que ce soit (Gate 0)
- ❌ Ne jamais inventer un chiffre, une source ou une contrainte

---

## 5. Structure du fichier .MD produit

```
en-tête : titre · type · date · version · statut

 0. COMMENT UTILISER CE FICHIER        ← 3 lignes, pour l'humain
 1. RÔLE DE L'IA
 2. CONTEXTE
 3. POURQUOI                            ← champ ①
 4. OBJECTIF & SIGNAL DE RÉUSSITE       ← champ ⑤
 5. LIVRABLES ATTENDUS (CAP-1…n)        ← champ ② + critères de recette
 6. CONTRAINTES DURES                   ← champ ③
 7. HORS PÉRIMÈTRE                      ← champ ④ (≥ 1 obligatoire)
 8. FORMAT DE SORTIE (+ 1 exemple)
 9. PLAN DE SESSION (étapes + gates)
10. TABLEAU DES GATES
11. RÈGLES DE FIABILITÉ
12. JOURNAL DE SESSION                  ← rempli par l'IA, en ajout seulement
13. ZONES [À CLARIFIER]
```

### La mécanique des gates (3 à 4 maximum)

```
🚦 GATE 2 — STOP. N'avance pas.
   Montre-moi : [l'artefact exact]
   Demande-moi : « Est-ce que X correspond ? »
   Options : (a) valider  (b) corriger  (c) changer d'approche
   Attends ma réponse écrite avant l'étape suivante.
```

> ⚠️ **Jamais plus de 4 gates.** Au-delà, l'utilisateur décroche et les ignore — et un gate ignoré est pire que pas de gate.

### 📓 La section 12 — le journal de session

C'est le mécanisme **anti-perte de contexte**, et c'est ce que personne ne met dans un prompt grand public. L'IA y note, **en ajout seulement** : décisions prises, avancement, points ouverts.

**Bénéfice concret pour l'utilisateur :** quand sa session devient trop longue ou qu'il revient le lendemain, il ouvre un nouveau chat, recolle le fichier **avec son journal**, et reprend exactement où il en était.

---

## 6. 📚 La bibliothèque de méthodes

> Le module ne produit pas qu'un prompt : il **greffe une méthode** adaptée au projet.

| Méthode | Ce qu'elle apporte | Déclenchée quand |
|---|---|---|
| **Noyau 5 champs + gates** (BMAD simplifié) | Cadre de base | Toujours |
| **Marqueur `[À CLARIFIER]`** (Spec Kit) | Interdit l'invention | Toujours |
| **Journal de session** | Reprise en nouveau chat | Toujours |
| **Chaîne de vérification** | Brouillon → questions de vérification → **réponses isolées du brouillon** → réécriture | 🔴 Dès qu'il y a des **chiffres, du droit ou du financement** |
| **Niveaux de conscience (Schwartz)** | Interdit le pitch direct quand l'audience n'est pas mûre | Projets contenu / offre commerciale |
| **Problème → Agitation → Solution** | Structure de persuasion | Contenu, argumentaire |
| **Arbre d'options** | 3 branches comparées sur critères explicites | Naming, positionnement, choix stratégique |
| **Cinq pourquoi** | Remonte à la cause racine | Diagnostic d'un problème |
| **Pyramide de Minto** | Réponse d'abord, puis 3 arguments | Note de synthèse, présentation |
| **Pilotage de session longue** | Liste de fonctionnalités en JSON avec champ `passes`, fichier de progression, test de référence avant tout nouveau travail | Projet > 1 session |

> 💡 **La chaîne de vérification est la méthode la plus précieuse pour nos clients.** Dès qu'un dirigeant demande à l'IA quelque chose sur ses financements, ses obligations ou ses chiffres, elle réduit nettement le risque d'affirmation inventée. **Son efficacité tient à un détail : les questions de vérification doivent recevoir une réponse SANS relire le brouillon.**

---

## 7. 🎙️ L'entrée vocale

| Point | Décision |
|---|---|
| **Pourquoi la voix ?** | Un dirigeant de TPE parle 5× plus vite qu'il n'écrit, et décrit mieux son problème à l'oral. **C'est le bon format d'entrée pour cette cible.** |
| **Technique** | **API, jamais auto-hébergé.** 100 clients × 4 dictées de 15 min = 6 000 min/mois ≈ **1 à 36 €/mois** selon le fournisseur. Auto-héberger pour économiser 30 €/mois serait absurde. |
| **Choix** | Privilégier un fournisseur **européen** (souveraineté + meilleure qualité en français), avec un repli sur un service de transcription standard |
| ⚠️ **RGPD** | **Les enregistrements vocaux sont des données personnelles.** Transcrire puis **supprimer l'audio** par défaut. Durée de conservation annoncée. |

---

## 8. Anatomie du prompt généré — règles 2026

> D'après les guides officiels de conception de prompts (consultés le 12/10/2026).

| Règle | Application dans le module |
|---|---|
| **Rôle en une phrase** | En tête du fichier |
| **Données longues EN HAUT**, question à la fin | Jusqu'à **+30 %** de qualité sur les contextes multi-documents |
| **Expliquer le POURQUOI de chaque consigne** | Le modèle généralise depuis l'explication. *« Structure PAS, parce que la cible est consciente du problème »* ≫ *« utilise PAS »* |
| **Dire quoi faire, pas quoi éviter** | Formulations positives |
| **Balises descriptives et cohérentes** | Structure le contexte |
| **3 à 5 exemples, DIVERS** | Des exemples trop semblables font apprendre un motif parasite |
| **Critères de succès explicites** | Section 5 du fichier |
| ⚠️ **Le préremplissage n'est plus supporté** | On obtient le format par consigne explicite — *tout guide de 2025 qui recommande le préremplissage est périmé* |
| **Sessions longues** | « Ne t'arrête pas par peur du budget de contexte, sauvegarde ton état » + demander des points de progression explicites |

---

## 9. Pourquoi ce module a sa place dans notre offre

| Objection | Réponse |
|---|---|
| *« Ce n'est pas notre métier »* | Si. Notre métier est de **rendre les dirigeants autonomes**. L'IA est devenue l'outil n°1 du dirigeant de TPE, et **personne ne leur apprend à s'en servir sérieusement.** |
| *« C'est hors sujet par rapport à la vidéo »* | C'est le **pont vers la formation IA** du catalogue, et un argument de rétention sur l'abonnement. |
| *« Ça se copie »* | Le générateur se copie. **La bibliothèque de méthodes greffées et la boucle de retour, non.** |
| **Valeur pédagogique** | Un prompt structuré rédigé par l'apprenant **est une preuve d'apprentissage** (livrable AFEST tracé). |

---

## 10. Plan de construction

| Étape | Contenu | Quand |
|---|---|---|
| **1** | **3 modèles .MD prêts à l'emploi** (voir `E2b`) — utilisables **dès maintenant**, sans aucun développement | ✅ Immédiat |
| **2** | v0 manuelle : le formateur fait l'entretien de cadrage en session, remplit le modèle avec le client | M1-M3 |
| **3** | Formulaire web : routage + questions adaptatives + génération | M6 |
| **4** | Entrée vocale | M7 |
| **5** | Bibliothèque de méthodes extensible + retour utilisateur (« ce prompt t'a-t-il servi ? ») | M8 |

> ✅ **L'étape 1 est livrée dans `E2b_Modeles_Prompts_Prets.md` — utilisable dès la première formation, sans une ligne de code.**

---

## 11. Points de vigilance

1. 🔴 **Ne pas transformer le module en formulaire.** La valeur est dans l'**entretien** (une question à la fois), pas dans les champs.
2. 🔴 **Hors périmètre obligatoire.** C'est le champ que tout le monde saute, et c'est celui qui sauve les sessions.
3. 🟠 **Maximum 4 gates.** Au-delà, ils sont ignorés.
4. 🟠 **Ne pas sur-promettre.** Le fichier .MD ne fait pas le travail : il le **cadre**. À dire clairement.
5. 🟠 **La chaîne de vérification est obligatoire** sur tout prompt touchant aux chiffres, au droit ou au financement — c'est précisément là que nos clients se feraient avoir.

---

> **Modèles prêts à l'emploi :** `E2b_Modeles_Prompts_Prets.md`

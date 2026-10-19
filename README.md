# Générateur de scripts vidéo

Un générateur de scripts de vidéos courtes pour les entreprises locales —
artisans, commerces, restaurants, salons, PME de services.

Il ne produit pas des « idées de contenu ». Il conduit un entretien sur votre
activité, vous propose des angles à valider, écrit des scripts tournables avec
leurs plans, et vérifie qu'aucun ne vous expose juridiquement.

**Il tourne dans votre Claude Code, sur votre abonnement.** Rien n'est envoyé
à un serveur tiers, rien n'est stocké ailleurs que chez vous.

---

## Installation — 3 minutes

### 1. Récupérer le dépôt

```bash
git clone -b generateur-scripts https://github.com/Alessandri34/voxy-matrix-hub.git generateur-scripts
cd generateur-scripts
```

### 2. Lancer Claude Code dans ce dossier

```bash
claude
```

C'est tout. Claude Code charge automatiquement le générateur et ses commandes
depuis le dossier `.claude/`.

### 3. Vérifier

Tapez `/` dans Claude Code : vous devez voir apparaître `entretien`, `angles`,
`scripts` et `controle`.

> **Si les commandes n'apparaissent pas** — vérifiez que vous avez bien lancé
> `claude` **depuis le dossier du dépôt** (`pwd` doit afficher
> `.../generateur-scripts`). Les commandes ne sont visibles que dans ce dossier.

---

## Utilisation

Quatre étapes, dans l'ordre. Chacune produit un fichier que vous gardez.

| Commande | Ce qu'elle fait | Durée | Produit |
|---|---|---|---|
| `/entretien` | Vous pose des questions sur votre activité | 20-30 min | `mon-entreprise.md` |
| `/angles` | Propose un signal, 3 profils de clients et 10 angles | 5 min | `mes-angles.md` |
| `/scripts` | Écrit les scripts | 10 min | `mes-scripts.md` |
| `/controle` | Vérifie la conformité et note chaque script | 5 min | rapport |

Vous pouvez aussi simplement écrire ce que vous voulez — *« je suis coiffeuse
à Sète et je ne sais pas quoi filmer »* — le générateur se déclenche tout seul.

### L'étape à ne pas sauter

Après `/angles`, le générateur **s'arrête et vous demande de valider**.

Ce n'est pas une politesse. Il y a toujours quelque chose de faux dans les
angles proposés, et vous seul pouvez le corriger. Et surtout : quelqu'un qui a
corrigé ses propres angles tourne ses vidéos. Quelqu'un à qui on livre dix
scripts tout faits ne les tourne pas.

---

## Ce qu'il refuse de faire

Le générateur bloque et réécrit quand un script contient :

- une **promesse de résultat** chiffrée ou garantie
- un **chiffre sans source**
- un **plan intournable** avec les moyens que vous avez déclarés
- pour une formation financée : « gratuit », « 100 % financé », « sans reste à charge »

Il refuse aussi de servir la **santé, le droit et les métiers à ordre
professionnel** : leur communication obéit à des règles propres qu'il ne
connaît pas.

Ce n'est pas une limitation : c'est la différence entre un outil
professionnel et un assistant généraliste qui vous laisserait publier
n'importe quoi.

---

## Ce qu'il y a dedans

```
.claude/
  skills/generateur-scripts/
    SKILL.md                    le moteur en 3 passes
    references/
      01-entonnoir.md           comment faire parler un dirigeant ⭐
      02-accroches.md           50 accroches classées
      03-niveaux-conscience.md  à qui on parle, et où il en est
      04-arc-narratif.md        la structure en 7 temps
      05-garde-fous.md          ce qui est bloqué, et pourquoi
      06-notation.md            la grille /100
    exemples/
      fiche-entreprise-modele.md
      sortie-attendue.md        un script complet, noté
  commands/                     les 4 commandes
```

La ressource la plus importante est `01-entonnoir.md`. Un générateur nourri de
réponses creuses produit des scripts creux, quel que soit le reste.

---

## Prérequis

- **Claude Code** installé ([instructions](https://code.claude.com/docs))
- Un abonnement Claude actif
- Git

---

## Licence et usage

Ce dépôt est remis aux participants des formations VFormations. Vous pouvez
l'utiliser pour votre propre activité, le modifier et l'adapter.

Les ressources de méthode (bibliothèque d'accroches, entonnoir, grille de
notation) restent la propriété de VFormations — organisme de formation
certifié Qualiopi.

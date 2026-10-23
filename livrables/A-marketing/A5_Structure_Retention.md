# A5 — Structure de rétention : les boucles décalées

> **Casquette :** CPO contenu. Couche **transverse** : elle s'applique aux scripts d'attraction (`A_scripts_ugc`), de transmission (`A2`) et techniques (`A4`). Elle ne remplace pas l'arc de transmission en 5 temps — elle s'y emboîte.
> **Date :** 23/10/2026. **Objectif :** le taux de rétention, pas le taux d'accroche.

---

## 1. Le problème, mesuré sur nos propres scripts

L'arc en 5 temps de `A2` décrit **ce qui est dit**. Il ne décrit nulle part **pourquoi le spectateur reste**. Résultat : toute l'ingénierie porte sur les 3 premières secondes, et les 50 suivantes tiennent sur la bonne volonté.

Prenons `V01`, tel qu'il est écrit aujourd'hui :

| Temps | Texte | Ce que fait le spectateur |
|---|---|---|
| Accroche | « Il y a une question à poser à votre organisme, et presque personne ne la pose. » | **Une boucle s'ouvre** : laquelle ? |
| Ancrage | « Si vous êtes artisan et que vous préparez une formation au web… » | il se reconnaît, il reste |
| Transmission | « Le taux technique métier, c'est celui du geste professionnel… » | **la boucle se referme**, vers 12 s |
| | *~30 secondes de contenu* | **plus rien ne le retient** |
| Nuance | « Et voilà ce qui rend l'erreur si facile… » | relance, vers 45 s — trop tard |

**Le défaut est structurel, pas rédactionnel.** La promesse de l'accroche est honorée au tiers de la vidéo. Entre la 12ᵉ et la 45ᵉ seconde, le script ne demande plus rien au spectateur : il expose. Or c'est exactement la zone où un Reel se perd.

Ce diagnostic vaut pour **les 30 scripts** de `A2` et `A4` : tous ouvrent une boucle unique et la referment dans le premier tiers.

---

## 2. La mécanique : ne jamais laisser le spectateur sans question en cours

**Principe.** À tout instant de la vidéo, il doit exister **au moins une question posée et non encore résolue**. Quand une boucle se referme, une autre doit déjà être ouverte.

C'est l'inverse de la façon dont on écrit naturellement, qui est séquentielle : question → réponse → question → réponse. La séquence crée des **points de sortie** — chaque réponse est une permission de partir. Le décalage les supprime :

```
       0s        10s       20s       30s       40s       50s      60s
       │         │         │         │         │         │        │
écriture naturelle (points de sortie) :
       ╔═ A ═════╗         ╔═ B ═════╗         ╔═ C ═════╗
       ouvre    ferme↑     ouvre    ferme↑     ouvre    ferme↑
                  ⚠ sortie            ⚠ sortie           ⚠ sortie

boucles décalées (aucun point de sortie) :
       ╔═ A ═══════════════╗
                 ╔═ B ═══════════════╗
                           ╔═ C ═══════════════╗
       └ jamais zéro question en cours ────────┘
```

**La boucle B s'ouvre AVANT que A se referme.** C'est tout le mécanisme. Il ne demande ni montage, ni musique, ni effet : seulement l'ordre des phrases.

### Le minimum praticable : deux boucles

Trois boucles sur 60 secondes deviennent difficiles à tenir sans embrouiller. **Deux suffisent**, décalées :

- **Boucle A** — ouverte à l'accroche, refermée **au temps 4 (la nuance)**, pas au temps 3.
- **Boucle B** — ouverte **dans le premier tiers de la transmission**, refermée en fin de transmission.

Ce qui change concrètement dans l'arc existant :

| Temps | Avant | Après |
|---|---|---|
| 1. Accroche | ouvre A | ouvre A — **inchangé** |
| 2. Ancrage | situe | situe — **inchangé** |
| 3. Transmission | **ferme A**, puis expose | **ouvre B**, transmet, **ferme B** — A reste ouverte |
| 4. Nuance | apporte l'exception | **ferme A** — l'exception EST la réponse promise |
| 5. Sortie | ouverte | ouverte — **inchangé** |

**L'arc en 5 temps n'est pas modifié. Seul l'endroit où A se referme change.** C'est ce qui rend la correction applicable aux 30 scripts sans les réécrire.

### Appliqué à V01

> **Accroche** — « Il y a une question à poser à votre organisme, et presque personne ne la pose. **Elle tient en six mots, et elle peut valoir 350 €.** » → A ouverte, et chiffrée
> **Ancrage** — inchangé
> **Transmission** — « Avant de vous la donner, il faut comprendre pourquoi elle existe. **La FAFCEA ne paie pas toutes les formations au même tarif — et le classement ne dépend pas de ce que vous croyez.** » → **B ouverte**, A toujours en suspens. Puis le contenu : taux technique, taux transverse, ce qui bascule l'un dans l'autre → **B refermée**
> **Nuance** — « Et la question à poser, la voici : *mon stage relève-t-il du technique ou du transverse ?* L'erreur est de bonne foi… » → **A refermée, à la 45ᵉ seconde**
> **Sortie** — inchangée

Le contenu transmis est **rigoureusement le même**. Seul l'ordre change. La promesse initiale est honorée à la 45ᵉ seconde au lieu de la 12ᵉ.

---

## 3. Les quatre boucles utilisables ici — et celles qu'on s'interdit

Une boucle n'est pas un *teasing*. Elle doit porter une **vraie** question dont la réponse sert au spectateur.

| Type | Forme | Exemple admissible chez nous |
|---|---|---|
| **Le seuil** | un chiffre nommé, non expliqué | « Il y a un seuil à 85 € qui décide de tout. On y vient. » |
| **L'ordre inversé** | la conséquence avant la cause | « Ce dossier a été refusé. Il était pourtant complet. » |
| **La condition suspendue** | une règle dont l'exception arrive plus tard | « C'est vrai dans tous les cas sauf un. Le sauf arrive. » |
| **La question rendue** | le spectateur doit se situer | « Notez votre réponse maintenant, on la vérifie dans trente secondes. » |

**Interdits**, parce qu'ils promettent sans livrer :

- ❌ « Restez jusqu'à la fin » — annonce la manœuvre sans contenu. Si la fin mérite d'être vue, la boucle le dit à sa place.
- ❌ La boucle qu'on ne referme pas. Une promesse non tenue dans la vidéo coûte plus cher que les secondes gagnées, surtout en MOFU où le capital est la confiance (`A2` R1).
- ❌ La boucle sur un résultat (« combien j'ai gagné avec… ») — interdite par `CLAUDE.md` §7bis et par la règle G1 du contrôleur.
- ❌ Le faux suspense sur une information banale. Le spectateur le sent, et il sanctionne la fois d'après.

---

## 4. Ce que valent les deux sources

Vous m'avez demandé de juger. Voici, avec le statut probatoire de chaque élément.

### Le Reel (@stephlovesdigital, 12/09/2026) — [Praticien, non vérifié]

⚠️ **Je n'ai pas pu regarder la vidéo** : Instagram ne sert qu'une coquille et je ne traite pas de contenu vidéo. **Ce que j'ai, c'est la légende**, récupérée au navigateur, qui énonce la thèse explicitement :

> « The open loop is what keeps people watching, and you have to run it twice. One open loop gets curiosity. Two gets commitment. »

C'est la mécanique décrite ci-dessus, et elle tient debout toute seule : un spectateur sans question en cours n'a aucune raison structurelle de rester. **Mais c'est l'affirmation d'une praticienne, pas une donnée.** Deux réserves honnêtes :

1. Le compte affiche **2 815 commentaires pour 2 525 j'aime** — plus de commentaires que de likes. C'est la signature d'un appât à commentaire : la légende dit « Comment SCRIPT and I'll send you… ». **Ces chiffres ne prouvent donc pas que la technique de rétention marche** ; ils prouvent que le mot-clé marche. Ne pas les citer comme preuve.
2. Le mécanisme rappelle l'**effet Zeigarnik** (une tâche inachevée occupe l'attention). ⚠️ Cet effet est **mal répliqué** en psychologie expérimentale : je ne l'invoque pas comme caution scientifique, seulement comme origine de l'idée.

**Verdict : à adopter**, parce que la logique est vérifiable par vous-même sur vos propres courbes de rétention — pas parce qu'une source l'affirme. C'est d'ailleurs le seul test qui vaille (§6).

### Le guide Orcalynx — [Partiellement utile, avec deux refus]

**Ce qu'il est vraiment** : un aimant à prospects d'agence. Le bundle contient des encarts `InlineCTA` répartis dans tout le guide (« Orcalynx researches your niche outliers and writes every hook for you »), et la dernière section s'appelle *Work With Me*. Ça ne le disqualifie pas, mais ça explique ses silences.

**Zéro source. Vérifié ligne par ligne :** les seuls pourcentages du guide sont **dans ses propres exemples de scripts** (« 90 % of traders miss… », « 80 % of trading success is psychology »), c'est-à-dire des chiffres d'accroche inventés, pas des preuves. Les mots *study*, *research* et *source* n'apparaissent que dans des noms de gabarits, des modèles de phrase, ou l'argumentaire de vente. **Aucune donnée, aucune citation, aucune mesure.**

Conséquence : ses affirmations hiérarchiques sont **invérifiables et parfois contradictoires** — *How-To* est « the safest angle », *Listicle* « the safest format to go viral », *Storytelling* a « the highest watch time of any angle ». Trois superlatifs incompatibles, aucun étayé.

**✅ Ce qu'on prend** — les **10 squelettes de script**, qui sont son vrai apport. Ce sont des structures battue par battue, et plusieurs portent nativement une boucle longue :

| Squelette | Pourquoi il tient la rétention |
|---|---|
| **Three Levels** | le spectateur s'identifie au niveau 1 ou 2 et reste pour le 3 |
| **Two People** | deux trajectoires ouvertes, résolues seulement à la fin |
| **Is It Possible** | la question du titre reste ouverte par construction |
| **Did You Know** | croyance fausse posée, correction différée |
| **Rapid-Fire** | « …et le plus important » garde un item en réserve |

Ces cinq-là sont **compatibles** avec notre arc et nos garde-fous. Les cinq autres (*Rating*, *Visual Indicator*, *If You*, *React & Rate*, *Transformation*) demandent soit un registre d'opinion, soit une preuve de résultat : à écarter ou à manier avec prudence.

**🔴 Ce qu'on refuse, et pourquoi :**

1. **Le truc ManyChat.** Le guide écrit, mot pour mot : *« Use ManyChat to auto-DM anyone who comments a keyword. **This tricks the algorithm** into thinking your content drives conversations. »* C'est une manipulation d'engagement assumée. Même catégorie que les backlinks automatiques déjà refusés (`CLAUDE.md` §6bis) : Meta démote l'appât à engagement, et le risque porte sur le compte qui finance les ADS. **S'y ajoute un problème RGPD** : collecter des contacts par message privé automatisé, pour un organisme de formation, demande une base légale et une information préalable qui n'existent pas ici.
2. **Le registre.** Tous les exemples viennent du *fitness* et du *trading* — les deux niches où la promesse de résultat est la norme (« 4 trade setups that print money on Monday mornings »). Transposer ce registre chez un organisme certifié Qualiopi déclenche mécaniquement les interdits de `CLAUDE.md` §4 et §7bis. **Les squelettes se prennent ; les exemples ne se traduisent pas.**
3. **Les CTA** du type « DM me READY if you want to work together » sautent au niveau 4 de conscience et violent `A2` R2 (on ne nomme pas l'offre en contenu de valeur).

**Un point d'accord utile**, à verser au dossier : la liste de contrôle du guide impose *« my script runs under 60 seconds when read out loud »*. C'est cohérent avec ce que `A2` §2 avait établi sur une base autrement plus solide — 9 771 822 Reels, pic simultané engagement + vues à 45-60 s.

---

## 5. Ce qui change dans le contrôle

`controle-scripts.py` vérifie l'arc, les formulations bannies et les promesses. Il ne voyait pas la rétention. Deux règles s'ajoutent, et un champ `boucles` apparaît dans les JSON :

- **L1** — chaque script déclare **deux boucles** (`A` et `B`) avec leur temps d'ouverture et de fermeture.
- **L2** — **A doit se refermer au temps 4 ou 5**, jamais au temps 3. Une boucle A refermée en transmission rouvre le trou de rétention et bloque la livraison.
- **L3** — toute boucle ouverte doit être refermée. Une boucle B sans fermeture est une erreur bloquante, pas un avertissement.

---

## 6. Comment savoir si ça marche — la seule mesure qui compte

Aucune des deux sources n'apporte de preuve. **La preuve, vous l'avez déjà** : Instagram donne la courbe de rétention de chaque Reel.

**Protocole, 6 vidéos :**

1. Trois scripts en version actuelle (boucle unique refermée au temps 3), trois en version décalée. **Même sujet, même persona, même format** — sinon on mesure le sujet, pas la structure.
2. Relever, sur la courbe de rétention : la **valeur à 15 s** et la **valeur à 40 s**. C'est entre les deux que la structure agit ; le taux à 3 s mesure l'accroche, pas la rétention.
3. Publier en alternance, aux mêmes créneaux, sur deux semaines.

**Ce qui vaudrait décision :** un écart net et répété sur la rétention à 40 s. Un écart sur les vues ne prouve rien — il dépend surtout de la distribution initiale.

⚠️ **Six vidéos ne font pas un test statistique.** C'est un faisceau d'indices, pas une démonstration — à traiter comme tel, et à ne jamais publier comme un résultat chiffré.

---

## 7. Résumé opérationnel

1. **Deux boucles, décalées.** B s'ouvre avant que A se referme.
2. **A se referme au temps 4**, jamais au temps 3. C'est la correction unique à apporter aux 30 scripts.
3. **Jamais « restez jusqu'à la fin »** : la boucle le dit mieux.
4. **Toute boucle ouverte se referme** dans la vidéo.
5. Des squelettes d'Orcalynx, on prend les **cinq** qui portent une boucle longue ; on refuse le ManyChat, le registre fitness/trading et ses CTA.
6. On mesure la **rétention à 40 s**, pas les vues.

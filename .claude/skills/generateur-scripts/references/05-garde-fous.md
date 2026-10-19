# Garde-fous — ce que le générateur refuse d'écrire

> Un générateur qui produit une formulation interdite ne fait pas gagner du
> temps : il crée un risque que son utilisateur ne voit pas. Cette passe est
> donc bloquante, et c'est aussi ce qui distingue cet outil d'un assistant
> généraliste.

## Niveaux

| Niveau | Signification | Action |
|---|---|---|
| 🔴 **Blocage** | Le script ne sort pas en l'état | Réécriture obligatoire |
| 🟠 **Alerte** | Le script sort, signalé | L'utilisateur tranche en connaissance de cause |

---

## 🔴 Blocages universels

### Promesse de résultat

Aucun script ne promet un résultat commercial chiffré ou garanti.

Interdit : « +30 % de clients », « des résultats garantis », « vous allez
doubler votre chiffre », « résultats assurés dès le premier mois ».

Pourquoi : c'est une allégation invérifiable. En publicité, elle expose à la
qualification de pratique commerciale trompeuse.

**Remplacer par** la description de ce qui est réellement fourni :
*« vous repartez avec vos premières vidéos et une méthode »*.

### Chiffre sans source

Tout pourcentage, classement ou statistique doit avoir une source nommée,
sinon il saute. Un chiffre inventé pour faire joli est une faute avant d'être
une maladresse.

### Le cas particulier de la formation professionnelle

Ces formulations sont interdites dès que le script parle d'une formation
financée :

`gratuit` · `100 % financé` · `sans reste à charge` · `formation offerte` ·
`0 €` · `cadeau` · `financé intégralement` · `ne vous coûte rien`

Pourquoi : les fonds de formation ne couvrent jamais la totalité, et ce type
de promesse est précisément ce que la réglementation anti-fraude vise.

**Remplacer par** : *« finançable (AGEFICE, FAFCEA, OPCO), reste à charge
annoncé au devis »*.

> ⚠️ Ces termes restent **autorisés** s'ils portent sur autre chose qu'une
> formation financée — un diagnostic réellement offert, une livraison
> réellement gratuite. Le blocage porte sur le couple formation + gratuité.

### Secteurs à ne pas servir

Santé, droit, et tout métier à ordre professionnel : la communication y est
encadrée par des règles propres que ce générateur ne connaît pas. Mieux vaut
refuser que produire un script non conforme.

---

## 🟠 Alertes

### Vocabulaire « emploi » (contexte publicitaire)

`reconversion` · `employabilité` · `diplôme` · `carrière` · `trouver un emploi`

Pourquoi : sur les plateformes publicitaires, ces termes peuvent faire
classer l'annonce en catégorie spéciale, ce qui restreint fortement le
ciblage — y compris le ciblage local.

### Secteurs réglementés

Assurance, immobilier, crédit, alimentaire, cosmétique : mentions obligatoires
et allégations encadrées. Signaler et rappeler de vérifier.

### Mention « Publicité »

Si le contenu est sponsorisé ou si la personne qui le présente est rémunérée
pour le faire, la mention est obligatoire. L'ajouter automatiquement.

### Personnes identifiables

Dès qu'un client, un salarié ou un passant est reconnaissable, un accord écrit
est nécessaire. Le rappeler sur chaque script concerné.

---

## 🔴 Producibilité — le blocage qu'on oublie

Chaque plan proposé doit figurer dans la liste de ce que la personne a déclaré
pouvoir filmer (question Q11 de l'entretien).

Un script qui demande un drone, une équipe ou un client qui témoigne alors
que rien de tout cela n'est disponible **ne sera jamais tourné**. Ce n'est pas
un détail de confort : c'est la différence entre dix scripts livrés et zéro
vidéo produite.

**Si un plan sort de la liste : le remplacer**, ne pas se contenter de le
signaler.

De même, si la personne a déclaré ne pas être à l'aise face caméra, aucun
script ne doit en comporter — même « juste une phrase face caméra à la fin ».

---

## 🟠 Unicité

Un script = un angle = un persona. Deux scripts qui traitent le même angle
pour le même persona sont un seul script écrit deux fois.

Vérifier aussi qu'aucune accroche n'est utilisée deux fois dans la série.

---

## Procédure de contrôle

Pour chaque script, dans cet ordre :

1. **Recherche textuelle** des formulations interdites, sans sensibilité à la
   casse ni aux accents
2. **Lecture** à la recherche de promesses implicites — une promesse se
   formule rarement avec les mots de la liste
3. **Vérification des chiffres** : chacun a-t-il une source ?
4. **Vérification des plans** contre les moyens déclarés
5. **Vérification de l'unicité** angle × persona sur la série entière
6. **Notation** selon `06-notation.md`

Un script qui échoue en 🔴 est réécrit, puis repasse le contrôle complet. Pas
de sortie partielle : un script non conforme ne se livre pas « avec un
avertissement ».

## Format du rapport

```
SCRIPT 03 — « Le devis d'agence »
  🔴 ligne 4 : « résultats garantis » → réécrit en « ce que vous repartez savoir faire »
  🟠 plan 2 : client identifiable → accord écrit requis
  ✅ formulations · chiffres · producibilité · unicité
  Note : 78/100
```

# Liens entrants — opportunités réelles et dossier prêt à soumettre

> **Ce que j'ai fait, ce que je n'ai pas fait.** J'ai identifié et vérifié les
> sources de liens légitimes pour un organisme de formation de l'Hérault, et
> préparé les éléments à soumettre. Je n'ai **créé aucun compte et envoyé
> aucune inscription** : chacune engage l'identité de VFormations et demande
> tes identifiants. Les démarches ci-dessous sont donc à faire par toi, mais
> le contenu est écrit — il n'y a plus qu'à copier-coller.
>
> Aucune technique artificielle n'est proposée ici. Pas d'achat de liens, pas
> d'annuaire de complaisance, pas d'échange croisé. Ces méthodes se détectent
> et exposent le site plutôt qu'elles ne l'aident.

---

## 0. La décision qui bloque tout le reste

**Une seule adresse publique, écrite de façon identique partout.** Aujourd'hui
le dépôt contient deux adresses :

| Où | Quoi | Statut |
|---|---|---|
| Mentions légales | 47 rue Vivienne, 75002 Paris | **Siège social — obligation légale, à garder** |
| Schema.org du site | Hérault (région seule) | Corrigé ; était « 75002 Paris », ce qui disait à Google « entreprise parisienne » |
| Fiche Google | *(inconnue de moi)* | **À relever** |

Avant toute inscription, relève l'adresse exacte affichée sur ta fiche Google
et renseigne-la dans `seo.json` :

```json
"villeBase": "Montpellier",        ← la commune, écrite COMME sur la fiche
"codePostalBase": "34000"
```

Dès que ces deux champs sont remplis, le site déclare automatiquement un
établissement local (`LocalBusiness`) au lieu d'une simple organisation —
c'est un signal que Google traite différemment.

**Si tu n'as pas de local recevant du public** (tu te déplaces chez les
clients) : laisse ces champs vides, et déclare des **zones desservies** sur la
fiche Google plutôt qu'une adresse. C'est plus exact et mieux traité qu'une
adresse affichée à tort.

**Puis renseigne les horaires** dans `seo.json`. Être ouvert au moment où
quelqu'un cherche est devenu l'un des premiers facteurs de classement local :
laisser ces champs vides, c'est renoncer à un levier gratuit.

```json
"horairesJours": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
"horairesDebut": "09:00",
"horairesFin": "18:00"
```

---

## 1. Priorité absolue — les référencements de droit

Ce sont les meilleurs liens possibles : domaines institutionnels, sans frais,
et ils te sont **ouverts parce que tu es un organisme déclaré**. Aucun autre
levier n'a ce rapport effort / autorité.

### 1.1 Carif-Oref Occitanie — `organismes.cariforefoccitanie.fr`

**Le plus rentable de toute cette liste.** Le Carif-Oref régional référence
l'offre de formation des organismes de la région, sans frais. L'intérêt est
double :

- une mention sur un domaine régional de référence ;
- et surtout, ton offre entre dans les **outils de prescription** utilisés par
  **France Travail** et les **Missions locales**. Ce n'est plus du
  référencement, c'est un canal de distribution.

| | |
|---|---|
| Portail | `organismes.cariforefoccitanie.fr` |
| Contact offre | `offre@cariforefoccitanie.fr` |
| Coût | aucun |
| À prévoir | NDA, SIRET, certificat Qualiopi, descriptif de chaque action |

> Le Carif-Oref a une mission de **collecte exhaustive** de l'offre régionale,
> et déclarait en 2023 chercher activement les organismes non encore
> référencés. Autrement dit : ta demande est attendue, pas subie.

### 1.2 Liste publique des organismes de formation — `data.gouv.fr`

Publiée par le ministère du Travail au titre de l'**article L.6351-7-1** du
Code du travail, mise à jour **quotidiennement**. Elle recense les organismes
déclarés auprès du préfet de région **et à jour de leur bilan pédagogique et
financier (BPF)**, et signale les titulaires d'une certification qualité en
cours de validité ainsi que les catégories d'actions couvertes.

**Ce n'est pas une inscription : c'est une conséquence.** Tu y figures
automatiquement si ta déclaration est active et ton BPF déposé.

**À vérifier — je n'ai pas pu le faire :** le domaine `data.gouv.fr` est
inaccessible depuis l'environnement où je travaille (DNS bloqué par le proxy).
La vérification te prend deux minutes :

1. Ouvre le jeu « Liste Publique des Organismes de Formation » sur data.gouv.fr
2. Cherche le **NDA `11757618175`**, ou le SIREN `103 940 227`
3. Contrôle que les colonnes de certification mentionnent bien « actions de
   formation »

Si tu n'y figures pas, la cause est presque toujours le **BPF non déposé** —
et c'est important bien au-delà du référencement, puisque l'absence de BPF
rend la déclaration caduque.

### 1.3 Autres registres selon l'évolution de l'offre

- **Mon Compte Formation (EDOF)** — seulement si une action devient éligible
  au CPF. Ce n'est pas le cas aujourd'hui, et il ne faut pas s'y engager pour
  le lien : le référencement y suppose une certification RS ou RNCP.
- **La Bonne Formation / France Travail** — alimenté en partie par les
  Carif-Oref. Le 1.1 travaille donc déjà pour toi ici.

---

## 2. Le territoire — réseaux économiques de l'Hérault

Deuxième famille, et la plus sous-exploitée par les petites structures. Ces
réseaux publient des annuaires d'adhérents, des comptes rendus, des pages
partenaires : des mentions sur des sites installés et géographiquement
cohérents avec la cible.

| Interlocuteur | Pourquoi | Entrée |
|---|---|---|
| **CCI Hérault** | Annuaire des réseaux économiques du département ; point d'entrée naturel pour savoir qui fait quoi | Zone aéroportuaire Montpellier-Méditerranée, CS 90066, 34137 Mauguio Cedex · 04 99 51 52 00 · `info@herault.cci.fr` |
| **Chambre de métiers et de l'artisanat** | La cible artisan est au cœur de l'offre (FAFCEA) | Via la CMA Occitanie, antenne Hérault |
| **Réseaux économiques locaux** | La CCI les recense par territoire (Pic Saint-Loup, bassin de Thau, Béziers…). Cotisations souvent modestes | Rubrique « Les Réseaux économiques de l'Hérault » du site de la CCI |
| **CPME Hérault · MEDEF Hérault · U2P** | Représentation TPE/PME, exactement la cible | Adhésion directe, modalités à demander |

**Ce que ça rapporte vraiment.** Le lien est un bonus. Ce que ces réseaux
produisent, ce sont des **rencontres**, et une rencontre produit parfois un
client — ce qu'aucun annuaire payant ne fera jamais.

> ⚠️ L'annuaire des réseaux économiques que j'ai trouvé en ligne est l'**édition
> 2022**. Les cotisations et les contacts qu'il cite ont pu changer. Demande
> l'édition courante avant de t'appuyer sur ces chiffres.

---

## 3. Les contenus qui attirent les liens sans les demander

C'est le levier le plus lent et le seul qui compose dans le temps. Un contenu
qu'on cite est un contenu qui répond à une question précise mieux que les
autres. Trois pistes que le Mag permet déjà :

1. **Les articles de financement tiennent cette promesse.** Les pages sur le
   [taux transverse FAFCEA](https://vformations.fr/mag/fafcea-taux-transverse-numerique/),
   le [calcul du reste à charge](https://vformations.fr/mag/reste-a-charge-formation/)
   et les [causes de refus](https://vformations.fr/mag/refus-prise-en-charge-formation/)
   corrigent des erreurs très répandues, avec des chiffres sourcés. Ce sont
   elles qu'un confrère ou un expert-comptable citera.
2. **Un outil simple vaut dix articles.** Un calculateur de reste à charge, qui
   demande le fonds, le nombre d'heures, la modalité et le plafond restant,
   serait l'actif le plus citable du site. À chiffrer : c'est un vrai
   développement, pas un article.
3. **Les données locales.** Un recensement des Points d'Accueil AGEFICE de
   l'Hérault, tenu à jour, serait utile à tout le département — et c'est
   précisément le genre de page que d'autres sites reprennent. À condition de
   le maintenir : une liste périmée fait plus de mal que pas de liste.

---

## 4. Presse et médias locaux

À n'aborder qu'avec un sujet réel, jamais avec une annonce d'entreprise.

| Média | Angle qui peut passer |
|---|---|
| **Midi Libre** (édition Hérault) | Un sujet pratique : ce que les dirigeants ignorent de leurs droits à la formation |
| **Hérault Tribune** | Même logique, ancrage Agde / Béziers |
| **ToulÉco · Objectif Languedoc-Roussillon** | Presse économique régionale : création d'organisme, Qualiopi, chiffres du département |
| **Radios et podcasts locaux** | Format interview, plus accessible qu'un article de presse |

**Le seul angle qui fonctionne** : apporter une information utile à leurs
lecteurs, pas parler de soi. Le piège du taux FAFCEA à 25 €/h confondu avec
35 €/h, ou le plafond AGEFICE de 5 000 € réservé aux titres RNCP, sont des
sujets d'intérêt général pour un lectorat de dirigeants.

---

## 5. Ce qu'il faut refuser

- **L'appel sortant** qui propose une inscription « avant la clôture de
  l'édition ». L'urgence est fabriquée.
- **Les offres de « X centaines de liens ».** Relèvent des pratiques que les
  moteurs neutralisent explicitement.
- **Les annuaires sans audience propre** — pas de contenu éditorial, des
  catégories vides.
- **Toute inscription que tu ne pourras pas mettre à jour.** Une fiche figée
  devient un jour une fiche fausse, et une fiche fausse travaille contre toi.
- **Les mots-clés dans le nom de l'établissement.** Avantage réel, risque de
  suspension réel aussi. Le gain ne vaut pas la fiche.

**Le test qui tranche** : *cet annuaire existerait-il si le référencement
n'existait pas ?* Registre officiel, chambre consulaire, plateforme métier :
oui. Annuaire créé pour vendre des liens : non.

---

## 6. Le bloc d'identité à recopier partout

**Recopie-le sans le réécrire.** La valeur vient de l'identité stricte entre
toutes les sources — une variation, et le signal s'affaiblit au lieu de se
renforcer.

```
Nom              VFormations
Nom commercial   Voxy Formations   (nom figurant sur le certificat Qualiopi)
SIREN            103 940 227
SIRET (siège)    103 940 227 00012
APE              85.59A — formation continue d'adultes
NDA              11757618175
Qualiopi         VFO12912026001 — catégorie « actions de formation » (L.6313-1 1°)
                 délivré par evolve, accréditation Cofrac n° 5-0670
                 valable du 31/07/2026 au 30/07/2029
TVA              FR31 103 940 227
E-mail           contact@vformations.fr
Téléphone        07 63 67 82 92
Site             https://vformations.fr
Zone             Hérault (34) et Occitanie
Adresse publique ⚠️ À FIXER — voir §0. Doit être identique à la fiche Google.
```

### Descriptif court (160 caractères — annuaires, méta)

> Organisme de formation certifié Qualiopi dans l'Hérault. Formations-action
> en vidéo, site internet, boutique en ligne et prospection B2B pour
> dirigeants de TPE.

### Descriptif moyen (environ 400 caractères — fiches d'annuaire)

> VFormations est un organisme de formation certifié Qualiopi, basé dans
> l'Hérault et intervenant sur l'ensemble du département et de l'Occitanie.
> Nous formons les dirigeants de très petites entreprises — commerçants,
> artisans, restaurateurs, professions libérales — à la visibilité locale par
> la vidéo, à la création de site internet, à la boutique en ligne et à la
> prospection B2B. Nos parcours sont courts, construits sur l'activité réelle
> du stagiaire, et finançables selon son statut (AGEFICE, FAFCEA, FIF PL,
> OPCO).

### Descriptif long (environ 900 caractères — Carif-Oref, presse)

> VFormations est un organisme de formation déclaré sous le numéro 11757618175
> et certifié Qualiopi au titre des actions de formation (certificat
> VFO12912026001, délivré par evolve). Implanté dans l'Hérault, il intervient
> auprès des dirigeants de très petites entreprises du département et de la
> région Occitanie : commerçants, artisans, restaurateurs, salons, professions
> libérales.
>
> L'offre couvre quatre domaines : le développement de la visibilité locale par
> la vidéo, la création et le pilotage d'un site internet, la mise en place
> d'une boutique en ligne, et la structuration de la prospection commerciale
> B2B.
>
> La pédagogie repose sur la formation-action : chaque stagiaire travaille
> pendant la session sur sa propre activité, et repart avec un livrable
> utilisable — sa fiche d'établissement optimisée, son site en ligne, ses
> premières vidéos publiées. Les parcours sont finançables selon le statut du
> dirigeant et son fonds de rattachement.

---

## 7. Tableau de suivi

À tenir à jour : c'est lui qui servira le jour d'un changement de coordonnées.

| Source | Type | Fait le | Informations publiées | Vérifié le |
|---|---|---|---|---|
| Fiche Google | Établissement | | | |
| Carif-Oref Occitanie | Registre régional | | | |
| Liste publique des OF | Registre national | *(automatique)* | | |
| CCI Hérault | Réseau | | | |
| CMA Occitanie | Réseau | | | |
| Réseau économique local | Réseau | | | |
| CPME ou MEDEF Hérault | Réseau | | | |
| | | | | |

---

## 8. Dans quel ordre, concrètement

| Quand | Quoi | Durée |
|---|---|---|
| **Cette semaine** | Relever l'adresse de la fiche Google, remplir `villeBase`, `codePostalBase` et les horaires dans `seo.json` | 15 min |
| **Cette semaine** | Vérifier la présence dans la liste publique des OF (NDA 11757618175) | 5 min |
| **Cette semaine** | Demander le référencement au Carif-Oref Occitanie | 1 h |
| **Ce mois** | Appeler la CCI Hérault : réseaux économiques et Point d'Accueil AGEFICE du département | 1 h |
| **Ce mois** | Chercher « VFormations » et l'ancien numéro de téléphone dans Google, corriger ce qui traîne | 30 min |
| **Ce trimestre** | Une adhésion à un réseau local | — |
| **Ce trimestre** | Un contact presse locale, avec un sujet, pas une annonce | — |

**L'ordre n'est pas négociable sur le premier point.** Multiplier les
inscriptions avant d'avoir fixé l'adresse publique, c'est diffuser une
incohérence sur dix sites au lieu d'un.

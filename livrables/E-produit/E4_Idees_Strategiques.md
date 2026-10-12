# E4 — Analyse libre : 10 opportunités non sollicitées

> **Casquette : PDG.** Ce document n'a été demandé par aucune consigne précise — c'est l'exercice de regarder le dossier et de dire **ce que je ferais si c'était mon entreprise**.
> **Date : 12 octobre 2026.**
> **Méthode :** j'ai cherché (a) les actifs qu'on construit pour nous-mêmes et qui ont une valeur pour d'autres, (b) les contraintes réglementaires qui sont des barrières pour les concurrents, (c) les canaux de distribution que personne ne travaille, (d) les angles morts du dossier.

---

# 🥇 IDÉE 1 — Vendre le moteur de preuves Qualiopi aux autres organismes de formation

> **C'est probablement une opportunité plus grande que le métier de formation lui-même.**

### Le constat
Trois faits se sont alignés en 2026, et personne ne semble en avoir tiré les conséquences :

| Fait | Source |
|---|---|
| **14 274 organismes de formation en Occitanie**, +13 %/an, dont **~28 % certifiés Qualiopi** | Étude de marché interne |
| La loi anti-fraude **2026-534** élargit les cas où une action est **réputée inexécutée** → remboursement des fonds | [Vérifié] |
| Les **DREETS prononcent désormais directement** des amendes administratives, **sans passer par le procureur**, avec publication possible des sanctions | [Vérifié] |
| **Qualiopi est obligatoire pour tout financement FAFCEA depuis le 1/7/2026** | [Vérifié] |

**Traduction :** des milliers d'organismes viennent de voir leur risque juridique changer de nature. Leur problème n°1 n'est plus de vendre — c'est de **prouver**.

### L'idée
Nous construisons de toute façon le **moteur de preuves Qualiopi** (`E0` module ⑨) pour notre propre usage : journal d'activité horodaté, analyse d'activité AFEST, phases réflexives tracées, grilles d'évaluation générées.

> **C'est un produit, pas un outil interne.**

| | Notre produit TPE | Produit « OF » |
|---|---|---|
| Cible | Dirigeants de TPE | Organismes de formation |
| Nombre en Occitanie | ~30 000 | **~14 274** |
| Capacité à payer | Faible | **Élevée** (c'est leur licence d'exploitation) |
| Douleur | « je ne sais pas quoi publier » | **« un contrôle peut me coûter mon agrément »** |
| Cycle de vente | Long, pédagogique | **Court — la peur vend vite** |

### Pourquoi nous et pas un éditeur classique
Les logiciels de gestion d'organismes existants sont des outils administratifs conçus **avant** la loi. Nous construisons **après**, nativement sur les 4 conditions cumulatives de l'AFEST. Et surtout : **nous sommes nous-mêmes un OF certifié qui passe les audits.** Crédibilité qu'aucun éditeur pur n'a.

### Le risque
⚠️ Dispersion. C'est un autre métier, une autre cible, un autre cycle de vente. **À ne pas lancer avant 12 mois.** Mais **à concevoir dès maintenant dans l'architecture** : si le module ⑨ est construit multi-locataire dès le départ, le coût de bascule est quasi nul. S'il est codé en dur pour nous, il faudra tout refaire.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🔵 Faible aujourd'hui (une décision d'architecture) · Élevé plus tard | 🔴 **Très élevé** | ✅ **Construire le module ⑨ en multi-locataire dès la v1.** Décision gratuite aujourd'hui, option ouverte pour demain. |

---

# 🥈 IDÉE 2 — Les courtiers en assurance comme réseau de distribution (pas comme clients)

### Le constat
Tu as créé le persona « Marc, courtier en assurance » comme **cible**. C'est une erreur de cadrage : **un courtier est d'abord un canal**.

Un courtier d'assurance professionnelle local a **200 à 500 TPE en portefeuille**. Il les voit une fois par an. Il cherche en permanence des raisons de les rappeler qui ne soient pas une hausse de tarif.

### L'idée
**Un courtier = 200 à 500 prospects qualifiés, avec une introduction chaude.** Dix courtiers partenaires dans l'Hérault = la totalité du marché adressable identifié en `D1` §6bis.

**La proposition au courtier :**
> *« Je fais un webinaire de 45 minutes pour vos clients sur la visibilité locale. Vous l'organisez, c'est vous qui leur apportez de la valeur. Je ne vends rien pendant. Ceux qui veulent aller plus loin prennent un diagnostic avec moi. »*

Il y gagne : un motif de contact valorisant, une image de conseiller, zéro effort.

### Pourquoi ça marche mieux que la publicité
| | Publicité Meta | Courtier prescripteur |
|---|---|---|
| Coût par rendez-vous | 120-250 € | **~0 €** |
| Confiance initiale | Nulle | **Transférée** |
| Qualification | À faire | **Déjà faite** (il connaît leur situation) |

### Le risque
Cycle d'amorçage lent (2-3 mois pour le premier webinaire). À lancer **tout de suite** pour cette raison.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🟢 Faible | 🔴 **Très élevé** | ✅ **À démarrer cette semaine.** Reclasser Marc de « persona » à « partenaire » dans `A0`. |

---

# 🥉 IDÉE 3 — Le diagnostic automatisé : un seul outil, quatre usages

### Le constat
On prévoit un « diagnostic de visibilité » comme outil de vente (`D2` §4). On sous-estime ce qu'il est réellement.

### L'idée
Un diagnostic **automatisé, gratuit, sans rendez-vous** : le dirigeant saisit le nom de son entreprise, reçoit en 2 minutes un rapport sur sa fiche Google Business, son site, ses réseaux — **comparé à 3 concurrents locaux réels**.

**Il sert quatre fois :**

| # | Usage | Valeur |
|---|---|---|
| 1 | **Aimant à prospects** à coût marginal nul | Le seul contenu d'acquisition qui scale sans temps humain |
| 2 | **Outil de vente** en rendez-vous — on lui *montre* son problème au lieu de le lui décrire | Taux de transformation |
| 3 | 🔑 **L'autodiagnostic préalable exigé par le FAFCEA** pour le parcours individualisé à 80 €/h (`D1` §2bis) | **Débloque le dispositif le plus rémunérateur** |
| 4 | **Mesure d'impact à J+90** — refaire le diagnostic après la formation produit un **indicateur de résultat Qualiopi objectif** (ind. 2) | Preuve chiffrée, non déclarative |

> 💡 **L'usage n°4 est le plus précieux et personne ne le fait.** La quasi-totalité des OF publient des taux de satisfaction déclaratifs. Nous pourrions publier une **progression mesurée**. C'est un argument d'audit **et** un argument de vente.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🟡 Moyen | 🔴 **Très élevé** | ✅ **Prioritaire en v1.** Quatre problèmes résolus par un seul module. |

---

# IDÉE 4 — La saisonnalité : vendre quand ils ont mal

### Le constat
Nos cibles ont des cycles d'activité violents et **parfaitement prévisibles**. Aucun concurrent n'en tient compte : ils vendent uniformément toute l'année.

| Mois | Restauration / commerce | Artisan BTP | **Notre action** |
|---|---|---|---|
| **Janvier-février** | 🔻 Creux maximal, trésorerie tendue, **temps disponible** | 🔻 Creux hivernal | 🎯 **Fenêtre de vente n°1** — ils ont le temps ET ils ont mal |
| Mars-mai | Reprise | Haute activité | Vente pour septembre |
| Juin-août | 🔺 Saturation | 🔺 Saturation | ❌ **Ne rien vendre.** Produire, préparer |
| **Septembre-octobre** | 🔻 Chute post-saison | Reprise | 🎯 **Fenêtre de vente n°2** |
| Nov-déc | Fêtes | 🔻 Creux | Vente pour janvier |

### L'idée
**Caler le calendrier des cohortes sur la douleur**, pas sur notre confort :
- **Cohortes de janvier et de septembre** = les deux grosses promotions
- **Juin-août** = zéro effort commercial, on produit les contenus et on forme les partenaires
- Le message change : en janvier, *« c'est maintenant que vous avez le temps »* ; en septembre, *« préparez la saison prochaine »*

> ⚠️ **Conséquence immédiate sur `D2` :** la roadmap 90 jours démarre en novembre et vise une cohorte fondatrice en janvier. **C'est le bon timing** — à condition que les dossiers AGEFICE soient déposés **15 jours avant minimum, via un Point d'Accueil**.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🟢 Nul (une décision de calendrier) | 🟠 Élevé | ✅ **Acter le calendrier maintenant.** |

---

# IDÉE 5 — L'engagement de moyens renforcé (au lieu d'une garantie de résultat interdite)

### Le constat
On ne peut pas garantir un résultat (interdit, `D3` §1.3). Mais l'objection n°1 reste : *« et si ça ne marche pas ? »* Tout le monde la subit, personne ne la traite.

### L'idée
Garantir **notre** engagement, pas **leur** résultat :

> **« Si à la fin du parcours vous n'avez pas produit et publié vos 12 vidéos, on vous reprend dans la session suivante, sans frais supplémentaires. »**

### Pourquoi c'est malin
| Avantage | Détail |
|---|---|
| ⚖️ **Juridiquement propre** | C'est un engagement sur **notre prestation**, pas sur un résultat commercial. Aucune formulation bannie. |
| 🎯 **Ça force l'activation** | Le client sait qu'on l'attend sur un livrable concret. **C'est exactement ce que la courbe de décrochage de `E0` §1 cherche à casser.** |
| 📊 **Ça produit la preuve** | « 12 vidéos publiées » est un indicateur de résultat objectif, publiable au titre de l'indicateur 2. |
| 💰 **Le coût réel est faible** | Une place supplémentaire dans une cohorte déjà lancée a un coût marginal quasi nul (le formateur est déjà payé). |

### Le risque
⚠️ À cadrer : **conditionné à l'assiduité** (présence aux séances, remise des travaux). Sinon on offre une session à qui n'a rien fait. À écrire dans les CGV.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🟢 Faible | 🟠 Élevé | ✅ **À intégrer aux CGV et à l'argumentaire.** |

---

# IDÉE 6 — L'émission locale : le cheval de Troie du réseau

### Le constat
On a besoin de trois choses difficiles à obtenir : **de la notoriété locale**, **un réseau de prescripteurs**, **du contenu**. On les traite séparément. Un seul format les produit simultanément.

### L'idée
Une **émission locale régulière** : 20 minutes d'entretien avec un dirigeant de TPE héraultais sur son métier. Diffusée en extraits vidéo + version audio.

**Ce que ça produit, par épisode :**
1. 📞 **Une raison légitime d'appeler n'importe quel dirigeant** — personne ne refuse une interview sur son métier (vs tout le monde refuse un rendez-vous commercial)
2. 🤝 **L'interviewé devient prospect ou prescripteur** — il a passé 20 minutes avec nous, en confiance
3. 🎬 **5 à 8 extraits vidéo** par épisode → notre propre présence
4. 📈 **Du contenu longue traîne** pour le SEO local déjà construit
5. 🏆 **Une démonstration vivante de notre savoir-faire** : on ne dit pas qu'on sait filmer, on le montre

### Pourquoi c'est sous-estimé
C'est le seul format où **la prospection ne ressemble pas à de la prospection** — et où le refus est socialement improbable.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🟠 Moyen (régularité à tenir) | 🟠 Élevé | ✅ **Démarrer à 1 épisode / 2 semaines.** Ne pas promettre plus. |

---

# IDÉE 7 — Déverrouiller la géographie par le distanciel synchrone

### Le constat
`D1` §6bis le démontre : **le marché héraultais plafonne à 400-700 k€/an**, soit ~100 k€/an pour nous à 15 % de part. **Le positionnement local est un excellent point de départ et un plafond.**

### L'idée
Le **distanciel synchrone** est financé par l'AGEFICE à **35 €/h** (contre 42 €/h en présentiel) — soit **−17 % de financement, mais −100 % de coût de déplacement et de salle**.

| | Présentiel Hérault | Distanciel synchrone France |
|---|---|---|
| Financement 35 h | 1 470 € | 1 225 € |
| Déplacements + salle | ~600 €/session | **0 €** |
| Marché adressable | ~30 000 entreprises | **~2 millions** |

> 💡 **Le distanciel n'est pas une dégradation : c'est le même métier, sans les frais, sur un marché 50× plus grand.**

### ⚠️ Les deux limites à respecter
1. ❌ **Interdit pour le parcours individualisé FAFCEA** (le 100 % distanciel disqualifie, `D1` §2bis). Les deux relais sont donc **complémentaires**, pas substituables.
2. ⚠️ Le positionnement « on vient filmer chez vous » **ne se transpose pas**. Il faut une **offre distincte**, pas une version dégradée. *« Visibilité locale »* en présentiel dans l'Hérault, *« autonomie vidéo »* en distanciel partout.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🟡 Moyen | 🔴 Très élevé | ✅ **À préparer en an 1, à activer en an 2.** Ne pas diluer l'ancrage local avant la preuve. |

---

# IDÉE 8 — Courtiser les Points d'Accueil AGEFICE

### Le constat
> **L'AGEFICE n'instruit aucun dossier qui ne transite pas par un Point d'Accueil.** [Vérifié]

C'est un **goulot institutionnel absolu** sur notre financeur prioritaire. Et c'est un angle mort total : aucun concurrent observé ne travaille cette relation — tous renvoient le client vers son financeur en se lavant les mains.

### L'idée
Traiter les Points d'Accueil AGEFICE de l'Hérault comme un **canal institutionnel à part entière** :
- Les identifier, les rencontrer physiquement, se présenter
- Leur fournir des **dossiers propres, complets, du premier coup** — ils traitent du volume, un OF qui leur simplifie la vie devient un OF qu'ils recommandent
- Comprendre leur calendrier et leurs critères de rejet
- Leur demander ce qui bloque le plus souvent → en faire une fiche pour nos clients

### Pourquoi c'est puissant
Ce n'est **pas un avantage pédagogique mais opérationnel** — donc invisible pour la concurrence et lent à copier. Et ça agit directement sur le goulot n°1 identifié en `D0` §4.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🟢 Faible (quelques rendez-vous) | 🔴 **Très élevé** | ✅ **À faire dans les 15 jours.** Le meilleur rapport effort/impact de tout le document. |

---

# IDÉE 9 — Le club des diplômés : transformer la fin de formation en début de relation

### Le constat
La formation se termine, le client disparaît. On a construit l'abonnement logiciel (`D1` §5) comme réponse — mais un logiciel seul ne retient pas un dirigeant de TPE.

### L'idée
Un **rendez-vous mensuel entre anciens** (visio d'1 h) : chacun montre ce qu'il a publié, ce qui a marché, ce qui a raté. On anime, on ne forme pas.

| Bénéfice | Pour qui |
|---|---|
| **Pression sociale positive** → casse la courbe de décrochage (`E0` §1) | Le client |
| **Justifie l'abonnement** bien mieux qu'un logiciel seul | Nous |
| **Produit des témoignages en continu** | Nous |
| **Génère du parrainage** — un dirigeant satisfait en amène un autre | Nous |
| **Coût : 1 h/mois** | Nous |

> ⚖️ **Garde-fou :** le club fait partie de l'**abonnement payant** (périmètre 2), **jamais** de la convention de formation. Un ancien non abonné n'y a pas accès — sinon le périmètre se brouille.

| Effort | Impact | **Verdict** |
|---|---|---|
| 🟢 Très faible | 🟠 Élevé | ✅ **À lancer dès la cohorte fondatrice.** |

---

# IDÉE 10 — Deux angles morts à traiter

### 🔴 Angle mort A — Le risque de dépendance à une personne
**2 dirigeants, et probablement un seul qui délivre réellement les formations.** Si cette personne est indisponible 3 semaines, **tout s'arrête** : les sessions, les dossiers, la facturation. Et pour Qualiopi, une session annulée sans solution de remplacement est un manquement.

> ✅ **Action : qualifier un second formateur dès les 3 premières cohortes.** Contrat de sous-traitance + CV + preuves de qualification (indicateur 27, et la loi 2026-534 précise qu'une formation sans preuve de qualification du formateur peut être jugée **inexécutée**).

### 🔴 Angle mort B — La règle des 5 ans du parcours individualisé FAFCEA
Le dispositif à 80 €/h est limité à **1 parcours par entreprise tous les 5 ans**.

> **Conséquence :** sur ce segment, **aucune récurrence possible**. C'est un modèle d'acquisition pure. Si le parcours FAFCEA devient un pilier, il faut un moteur d'acquisition continu — ou convertir systématiquement ces clients vers l'abonnement logiciel, **seul revenu récurrent disponible**.
> *C'est une validation supplémentaire de la thèse `D0`.*

---

# 📊 Matrice de priorisation

| # | Idée | Effort | Impact | Quand |
|---|---|---|---|---|
| **8** | **Courtiser les Points d'Accueil AGEFICE** | 🟢 | 🔴 | **15 jours** |
| **2** | **Courtiers = canal, pas cible** | 🟢 | 🔴 | **Cette semaine** |
| **4** | Caler le calendrier sur la saisonnalité | 🟢 | 🟠 | Immédiat |
| **1** | **Moteur de preuves multi-locataire** (décision d'architecture) | 🟢 | 🔴 | **À l'écriture de la v1** |
| **9** | Club des diplômés | 🟢 | 🟠 | Cohorte fondatrice |
| **5** | Engagement de moyens renforcé | 🟢 | 🟠 | Rédaction des CGV |
| **3** | **Diagnostic automatisé (4 usages)** | 🟡 | 🔴 | v1 produit |
| **6** | Émission locale | 🟠 | 🟠 | M2 |
| **7** | Distanciel synchrone national | 🟡 | 🔴 | An 2 |
| **10** | Second formateur qualifié | 🟡 | 🔴 | 3 premières cohortes |

---

# 🎯 Si je ne devais en retenir que 3

1. **🏆 Les Points d'Accueil AGEFICE (idée 8).** Quelques rendez-vous, et on débloque le goulot qui tue les ventes de tout le marché. Meilleur rapport effort/impact du dossier.
2. **🏆 Les courtiers comme canal (idée 2).** Dix partenaires couvrent le marché adressable identifié, à coût d'acquisition quasi nul. Reclassement de persona, pas un nouveau chantier.
3. **🏆 Le moteur de preuves en multi-locataire (idée 1).** **Une décision d'architecture gratuite aujourd'hui** qui ouvre un marché de 14 000 organismes demain. Le coût de ne pas la prendre maintenant est de tout réécrire plus tard.

> **Le fil rouge de ces 10 idées :** les meilleures opportunités de ce dossier ne sont **ni pédagogiques ni technologiques — elles sont administratives et relationnelles.** Le marché est encombré d'acteurs qui font du contenu. Il est vide d'acteurs qui maîtrisent le labyrinthe du financement et le réseau local. **C'est là qu'est la marge.**

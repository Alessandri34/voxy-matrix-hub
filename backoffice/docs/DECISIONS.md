# Décisions

Une ligne par décision, avec sa raison. Ce qui n'est pas écrit ici se
re-discutera dans trois mois.

## 2026-11-09 — Django 5.2.19, et non 6.1.3
Le master prompt impose « la dernière LTS ». Le cycle LTS de Django est en
x.2 : 4.2, 5.2, puis 6.2. La 6.1.3 est plus récente mais n'est pas LTS, donc
pas de correctifs de sécurité à long terme. **5.2.19**, dernier correctif de la
branche LTS.

## 2026-11-09 — `django-otp` pour la double authentification
`OTPAdminSite` refuse la session tant qu'aucun appareil n'est vérifié : le
critère de sortie est tenu par la bibliothèque, pas par du code à nous.
Alternative écartée : `django-two-factor-auth`, qui apporte des vues de
connexion dont la phase 0 n'a pas besoin, et deux dépendances de plus.

## 2026-11-09 — Le rôle est un champ de l'utilisateur, pas un groupe seul
Cinq rôles fixés par le PRD, stables. Un champ se lit sans jointure, se filtre
en base, et un test l'affirme en une ligne. Les permissions fines restent
celles de Django : **le rôle décide de ce qu'on voit, la permission de ce qu'on
peut faire**. La table `ACCES` de `apps/accounts/models.py` est la seule source
de vérité ; aucune vue ne redéfinit la règle.

## 2026-11-09 — Fichiers statiques par WhiteNoise, pas par un volume partagé
Caddy ne sert que de terminaison TLS et de proxy. Un volume partagé entre
Django et Caddy crée deux chemins de vérité à resynchroniser à chaque
déploiement.

## 2026-11-09 — Les migrations échappent à la règle de longueur de ligne
Django les écrit et les réécrira. Les erreurs réelles (`F`) restent vérifiées.

## 2026-11-09 — Bloc financement gelé
Trois écarts entre le PRD et les paramètres vérifiés du dépôt documentaire, dont
l'aiguillage CMA / FAFCEA transverse qui décide du routage de chaque dossier
artisan. Détail dans `PRD.md`. **La phase 3 ne démarre pas avant l'arbitrage.**

## 2026-11-09 — ⚠️ Le dépôt hôte est public
`voxy-matrix-hub` est public. La phase 0 ne contient ni donnée personnelle ni
secret (`.env` est ignoré par Git), donc rien n'est exposé aujourd'hui. **Mais
la phase 1 introduit des données de prospects.** À régler avant : dépôt privé,
ou déplacement du back-office dans son propre dépôt privé.

---

## 2026-11-09 — Phase 1 : ce que les sources primaires ont impose

### D7. Le routage financeur reste gele, le champ existe

`Opportunite.financeur_probable` est **informatif**. Aucune regle ne le
remplit automatiquement. L'arbitrage CMA contre FAFCEA transverse n'est pas
tranche sur sources primaires, et le site public a deja annonce la FAFCEA a
35 €/h alors que le numerique y est transverse a 25 €/h. Ecrire une regle de
routage avant cet arbitrage figerait dans le code un taux deja faux une fois.

### D8. La resolution SIREN ne rattache jamais sur un signal ambigu

Mesure faite le 09/11/2026 sur **30 entreprises reelles de l'Herault dont le
SIREN etait connu**, contre l'API Recherche d'entreprises, avec le code de
`apps/crm/services/recherche_entreprises.py` :

| Ce que le formulaire Meta transmet | Juste | **Faux** | Ambigu | Aucun |
|---|---|---|---|---|
| Nom d'entreprise exact + email pro | 90 % | **0 %** | 10 % | 0 % |
| Nom tape a la main (abrege, sans accent) | 87 % | **0 %** | 13 % | 0 % |
| Gmail, mais nom d'entreprise rempli | 87 % | **0 %** | 13 % | 0 % |
| Aucun nom, email professionnel seul | 80 % | **0 %** | 13 % | 7 % |
| **Aucun nom, Gmail** | **0 %** | 0 % | 0 % | 100 % |

**Aucun rattachement faux dans aucun scenario.** Les cas douteux sont marques
« ambigu » et laisses a un humain. C'est le but : un faux SIREN sur un
dossier de financement se decouvre au depot, apres que le client a signe.

🔴 **Consequence operationnelle, a appliquer avant la premiere campagne :
le formulaire Meta DOIT comporter un champ « nom de l'entreprise ».** Sans
lui ni email professionnel, la resolution tombe a 0 % et le critere de sortie
de 70 % devient inatteignable. Ce n'est pas un reglage du code, c'est un
reglage du formulaire.

⚠️ Reserve de methode : le scenario « email professionnel seul » emploie un
domaine fabrique a partir de la raison sociale. Un vrai domaine ne lui
ressemble pas toujours (`contact@letaxi34.fr` pour « TAXI HERAULT
TRANSFERT »). Ce 80 % est donc optimiste ; les quatre autres lignes ne le
sont pas.

### D9. Un tiers des TPE heraultaises refuse la prospection commerciale

Mesure sur **106 entreprises dont le siege est dans l'Herault**, sur les codes
NAF vises par les offres (restauration, coiffure, BTP, commerce, taxi) :

- **34 % sont formellement opposees** a la reutilisation de leurs donnees a
  des fins de prospection (`opposition_diffusion_commerciale: true` — RGPD
  art. 21 §2, art. R.123-320 du Code de commerce) ;
- 65 % ne le sont pas ; 1 % sont absentes du RNE, ce qui n'est pas une
  absence d'opposition ;
- 32 % sont inscrites au Registre des Metiers — critere d'eligibilite FAFCEA.

⚠️ Echantillon de convenance (premiere page de resultats par code NAF), pas
tirage aleatoire : l'ordre de grandeur vaut, la decimale non.

**Consequence pour la phase 5 (sourcing et sequences)** : un tiers d'une
liste de prospection heraultaise est hors d'atteinte en demarchage a froid.
Toute economie de sourcing batie sur 100 % de la liste est fausse d'un tiers.
L'opposition est donc relevee a chaque resolution SIREN et inscrite
automatiquement au registre des oppositions.

### D10. Le critere « moins d'1 minute » se mesure a partir de notre reception

La documentation Meta annonce elle-meme que ses notifications arrivent « avec
un delai pouvant aller jusqu'a quelques minutes ». Mesurer le trajet complet
depuis l'envoi du formulaire reviendrait a mesurer le reseau de Meta.
`ReceptionWebhook.delai_de_traitement_secondes` compte donc de **notre**
reception a l'ecriture du lead.

Fait verifie, qui change l'architecture : **la charge utile du webhook ne
contient aucune reponse du prospect**, seulement `leadgen_id`, `page_id`,
`form_id`, `adgroup_id`, `ad_id`, `created_time`. Les reponses demandent un
appel Graph API avec les permissions `leads_retrieval` et `pages_manage_ads`,
**soumises a App Review**. Les noms de campagne et d'ensemble demandent un
appel de plus. D'ou : corps brut conserve, traitement differe, rejouable.

### D11. La file SIREN a un seul consommateur

La specification de l'API Recherche d'entreprises annonce **7 requetes par
seconde et par adresse IP** et previent : « Il est donc probable de faire face
a cette limite sur les cloud publics. » Le VPS en est un.

Un compteur local serait faux des qu'une seconde instance de worker demarre.
La resolution part donc sur une file Celery dediee, servie par **un seul**
worker (`--queue siren --concurrency 1`), plafonnee a 4 appels/seconde.

### D12. `activite_principale_naf25` est un champ temporaire

La specification de l'API annonce sa **suppression au 1er janvier 2027**. Le
champ `Entreprise.naf_2025` est alimente tant qu'il existe, mais rien de
durable ne doit en dependre. A reverifier avant cette date.

### D13. Le glisser-deposer sans bibliotheque

L'API Drag and Drop du navigateur suffit. SortableJS pesait 45 Ko et un CDN
de plus a joindre, pour un comportement que le navigateur sait deja faire —
et le back-office doit s'ouvrir meme quand le reseau sortant est coupe.

---

## 2026-11-09 — Phase 2 : ce que l'exécution de la vraie pile a revele

### D14. Deux defauts de la phase 1 que seule la pile reelle montrait

Les tests de la phase 1 etaient verts, et deux taches de fond sur trois
n'auraient jamais tourne en production.

**1. Aucune tache Celery n'etait enregistree.** `autodiscover_tasks()`
cherche par defaut un module nomme **`tasks`** dans chaque application. Les
notres s'appellent **`taches`**, selon la convention de langue du projet.
Corrige par `autodiscover_tasks(related_name="taches")`, plus
`apps/integrations/taches.py` — la decouverte ne regarde que la racine de
chaque application, jamais ses sous-paquets.

Le symptome aurait ete muet : la vue repond 200, la tache part dans Redis,
un worker la recoit, leve `KeyError` dans son propre journal et l'abandonne.
Cote application, rien — juste des leads dont le SIREN n'est jamais resolu
et des webhooks Meta jamais traites.

**2. La file `siren` n'avait aucun consommateur.** La pile ne lancait qu'un
worker, sur la file par defaut. Reproduit : `LLEN siren` restait a 1
indefiniment. Corrige par un service `worker-siren` dedie — qui est aussi,
exactement, le mecanisme de D11 : la cadence de l'API est tenue par la
topologie des files, pas par un compteur dans le code.

Les tests de la phase 1 ne pouvaient voir ni l'un ni l'autre : ils executent
les taches en direct, sans courtier. D'ou deux tests nouveaux, qui lisent le
source et la pile Docker plutot que d'executer :
`tests/test_decouverte_taches.py` et `tests/test_files_celery.py`. Les deux
ont ete verifies en remettant le defaut : ils echouent bien.

### D15. Caddy sort de la pile par defaut

Le VPS fait tourner **HestiaCP avec nginx sur 80 et 443**, qui sert
`vformations.fr`. La pile de la phase 0 reclamait ces memes ports pour
Caddy : deployee telle quelle, elle aurait fait tomber le site.

La pile par defaut est donc desormais **celle du VPS**, sans Caddy, avec
gunicorn sur `127.0.0.1:8000` et nginx en mandataire. Caddy est passe dans
`compose.autonome.yaml`, a activer explicitement pour un serveur nu.

Le raisonnement : **la configuration dangereuse ne doit pas etre celle par
defaut.** Le workflow de deploiement refuse en plus de partir si
`compose.yaml` reclame 80 ou 443 — garde-fou verifie sur quatre ecritures
differentes, dont une qui ne devait pas declencher de faux positif.

### D16. Le point de sante est exempte de la redirection HTTPS

Le healthcheck Docker appelle `http://127.0.0.1:8000/sante/` depuis le
conteneur, sans en-tete de mandataire. Avec `SECURE_SSL_REDIRECT` et sans
exemption, il recevait un 301 vers une URL HTTPS que rien ne sert sur cette
interface : le conteneur serait reste « unhealthy » en permanence, et le
deploiement bloque a chaque fois.

`SECURE_REDIRECT_EXEMPT = [r"^sante/$"]`, cette route seulement. Elle ne
porte ni session, ni cookie, ni donnee : deux booleens.

### D17. Le deploiement est manuel, et sauvegarde avant de migrer

Le site vitrine se deploie automatiquement : il est statique, une mauvaise
version se corrige en reposant la precedente. Le back-office applique des
**migrations de base sur des donnees de prospects**. Une migration ne se
repose pas.

Le workflow est donc en declenchement manuel, avec confirmation a taper, et
il prend un `pg_dump` **avant** la migration — pas apres. Le retour arriere
remet les images precedentes et **le dit explicitement** : le code revient,
une migration deja appliquee ne revient pas.

### D18. Ce qui n'a pas pu etre verifie depuis la session

Honnetement : la cle SSH du VPS est dans les secrets GitHub, pas ici. Ont
ete eprouves **reellement** — PostgreSQL 17 et Redis 8 en conteneurs,
migrations, contraintes `CHECK` et index uniques partiels, resolution SIREN
de bout en bout par la file Celery (SIREN 776054090 resolu avec certitude),
syntaxe nginx validee par un vrai nginx, et la chaine nginx → gunicorn →
Django avec TLS, en-tetes, statiques et refus de signature du webhook.

N'ont **pas** pu l'etre : les commandes `v-*` d'Hestia, ecrites d'apres sa
documentation ; la construction de l'image Docker, bloquee ici par le
certificat du mandataire de ce bac a sable — refuser de desactiver la
verification TLS dans le Dockerfile etait preferable a une regression de
securite expediee en production.

---

## 2026-11-09 — Phase 3 : le financement

### D19. L'arbitrage gele en phase 1 n'avait plus d'objet

La question posee etait : pour un artisan, le dossier part-il au FAFCEA au
taux transverse, ou au Conseil de la Formation de sa Chambre de Metiers ?

**Le Conseil de la Formation n'existe plus.** Loi n° 2022-172 du 14/02/2022
(supprime la ventilation de la contribution) · decret n° 2022-956 du
29/06/2022 (abroge les articles correspondants) · arrete du 29/08/2022
(agrement du FAFCEA, **seul agree** pour gerer la contribution des chefs
d'entreprise inscrits au repertoire des metiers, hors parts CPF et CEP).
Le FAFCEA a repris les formations transverses. La CMA reste un lieu de
depot et de conseil, pas un financeur.

Detail et citations : `livrables/D-strategie/D4_Financement_Arbitrage.md`.

### D20. Les baremes sont dates, sources et versionnes

`apps/financement/bareme.py` est le seul endroit ou un taux est ecrit. Chaque
bareme porte sa date d'effet, l'URL du document officiel, l'instance qui l'a
valide et la date de lecture.

`bareme_applicable()` choisit par la **date de debut de la formation**, pas
par la date du devis : les financeurs raisonnent en « formations debutant a
compter du... ». Une date anterieure au plus ancien bareme **leve une
exception** plutot que de se replier sur le plus proche — un repli
silencieux donnerait un reste a charge faux, annonce a un client.

Trois faits releves sur les documents officiels et absents de nos notes :

1. **Un troisieme taux FAFCEA a 15 €/h** pour les « autres modalites »
   (FOAD sans formateur). Notre AFEST avec formateur reste a 25 €/h.
2. **Action de moins de 4 heures : pas de prise en charge** (FAFCEA).
3. **Action en distanciel de plus de 12 stagiaires : pas de prise en
   charge** (FAFCEA), quand l'AGEFICE en tolere 25.

### D21. La TVA n'est financee par personne

Le document du FAFCEA porte « Cout horaire maximum (Hors TVA - non financé) »
en toutes lettres. `D1` calculait les restes a charge en HT : pour un
micro-entrepreneur non assujetti qui ne recupere rien, le reste a charge
reel d'un Integral n'est pas 380 € mais **960 €** (2 900 € HT → 3 480 € TTC,
moins 2 520 € d'AGEFICE). L'exoneration DREETS, si elle est obtenue,
ramene bien ce cas a 380 €.

La simulation calcule donc en TTC et signale toute TVA non exoneree.

### D22. On ne route jamais sur une inscription non etablie

`inscrite_repertoire_metiers` vaut `None` quand l'API Recherche
d'entreprises ne dit rien — ce qui est le cas le plus frequent : sur
l'echantillon heraultais, 32 % seulement portaient cette information.
**Nul ne vaut pas « non inscrit ».** Le routage renvoie alors
« indetermine » et demande l'extrait D1 ou l'attestation URSSAF.

Un dossier parti au mauvais guichet revient refuse apres plusieurs semaines,
delai pendant lequel la fenetre de depot de l'autre financeur peut s'etre
fermee.

### D23. Le calcul est fige sur le dossier

Le bareme applique, le taux, la prise en charge et le detail du calcul sont
inscrits sur le dossier au moment du calcul. Recalculer a la lecture
donnerait, six mois plus tard, un montant different de celui annonce au
client et accepte par le financeur.

`detail_calcul` conserve les limites, les blocages et les avertissements :
c'est ce qui permet d'expliquer un montant longtemps apres.

---

## 2026-11-09 — Phase 4 : le réacteur (séquences, sourcing, pièces)

### D24. Les envois de séquences sont désactivés par défaut, dans le code

`SEQUENCES_ENVOI_REEL = False`. Le moteur calcule qui reçoit quoi et quand,
prépare les messages, les rend consultables — et n'expédie rien.

Le garde-fou est dans le code autant que dans la configuration : un `.env`
recopié d'une préproduction vers la production ne doit pas suffire à
déclencher une campagne. Un moteur de relance branché par erreur sur une
vraie base envoie des centaines de messages avant que quiconque s'en
aperçoive, et un envoi ne se reprend pas.

L'avancement et l'expédition sont **deux tâches Celery séparées** : on peut
faire tourner le moteur et relire ce qu'il produit pendant des semaines sans
qu'un seul message parte.

### D25. L'opposition est vérifiée avant CHAQUE envoi

Pas à l'inscription. Une personne peut s'opposer entre deux étapes — c'est
même le cas le plus fréquent, puisque c'est le premier message qui déclenche
l'opposition. Vérifier à l'inscription seulement enverrait la relance.

Une dernière vérification a lieu **juste avant l'expédition**, parce que
l'opposition a pu être inscrite pendant que le message attendait en file.

Deux autres arrêts : toute relance s'arrête dès que la personne répond, et un
prospect devenu affaire sort de la prospection. ⚠️ Le moteur **ne lit aucune
boîte mail** : une réponse par email ne se détecte pas toute seule. Elle est
inscrite à la main, ou parce qu'un humain a journalisé un échange.

### D26. Le sourcing passe par l'API officielle, pas par un scraper

Demandé : scraper Google Maps et `societe.com`. Vérifié le 09/11/2026 :

- **Google interdit explicitement le scraping de Maps.** Seul le `place_id`
  est conservable durablement, les coordonnées 30 jours ; le nom, l'adresse,
  la note et les avis n'ont **aucune exception de cache**.
- **Pappers et `societe.com` vendent une API** pour les mêmes données que
  l'API publique Recherche d'entreprises, déjà intégrée, gratuite.
- **Seule l'API officielle porte `opposition_diffusion_commerciale`.** Sur
  l'échantillon héraultais, 34 % des TPE des NAF cibles le portent. Une liste
  constituée autrement démarche ces 34 % sans le savoir.

`apps/sourcing` fait donc ce qu'un scraper ferait, en mieux : il cible par
NAF et département, écarte les opposées, vérifie que le siège est bien local
(l'API filtre sur les établissements), et crée des leads dédoublonnés.

L'enrichissement Places existe (`apps/sourcing/places.py`) : il interroge
l'API **au moment de l'usage**, sert les signaux de qualification à l'écran,
et n'écrit que le `place_id`. Un test de non-régression parcourt tous les
modèles et refuse un champ qui stockerait une note ou un nombre d'avis.

### D27. Une pièce peut vivre ailleurs que sur le VPS

`Piece` accepte **un fichier ou un lien externe**, et l'un ou l'autre suffit
pour qu'elle compte comme fournie. Le fichier est sauvegardé avec la base
mais occupe le disque ; le lien ne pèse rien ici, mais **la sauvegarde
chiffrée du back-office ne le couvre pas** et un lien peut casser. Le choix
est laissé, et les deux conséquences sont écrites dans l'administration.

⚠️ La liste des pièces par financeur est établie sur les procédures connues,
**pas extraite d'un document officiel** : à recouper avec le Point d'Accueil
AGEFICE et le FAFCEA avant le premier dépôt réel. `Controle` le signale
(`liste_non_officielle`).

### D28. Le volume financable est un plafond, pas une durée

`apps/financement/volume.py` dit combien d'heures une enveloppe couvre. Son
résumé rappelle, à chaque appel, que c'est un **plafond de financement et non
une durée de formation** : celle-là se justifie par les objectifs
pédagogiques et le niveau de départ de l'apprenant, ce que vérifie un
auditeur Qualiopi (indicateurs 4 et 8).

Construire 100 heures parce que l'enveloppe permet 100 heures, et non parce
que l'apprenant en a besoin, est précisément ce que vise la loi anti-fraude
n° 2026-534 — et ce que la règle d'or du projet interdit.

### D29. Le journal d'audit ne doit jamais faire échouer ce qu'il trace

`_ecrire` appelait `str(instance)` sans filet pour remplir `libelle_objet`.
Or un `__str__` de modèle Django traverse librement ses relations :
`Inscription.__str__` lisait son contact. Pendant une **suppression en
cascade**, la ligne liée pouvait déjà avoir disparu, l'exception remontait
depuis le signal `post_delete`, et **la suppression entière échouait**. Le
témoin cassait l'opération.

Deux corrections, à deux étages :

1. `_libelle()` attrape tout et retombe sur `label#pk`, qui reste
   identifiant. Aucune exception ne sort du journal.
2. `Inscription.__str__` lit ses relations par identifiant et dit
   « contact supprimé » plutôt que de lever.

Le premier est le filet générique — il couvre tous les `__str__` du projet,
y compris ceux qui n'existent pas encore. Le second corrige le cas connu.

Trouvé en vidant les données de démonstration, pas par les tests : aucun des
501 ne supprimait un contact dont une inscription partait dans la même
cascade. Deux tests de non-régression le couvrent désormais.

### D30. Une page ne redéfinit jamais une classe du squelette

Le CSS échoue en silence : une classe inconnue ne fait rien, un sélecteur
redéfini écrase. Les deux se sont produits le même jour.

- `kanban.html` redéfinissait **`.rail`**, qui est la barre latérale. Sur
  cette page, la navigation disparaissait et les onze colonnes se logeaient
  dans ses 244 px. La page renvoyait 200, et l'identifiant `rail` était en
  double dans le document.
- `conformite.html` redéfinissait **`.barre`** (la barre de titre) et posait
  `class="kpis"`, `etiquette`, `detail` — trois noms qui n'existent nulle
  part. Les cartes de chiffres s'empilaient en pleine largeur.

Règle : le squelette possède `.rail .zone .barre .marque .cartes .kpi
.panneau .defile .badge .avis .vide .sous`. Une page qui a besoin d'autre
chose le nomme autrement. La variante d'un élément partagé remonte dans le
squelette (`.defile.seul` pour un tableau posé hors d'un `.panneau`, qui
était recopié à l'identique dans deux gabarits) plutôt que d'être réécrite
page par page.

`apps/pipeline/tests/test_gabarits.py` lit le CSS comme du texte et refuse :
une classe du squelette redéfinie, une classe employée sans être définie
nulle part, un identifiant du squelette réutilisé.

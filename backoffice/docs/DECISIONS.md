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

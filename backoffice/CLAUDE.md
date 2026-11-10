# CLAUDE.md — back-office VFormations

> Toute reprise commence ici, puis par `docs/DECISIONS.md`, qui dit **pourquoi**
> chaque choix a été fait. Les décisions y sont numérotées et datées.

## Le contexte en trois lignes

VFormations est un organisme de formation professionnelle **certifié
Qualiopi**, dans l'Hérault, qui vend à des **professionnels** (TPE :
restauration, coiffure, BTP, commerce). Ce dépôt est son back-office.
Le reste du projet — site vitrine, livrables Qualiopi, marketing — vit dans
le dépôt `voxy-matrix-hub`.

## Règles non négociables

1. **Les fonds de formation ne financent que de la formation réelle.** Ce qui
   est produit *à la place* du client est une prestation commerciale séparée,
   facturée hors financement, jamais conditionnée à l'inscription.
   Base : loi anti-fraudes n° 2026-534, AFEST (D.6313-3-2).
2. **Rien d'irréversible sans accord explicite** : pas de `git push`, pas de
   suppression, pas de déploiement, pas d'envoi.
3. **Les secrets restent hors Git** — `.env`, couvert par `.gitignore`.
4. **Pas d'identifiant de modèle comme auteur** dans les fichiers du dépôt.
5. **Ce dépôt est privé et doit le rester** : il traite des données de
   prospects.
6. **Tout ce qui touche Qualiopi, le financement ou la règle 1 se traite au
   palier de raisonnement le plus élevé.** Un taux faux ou une promesse mal
   cadrée coûte infiniment plus que l'écart de prix entre deux modèles — le
   site public a déjà annoncé la FAFCEA à 35 €/h alors que le numérique y
   est transverse à 25 €/h.

## Ce qui est tranché, et ce qui ne l'est pas

✅ **Le routage financeur est dégelé** depuis le 09/11/2026. L'arbitrage
« CMA contre FAFCEA transverse » n'avait plus d'objet : le Conseil de la
Formation des chambres de métiers **n'existe plus depuis le 1ᵉʳ septembre
2022**, et le FAFCEA est le guichet unique des artisans. → D19.

🔴 **On ne route jamais sur une inscription non établie.**
`inscrite_repertoire_metiers` vaut `None` quand l'API ne dit rien, et **nul
ne vaut pas « non inscrit »**. Sur l'échantillon héraultais, 32 % seulement
portaient cette information. → D22.

🔴 **Les envois de séquences sont désactivés par défaut.**
`SEQUENCES_ENVOI_REEL = False`, et le garde-fou est dans le code autant que
dans la configuration : un `.env` recopié d'une préproduction ne doit pas
suffire à déclencher une campagne. → D24.

🔴 **Rien de Google Maps n'est stocké** hors du `place_id`. Les conditions de
Google Maps Platform n'accordent aucune exception de cache à la note, aux
avis, au nom ni à l'adresse, et interdisent le scraping. Un test de
non-régression refuse tout champ qui les stockerait. → D26.

## Ce qui a déjà coûté cher ici

- **`autodiscover_tasks()` cherche `tasks`, nos modules s'appellent
  `taches`** : sans `related_name`, aucune tâche n'est enregistrée, et
  l'échec est **muet**. Deux tâches sur trois étaient dans ce cas alors que
  214 tests étaient verts. → D14, `tests/test_decouverte_taches.py`.
- **Une file Celery routée sans consommateur** avale les tâches sans erreur.
  → D14, `tests/test_files_celery.py`.
- **Caddy réclamait 80 et 443**, que nginx occupe pour `vformations.fr` :
  déployé tel quel, il aurait fait tomber le site. → D15.
- **Le Kanban ne posait aucun jeton CSRF** : refusé en 403 dans un vrai
  navigateur, invisible aux tests Django dont le client désactive CSRF.
- **`{# … #}` de Django ne vaut que pour UNE ligne** : sur plusieurs, le
  commentaire s'affiche en clair aux utilisateurs.
- **Le journal d'audit faisait échouer les suppressions qu'il traçait.**
  `str(instance)` appelé sans filet, sur un `__str__` qui lisait une
  relation déjà emportée par la cascade. → D29.
- **Une page qui redéfinit une classe du squelette le casse chez elle
  seule, en silence.** `kanban.html` redéfinissait `.rail` : plus aucune
  navigation sur la page du pipeline, et un 200 en réponse. Le CSS n'a
  aucune erreur à lever. → D30, `apps/pipeline/tests/test_gabarits.py`.
- **`|default` n'est pas `|default_if_none`** : il remplace aussi `False`
  et la chaîne vide. Dans le journal, un passage de `False` à `True`
  s'affichait « — → — ».
- **Un test qui dépend de l'heure réelle est instable.** Le moteur de
  séquences refuse d'envoyer hors de la fenêtre ouvrable : un test qui passe
  par `traiter_echeances` doit forcer les échéances dans le passé, sinon il
  échoue le soir et passe le matin.

## La méthode qui marche ici

- **Les tests verts ne suffisent pas.** Les deux défauts les plus graves de
  ce dépôt sont passés sous 214 tests verts. Faire tourner la vraie pile —
  PostgreSQL, Redis, un courtier, un navigateur — trouve ce que les tests ne
  peuvent pas voir.
- **Un chiffre affirmé se recontrôle à la source** avant d'entrer dans une
  décision ou un livrable.
- **Ne jamais inventer un endpoint, un champ ou un paramètre d'API** :
  vérifier dans la documentation officielle, et donner le lien.

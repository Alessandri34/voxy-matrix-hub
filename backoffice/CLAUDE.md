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

## Ce qui est gelé, et pourquoi

🔴 **Le routage financeur.** `Opportunite.financeur_probable` existe ; aucune
règle ne le remplit. L'arbitrage CMA contre FAFCEA transverse n'est pas
tranché sur sources primaires. Écrire une règle avant cet arbitrage figerait
dans le code un taux déjà annoncé faux une fois. → `docs/DECISIONS.md` D7.

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

## La méthode qui marche ici

- **Les tests verts ne suffisent pas.** Les deux défauts les plus graves de
  ce dépôt sont passés sous 214 tests verts. Faire tourner la vraie pile —
  PostgreSQL, Redis, un courtier, un navigateur — trouve ce que les tests ne
  peuvent pas voir.
- **Un chiffre affirmé se recontrôle à la source** avant d'entrer dans une
  décision ou un livrable.
- **Ne jamais inventer un endpoint, un champ ou un paramètre d'API** :
  vérifier dans la documentation officielle, et donner le lien.

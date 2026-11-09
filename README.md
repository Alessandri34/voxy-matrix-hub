# Back-office VFormations

Le back-office de **VFormations**, organisme de formation professionnelle
certifié Qualiopi, basé dans l'Hérault : CRM, pipeline commercial, réception
des leads Meta, résolution automatique du SIREN, et le suivi Qualiopi à
venir.

🔒 **Dépôt privé, et il doit le rester.** Il porte le code qui traite des
données de prospects : noms, téléphones, adresses, et les oppositions à la
prospection commerciale.

---

## Par où commencer

| Pour | Lire |
|---|---|
| Comprendre ce qui est construit et pourquoi | `docs/PRD.md` |
| Savoir où on en est | `docs/ROADMAP.md` |
| Comprendre un choix technique | `docs/DECISIONS.md` |
| Exploiter, déboguer, déployer | `docs/RUNBOOK.md` |
| Installer sur le serveur, la première fois | `deploiement/premiere-installation.md` |

## Démarrer en local

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env          # puis remplir
python manage.py migrate
python manage.py peupler_demo # jeu de démonstration (DEBUG seulement)
python manage.py runserver
```

- `http://127.0.0.1:8000/pipeline/` — le Kanban
- `http://127.0.0.1:8000/admin/` — l'administration (double authentification exigée)

```bash
python -m pytest -q      # la suite complète
ruff check . && ruff format --check .
```

## Trois règles qui expliquent la forme du code

**1. Les fonds de formation ne financent que de la formation réelle.**
Tout ce qui est produit *à la place* du client est une prestation
commerciale séparée, hors financement. Le code ne doit jamais faciliter le
contraire.

**2. Le routage financeur est gelé.** Le champ `financeur_probable` existe,
aucune règle ne le remplit. L'arbitrage CMA contre FAFCEA transverse n'est
pas tranché sur sources primaires — et un taux faux coûte infiniment plus
qu'un champ vide. Voir `docs/DECISIONS.md` D7.

**3. Rien ne se rattache sur un signal ambigu.** Dédoublonnage comme
résolution SIREN : quand plusieurs candidats se valent, un humain tranche.
Un faux SIREN sur un dossier de financement se découvre au dépôt, après que
le client a signé.

## Deux pièges, déjà payés une fois

**Les tâches Celery s'appellent `taches`, pas `tasks`.** Sans
`autodiscover_tasks(related_name="taches")`, aucune tâche n'est enregistrée
— et l'échec est muet : la vue répond 200, le worker lève `KeyError` dans
son seul journal. `tests/test_decouverte_taches.py` le surveille.

**La file `siren` a un seul consommateur, volontairement.** L'API Recherche
d'entreprises plafonne à 7 requêtes/seconde par IP. La cadence est tenue par
la topologie des files, pas par un compteur dans le code : ne jamais passer
`worker-siren` à l'échelle ni augmenter sa concurrence.
`tests/test_files_celery.py` le surveille.

## Aucun conteneur ne prend les ports 80 ni 443

Le VPS fait tourner nginx sous HestiaCP, qui sert `vformations.fr`. Un
conteneur qui réclamerait ces ports ferait tomber le site vitrine. Caddy vit
dans `compose.autonome.yaml`, réservé à un serveur nu ; le workflow de
déploiement refuse de partir si `compose.yaml` les réclame.

---

Le reste du projet VFormations — site vitrine, livrables Qualiopi, marketing
— vit dans le dépôt `voxy-matrix-hub`.

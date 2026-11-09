"""Les files Celery routees doivent avoir un consommateur.

Non-regression d'un defaut reel : la phase 1 routait
`resoudre_siren_du_lead` vers la file « siren », mais la pile ne lancait
qu'un worker, sur la file par defaut. Les taches partaient dans Redis et
n'en sortaient jamais — aucune erreur, aucun journal, juste des leads dont
le SIREN n'etait jamais resolu. Rien dans la suite de tests ne pouvait le
voir : les tests executent les taches en direct.

Ce test lit la pile Docker et la confronte au routage Django.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from django.conf import settings

COMPOSE = Path(__file__).resolve().parent.parent / "compose.yaml"


def files_consommees() -> dict[str, dict]:
    """Les files lues par chaque service de la pile, avec leur concurrence.

    Lecture par expression reguliere plutot que par un analyseur YAML :
    cela evite une dependance de test pour quatre lignes, et la forme des
    commandes est stable.
    """
    texte = COMPOSE.read_text(encoding="utf8")
    services = {}
    for bloc in re.finditer(r"^  ([a-z0-9-]+):\n((?:(?:    .*)?\n)*)", texte, re.MULTILINE):
        nom, corps = bloc.group(1), bloc.group(2)
        if '"celery"' not in corps or '"worker"' not in corps:
            continue
        queues = re.search(r'"--queues",\s*"([^"]+)"', corps)
        concurrence = re.search(r'"--concurrency",\s*"(\d+)"', corps)
        services[nom] = {
            "files": set((queues.group(1) if queues else "celery").split(",")),
            "concurrence": int(concurrence.group(1)) if concurrence else None,
        }
    return services


def test_la_pile_declare_au_moins_un_worker():
    assert files_consommees(), "aucun worker Celery trouve dans compose.yaml"


def test_chaque_file_routee_a_un_consommateur():
    """Le defaut exact de la phase 1."""
    lues = set().union(*(s["files"] for s in files_consommees().values()))
    routees = {
        regle["queue"]
        for regle in getattr(settings, "CELERY_TASK_ROUTES", {}).values()
        if "queue" in regle
    }
    orphelines = routees - lues
    assert not orphelines, (
        f"files routees sans consommateur : {orphelines}. "
        "Les taches y entreraient sans jamais en sortir, sans erreur ni "
        "journal. Ajouter un worker dans compose.yaml."
    )


def test_la_file_par_defaut_a_un_consommateur():
    """Un worker lance avec `--queues siren` ne lit PLUS la file par defaut.
    Restreindre un worker sans en garder un sur « celery » ferait disparaitre
    les taches non routees."""
    lues = set().union(*(s["files"] for s in files_consommees().values()))
    assert "celery" in lues


@pytest.mark.parametrize("tache", ["apps.crm.taches.resoudre_siren_du_lead"])
def test_les_taches_routees_existent(tache):
    """Une faute de frappe dans `CELERY_TASK_ROUTES` donnerait une regle qui
    ne s'applique a rien, sans jamais lever d'erreur."""
    module, _, nom = tache.rpartition(".")
    import importlib

    assert hasattr(importlib.import_module(module), nom)
    assert tache in settings.CELERY_TASK_ROUTES


def test_le_worker_siren_reste_a_une_seule_execution():
    """La cadence de l'API Recherche d'entreprises (7 requetes/seconde par
    IP) est tenue par la topologie, pas par le code : un `--concurrency 2`
    la doublerait silencieusement."""
    services = files_consommees()
    sirens = [s for s in services.values() if "siren" in s["files"]]
    assert sirens, "aucun worker sur la file siren"
    for service in sirens:
        assert service["concurrence"] == 1, (
            "le worker de la file siren doit rester a --concurrency 1 : "
            "l'API plafonne a 7 requetes/seconde par adresse IP."
        )

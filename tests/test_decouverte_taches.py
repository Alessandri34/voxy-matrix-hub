"""Toute tache declaree doit etre connue du worker.

Non-regression d'un defaut qui serait passe en production sans bruit :
`autodiscover_tasks()` cherche par defaut un module nomme **`tasks`** dans
chaque application. Les notres s'appellent `taches`, selon la convention de
langue du projet. Resultat : aucune tache n'etait enregistree.

Le symptome n'aurait rien dit. La vue repond 200, la tache part dans Redis,
un worker la recoit, leve `KeyError: <nom de la tache>` dans son propre
journal et l'abandonne. Cote application : des leads dont le SIREN n'est
jamais resolu et des webhooks Meta jamais traites, sans une seule erreur
visible.

Les tests de la phase 1 ne pouvaient pas le voir : ils executent les taches
en direct, sans passer par le courtier.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
APPS = RACINE / "apps"


def taches_declarees() -> set[str]:
    """Les fonctions decorees par `@shared_task`, lues dans le source.

    Analyse syntaxique plutot qu'import : importer suffirait a enregistrer
    la tache, ce qui rendrait le test incapable de constater son absence.
    """
    trouvees = set()
    for fichier in APPS.rglob("*.py"):
        if "migrations" in fichier.parts or "tests" in fichier.parts:
            continue
        arbre = ast.parse(fichier.read_text(encoding="utf8"), str(fichier))
        module = ".".join(fichier.relative_to(RACINE).with_suffix("").parts)
        for noeud in ast.walk(arbre):
            if not isinstance(noeud, ast.FunctionDef):
                continue
            for decorateur in noeud.decorator_list:
                cible = decorateur.func if isinstance(decorateur, ast.Call) else decorateur
                nom = getattr(cible, "attr", None) or getattr(cible, "id", None)
                if nom == "shared_task":
                    trouvees.add(f"{module}.{noeud.name}")
    return trouvees


@pytest.fixture(scope="module")
def taches_enregistrees() -> set[str]:
    from config.celery import app

    app.loader.import_default_modules()
    return {nom for nom in app.tasks if nom.startswith("apps.")}


def test_il_y_a_des_taches_a_decouvrir():
    """Garde-fou du test lui-meme : s'il ne trouve plus rien a verifier,
    c'est le test qui est casse, pas le code qui est devenu parfait."""
    assert taches_declarees(), "aucun @shared_task trouve dans apps/"


def test_chaque_tache_declaree_est_enregistree(taches_enregistrees):
    """Le defaut exact : `taches.py` au lieu de `tasks.py`."""
    manquantes = taches_declarees() - taches_enregistrees
    assert not manquantes, (
        f"taches invisibles du worker : {sorted(manquantes)}. "
        "Elles partiraient dans Redis sans jamais etre executees, et le "
        "worker ne leverait qu'un KeyError dans son propre journal. "
        "Verifier `autodiscover_tasks(related_name=...)` dans config/celery.py "
        "et, pour un sous-paquet, son export a la racine de l'application."
    )


def test_la_decouverte_cherche_bien_le_nom_francais():
    """Rend la cause explicite plutot que de laisser deduire la correction
    du message d'echec du test precedent."""
    source = (RACINE / "config" / "celery.py").read_text(encoding="utf8")
    assert 'related_name="taches"' in source, (
        "sans `related_name`, Celery cherche un module `tasks` : les modules "
        "`taches` du projet ne seraient jamais importes."
    )


def test_les_taches_en_sous_paquet_sont_exposees_a_la_racine(taches_enregistrees):
    """`autodiscover_tasks` ne regarde que `<application>.taches` : il ne
    descend pas dans les sous-paquets comme `apps/integrations/meta/`."""
    assert "apps.integrations.meta.taches.traiter_reception" in taches_enregistrees

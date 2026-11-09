"""Qui agit, vu depuis un signal.

Un signal `post_save` ne recoit pas la requete HTTP : il ne sait donc pas qui
a provoque l'enregistrement. On le lui dit par une variable de contexte.

`contextvars` plutot que `threading.local` : une variable de contexte suit la
tache asynchrone, pas le fil d'execution. Avec `threading.local`, deux
requetes servies par le meme fil sous ASGI pourraient se voir attribuer le
mauvais acteur — exactement le genre d'erreur qu'un journal d'audit ne doit
pas commettre.
"""

from __future__ import annotations

import contextlib
from contextvars import ContextVar
from typing import Any

_acteur: ContextVar[Any] = ContextVar("acteur_audit", default=None)
_origine: ContextVar[str] = ContextVar("origine_audit", default="application")
_ip: ContextVar[str | None] = ContextVar("ip_audit", default=None)


def acteur_courant():
    return _acteur.get()


def origine_courante() -> str:
    return _origine.get()


def ip_courante() -> str | None:
    return _ip.get()


@contextlib.contextmanager
def agir_en_tant_que(acteur=None, origine: str = "application", ip: str | None = None):
    """Declare l'auteur des enregistrements faits dans ce bloc.

    A utiliser dans une tache Celery, une commande de gestion ou un import :
    sans cela, le journal attribue l'action a « application » sans acteur.
    """
    jetons = (
        _acteur.set(acteur),
        _origine.set(origine),
        _ip.set(ip),
    )
    try:
        yield
    finally:
        _acteur.reset(jetons[0])
        _origine.reset(jetons[1])
        _ip.reset(jetons[2])

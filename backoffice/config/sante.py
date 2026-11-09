"""Point de sante, interroge par Docker et par le deploiement.

Ce qu'il verifie et pourquoi : un gunicorn qui accepte la connexion mais ne
peut plus joindre PostgreSQL repond « 200 » a un simple test de port, et le
mandataire continue de lui envoyer des visiteurs qui recoivent des erreurs.
Un point de sante utile interroge donc les dependances, pas le socket.

Ce qu'il ne dit pas : ni version, ni nom d'hote, ni trace. Il est joignable
sans authentification — c'est necessaire pour qu'un conteneur se teste
lui-meme — donc il ne doit rien apprendre a un visiteur de passage.
"""

from __future__ import annotations

import logging

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

logger = logging.getLogger(__name__)


def _base() -> bool:
    try:
        with connection.cursor() as curseur:
            curseur.execute("SELECT 1")
            return curseur.fetchone() == (1,)
    except Exception as erreur:  # noqa: BLE001 — toute panne compte pareil
        logger.error("Sante : base injoignable (%s)", type(erreur).__name__)
        return False


def _redis() -> bool:
    try:
        import redis
        from django.conf import settings

        client = redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=3)
        return bool(client.ping())
    except Exception as erreur:  # noqa: BLE001
        logger.error("Sante : Redis injoignable (%s)", type(erreur).__name__)
        return False


@never_cache
def sante(request):
    """200 si tout repond, 503 sinon. Le detail tient en deux booleens."""
    etats = {"base": _base(), "redis": _redis()}
    tout_va_bien = all(etats.values())
    return JsonResponse(
        {"etat": "ok" if tout_va_bien else "degrade", **etats},
        status=200 if tout_va_bien else 503,
    )

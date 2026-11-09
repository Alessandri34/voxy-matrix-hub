"""Avancement automatique des sequences.

Toutes les heures, aux heures ouvrables : le moteur refuse de toute facon
d'envoyer hors de la fenetre de chaque sequence, mais passer toutes les
heures plutot qu'une fois par jour permet a une etape « J+0 » de partir dans
l'heure qui suit l'inscription, ce qui est exactement ce qu'on attend d'une
relance a chaud.
"""

from __future__ import annotations

import logging

from celery import shared_task

from apps.audit.contexte import agir_en_tant_que

logger = logging.getLogger(__name__)


@shared_task
def faire_avancer_sequences(limite: int = 500) -> dict:
    from apps.sequences.moteur import traiter_echeances

    with agir_en_tant_que(origine="sequences"):
        resultat = traiter_echeances(limite=limite)
    if resultat["prepares"] or resultat["arretes"]:
        logger.info(
            "Sequences : %s message(s) prepare(s), %s inscription(s) arretee(s).",
            resultat["prepares"],
            resultat["arretes"],
        )
    return resultat


@shared_task
def expedier_envois_prets(limite: int = 200) -> dict:
    """Expedie ce qui est pret. Sans autorisation, ne fait que le constater.

    Tache SEPAREE de l'avancement, volontairement : on peut faire tourner le
    moteur et relire ce qu'il produit pendant des semaines sans qu'un seul
    message parte.
    """
    from django.conf import settings

    from apps.sequences.models import Envoi, EtatEnvoi
    from apps.sequences.moteur import expedier

    prets = list(
        Envoi.objects.filter(etat=EtatEnvoi.A_ENVOYER).select_related(
            "inscription__sequence", "inscription__lead", "inscription__contact"
        )[:limite]
    )
    if not getattr(settings, "SEQUENCES_ENVOI_REEL", False):
        logger.info(
            "%s message(s) pret(s), expedition desactivee "
            "(SEQUENCES_ENVOI_REEL = False). Rien n'est parti.",
            len(prets),
        )
        return {"prets": len(prets), "envoyes": 0, "expedition_active": False}

    envoyes = sum(1 for envoi in prets if expedier(envoi))
    return {"prets": len(prets), "envoyes": envoyes, "expedition_active": True}

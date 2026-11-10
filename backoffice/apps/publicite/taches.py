"""Rapprochement automatique des leads et des campagnes."""

from __future__ import annotations

import logging

from celery import shared_task

from apps.audit.contexte import agir_en_tant_que

logger = logging.getLogger(__name__)


@shared_task
def rapprocher_campagnes() -> dict:
    """Relie les leads Meta a leur campagne.

    Toutes les heures : un lead arrive, il doit etre rattachable le jour
    meme, sinon le tableau de bord publicitaire ment pendant 24 h.
    """
    from apps.publicite.attribution import creer_les_campagnes_manquantes, rapprocher_les_leads

    with agir_en_tant_que(origine="rapprochement-publicite"):
        crees = creer_les_campagnes_manquantes()
        resultat = rapprocher_les_leads()

    resultat["campagnes_creees"] = crees
    if resultat["campagnes_inconnues"]:
        logger.warning(
            "Campagnes vues sur des leads mais absentes du referentiel : %s",
            ", ".join(f"{k} ({v})" for k, v in resultat["campagnes_inconnues"].items()),
        )
    return resultat

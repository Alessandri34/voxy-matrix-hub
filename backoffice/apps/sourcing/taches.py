"""Veille automatique des creations d'entreprise.

Une fois par jour, en fin de matinee : le BODACC publie en continu, et une
immatriculation reperee le jour meme laisse le temps d'appeler avant que
trois concurrents aient fait pareil.

⚠️ **La tache ne cree rien par defaut.** Elle releve, qualifie, et
journalise ce qu'elle aurait cree. Verser quarante prospects par jour dans
le CRM sans avoir regarde ce que le filtre laisse passer est le genre de
decision qui se prend une fois, en connaissance de cause — d'ou le reglage
`VEILLE_BODACC_AUTOMATIQUE`, faux par defaut.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from celery import shared_task
from django.conf import settings

from apps.audit.contexte import agir_en_tant_que
from apps.sourcing.bodacc import ErreurBodacc

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(ErreurBodacc,),
    retry_backoff=60,
    retry_backoff_max=1800,
    retry_jitter=True,
    max_retries=4,
)
def veiller_les_creations(self, jours: int = 2, pages: int = 3) -> dict:
    from apps.sourcing.veille import veiller_et_integrer

    applique = getattr(settings, "VEILLE_BODACC_AUTOMATIQUE", False)
    with agir_en_tant_que(origine="veille-bodacc"):
        resultat = veiller_et_integrer(
            depuis=date.today() - timedelta(days=jours),
            pages_max=pages,
            appliquer=applique,
        )

    if resultat.veille and resultat.veille.erreurs:
        # Remonte en erreur pour que la politique de reprise s'applique :
        # une veille qui echoue en silence est une veille qui n'existe pas.
        raise ErreurBodacc(resultat.veille.erreurs[0])

    logger.info(
        "Veille BODACC : %s retenue(s), %s ecartee(s) pour opposition, %s lead(s) %s.",
        len(resultat.retenus),
        resultat.opposees,
        resultat.leads_crees,
        "crees" if applique else "qu'on aurait pu creer (creation automatique desactivee)",
    )
    return {
        "retenus": len(resultat.retenus),
        "opposees": resultat.opposees,
        "deja_connues": resultat.deja_connues,
        "hors_cible": resultat.hors_cible,
        "introuvables": resultat.introuvables,
        "leads_crees": resultat.leads_crees,
        "creation_automatique": applique,
    }

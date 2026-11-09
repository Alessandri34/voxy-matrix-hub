"""Alertes sur les fenetres de depot.

Pourquoi c'est une tache et non un simple affichage : une fenetre de depot
qui se ferme ne previent pas. L'AGEFICE exige le dossier **15 jours
calendaires avant** le demarrage, et un dossier depose le quatorzieme jour
n'est pas instruit. Le client a signe, la formation est planifiee, et le
financement n'existe plus — c'est l'organisme qui porte la difference.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def alerter_fenetres_de_depot(jours: int = 7) -> dict:
    """Compte et journalise les dossiers dont la fenetre se ferme.

    Comme l'alerte des 24 h du CRM, cette tache compte et journalise : elle
    n'envoie pas de courriel. Le canal se decide avec Pierre, pas a sa place.
    """
    from apps.financement.models import Dossier, EtatDossier

    a_deposer = Dossier.objects.filter(
        etat__in=[EtatDossier.BROUILLON, EtatDossier.A_DEPOSER]
    ).select_related("opportunite__entreprise")

    urgents, fermes = [], []
    for dossier in a_deposer:
        restants = dossier.jours_avant_cloture
        if restants is None:
            continue
        if restants < 0:
            fermes.append(dossier)
        elif restants <= jours:
            urgents.append(dossier)

    if fermes:
        logger.error(
            "%s dossier(s) de financement dont la fenetre de depot est FERMEE : %s. "
            "Le financement n'est plus mobilisable : prevenir le client avant "
            "le demarrage.",
            len(fermes),
            ", ".join(f"#{d.pk} ({d.financeur})" for d in fermes[:10]),
        )
    if urgents:
        logger.warning(
            "%s dossier(s) a deposer sous %s jours : %s.",
            len(urgents),
            jours,
            ", ".join(f"#{d.pk} ({d.financeur}, {d.jours_avant_cloture} j)" for d in urgents[:10]),
        )

    return {
        "verifie_le": timezone.now().isoformat(),
        "fenetre_fermee": [d.pk for d in fermes],
        f"a_deposer_sous_{jours}_jours": [d.pk for d in urgents],
    }

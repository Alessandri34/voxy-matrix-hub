"""Taches de fond du CRM.

La file `siren` est **dediee et a consommateur unique**. L'API Recherche
d'entreprises plafonne a 7 requetes par seconde et par adresse IP, et sa
specification previent : « Il est donc probable de faire face a cette limite
sur les cloud publics. » Le VPS en est un.

Un compteur local ne suffirait pas : deux instances de worker le rendraient
faux. Une file a consommateur unique (`--queue siren --concurrency 1`) tient
la cadence par construction, sans etat partage.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.audit.contexte import agir_en_tant_que
from apps.crm.models import Lead
from apps.crm.services.recherche_entreprises import ErreurApi
from apps.crm.services.resolution import resoudre_lead

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(ErreurApi,),
    retry_backoff=20,
    retry_backoff_max=900,
    retry_jitter=True,
    max_retries=6,
    # 4 appels/seconde : la marge sous le plafond de 7 absorbe les autres
    # usages de la meme adresse IP (recherche manuelle, import CSV).
    rate_limit="4/s",
    acks_late=True,
)
def resoudre_siren_du_lead(self, lead_id: int) -> dict:
    lead = Lead.objects.filter(pk=lead_id).first()
    if lead is None:
        return {"lead": lead_id, "etat": "disparu"}
    with agir_en_tant_que(origine="resolution-siren"):
        resultat = resoudre_lead(lead)
    return {"lead": lead_id, "certitude": resultat.certitude, "siren": resultat.siren}


@shared_task
def alerter_leads_sans_contact(heures: int = 24) -> dict:
    """Critere de sortie de la phase 1 : « alerte a 24 h sans contact ».

    Ce que la tache fait : elle compte et journalise. Ce qu'elle ne fait pas :
    envoyer un courriel. Une alerte qui part avant que quiconque regarde le
    Kanban n'a pas d'utilite, et le canal d'alerte (courriel, notification)
    se decide avec Pierre — pas a sa place.
    """
    limite = timezone.now() - timezone.timedelta(hours=heures)
    en_retard = (
        Lead.objects.filter(
            date_premier_contact__isnull=True,
            doublon_de__isnull=True,
            date_reception__lt=limite,
        )
        .select_related("entreprise")
        .order_by("date_reception")
    )
    liste = list(en_retard[:200])
    if liste:
        logger.warning(
            "%s lead(s) sans contact depuis plus de %s h. Le plus ancien : #%s recu le %s.",
            en_retard.count(),
            heures,
            liste[0].pk,
            liste[0].date_reception.strftime("%d/%m/%Y %H:%M"),
        )
    return {
        "heures": heures,
        "en_retard": en_retard.count(),
        "identifiants": [lead.pk for lead in liste],
    }

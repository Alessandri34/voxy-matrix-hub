"""Traitement differe des leads Meta.

Pourquoi en tache plutot que dans la vue : la vue doit repondre 200 vite —
Meta reemet tant qu'il n'a pas de 200, et un appel Graph lent dans la vue
produirait des doublons. Mais le 200 ne part qu'une fois le corps brut
enregistre, sinon Meta considererait le lead livre alors qu'il serait perdu.

La resolution SIREN est une tache SEPAREE, sur une file dediee a
consommateur unique. L'API Recherche d'entreprises plafonne a 7 requetes par
seconde et par IP, et sa specification previent : « il est donc probable de
faire face a cette limite sur les cloud publics. » Une file a consommateur
unique tient la cadence sans compteur partage, qu'une seconde instance de
worker rendrait faux de toute facon.
"""

from __future__ import annotations

import json
import logging

from celery import shared_task
from django.utils import timezone

from apps.audit.contexte import agir_en_tant_que
from apps.crm.dedoublonnage import enregistrer_lead
from apps.integrations.meta.graph import (
    ErreurGraph,
    recuperer_contexte_publicite,
    recuperer_lead,
    vers_donnees_lead,
)
from apps.integrations.models import EtatReception, ReceptionWebhook

logger = logging.getLogger(__name__)


def evenements_leadgen(corps: str) -> list[dict]:
    """Extrait les evenements « leadgen » d'une charge utile Meta.

    Forme officielle : `{"object": "page", "entry": [{"changes": [{"field":
    "leadgen", "value": {...}}]}]}`. Un seul appel peut porter plusieurs
    entrees et plusieurs changements — Meta regroupe. Les champs autres que
    `leadgen` (messages, mentions) sont ignores sans erreur : s'abonner a
    un champ de plus ne doit pas casser la reception.
    """
    try:
        charge = json.loads(corps)
    except (TypeError, ValueError):
        return []
    if not isinstance(charge, dict):
        return []
    evenements = []
    for entree in charge.get("entry") or []:
        if not isinstance(entree, dict):
            continue
        for changement in entree.get("changes") or []:
            if not isinstance(changement, dict):
                continue
            if changement.get("field") != "leadgen":
                continue
            valeur = changement.get("value")
            if isinstance(valeur, dict):
                evenements.append({**valeur, "page_id_entry": entree.get("id")})
    return evenements


@shared_task(
    bind=True,
    autoretry_for=(ErreurGraph,),
    retry_backoff=10,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=8,
    acks_late=True,
)
def traiter_reception(self, reception_id: int) -> dict:
    """Transforme une reception en lead. Rejouable sans creer de doublon.

    Les reessais couvrent les pannes du Graph API : jeton expire le temps
    d'un renouvellement, limite de debit, coupure. Huit reessais a
    retardement croissant couvrent environ une heure et demie.
    """
    reception = ReceptionWebhook.objects.get(pk=reception_id)
    reception.tentatives += 1

    evenements = evenements_leadgen(reception.corps)
    if not evenements:
        reception.etat = EtatReception.IGNOREE
        reception.erreur = "aucun evenement « leadgen » dans la charge utile"
        reception.traitee_le = timezone.now()
        reception.save()
        return {"etat": reception.etat, "leads": 0}

    cree = []
    with agir_en_tant_que(origine="webhook-meta"):
        for evenement in evenements:
            try:
                reponse = recuperer_lead(str(evenement.get("leadgen_id") or ""))
                contexte = recuperer_contexte_publicite(str(evenement.get("ad_id") or ""))
            except ErreurGraph as erreur:
                reception.etat = EtatReception.ECHOUEE
                reception.erreur = str(erreur)[:2000]
                reception.save()
                logger.warning(
                    "Lead Meta %s non recupere (tentative %s) : %s",
                    evenement.get("leadgen_id"),
                    reception.tentatives,
                    erreur,
                )
                raise

            donnees = vers_donnees_lead(reponse, contexte, evenement)
            lead, nouveau, verdict = enregistrer_lead(donnees)
            if nouveau:
                cree.append(lead.pk)
            if reception.lead_id is None:
                reception.lead = lead

            # La resolution SIREN part a part, sur sa file dediee : si
            # l'API Recherche d'entreprises est lente ou indisponible, le
            # lead est deja dans le CRM et visible par le commercial.
            from apps.crm.taches import resoudre_siren_du_lead

            resoudre_siren_du_lead.apply_async((lead.pk,), queue="siren")

    reception.etat = EtatReception.TRAITEE
    reception.erreur = ""
    reception.traitee_le = timezone.now()
    reception.save()
    logger.info(
        "Reception %s traitee en %s s : %s lead(s) cree(s), %s evenement(s).",
        reception.pk,
        reception.delai_de_traitement_secondes,
        len(cree),
        len(evenements),
    )
    return {
        "etat": reception.etat,
        "leads": len(cree),
        "delai_secondes": reception.delai_de_traitement_secondes,
    }

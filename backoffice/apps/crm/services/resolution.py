"""Rattacher un lead a une entreprise reelle.

Critere de sortie de la phase 1 : « le SIREN est retrouve automatiquement
pour au moins 70 % des leads Meta ». Ce module est ce qui est mesure.

La regle qui compte : un rattachement **ambigu n'est jamais applique**. Mieux
vaut 70 % de rattachements justes et 30 % a faire a la main que 100 % dont
quelques-uns sont faux — un faux SIREN sur un dossier de financement se
decouvre au depot, apres que le client a signe.
"""

from __future__ import annotations

import logging

import httpx
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from apps.crm.dedoublonnage import rattacher_contact
from apps.crm.models import Activite, Lead, Opposition, TypeActivite
from apps.crm.services.entreprises import enregistrer_depuis_api
from apps.crm.services.recherche_entreprises import (
    AMBIGU,
    CERTAIN,
    PROBABLE,
    ErreurApi,
    Resolution,
    resoudre,
)

logger = logging.getLogger(__name__)


def _tracer(lead: Lead, contenu: str) -> Activite:
    return Activite.objects.create(
        type=TypeActivite.SYSTEME,
        type_objet=ContentType.objects.get_for_model(Lead),
        id_objet=str(lead.pk),
        contenu=contenu,
    )


@transaction.atomic
def resoudre_lead(lead: Lead, *, client: httpx.Client | None = None) -> Resolution:
    """Cherche l'entreprise du lead, la rattache si la certitude le permet.

    Ecrit toujours `candidats_siren`, `certitude_resolution` et
    `motif_resolution`, meme en cas d'echec : sans trace de ce qui a ete
    tente, le 30 % non resolu est impossible a traiter a la main.
    """
    if lead.entreprise_id is not None:
        return Resolution(siren=lead.entreprise.siren, certitude=CERTAIN, motif="deja rattache")

    try:
        resultat = resoudre(
            siren_declare=(lead.payload_origine or {}).get("siren", ""),
            denomination=lead.entreprise_declaree,
            email=lead.email_declare,
            client=client,
        )
    except ErreurApi as erreur:
        # L'echec d'appel n'est PAS une absence de resultat : il se reessaie.
        # Le distinguer evite de marquer « aucun candidat » un lead que
        # l'API n'a simplement pas pu traiter.
        logger.warning("Resolution du lead %s impossible : %s", lead.pk, erreur)
        raise

    lead.candidats_siren = resultat.candidats
    lead.certitude_resolution = resultat.certitude
    lead.motif_resolution = resultat.motif[:300]

    if resultat.certitude not in (CERTAIN, PROBABLE) or not resultat.siren:
        lead.save()
        detail = {
            AMBIGU: "Plusieurs entreprises correspondent : a trancher a la main.",
        }.get(resultat.certitude, "Aucune entreprise trouvee automatiquement.")
        _tracer(lead, f"Resolution SIREN sans suite. {detail} {resultat.motif}")
        return resultat

    entreprise, creee = enregistrer_depuis_api(resultat.donnees)
    rattacher_contact(lead, entreprise)
    lead.save()

    verbe = "creee" if creee else "retrouvee"
    note = (
        f"Rattache au SIREN {entreprise.siren} ({entreprise.denomination}), "
        f"fiche {verbe}. Certitude : {resultat.certitude}. {resultat.motif}"
    )
    if Opposition.est_oppose(siren=entreprise.siren):
        note += (
            " ⚠️ Cette entreprise figure au registre des oppositions a la "
            "prospection commerciale : ne pas la demarcher. Une demande "
            "entrante de sa part reste traitable, c'est elle qui a pris "
            "contact."
        )
    if entreprise.etat_administratif == "C":
        note += " ⚠️ Unite legale cessee : verifier avant tout devis."
    _tracer(lead, note)
    return resultat

"""Transforme une moisson en leads exploitables.

Tout passe par `enregistrer_lead`, donc par le dedoublonnage : un sourcing
qui ecrirait en direct creerait des doublons avec les leads entrants des la
deuxieme campagne.
"""

from __future__ import annotations

import logging

from django.db import transaction

from apps.crm.models import SourceLead
from apps.crm.services.entreprises import enregistrer_depuis_api
from apps.sourcing.ciblage import Moisson

logger = logging.getLogger(__name__)


@transaction.atomic
def integrer(moisson: Moisson, *, appliquer: bool = False, proprietaire=None) -> dict:
    """Cree les entreprises et les leads. Apercu par defaut.

    On n'importe pas 400 prospects en aveugle : sans aperçu, une erreur de
    ciblage ne se decouvre qu'apres avoir pollue la base.
    """
    from apps.crm.dedoublonnage import enregistrer_lead
    from apps.crm.models import EtapeAmont

    class Annuler(Exception):
        pass

    compte = {"entreprises": 0, "leads": 0, "deja_connus": 0, "sans_siren": 0}

    def travailler():
        for prospect in moisson.prospects:
            if not prospect.siren:
                compte["sans_siren"] += 1
                continue
            entreprise, creee = enregistrer_depuis_api(prospect.donnees)
            if creee:
                compte["entreprises"] += 1

            _, nouveau, _ = enregistrer_lead(
                {
                    "source": SourceLead.SOURCING,
                    "entreprise_declaree": prospect.denomination,
                    "entreprise": entreprise,
                    "etape_amont": EtapeAmont.IDENTIFIE,
                    "proprietaire": proprietaire,
                    "payload_origine": {
                        "siren": prospect.siren,
                        "note_ciblage": prospect.note,
                        "naf": prospect.naf,
                        "commune": prospect.commune,
                    },
                    "message": (
                        f"Prospect source : {prospect.denomination}, "
                        f"{prospect.commune} ({prospect.code_postal}), "
                        f"NAF {prospect.naf}. Note de ciblage {prospect.note}/100."
                    ),
                }
            )
            if nouveau:
                compte["leads"] += 1
            else:
                compte["deja_connus"] += 1

    if appliquer:
        travailler()
    else:
        try:
            with transaction.atomic():
                travailler()
                raise Annuler
        except Annuler:
            pass

    compte["applique"] = appliquer
    return compte

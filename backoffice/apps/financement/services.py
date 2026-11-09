"""Operations sur les dossiers de financement."""

from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from apps.crm.models import Activite, TypeActivite
from apps.financement.models import Dossier
from apps.financement.routage import router_entreprise
from apps.financement.simulation import Simulation, simuler


def _tracer(dossier: Dossier, contenu: str, auteur=None) -> Activite:
    return Activite.objects.create(
        type=TypeActivite.SYSTEME,
        type_objet=ContentType.objects.get_for_model(Dossier),
        id_objet=str(dossier.pk),
        auteur=auteur,
        contenu=contenu,
    )


def simuler_dossier(dossier: Dossier, *, organisme_qualiopi: bool = True) -> Simulation:
    """Calcule sans rien ecrire. Sert au devis comme a la verification."""
    return simuler(
        financeur=dossier.financeur,
        date_debut=dossier.date_debut_formation,
        heures=dossier.heures,
        prix_ht_centimes=dossier.prix_ht_centimes,
        modalite=dossier.modalite,
        nature=dossier.nature,
        cfp_centimes=dossier.cfp_centimes,
        heures_deja_consommees=dossier.heures_deja_consommees,
        montant_deja_consomme_centimes=dossier.montant_deja_consomme_centimes,
        nb_stagiaires=dossier.nb_stagiaires,
        exonere_tva=dossier.exonere_tva,
        organisme_qualiopi=organisme_qualiopi,
    )


@transaction.atomic
def figer_calcul(dossier: Dossier, *, auteur=None, organisme_qualiopi: bool = True) -> Simulation:
    """Calcule et inscrit le resultat sur le dossier.

    Le bareme applique est fige : un dossier garde ses conditions meme si le
    financeur change ses taux ensuite. Sans cela, un montant annonce au
    client et accepte par le financeur deviendrait irreproductible.
    """
    simulation = simuler_dossier(dossier, organisme_qualiopi=organisme_qualiopi)

    dossier.bareme_en_vigueur_du = simulation.bareme.en_vigueur_du
    dossier.taux_horaire_centimes = simulation.taux_horaire_centimes
    dossier.prise_en_charge_centimes = simulation.prise_en_charge_centimes
    dossier.reste_a_charge_centimes = simulation.reste_a_charge_centimes
    dossier.detail_calcul = {
        "limites": simulation.limites,
        "blocages": simulation.blocages,
        "avertissements": simulation.avertissements,
        "source_bareme": simulation.bareme.source,
        "bareme_valide_par": simulation.bareme.valide_par,
        "cout_ht_centimes": simulation.cout_ht_centimes,
        "tva_centimes": simulation.tva_centimes,
    }
    dossier.save()

    _tracer(dossier, simulation.resume(), auteur)
    return simulation


def proposer_financeur(opportunite):
    """Le financeur pressenti pour une opportunite, sans rien ecrire."""
    return router_entreprise(opportunite.entreprise, opportunite.contact)

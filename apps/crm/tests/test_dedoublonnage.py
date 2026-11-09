"""Le dedoublonnage est un critere de sortie de la phase 1 : « import CSV de
tes leads existants sans doublon ». Il est teste sur les trois chemins reels —
Meta, formulaire du site, tableur — et sur ce qu'il doit refuser de fusionner.
"""

import pytest

from apps.crm.dedoublonnage import (
    AUCUN,
    CERTAIN,
    PROBABLE,
    chercher_doublon,
    enregistrer_lead,
    rattacher_contact,
)
from apps.crm.models import Activite, Contact, Entreprise, Lead, SourceLead

pytestmark = pytest.mark.django_db


def lead_meta(**extra):
    donnees = {
        "source": SourceLead.META_LEAD_ADS,
        "nom_declare": "Sophie Martin",
        "email_declare": "sophie@le-comptoir-34.fr",
        "telephone_declare": "06 12 34 56 78",
        "entreprise_declaree": "Le Comptoir",
        "meta_leadgen_id": "lead_001",
        "meta_campagne_nom": "Visibilite locale — Herault",
    }
    donnees.update(extra)
    return donnees


def test_premier_lead_est_cree():
    lead, cree, verdict = enregistrer_lead(lead_meta())
    assert cree is True
    assert verdict.certitude == AUCUN
    assert lead.email_normalise == "sophie@le-comptoir-34.fr"
    assert lead.telephone_normalise == "+33612345678"


def test_meme_identifiant_meta_ne_cree_rien():
    """Meta reemet le meme webhook jusqu'a recevoir un 200. Sans idempotence,
    une seule demande apparaitrait trois fois dans le CRM."""
    premier, _, _ = enregistrer_lead(lead_meta())
    second, cree, verdict = enregistrer_lead(lead_meta())
    assert cree is False
    assert second.pk == premier.pk
    assert verdict.certitude == CERTAIN
    assert "lead_001" in verdict.motif
    assert Lead.objects.count() == 1


def test_meme_telephone_ecrit_autrement():
    """Le cas le plus courant : Meta lundi, formulaire du site jeudi."""
    premier, _, _ = enregistrer_lead(lead_meta())
    second, cree, verdict = enregistrer_lead(
        {
            "source": SourceLead.FORMULAIRE_SITE,
            "nom_declare": "S. Martin",
            "telephone_declare": "+33 6 12 34 56 78",
        }
    )
    assert cree is False
    assert second.pk == premier.pk
    assert verdict.certitude == CERTAIN
    assert Lead.objects.count() == 1


def test_meme_email_casse_differente():
    premier, _, _ = enregistrer_lead(lead_meta())
    _, cree, _ = enregistrer_lead(
        {"source": SourceLead.IMPORT_CSV, "email_declare": "Sophie@Le-Comptoir-34.FR"}
    )
    assert cree is False
    assert Lead.objects.count() == 1


def test_le_second_passage_enrichit_sans_ecraser():
    """Regle tenue : on remplit les champs vides, on n'en remplace aucun.
    Sinon un import CSV ancien ecraserait une donnee recente et verifiee."""
    premier, _, _ = enregistrer_lead(
        {
            "source": SourceLead.META_LEAD_ADS,
            "nom_declare": "Sophie Martin",
            "telephone_declare": "0612345678",
            "meta_campagne_nom": "Campagne A",
        }
    )
    enregistrer_lead(
        {
            "source": SourceLead.FORMULAIRE_SITE,
            "telephone_declare": "0612345678",
            "nom_declare": "Sophie MARTIN-DURAND",
            "email_declare": "sophie@exemple.fr",
            "meta_campagne_nom": "Campagne B",
            "formation_demandee": "Visibilite locale",
        }
    )
    premier.refresh_from_db()
    # Ajoute, parce que vide :
    assert premier.email_declare == "sophie@exemple.fr"
    assert premier.formation_demandee == "Visibilite locale"
    # Pas ecrase, parce que deja renseigne :
    assert premier.nom_declare == "Sophie Martin"
    assert premier.meta_campagne_nom == "Campagne A"


def test_le_second_passage_est_trace():
    """Une fusion silencieuse est indefendable : si le compte de leads d'une
    campagne est discute, il faut pouvoir montrer ce qui a ete fusionne."""
    premier, _, _ = enregistrer_lead(lead_meta())
    enregistrer_lead(
        lead_meta(meta_leadgen_id="lead_002", email_declare="sophie@le-comptoir-34.fr")
    )
    activites = Activite.objects.filter(id_objet=str(premier.pk))
    assert activites.count() == 1
    assert "Seconde arrivee" in activites.first().contenu


def test_homonymes_sans_contact_commun_ne_sont_pas_fusionnes():
    """« Martin » chez deux entreprises differentes : deux clients."""
    enregistrer_lead(
        {
            "source": SourceLead.IMPORT_CSV,
            "nom_declare": "Sophie Martin",
            "entreprise_declaree": "Le Comptoir",
        }
    )
    _, cree, verdict = enregistrer_lead(
        {
            "source": SourceLead.IMPORT_CSV,
            "nom_declare": "Sophie Martin",
            "entreprise_declaree": "Garage Durand",
        }
    )
    assert cree is True
    assert verdict.certitude == AUCUN
    assert Lead.objects.count() == 2


def test_meme_nom_meme_entreprise_est_probable_pas_certain():
    """Signal faible : le lead est ecrit, mais hors pipeline, pour qu'un
    humain tranche. Fusionner la-dessus perdrait deux associes homonymes."""
    premier, _, _ = enregistrer_lead(
        {
            "source": SourceLead.IMPORT_CSV,
            "nom_declare": "Sophie Martin",
            "entreprise_declaree": "Le Comptoir",
        }
    )
    second, cree, verdict = enregistrer_lead(
        {
            "source": SourceLead.SAISIE_MANUELLE,
            "nom_declare": "sophie martin",
            "entreprise_declaree": "le comptoir",
        }
    )
    assert cree is True
    assert verdict.certitude == PROBABLE
    assert second.doublon_de_id == premier.pk
    assert Lead.objects.filter(doublon_de__isnull=True).count() == 1


def test_un_doublon_ne_sert_pas_de_point_de_rattachement():
    """Sinon une chaine de doublons pointerait sur un doublon, et l'original
    ne serait plus retrouvable."""
    original, _, _ = enregistrer_lead(lead_meta())
    doublon = Lead.objects.create(
        source=SourceLead.IMPORT_CSV,
        nom_declare="Sophie Martin",
        telephone_declare="0612345678",
        doublon_de=original,
    )
    verdict = chercher_doublon(telephone="06 12 34 56 78")
    assert verdict.lead.pk == original.pk
    assert verdict.lead.pk != doublon.pk


def test_telephone_illisible_ne_fusionne_personne():
    """Deux leads dont le telephone est vide ou illisible ne sont pas pour
    autant la meme personne : la chaine vide ne doit jamais etre une cle."""
    enregistrer_lead({"source": SourceLead.IMPORT_CSV, "telephone_declare": "a renseigner"})
    _, cree, verdict = enregistrer_lead(
        {"source": SourceLead.IMPORT_CSV, "telephone_declare": "inconnu"}
    )
    assert cree is True
    assert verdict.certitude == AUCUN


def test_payload_origine_est_conserve():
    donnees = lead_meta()
    donnees["payload_origine"] = {"field_data": [{"name": "phone", "values": ["0612345678"]}]}
    lead, _, _ = enregistrer_lead(donnees)
    lead.refresh_from_db()
    assert lead.payload_origine["field_data"][0]["values"] == ["0612345678"]


def test_rattacher_contact_ne_cree_pas_deux_fois_la_meme_personne():
    entreprise = Entreprise.objects.create(denomination="Le Comptoir", siren="552032534")
    premier, _, _ = enregistrer_lead(lead_meta())
    contact = rattacher_contact(premier, entreprise)
    assert contact.prenom == "Sophie"
    assert contact.nom == "Martin"

    autre = Lead.objects.create(
        source=SourceLead.SAISIE_MANUELLE,
        nom_declare="Sophie Martin",
        email_declare="SOPHIE@le-comptoir-34.fr",
    )
    assert rattacher_contact(autre, entreprise).pk == contact.pk
    assert Contact.objects.count() == 1


def test_base_legale_depend_de_la_source():
    """Un formulaire rempli vaut consentement ; une ligne de tableur ne le
    vaut pas. Ecrire « consentement » partout rendrait la mention fausse, et
    c'est exactement ce qu'un controle verifie."""
    entreprise = Entreprise.objects.create(denomination="Le Comptoir")
    depuis_meta, _, _ = enregistrer_lead(lead_meta())
    assert rattacher_contact(depuis_meta, entreprise).base_legale == "consentement"

    depuis_csv = Lead.objects.create(
        source=SourceLead.IMPORT_CSV, nom_declare="Karim Benali", email_declare="k@btp34.fr"
    )
    assert rattacher_contact(depuis_csv, entreprise).base_legale == "interet_legitime"

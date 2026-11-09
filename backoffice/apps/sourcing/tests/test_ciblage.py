"""Sourcing : ce qui entre dans une liste de prospection, et ce qui n'y entre pas.

Le test central est celui des opposees : sur l'echantillon heraultais, 34 %
des TPE des NAF cibles se sont formellement opposees a la prospection. Une
liste qui les garde demarche precisement ceux qui l'ont refuse.
"""

import json
from pathlib import Path

import httpx
import pytest

from apps.crm.models import CanalOpposition, Entreprise, Lead, Opposition, SourceLead
from apps.sourcing.ciblage import FAMILLES_NAF, Cible, moissonner
from apps.sourcing.integration import integrer

FIXTURES = Path(__file__).resolve().parent.parent.parent / "crm/tests/fixtures"


def charger(nom: str) -> dict:
    return json.loads((FIXTURES / f"{nom}.json").read_text(encoding="utf8"))


def client_servant(pages: list[dict]) -> httpx.Client:
    """Sert une page differente a chaque appel, puis du vide."""
    restantes = list(pages)

    def repondre(requete):
        return httpx.Response(200, json=restantes.pop(0) if restantes else {"results": []})

    return httpx.Client(
        base_url="https://recherche-entreprises.api.gouv.fr",
        transport=httpx.MockTransport(repondre),
    )


@pytest.fixture
def cible():
    return Cible(departement="34", codes_naf=["56.10A"], pages_max=1)


def test_les_familles_couvrent_les_offres():
    """Les codes NAF ciblés doivent correspondre aux personas du dossier :
    artisan BTP, restauration, coiffure, commerce."""
    tous = {code for codes in FAMILLES_NAF.values() for code in codes}
    assert "56.10A" in tous  # restauration
    assert "96.02A" in tous  # coiffure
    assert "43.32A" in tous  # menuiserie
    assert "47.11B" in tous  # commerce alimentaire


@pytest.mark.django_db
def test_une_entreprise_opposee_est_ecartee(cible):
    """`opposition_diffusion_commerciale: true` = opposition formelle au
    titre du RGPD art. 21 §2."""
    page = charger("avec_opposition")
    assert page["results"][0]["opposition_diffusion_commerciale"] is True

    moisson = moissonner(cible, client=client_servant([page]))
    assert moisson.opposees == 1
    assert moisson.prospects == []


@pytest.mark.django_db
def test_on_peut_les_garder_mais_il_faut_le_demander(cible):
    cible.exclure_opposees = False
    moisson = moissonner(cible, client=client_servant([charger("avec_opposition")]))
    assert moisson.opposees == 0
    assert len(moisson.prospects) == 1


@pytest.mark.django_db
def test_une_opposition_deja_en_base_ecarte_aussi(cible):
    """Un desabonnement enregistre chez nous vaut autant que le drapeau du
    registre."""
    page = charger("un_resultat_local")
    siren = page["results"][0]["siren"]
    Opposition.objects.create(siren=siren, canal=CanalOpposition.DESABONNEMENT)

    moisson = moissonner(cible, client=client_servant([page]))
    assert moisson.opposees == 1
    assert moisson.prospects == []


@pytest.mark.django_db
def test_un_siege_hors_departement_est_ecarte(cible):
    """L'API filtre sur les ETABLISSEMENTS : sans ce controle, un groupe
    national avec une agence a Montpellier remonte comme une TPE locale."""
    page = json.loads(json.dumps(charger("un_resultat_local")))
    page["results"][0]["siege"]["departement"] = "69"

    moisson = moissonner(cible, client=client_servant([page]))
    assert moisson.hors_departement == 1
    assert moisson.prospects == []


@pytest.mark.django_db
def test_on_peut_accepter_les_etablissements_secondaires(cible):
    cible.siege_dans_le_departement = False
    page = json.loads(json.dumps(charger("un_resultat_local")))
    page["results"][0]["siege"]["departement"] = "69"
    moisson = moissonner(cible, client=client_servant([page]))
    assert len(moisson.prospects) == 1


@pytest.mark.django_db
def test_une_entreprise_deja_en_base_n_est_pas_reproposee(cible):
    page = charger("un_resultat_local")
    Entreprise.objects.create(denomination="Deja connue", siren=page["results"][0]["siren"])
    moisson = moissonner(cible, client=client_servant([page]))
    assert moisson.deja_connues == 1
    assert moisson.prospects == []


@pytest.mark.django_db
def test_les_prospects_sont_tries_par_note(cible):
    moisson = moissonner(cible, client=client_servant([charger("plusieurs_homonymes")]))
    notes = [p.note for p in moisson.prospects]
    assert notes == sorted(notes, reverse=True)


@pytest.mark.django_db
def test_une_panne_d_api_n_efface_pas_la_moisson(cible):
    def tombe(requete):
        raise httpx.ConnectTimeout("delai depasse")

    client = httpx.Client(
        base_url="https://recherche-entreprises.api.gouv.fr",
        transport=httpx.MockTransport(tombe),
    )
    moisson = moissonner(cible, client=client)
    assert moisson.erreurs
    assert moisson.prospects == []


@pytest.mark.django_db
def test_le_resume_est_lisible(cible):
    moisson = moissonner(cible, client=client_servant([charger("avec_opposition")]))
    texte = moisson.resume()
    assert "opposees a la prospection" in texte


# --------------------------------------------------------------------------
# Integration au CRM
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_apercu_n_ecrit_rien(cible):
    moisson = moissonner(cible, client=client_servant([charger("un_resultat_local")]))
    compte = integrer(moisson)
    assert compte["applique"] is False
    assert compte["leads"] == 1
    assert Lead.objects.count() == 0
    assert Entreprise.objects.count() == 0


@pytest.mark.django_db
def test_appliquer_cree_entreprise_et_lead(cible):
    moisson = moissonner(cible, client=client_servant([charger("un_resultat_local")]))
    compte = integrer(moisson, appliquer=True)

    assert compte["entreprises"] == 1
    assert compte["leads"] == 1
    lead = Lead.objects.get()
    assert lead.source == SourceLead.SOURCING
    assert lead.etape_amont == "identifie"
    assert lead.entreprise is not None
    assert lead.payload_origine["siren"] == lead.entreprise.siren
    assert "Note de ciblage" in lead.message


@pytest.mark.django_db
def test_deux_sourcings_ne_creent_pas_deux_leads(cible):
    """Tout passe par le dedoublonnage : sans cela, la deuxieme campagne
    doublerait la premiere."""
    for _ in range(2):
        moisson = moissonner(cible, client=client_servant([charger("un_resultat_local")]))
        integrer(moisson, appliquer=True)
    assert Lead.objects.count() == 1
    assert Entreprise.objects.count() == 1

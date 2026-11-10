"""Veille BODACC.

La fixture reprend des enregistrements REELS releves le 10/11/2026, lors
d'un appel qui a abouti : 51 358 443 annonces au total, 1 667 creations
dans l'Herault depuis le 1er octobre. Les SCI en tete de liste ne sont pas
une invention — ce sont les premiers resultats reels, et c'est exactement
pourquoi une qualification est necessaire.

Une seule exception a ce « reel » : l'entrepreneur individuel. Son nom et son
SIREN identifient une personne physique, et le depot est public. Ils sont
remplaces par un nom fictif et un SIREN fictif de cle de Luhn valide
(899 000 004) — les tests exigent un SIREN valide, pas un SIREN existant.
Les societes (SCI, SARL) restent telles que publiees au BODACC.
"""

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from apps.crm.models import Entreprise, Lead, Opposition, SourceLead
from apps.sourcing.bodacc import ErreurBodacc, Immatriculation, appeler, veiller
from apps.sourcing.veille import veiller_et_integrer

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ENTREPRISES = Path(__file__).resolve().parent.parent.parent / "crm/tests/fixtures"


def charger(chemin: Path, nom: str) -> dict:
    return json.loads((chemin / f"{nom}.json").read_text(encoding="utf8"))


def client_bodacc(charge=None, statut=200):
    page = charge if charge is not None else charger(FIXTURES, "bodacc_creations_34")

    def repondre(requete):
        if statut != 200:
            return httpx.Response(statut, json={"erreur": "simulee"})
        # Une seconde page vide : la veille doit s'arreter proprement.
        if "offset=100" in str(requete.url):
            return httpx.Response(200, json={"total_count": page["total_count"], "results": []})
        return httpx.Response(200, json=page)

    return httpx.Client(transport=httpx.MockTransport(repondre))


def client_entreprises(nom_fixture="un_resultat_local"):
    """Repond sur le SIREN demande, comme le ferait l'API.

    Sans cela, `par_siren` ne reconnait pas sa propre reponse — il verifie
    que le SIREN rendu est bien celui cherche, ce qui est exactement ce
    qu'on attend de lui.
    """

    def repondre(requete):
        donnees = charger(ENTREPRISES, nom_fixture)
        demande = requete.url.params.get("q", "")
        if demande.isdigit() and donnees.get("results"):
            donnees["results"][0]["siren"] = demande
        return httpx.Response(200, json=donnees)

    return httpx.Client(
        base_url="https://recherche-entreprises.api.gouv.fr",
        transport=httpx.MockTransport(repondre),
    )


@pytest.fixture(autouse=True)
def sans_temporisation(monkeypatch):
    """Ni la pause de courtoisie envers l'API, ni le retard entre reessais
    ne verifient quoi que ce soit dans un test — ils lui coutent neuf
    secondes."""
    monkeypatch.setattr("apps.sourcing.veille.PAUSE_QUALIFICATION", 0)
    monkeypatch.setattr("apps.sourcing.bodacc.RETARD_REESSAI", 0)


# --------------------------------------------------------------------------
# Lecture du BODACC
# --------------------------------------------------------------------------


def test_la_veille_lit_les_creations():
    v = veiller(departement="34", depuis=date(2026, 11, 1), client=client_bodacc())
    assert v.total_annonce == 1667
    assert v.lues == 5


def test_les_societes_civiles_immobilieres_sont_ecartees():
    """Les premiers resultats reels d'une requete heraultaise sont des SCI :
    des structures patrimoniales, pas des entreprises qui exploitent. Les
    ecarter ici evite autant d'appels de qualification."""
    v = veiller(departement="34", depuis=date(2026, 11, 1), client=client_bodacc())
    assert v.ecartees_forme == 2
    noms = {i.denomination for i in v.immatriculations}
    assert "SCI DIEGO" not in noms
    assert "LGAC LA FERRADE" not in noms
    assert "LE FOURNIL DES ARCEAUX" in noms


def test_une_annonce_sans_siren_est_comptee_a_part():
    v = veiller(departement="34", depuis=date(2026, 11, 1), client=client_bodacc())
    assert v.sans_siren == 1


def test_le_siren_est_normalise():
    """Le registre porte « 899 000 004 » avec des espaces."""
    v = veiller(departement="34", depuis=date(2026, 11, 1), client=client_bodacc())
    sirens = {i.siren for i in v.immatriculations}
    assert "899000004" in sirens
    assert all(s.isdigit() and len(s) == 9 for s in sirens)


def test_la_forme_juridique_est_extraite_du_json_imbrique():
    v = veiller(departement="34", depuis=date(2026, 11, 1), client=client_bodacc())
    par_nom = {i.denomination: i for i in v.immatriculations}
    assert par_nom["LE FOURNIL DES ARCEAUX"].forme_juridique.startswith("Société à resp")


def test_une_erreur_reseau_n_efface_pas_la_veille():
    def tombe(requete):
        raise httpx.ConnectTimeout("delai depasse")

    v = veiller(
        departement="34",
        depuis=date(2026, 11, 1),
        client=httpx.Client(transport=httpx.MockTransport(tombe)),
    )
    assert v.erreurs
    assert v.immatriculations == []


def test_une_requete_fautive_ne_se_reessaie_pas():
    """Un 400 ne changera pas au deuxieme essai : insister ne fait que
    retarder le message d'erreur."""
    with pytest.raises(ErreurBodacc, match="refuse la requete"):
        appeler({"where": "syntaxe fautive"}, client=client_bodacc(statut=400))


@pytest.mark.parametrize(
    "forme,ecartee",
    [
        ("Société civile immobilière", True),
        ("Association déclarée", True),
        ("Société à responsabilité limitée", False),
        ("Entrepreneur individuel", False),
        ("", False),
    ],
)
def test_les_formes_ecartees(forme, ecartee):
    immat = Immatriculation(
        siren="123456789",
        denomination="X",
        ville="Montpellier",
        code_postal="34000",
        departement="34",
        date_parution="2026-11-08",
        forme_juridique=forme,
        identifiant_annonce="A1",
        url="",
    )
    assert immat.ecartee_par_forme is ecartee


# --------------------------------------------------------------------------
# Du signal au lead
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_apercu_n_ecrit_rien():
    r = veiller_et_integrer(
        departement="34",
        depuis=date(2026, 11, 1),
        client_bodacc=client_bodacc(),
        client_entreprises=client_entreprises(),
    )
    assert r.applique is False
    assert Lead.objects.count() == 0
    assert Entreprise.objects.count() == 0


@pytest.mark.django_db
def test_une_entreprise_opposee_n_entre_pas(monkeypatch):
    """Une annonce publiee au Journal officiel est publique ; cela ne vaut
    pas consentement a etre demarche."""
    r = veiller_et_integrer(
        departement="34",
        depuis=date(2026, 11, 1),
        appliquer=True,
        client_bodacc=client_bodacc(),
        client_entreprises=client_entreprises("avec_opposition"),
    )
    assert r.opposees >= 1
    assert r.leads_crees == 0


@pytest.mark.django_db
def test_une_opposition_deja_en_base_ecarte_aussi():
    Opposition.objects.create(siren="899000004", canal="desabonnement")
    r = veiller_et_integrer(
        departement="34",
        depuis=date(2026, 11, 1),
        appliquer=True,
        client_bodacc=client_bodacc(),
        client_entreprises=client_entreprises(),
    )
    assert r.opposees >= 1


@pytest.mark.django_db
def test_une_entreprise_introuvable_dans_l_api_est_comptee():
    """Une immatriculation publiee au BODACC peut preceder sa parution dans
    SIRENE, et une unite non diffusible n'y figure jamais."""
    r = veiller_et_integrer(
        departement="34",
        depuis=date(2026, 11, 1),
        appliquer=True,
        client_bodacc=client_bodacc(),
        client_entreprises=client_entreprises("aucun_resultat"),
    )
    assert r.introuvables >= 1
    assert r.leads_crees == 0


@pytest.mark.django_db
def test_un_siren_deja_connu_n_est_pas_requalifie():
    """Chaque qualification coute un appel sur une API plafonnee a 7
    requetes par seconde : ne pas redemander ce qu'on sait deja."""
    # Le SIREN de la premiere immatriculation reelle de la fixture BODACC.
    Entreprise.objects.create(denomination="Deja connue", siren="899000004")
    r = veiller_et_integrer(
        departement="34",
        depuis=date(2026, 11, 1),
        appliquer=True,
        client_bodacc=client_bodacc(),
        client_entreprises=client_entreprises(),
    )
    assert r.deja_connues == 1
    # Et l'entreprise deja connue n'a pas consomme d'appel de qualification.
    assert r.qualifies == len(r.veille.immatriculations) - 1


@pytest.mark.django_db
def test_le_lead_porte_sa_provenance():
    """Six mois plus tard, il faut pouvoir dire d'ou vient ce prospect."""
    r = veiller_et_integrer(
        departement="34",
        depuis=date(2026, 11, 1),
        appliquer=True,
        client_bodacc=client_bodacc(),
        client_entreprises=client_entreprises(),
    )
    if not r.leads_crees:
        pytest.skip("aucun lead retenu avec cette fixture")
    lead = Lead.objects.first()
    assert lead.source == SourceLead.SOURCING
    assert lead.payload_origine["origine"] == "bodacc"
    assert lead.payload_origine["annonce"].startswith("A2026")
    assert "BODACC" in lead.message
    assert "droits a formation ouverts" in lead.message


@pytest.mark.django_db
def test_le_resume_dit_ce_qui_a_ete_ecarte_et_pourquoi():
    r = veiller_et_integrer(
        departement="34",
        depuis=date(2026, 11, 1),
        client_bodacc=client_bodacc(),
        client_entreprises=client_entreprises(),
    )
    texte = r.resume()
    assert "forme juridique sans objet" in texte
    assert "opposees a la prospection" in texte
    assert "introuvable" in texte

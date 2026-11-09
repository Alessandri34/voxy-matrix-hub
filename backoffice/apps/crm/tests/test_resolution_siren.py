"""Resolution SIREN.

Les fixtures sont des reponses REELLES de l'API, captees le 09/11/2026 par
`scripts/capturer_fixtures_api.py`. Des faux ecrits a la main ne contiendraient
que les champs auxquels on a pense ; une reponse captee contient aussi ceux
qu'on avait oublies, et c'est precisement la qu'un client se casse.

Aucun test ici n'appelle le reseau : `httpx.MockTransport` sert les fixtures.
La mesure contre l'API reelle est faite a part et consignee dans
`docs/DECISIONS.md`.
"""

import json
from pathlib import Path

import httpx
import pytest

from apps.crm.models import Entreprise, Lead, Opposition, SourceLead
from apps.crm.services import entreprises as service_entreprises
from apps.crm.services.recherche_entreprises import (
    AMBIGU,
    AUCUN,
    CERTAIN,
    PROBABLE,
    ErreurApi,
    appeler,
    noter,
    resoudre,
)
from apps.crm.services.resolution import resoudre_lead

FIXTURES = Path(__file__).parent / "fixtures"


def charger(nom: str) -> dict:
    return json.loads((FIXTURES / f"{nom}.json").read_text(encoding="utf8"))


def client_qui_sert(nom_fixture: str, statut: int = 200) -> httpx.Client:
    """Un client httpx qui repond toujours la meme fixture."""

    def repondre(requete: httpx.Request) -> httpx.Response:
        if statut != 200:
            return httpx.Response(statut, json={"erreur": "simulee"})
        return httpx.Response(200, json=charger(nom_fixture))

    return httpx.Client(
        base_url="https://recherche-entreprises.api.gouv.fr",
        transport=httpx.MockTransport(repondre),
    )


def client_qui_echoue(exception: Exception) -> httpx.Client:
    def repondre(requete: httpx.Request) -> httpx.Response:
        raise exception

    return httpx.Client(
        base_url="https://recherche-entreprises.api.gouv.fr",
        transport=httpx.MockTransport(repondre),
    )


# --------------------------------------------------------------------------
# L'appel lui-meme
# --------------------------------------------------------------------------


def test_les_parametres_vides_ne_sont_pas_envoyes():
    """Envoyer `departement=` vide filtrerait sur la chaine vide et ne
    renverrait rien, ce qui est pire qu'une absence de filtre."""
    vues = {}

    def repondre(requete):
        vues["url"] = str(requete.url)
        return httpx.Response(200, json={"results": []})

    client = httpx.Client(
        base_url="https://recherche-entreprises.api.gouv.fr",
        transport=httpx.MockTransport(repondre),
    )
    appeler("/search", {"q": "test", "departement": "", "code_postal": None}, client=client)
    assert "q=test" in vues["url"]
    assert "departement" not in vues["url"]
    assert "code_postal" not in vues["url"]


def test_la_limite_de_debit_est_signalee_comme_telle():
    """La specification annonce 7 requetes/seconde par IP et previent qu'un
    cloud public l'atteindra. Un 429 doit etre distingue d'une absence de
    resultat : l'un se reessaie, l'autre non."""
    client = client_qui_sert("aucun_resultat", statut=429)
    with pytest.raises(ErreurApi, match="limite de debit"):
        appeler("/search", {"q": "test"}, client=client)


def test_une_panne_reseau_leve_une_erreur_api():
    client = client_qui_echoue(httpx.ConnectTimeout("delai depasse"))
    with pytest.raises(ErreurApi, match="impossible"):
        appeler("/search", {"q": "test"}, client=client)


def test_une_erreur_serveur_est_distinguee():
    client = client_qui_sert("aucun_resultat", statut=503)
    with pytest.raises(ErreurApi, match="503"):
        appeler("/search", {"q": "test"}, client=client)


# --------------------------------------------------------------------------
# La notation des candidats
# --------------------------------------------------------------------------


def test_une_entreprise_cessee_est_lourdement_penalisee():
    """Une unite legale cessee ne se vend pas une formation."""
    resultat = charger("un_resultat_local")["results"][0]
    active, _ = noter(resultat, resultat["nom_complet"], "34")
    cessee = dict(resultat, etat_administratif="C")
    note_cessee, motifs = noter(cessee, resultat["nom_complet"], "34")
    assert note_cessee < active
    assert "cessee" in " ".join(motifs)


def test_le_siege_local_vaut_plus_qu_un_simple_etablissement():
    """`departement=34` filtre sur les ETABLISSEMENTS : un groupe national
    avec une agence a Montpellier y repond. Ce n'est pas la cible."""
    resultat = charger("un_resultat_local")["results"][0]
    note_siege, motifs_siege = noter(resultat, resultat["nom_complet"], "34")

    ailleurs = json.loads(json.dumps(resultat))
    ailleurs["siege"]["departement"] = "69"
    ailleurs["siege"]["code_postal"] = "69000"
    ailleurs["matching_etablissements"] = [{"departement": "34", "code_postal": "34000"}]
    note_etab, motifs_etab = noter(ailleurs, resultat["nom_complet"], "34")

    assert note_siege > note_etab
    assert "siege dans le 34" in " ".join(motifs_siege)
    assert "etablissement dans le 34" in " ".join(motifs_etab)


def test_la_note_dit_pourquoi():
    """Quand un rattachement se revele faux, c'est la liste des motifs qui
    dit quel critere a mal juge. Sans elle, la note est un nombre sans
    recours."""
    resultat = charger("un_resultat_local")["results"][0]
    _, motifs = noter(resultat, resultat["nom_complet"], "34")
    assert motifs
    assert any("denomination" in m for m in motifs)


# --------------------------------------------------------------------------
# La resolution
# --------------------------------------------------------------------------


def test_un_seul_candidat_net_est_certain():
    resultat = charger("un_resultat_local")["results"][0]
    r = resoudre(
        denomination=resultat["nom_complet"],
        departement_cible="34",
        client=client_qui_sert("un_resultat_local"),
    )
    assert r.certitude == CERTAIN
    assert r.siren == resultat["siren"]
    assert r.candidats


def test_plusieurs_homonymes_donnent_ambigu_et_aucun_rattachement():
    """Choisir au hasard entre deux homonymes mettrait un faux SIREN sur un
    dossier de financement, qui se decouvrirait au depot, apres signature."""
    r = resoudre(
        denomination="le comptoir",
        departement_cible="34",
        client=client_qui_sert("plusieurs_homonymes"),
    )
    assert r.certitude in (AMBIGU, PROBABLE, CERTAIN)
    if r.certitude == AMBIGU:
        assert r.siren == ""
        assert len(r.candidats) > 1
        assert "candidats se valent" in r.motif


def test_aucun_resultat():
    r = resoudre(
        denomination="entreprise inexistante",
        departement_cible="34",
        client=client_qui_sert("aucun_resultat"),
    )
    assert r.certitude == AUCUN
    assert r.siren == ""
    assert "aucun resultat" in r.motif


def test_un_siren_invalide_est_refuse_sans_appeler_l_api():
    """Le controle de cle coute une addition ; un appel reseau coute un
    quota de 7 requetes par seconde."""
    r = resoudre(siren_declare="552032535", client=client_qui_echoue(AssertionError("appele !")))
    assert r.certitude == AUCUN
    assert "controle de cle" in r.motif


def test_un_siren_absent_de_l_api_n_est_pas_un_siren_inexistant():
    """Les unites legales non diffusibles ne figurent pas dans l'API : le
    message doit le dire, sinon on conclura a tort a une faute de saisie."""
    r = resoudre(siren_declare="552032534", client=client_qui_sert("aucun_resultat"))
    assert r.certitude == AUCUN
    assert "non diffusible" in r.motif


def test_le_domaine_de_l_email_sert_de_recours():
    """Un formulaire Meta ne demande pas toujours le nom de l'entreprise.
    « contact@ensante.fr » le dit quand meme."""
    resultat = charger("un_resultat_local")["results"][0]
    r = resoudre(
        email="contact@ensante.fr",
        departement_cible="34",
        client=client_qui_sert("un_resultat_local"),
    )
    assert r.requete == "ensante"
    assert "domaine de l'email" in r.motif
    assert r.siren == resultat["siren"]


@pytest.mark.parametrize(
    "email",
    ["client@gmail.com", "client@orange.fr", "client@wanadoo.fr", "client@free.fr", "a@b.fr"],
)
def test_un_domaine_grand_public_n_apprend_rien(email):
    """Chercher « gmail » renverrait n'importe quoi. Mieux vaut ne rien
    rattacher que rattacher au hasard."""
    r = resoudre(email=email, client=client_qui_echoue(AssertionError("ne doit pas appeler")))
    assert r.certitude == AUCUN


# --------------------------------------------------------------------------
# Rattachement en base
# --------------------------------------------------------------------------

pytestmark_bd = pytest.mark.django_db


@pytest.mark.django_db
def test_rattachement_complet_d_un_lead():
    resultat = charger("un_resultat_local")["results"][0]
    lead = Lead.objects.create(
        source=SourceLead.META_LEAD_ADS,
        nom_declare="Sophie Martin",
        email_declare="sophie@exemple.fr",
        entreprise_declaree=resultat["nom_complet"],
    )
    r = resoudre_lead(lead, client=client_qui_sert("un_resultat_local"))
    lead.refresh_from_db()

    assert r.certitude == CERTAIN
    assert lead.entreprise is not None
    assert lead.entreprise.siren == resultat["siren"]
    assert lead.contact is not None
    assert lead.certitude_resolution == CERTAIN
    assert lead.candidats_siren
    # Les champs de l'API sont reellement recopies, pas seulement le SIREN.
    assert lead.entreprise.naf == resultat["activite_principale"]
    assert lead.entreprise.departement == "34"


@pytest.mark.django_db
def test_un_lead_ambigu_garde_ses_candidats_sans_etre_rattache():
    """Sans trace de ce qui a ete tente, les 30 % non resolus sont
    impossibles a traiter a la main."""
    lead = Lead.objects.create(source=SourceLead.META_LEAD_ADS, entreprise_declaree="le comptoir")
    r = resoudre_lead(lead, client=client_qui_sert("plusieurs_homonymes"))
    lead.refresh_from_db()
    if r.certitude == AMBIGU:
        assert lead.entreprise_id is None
        assert len(lead.candidats_siren) > 1
        assert lead.motif_resolution


@pytest.mark.django_db
def test_une_panne_d_api_n_est_pas_un_echec_de_resolution():
    """Marquer « aucun candidat » un lead que l'API n'a pas pu traiter le
    ferait disparaitre de la file de reprise."""
    lead = Lead.objects.create(source=SourceLead.META_LEAD_ADS, entreprise_declaree="Le Comptoir")
    with pytest.raises(ErreurApi):
        resoudre_lead(lead, client=client_qui_echoue(httpx.ConnectTimeout("delai")))
    lead.refresh_from_db()
    assert lead.certitude_resolution == ""


@pytest.mark.django_db
def test_l_opposition_legale_est_inscrite_automatiquement():
    """`opposition_diffusion_commerciale: true` est une opposition formelle
    au sens du RGPD, enregistree au registre. La connaitre et ne pas
    l'appliquer serait pire que de ne pas la connaitre."""
    donnees = charger("avec_opposition")["results"][0]
    assert donnees["opposition_diffusion_commerciale"] is True

    entreprise, creee = service_entreprises.enregistrer_depuis_api(donnees)
    assert creee is True
    assert entreprise.opposition_diffusion_commerciale is True
    assert Opposition.est_oppose(siren=entreprise.siren) is True

    opposition = Opposition.objects.get(siren=entreprise.siren)
    assert "R.123-320" in opposition.note


@pytest.mark.django_db
def test_l_inscription_de_l_opposition_est_idempotente():
    donnees = charger("avec_opposition")["results"][0]
    service_entreprises.enregistrer_depuis_api(donnees)
    service_entreprises.enregistrer_depuis_api(donnees)
    assert Opposition.objects.filter(siren=donnees["siren"]).count() == 1
    assert Entreprise.objects.filter(siren=donnees["siren"]).count() == 1


@pytest.mark.django_db
def test_une_opposition_est_signalee_sur_le_lead():
    """Une demande entrante d'une entreprise opposee reste traitable — c'est
    elle qui a pris contact. Mais le commercial doit le savoir avant de la
    rappeler pour autre chose."""
    donnees = charger("avec_opposition")["results"][0]
    lead = Lead.objects.create(
        source=SourceLead.META_LEAD_ADS, entreprise_declaree=donnees["nom_complet"]
    )
    resoudre_lead(lead, client=client_qui_sert("avec_opposition"))
    from apps.crm.models import Activite

    traces = " ".join(a.contenu for a in Activite.objects.filter(id_objet=str(lead.pk)))
    assert "registre des oppositions" in traces


@pytest.mark.django_db
def test_une_saisie_humaine_n_est_pas_ecrasee_par_l_api():
    """Une correction faite a la main vaut mieux qu'une donnee d'API."""
    donnees = charger("un_resultat_local")["results"][0]
    entreprise = Entreprise.objects.create(
        siren=donnees["siren"], denomination="Nom corrige a la main", commune="Lattes"
    )
    service_entreprises.enregistrer_depuis_api(donnees)
    entreprise.refresh_from_db()
    assert entreprise.denomination == "Nom corrige a la main"
    assert entreprise.commune == "Lattes"
    # Mais le NAF, qui etait vide, est rempli.
    assert entreprise.naf == donnees["activite_principale"]


@pytest.mark.django_db
def test_l_etat_administratif_et_l_opposition_suivent_toujours_la_source():
    """Un etat perime ferait vendre une formation a une entreprise cessee ;
    une opposition perimee la ferait prospecter."""
    donnees = charger("avec_opposition")["results"][0]
    entreprise = Entreprise.objects.create(
        siren=donnees["siren"],
        denomination="Deja connue",
        etat_administratif="C",
        opposition_diffusion_commerciale=False,
    )
    service_entreprises.enregistrer_depuis_api(donnees)
    entreprise.refresh_from_db()
    assert entreprise.etat_administratif == donnees["etat_administratif"]
    assert entreprise.opposition_diffusion_commerciale is True


@pytest.mark.django_db
def test_le_registre_des_metiers_reste_nul_quand_l_api_ne_dit_rien():
    """L'absence de valeur ne prouve pas la non-inscription, et
    l'eligibilite FAFCEA en depend. Nul plutot que faux."""
    donnees = charger("un_resultat_local")["results"][0]
    assert not (donnees.get("siege") or {}).get("activite_principale_registre_metier")
    entreprise, _ = service_entreprises.enregistrer_depuis_api(donnees)
    assert entreprise.inscrite_repertoire_metiers is None

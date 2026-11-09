"""Webhook Meta Lead Ads.

Les faits verifies sur la documentation officielle (09/11/2026) et tenus par
ces tests :

- en-tete `X-Hub-Signature-256`, prefixe `sha256=`, SHA256 sur le corps brut
  avec le secret de l'application ;
- poignee de main GET : `hub.mode=subscribe`, `hub.verify_token`,
  `hub.challenge` a renvoyer tel quel ;
- la charge utile ne contient QUE des identifiants : `leadgen_id`, `page_id`,
  `form_id`, `adgroup_id`, `ad_id`, `created_time` ;
- Meta reemet tant qu'il n'a pas recu un 200.
"""

import hashlib
import hmac
import json

import pytest
from django.test import Client

from apps.integrations.meta.graph import aplatir_field_data, vers_donnees_lead
from apps.integrations.meta.signature import SignatureInvalide, calculer, verifier
from apps.integrations.meta.taches import evenements_leadgen
from apps.integrations.models import EtatReception, ReceptionWebhook

SECRET = "secret-application-de-test"
JETON = "jeton-de-verification-de-test"

#: Charge utile a la forme officielle.
CHARGE = {
    "object": "page",
    "entry": [
        {
            "id": "102938475610",
            "time": 1762690000,
            "changes": [
                {
                    "field": "leadgen",
                    "value": {
                        "leadgen_id": "1122334455",
                        "page_id": "102938475610",
                        "form_id": "998877",
                        "adgroup_id": "556677",
                        "ad_id": "334455",
                        "created_time": 1762689990,
                    },
                }
            ],
        }
    ],
}


def corps_signe(charge=None) -> tuple[bytes, str]:
    brut = json.dumps(charge if charge is not None else CHARGE).encode("utf-8")
    return brut, calculer(brut, SECRET)


# --------------------------------------------------------------------------
# Signature
# --------------------------------------------------------------------------


def test_signature_juste():
    brut, signature = corps_signe()
    verifier(brut, signature, SECRET)  # ne leve pas


def test_un_corps_modifie_invalide_la_signature():
    """C'est tout l'interet : la signature prouve l'origine ET l'integrite."""
    brut, signature = corps_signe()
    altere = brut.replace(b"1122334455", b"9999999999")
    with pytest.raises(SignatureInvalide, match="non concordante"):
        verifier(altere, signature, SECRET)


def test_sans_secret_la_verification_echoue_au_lieu_de_passer():
    """Fermeture par defaut. Un webhook ouvert accepterait de faux leads de
    n'importe qui, et ces faux leads entreraient dans le pipeline."""
    brut, signature = corps_signe()
    with pytest.raises(SignatureInvalide, match="aucun secret"):
        verifier(brut, signature, "")


def test_signature_absente():
    brut, _ = corps_signe()
    with pytest.raises(SignatureInvalide, match="absent"):
        verifier(brut, None, SECRET)


def test_prefixe_sha1_refuse():
    """Meta a employe `X-Hub-Signature` en SHA1 ; accepter l'ancien prefixe
    accepterait un algorithme casse."""
    brut, _ = corps_signe()
    sha1 = "sha1=" + hmac.new(SECRET.encode(), brut, hashlib.sha1).hexdigest()
    with pytest.raises(SignatureInvalide, match="prefixe"):
        verifier(brut, sha1, SECRET)


def test_la_signature_porte_sur_le_corps_brut_pas_sur_le_json_reinterprete():
    """Re-serialiser le JSON change les espaces et l'ordre des cles : la
    signature ne concorderait plus pour la meme donnee."""
    brut, signature = corps_signe()
    reserialise = json.dumps(json.loads(brut), indent=2, sort_keys=True).encode()
    assert reserialise != brut
    with pytest.raises(SignatureInvalide):
        verifier(reserialise, signature, SECRET)


# --------------------------------------------------------------------------
# Lecture de la charge utile
# --------------------------------------------------------------------------


def test_extraction_des_evenements():
    evenements = evenements_leadgen(json.dumps(CHARGE))
    assert len(evenements) == 1
    assert evenements[0]["leadgen_id"] == "1122334455"
    assert evenements[0]["form_id"] == "998877"


def test_un_champ_autre_que_leadgen_est_ignore_sans_erreur():
    """S'abonner a un champ de plus (messages, mentions) ne doit pas casser
    la reception des leads."""
    charge = json.loads(json.dumps(CHARGE))
    charge["entry"][0]["changes"].append({"field": "messages", "value": {"x": 1}})
    assert len(evenements_leadgen(json.dumps(charge))) == 1


def test_plusieurs_leads_dans_un_seul_appel():
    """Meta regroupe : une charge utile peut porter plusieurs entrees."""
    charge = json.loads(json.dumps(CHARGE))
    seconde = json.loads(json.dumps(charge["entry"][0]))
    seconde["changes"][0]["value"]["leadgen_id"] = "2233445566"
    charge["entry"].append(seconde)
    evenements = evenements_leadgen(json.dumps(charge))
    assert [e["leadgen_id"] for e in evenements] == ["1122334455", "2233445566"]


@pytest.mark.parametrize("corps", ["", "pas du json", "[]", "null", '{"entry": "pas une liste"}'])
def test_une_charge_utile_illisible_ne_leve_pas(corps):
    assert evenements_leadgen(corps) == []


def test_aplatissement_des_reponses():
    plat = aplatir_field_data(
        [
            {"name": "full_name", "values": ["Sophie Martin"]},
            {"name": "email", "values": ["sophie@le-comptoir-34.fr"]},
            {"name": "besoins", "values": ["Visibilite", "Site web"]},
            {"name": "vide", "values": []},
        ]
    )
    assert plat["full_name"] == "Sophie Martin"
    # Une reponse multiple est jointe, pas tronquee : perdre silencieusement
    # la deuxieme reponse serait pire que de la presenter mal.
    assert plat["besoins"] == "Visibilite ; Site web"
    assert plat["vide"] == ""


def test_assemblage_des_trois_sources():
    """Le webhook donne les identifiants, le Graph donne les reponses, un
    second appel donne les libelles de campagne."""
    evenement = CHARGE["entry"][0]["changes"][0]["value"]
    reponse = {
        "id": "1122334455",
        "created_time": "2026-11-09T10:00:00+0000",
        "ad_id": "334455",
        "form_id": "998877",
        "field_data": [
            {"name": "full_name", "values": ["Sophie Martin"]},
            {"name": "email", "values": ["sophie@le-comptoir-34.fr"]},
            {"name": "phone_number", "values": ["+33612345678"]},
            {"name": "company_name", "values": ["Le Comptoir"]},
            {"name": "quand_demarrer", "values": ["Dans le mois"]},
        ],
    }
    contexte = {
        "name": "Visibilite locale — video 1",
        "campaign": {"id": "900", "name": "Visibilite locale Herault"},
        "adset": {"id": "910", "name": "Restaurateurs 34"},
    }
    donnees = vers_donnees_lead(reponse, contexte, evenement)

    assert donnees["nom_declare"] == "Sophie Martin"
    assert donnees["email_declare"] == "sophie@le-comptoir-34.fr"
    assert donnees["telephone_declare"] == "+33612345678"
    assert donnees["entreprise_declaree"] == "Le Comptoir"
    assert donnees["meta_campagne_nom"] == "Visibilite locale Herault"
    assert donnees["meta_ensemble_nom"] == "Restaurateurs 34"
    assert donnees["meta_leadgen_id"] == "1122334455"
    # Les questions personnalisees finissent dans le message, pas aux oubliettes.
    assert "quand_demarrer : Dans le mois" in donnees["message"]
    # Et tout est conserve brut, y compris ce que Meta ajoutera plus tard.
    assert donnees["payload_origine"]["reponse_graph"]["field_data"]


def test_prenom_et_nom_separes_sont_recolles():
    """Certains formulaires demandent « first_name » et « last_name » plutot
    que « full_name » : n'en garder qu'un amputerait le nom."""
    donnees = vers_donnees_lead(
        {
            "field_data": [
                {"name": "first_name", "values": ["Sophie"]},
                {"name": "last_name", "values": ["Martin"]},
            ]
        },
        {},
        {"leadgen_id": "1"},
    )
    assert donnees["nom_declare"] == "Sophie Martin"


def test_le_contexte_absent_ne_perd_pas_le_lead():
    """Si l'enrichissement de campagne echoue, le lead entre quand meme —
    avec ses identifiants, sans les libelles."""
    donnees = vers_donnees_lead(
        {"field_data": [{"name": "email", "values": ["a@b.fr"]}]},
        {},
        CHARGE["entry"][0]["changes"][0]["value"],
    )
    assert donnees["email_declare"] == "a@b.fr"
    assert donnees["meta_publicite_id"] == "334455"
    assert donnees["meta_campagne_nom"] == ""


# --------------------------------------------------------------------------
# La vue, en HTTP
# --------------------------------------------------------------------------

URL = "/integrations/meta/webhook/"


@pytest.fixture
def reglages(settings):
    settings.META_APP_SECRET = SECRET
    settings.META_VERIFY_TOKEN = JETON
    # Les taches s'executent dans le processus de test : on verifie la vue,
    # pas le courtier.
    settings.CELERY_TASK_ALWAYS_EAGER = True
    return settings


def poster(client: Client, charge=None, *, signature=None):
    brut, calculee = corps_signe(charge)
    return client.post(
        URL,
        data=brut,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=signature if signature is not None else calculee,
    )


def test_poignee_de_main_renvoie_le_challenge(client, reglages):
    """Meta compare la reponse caractere par caractere : le challenge sort en
    texte brut, sans guillemets JSON."""
    reponse = client.get(
        URL,
        {"hub.mode": "subscribe", "hub.verify_token": JETON, "hub.challenge": "1580919315"},
    )
    assert reponse.status_code == 200
    assert reponse.content == b"1580919315"
    assert reponse["Content-Type"].startswith("text/plain")


def test_poignee_de_main_refusee_si_le_jeton_ne_correspond_pas(client, reglages):
    reponse = client.get(
        URL, {"hub.mode": "subscribe", "hub.verify_token": "faux", "hub.challenge": "123"}
    )
    assert reponse.status_code == 403


def test_poignee_de_main_refusee_sans_jeton_configure(client, settings):
    settings.META_VERIFY_TOKEN = ""
    reponse = client.get(
        URL, {"hub.mode": "subscribe", "hub.verify_token": "", "hub.challenge": "123"}
    )
    assert reponse.status_code == 403


@pytest.mark.django_db
def test_une_signature_invalide_est_refusee_mais_conservee(client, reglages):
    """Une serie de signatures invalides signale un secret desynchronise ou
    une tentative d'injection de faux leads : la trace vaut mieux que rien."""
    reponse = poster(client, signature="sha256=00")
    assert reponse.status_code == 403
    reception = ReceptionWebhook.objects.get()
    assert reception.signature_valide is False
    assert reception.etat == EtatReception.IGNOREE
    assert "signature refusee" in reception.erreur


@pytest.mark.django_db
def test_une_reception_valide_enregistre_le_corps_brut(client, reglages, monkeypatch):
    """Le 200 ne part qu'une fois le corps en base : sinon Meta
    considererait le lead livre alors qu'il serait perdu."""
    appels = []
    monkeypatch.setattr(
        "apps.integrations.meta.taches.traiter_reception.delay", lambda pk: appels.append(pk)
    )
    reponse = poster(client)
    assert reponse.status_code == 200
    assert reponse.json()["recu"] is True

    reception = ReceptionWebhook.objects.get()
    assert reception.signature_valide is True
    assert reception.cle_idempotence == "1122334455"
    assert json.loads(reception.corps)["entry"][0]["changes"][0]["field"] == "leadgen"
    assert appels == [reception.pk]


@pytest.mark.django_db
def test_un_courtier_injoignable_ne_perd_pas_le_lead(client, reglages, monkeypatch):
    """Si Redis est tombe, la reception reste en base a l'etat « recue » et
    la commande `rejouer_receptions` la reprend. Renvoyer une erreur ferait
    reemettre Meta, ce qui serait aussi acceptable — mais on a deja la
    donnee, autant la garder."""

    def tombe(pk):
        raise ConnectionError("Redis injoignable")

    monkeypatch.setattr("apps.integrations.meta.taches.traiter_reception.delay", tombe)
    reponse = poster(client)
    assert reponse.status_code == 200
    reception = ReceptionWebhook.objects.get()
    assert reception.etat == EtatReception.RECUE


@pytest.mark.django_db
def test_un_reessai_de_meta_ne_cree_pas_un_second_lead(client, reglages, monkeypatch):
    """Meta reemet jusqu'a recevoir un 200. Un 200 perdu en route provoque
    un reessai : sans cle d'idempotence, il creerait un second lead."""
    monkeypatch.setattr("apps.integrations.meta.taches.traiter_reception.delay", lambda pk: None)
    poster(client)
    ReceptionWebhook.objects.update(etat=EtatReception.TRAITEE)

    reponse = poster(client)
    assert reponse.status_code == 200
    assert reponse.json()["deja_traite"] is True
    assert ReceptionWebhook.objects.count() == 1


@pytest.mark.django_db
def test_le_parcours_complet_du_webhook_au_lead(client, reglages, monkeypatch):
    """Critere de sortie : « un lead de test Meta apparait dans le CRM avec
    sa campagne ». Le Graph API et la resolution SIREN sont simules ; ce qui
    est verifie ici, c'est le chainage."""
    from apps.crm.models import Lead

    monkeypatch.setattr(
        "apps.integrations.meta.taches.recuperer_lead",
        lambda leadgen_id, **kw: {
            "id": leadgen_id,
            "field_data": [
                {"name": "full_name", "values": ["Sophie Martin"]},
                {"name": "email", "values": ["sophie@le-comptoir-34.fr"]},
                {"name": "phone_number", "values": ["06 12 34 56 78"]},
                {"name": "company_name", "values": ["Le Comptoir"]},
            ],
        },
    )
    monkeypatch.setattr(
        "apps.integrations.meta.taches.recuperer_contexte_publicite",
        lambda ad_id, **kw: {
            "name": "Video 1",
            "campaign": {"id": "900", "name": "Visibilite locale Herault"},
            "adset": {"id": "910", "name": "Restaurateurs 34"},
        },
    )
    monkeypatch.setattr("apps.crm.taches.resoudre_siren_du_lead.apply_async", lambda *a, **k: None)

    assert poster(client).status_code == 200

    lead = Lead.objects.get()
    assert lead.nom_declare == "Sophie Martin"
    assert lead.telephone_normalise == "+33612345678"
    assert lead.meta_campagne_nom == "Visibilite locale Herault"
    assert lead.meta_leadgen_id == "1122334455"

    reception = ReceptionWebhook.objects.get()
    assert reception.etat == EtatReception.TRAITEE
    assert reception.lead_id == lead.pk
    # Le critere « moins d'1 minute » se mesure a partir de NOTRE reception :
    # la documentation Meta annonce elle-meme un delai pouvant aller jusqu'a
    # quelques minutes avant l'emission du ping.
    assert reception.delai_de_traitement_secondes is not None
    assert reception.delai_de_traitement_secondes < 60


@pytest.mark.django_db
def test_le_meme_lead_recu_deux_fois_reste_un_seul_lead(client, reglages, monkeypatch):
    """Idempotence au niveau du lead, pas seulement de la reception : si la
    cle d'idempotence manquait, la contrainte `leadgen_meta_unique` et le
    dedoublonnage doivent encore tenir."""
    from apps.crm.models import Lead

    monkeypatch.setattr(
        "apps.integrations.meta.taches.recuperer_lead",
        lambda leadgen_id, **kw: {
            "id": leadgen_id,
            "field_data": [{"name": "email", "values": ["sophie@le-comptoir-34.fr"]}],
        },
    )
    monkeypatch.setattr(
        "apps.integrations.meta.taches.recuperer_contexte_publicite", lambda ad_id, **kw: {}
    )
    monkeypatch.setattr("apps.crm.taches.resoudre_siren_du_lead.apply_async", lambda *a, **k: None)

    poster(client)
    # On efface la cle pour forcer le second passage jusqu'au dedoublonnage.
    ReceptionWebhook.objects.update(cle_idempotence="")
    poster(client)

    assert Lead.objects.count() == 1
    assert ReceptionWebhook.objects.count() == 2

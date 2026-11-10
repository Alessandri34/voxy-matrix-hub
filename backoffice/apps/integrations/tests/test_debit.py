"""Limitation de debit sur le webhook public.

Le webhook est joignable par tout internet et ne porte aucune session :
c'est voulu, il s'authentifie par la signature HMAC de son corps. Mais la
verification coute un calcul et l'enregistrement coute une ecriture : sans
plafond, n'importe qui sature la base avec des requetes mal signees.
"""

import json

import pytest
from django.core.cache import cache

from apps.integrations.debit import (
    PLAFOND_NON_SIGNEES,
    PLAFOND_SIGNEES,
    adresse_client,
    compter,
)
from apps.integrations.models import ReceptionWebhook
from apps.integrations.tests.test_webhook_meta import CHARGE, JETON, SECRET, corps_signe

URL = "/integrations/meta/webhook/"


@pytest.fixture(autouse=True)
def cache_propre():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def reglages(settings):
    settings.META_APP_SECRET = SECRET
    settings.META_VERIFY_TOKEN = JETON
    settings.CELERY_TASK_ALWAYS_EAGER = True
    return settings


# --------------------------------------------------------------------------
# Le compteur
# --------------------------------------------------------------------------


def test_le_compteur_laisse_passer_sous_le_plafond():
    for n in range(1, 6):
        autorise, compte = compter("essai", "198.51.100.7", 10)
        assert autorise is True
        assert compte == n


def test_le_compteur_refuse_au_dela():
    for _ in range(3):
        compter("essai", "198.51.100.7", 3)
    autorise, compte = compter("essai", "198.51.100.7", 3)
    assert autorise is False
    assert compte == 4


def test_deux_adresses_comptent_separement():
    """Sinon un seul client bruyant bloquerait tous les autres."""
    for _ in range(3):
        compter("essai", "198.51.100.7", 3)
    autorise, _ = compter("essai", "203.0.113.9", 3)
    assert autorise is True


def test_un_cache_en_panne_laisse_passer(monkeypatch):
    """Un limiteur qui tombe ne doit pas faire tomber la reception des leads
    avec lui : la perte d'un plafond vaut mieux que la perte des demandes
    d'un client."""

    def tombe(*a, **k):
        raise ConnectionError("Redis injoignable")

    monkeypatch.setattr("apps.integrations.debit.cache.add", tombe)
    autorise, compte = compter("essai", "198.51.100.7", 1)
    assert autorise is True
    assert compte == 0


def test_l_adresse_vient_du_mandataire_mais_seulement_la_premiere():
    """`X-Forwarded-For` est fourni par le client et donc falsifiable, sauf
    la premiere valeur, que nginx reecrit."""

    class FausseRequete:
        META = {
            "HTTP_X_FORWARDED_FOR": "203.0.113.9, 198.51.100.7, 10.0.0.1",
            "REMOTE_ADDR": "172.17.0.1",
        }

    assert adresse_client(FausseRequete()) == "203.0.113.9"


def test_sans_mandataire_on_prend_l_adresse_directe():
    class FausseRequete:
        META = {"REMOTE_ADDR": "172.17.0.1"}

    assert adresse_client(FausseRequete()) == "172.17.0.1"


# --------------------------------------------------------------------------
# Sur le webhook
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_les_signatures_invalides_sont_plafonnees_serre(client, reglages):
    """Une requete mal signee ne vient pas de Meta : il n'existe aucune
    raison legitime d'en envoyer beaucoup, et chacune coute une ecriture."""
    brut = json.dumps(CHARGE).encode()
    refuses = 0
    for _ in range(PLAFOND_NON_SIGNEES + 5):
        reponse = client.post(
            URL,
            data=brut,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256="sha256=00",
        )
        if reponse.status_code == 429:
            refuses += 1
        else:
            assert reponse.status_code == 403
    assert refuses == 5


@pytest.mark.django_db
def test_au_dela_du_plafond_la_trace_n_est_plus_conservee(client, reglages):
    """Sinon le journal devient l'arme : chaque requete refusee ecrirait
    une ligne, et saturer la base deviendrait le moyen de l'attaquer."""
    brut = json.dumps(CHARGE).encode()
    for _ in range(PLAFOND_NON_SIGNEES + 10):
        client.post(
            URL,
            data=brut,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256="sha256=00",
        )
    assert ReceptionWebhook.objects.count() == PLAFOND_NON_SIGNEES


@pytest.mark.django_db
def test_une_rafale_legitime_de_meta_passe(client, reglages, monkeypatch):
    """Meta regroupe et peut reemettre : son plafond est large."""
    monkeypatch.setattr("apps.integrations.meta.taches.traiter_reception.delay", lambda pk: None)
    brut, signature = corps_signe()
    for n in range(50):
        charge = json.loads(brut)
        charge["entry"][0]["changes"][0]["value"]["leadgen_id"] = f"rafale-{n}"
        corps, sig = corps_signe(charge)
        reponse = client.post(
            URL, data=corps, content_type="application/json", HTTP_X_HUB_SIGNATURE_256=sig
        )
        assert reponse.status_code == 200


@pytest.mark.django_db
def test_le_plafond_large_finit_par_refuser(client, reglages, monkeypatch):
    monkeypatch.setattr("apps.integrations.meta.taches.traiter_reception.delay", lambda pk: None)
    for _ in range(PLAFOND_SIGNEES):
        compter("meta", "127.0.0.1", PLAFOND_SIGNEES)
    brut, signature = corps_signe()
    reponse = client.post(
        URL, data=brut, content_type="application/json", HTTP_X_HUB_SIGNATURE_256=signature
    )
    assert reponse.status_code == 429


def test_les_deux_plafonds_ne_sont_pas_les_memes():
    """Le point important : une requete bien signee vient de Meta, une mal
    signee non."""
    assert PLAFOND_NON_SIGNEES < PLAFOND_SIGNEES

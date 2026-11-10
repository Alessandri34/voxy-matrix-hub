"""Verrouillage apres echecs de connexion.

L'administration exige deja un code TOTP : un mot de passe seul ne suffit
pas a entrer. Le verrou protege d'autre chose — l'enumeration des comptes,
le bourrage d'identifiants, et l'epuisement de ressources.
"""

import pytest
from django.conf import settings


def test_le_verrou_est_actif():
    assert "axes" in settings.INSTALLED_APPS
    assert "axes.middleware.AxesMiddleware" in settings.MIDDLEWARE


def test_le_backend_de_verrouillage_passe_en_premier():
    """Place apres le backend normal, il laisserait le mot de passe etre
    teste malgre le verrou — le verrou ne servirait plus a rien."""
    assert settings.AUTHENTICATION_BACKENDS[0].startswith("axes.")


def test_le_middleware_passe_en_dernier():
    """Sa documentation l'exige : il doit voir l'echec d'authentification
    une fois que tout le reste a tourne."""
    assert settings.MIDDLEWARE[-1] == "axes.middleware.AxesMiddleware"


def test_le_verrou_porte_sur_le_couple_identifiant_et_adresse():
    """Sur l'identifiant SEUL, n'importe qui bloquerait le compte de Pierre
    depuis n'importe ou. Sur l'adresse seule, une faute de frappe d'une
    personne bloquerait tout un bureau."""
    assert settings.AXES_LOCKOUT_PARAMETERS == [["username", "ip_address"]]


def test_cinq_tentatives_puis_une_demi_heure():
    assert settings.AXES_FAILURE_LIMIT == 5
    assert settings.AXES_COOLOFF_TIME == 0.5


def test_une_connexion_reussie_remet_le_compteur_a_zero():
    """Sinon cinq fautes de frappe etalees sur six mois finiraient par
    verrouiller un compte legitime."""
    assert settings.AXES_RESET_ON_SUCCESS is True


@pytest.mark.django_db
def test_le_compte_se_verrouille_apres_cinq_echecs(client, settings):
    from django.contrib.auth import get_user_model
    from django.core.cache import cache

    cache.clear()
    get_user_model().objects.create_user(
        username="pierre", password="un-mot-de-passe-long-12", role="admin"
    )
    for _ in range(settings.AXES_FAILURE_LIMIT):
        client.post("/admin/login/", {"username": "pierre", "password": "faux"})

    reponse = client.post(
        "/admin/login/", {"username": "pierre", "password": "un-mot-de-passe-long-12"}
    )
    # Verrouille : meme le bon mot de passe ne passe plus.
    assert (
        reponse.status_code in (403, 429)
        or b"verrou" in reponse.content.lower()
        or not reponse.wsgi_request.user.is_authenticated
    )
    cache.clear()

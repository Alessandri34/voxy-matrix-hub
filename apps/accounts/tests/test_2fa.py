"""L'administration refuse une session sans second facteur verifie."""

import pytest
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import Role, Utilisateur


@pytest.fixture
def admin(db):
    return Utilisateur.objects.create_superuser(
        username="patron",
        email="patron@example.fr",
        password="motdepasse-long-12",
        role=Role.ADMIN,
    )


@pytest.mark.django_db
def test_mot_de_passe_seul_ne_donne_pas_l_acces(client, admin):
    """Connexion reussie mais sans appareil verifie : l'admin reste ferme."""
    client.force_login(admin)
    reponse = client.get("/admin/", follow=False)
    assert reponse.status_code == 302, "sans 2FA, l'administration doit rediriger"


@pytest.mark.django_db
def test_une_session_verifiee_ouvre_l_administration(client, admin):
    appareil = TOTPDevice.objects.create(user=admin, name="telephone", confirmed=True)
    client.force_login(admin)
    session = client.session
    # django_otp retient l'appareil verifie dans la session.
    session["otp_device_id"] = appareil.persistent_id
    session.save()
    reponse = client.get("/admin/")
    assert reponse.status_code == 200


@pytest.mark.django_db
def test_un_appareil_non_confirme_ne_compte_pas(client, admin):
    TOTPDevice.objects.create(user=admin, name="en cours", confirmed=False)
    client.force_login(admin)
    assert client.get("/admin/", follow=False).status_code == 302

"""Le point de sante.

Il est interroge par le healthcheck Docker et par le deploiement : s'il ment,
le deploiement declare un succes sur une application en panne.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_sante_repond_ok_quand_tout_repond(client, monkeypatch):
    monkeypatch.setattr("config.sante._redis", lambda: True)
    reponse = client.get(reverse("sante"))
    assert reponse.status_code == 200
    donnees = reponse.json()
    assert donnees["etat"] == "ok"
    assert donnees["base"] is True


@pytest.mark.django_db
def test_sante_repond_503_si_redis_est_tombe(client, monkeypatch):
    """503 et non 200 : sinon le mandataire continue d'envoyer des visiteurs
    a une application qui ne peut plus traiter une seule tache de fond."""
    monkeypatch.setattr("config.sante._redis", lambda: False)
    reponse = client.get(reverse("sante"))
    assert reponse.status_code == 503
    assert reponse.json()["etat"] == "degrade"


@pytest.mark.django_db
def test_sante_repond_503_si_la_base_est_tombee(client, monkeypatch):
    monkeypatch.setattr("config.sante._base", lambda: False)
    monkeypatch.setattr("config.sante._redis", lambda: True)
    reponse = client.get(reverse("sante"))
    assert reponse.status_code == 503
    assert reponse.json()["base"] is False


@pytest.mark.django_db
def test_sante_ne_divulgue_rien(client, monkeypatch):
    """Joignable sans authentification : il ne doit rien apprendre a un
    visiteur de passage — ni version, ni nom d'hote, ni trace."""
    monkeypatch.setattr("config.sante._redis", lambda: True)
    donnees = client.get(reverse("sante")).json()
    assert set(donnees) == {"etat", "base", "redis"}


@pytest.mark.django_db
def test_sante_n_est_jamais_mis_en_cache(client, monkeypatch):
    """Une reponse « ok » mise en cache par le mandataire survivrait a la
    panne qu'elle est censee detecter."""
    monkeypatch.setattr("config.sante._redis", lambda: True)
    reponse = client.get(reverse("sante"))
    assert "no-cache" in reponse["Cache-Control"]


@pytest.mark.django_db
def test_une_panne_de_redis_ne_leve_pas(client, monkeypatch):
    """Le point de sante doit repondre meme quand tout va mal : une
    exception donnerait un 500 sans detail, donc sans diagnostic."""

    def tombe(*a, **k):
        raise ConnectionError("Redis injoignable")

    monkeypatch.setattr("redis.from_url", tombe)
    reponse = client.get(reverse("sante"))
    assert reponse.status_code == 503
    assert reponse.json()["redis"] is False


def test_le_point_de_sante_echappe_a_la_redirection_https():
    """Non-regression.

    Le healthcheck Docker appelle `http://127.0.0.1:8000/sante/` depuis le
    conteneur, sans en-tete de mandataire. Avec `SECURE_SSL_REDIRECT` et
    sans exemption, il recevait un 301 vers une URL HTTPS que rien ne sert
    sur cette interface : le conteneur restait « unhealthy » en permanence
    et le deploiement etait bloque.
    """
    from config.settings import prod

    assert any("sante" in motif for motif in prod.SECURE_REDIRECT_EXEMPT), (
        "/sante/ doit figurer dans SECURE_REDIRECT_EXEMPT, sinon le "
        "healthcheck du conteneur echoue toujours."
    )


def test_seul_le_point_de_sante_est_exempte():
    """L'exemption ne doit pas s'elargir : toute autre route porte session,
    cookie ou donnee, et doit rester en HTTPS."""
    from config.settings import prod

    assert prod.SECURE_REDIRECT_EXEMPT == [r"^sante/$"]
    assert prod.SECURE_SSL_REDIRECT is True

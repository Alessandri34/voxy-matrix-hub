"""Enrichissement Google Places, et les limites que ses conditions imposent."""

import httpx
import pytest

from apps.sourcing.places import (
    CHAMP_STOCKABLE,
    PlacesIndisponible,
    argument_commercial,
    qualifier,
)

REPONSE = {
    "places": [
        {
            "id": "ChIJAbCdEfGhIjKlMnOp",
            "displayName": {"text": "Le Comptoir de la Loge"},
            "formattedAddress": "3 rue de la Loge, 34000 Montpellier",
            "rating": 4.3,
            "userRatingCount": 8,
            "websiteUri": "",
            "nationalPhoneNumber": "04 67 00 00 00",
            "businessStatus": "OPERATIONAL",
        }
    ]
}


def client_qui_repond(charge=REPONSE, statut=200):
    def repondre(requete):
        return httpx.Response(statut, json=charge)

    return httpx.Client(transport=httpx.MockTransport(repondre))


def test_sans_cle_le_module_le_dit_et_ne_contourne_rien(settings):
    settings.GOOGLE_PLACES_API_KEY = ""
    with pytest.raises(PlacesIndisponible, match="GOOGLE_PLACES_API_KEY"):
        qualifier("Le Comptoir", "Montpellier")


def test_avec_une_cle_les_signaux_remontent(settings):
    settings.GOOGLE_PLACES_API_KEY = "cle-de-test"
    signaux = qualifier("Le Comptoir", "Montpellier", client=client_qui_repond())
    assert signaux["place_id"] == "ChIJAbCdEfGhIjKlMnOp"
    assert signaux["nb_avis"] == 8
    assert signaux["note"] == 4.3


def test_un_seul_champ_est_conservable():
    """Les conditions de Google Maps Platform n'autorisent a conserver
    durablement que le place_id. Ce test existe pour que la regle soit
    lisible dans le code et non seulement dans un commentaire."""
    assert CHAMP_STOCKABLE == "place_id"


def test_aucun_modele_ne_stocke_une_note_ou_un_avis():
    """Non-regression : si quelqu'un ajoute un champ « note Google » ou
    « nombre d'avis » a une table, ce test le signale."""
    from django.apps import apps

    interdits = {"note_google", "nb_avis", "avis_google", "rating", "user_ratings"}
    for modele in apps.get_models():
        champs = {f.name for f in modele._meta.get_fields() if hasattr(f, "name")}
        fautifs = champs & interdits
        assert not fautifs, (
            f"{modele._meta.label} stocke {fautifs} : les conditions de Google "
            "Maps Platform n'autorisent aucune conservation durable de ces "
            "champs. Seul place_id peut etre conserve."
        )


def test_aucun_resultat():
    import django.conf

    django.conf.settings.GOOGLE_PLACES_API_KEY = "cle"
    assert qualifier("zzz", client=client_qui_repond({"places": []})) is None


def test_une_erreur_de_l_api_est_signalee(settings):
    settings.GOOGLE_PLACES_API_KEY = "cle"
    with pytest.raises(PlacesIndisponible, match="403"):
        qualifier("Le Comptoir", client=client_qui_repond(statut=403))


@pytest.mark.parametrize(
    "signaux,attendu",
    [
        ({"nb_avis": 12, "note": 4.5, "site_web": ""}, "site internet"),
        ({"nb_avis": 0, "note": None, "site_web": ""}, "Aucun site web"),
        ({"nb_avis": 4, "note": 4.8, "site_web": "https://x.fr"}, "visibilite locale"),
        ({"nb_avis": 40, "note": 3.2, "site_web": "https://x.fr"}, "reputation en ligne"),
        ({"nb_avis": 40, "note": 4.6, "site_web": "https://x.fr"}, "deja avance"),
        (None, ""),
    ],
)
def test_l_argument_commercial_suit_les_signaux(signaux, attendu):
    """L'usage legitime de ces donnees : preparer un appel, pas constituer
    un fichier."""
    assert attendu in argument_commercial(signaux)

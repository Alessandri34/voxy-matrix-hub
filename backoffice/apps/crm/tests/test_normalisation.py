"""La normalisation decide des doublons : elle est testee par les cas reels
rencontres dans les exports Meta et les tableurs du client, pas par des cas
d'ecole."""

import pytest

from apps.crm.normalisation import (
    normaliser_email,
    normaliser_nom,
    normaliser_siren,
    normaliser_telephone,
    siren_valide,
)


@pytest.mark.parametrize(
    "saisie,attendu",
    [
        ("06 12 34 56 78", "+33612345678"),
        ("0612345678", "+33612345678"),
        ("+33 6 12 34 56 78", "+33612345678"),
        ("+33612345678", "+33612345678"),
        ("0033612345678", "+33612345678"),
        ("+33 06 12 34 56 78", "+33612345678"),
        ("06.12.34.56.78", "+33612345678"),
        ("06-12-34-56-78", "+33612345678"),
        # Meta renvoie parfois le numero sans son zero initial.
        ("612345678", "+33612345678"),
        # Fixe heraultais : meme traitement.
        ("04 67 12 34 56", "+33467123456"),
        # Etranger : conserve, pas interprete.
        ("+1 415 555 0132", "+14155550132"),
        # Inexploitable : chaine vide, jamais d'exception. Un lead dont le
        # telephone est illisible doit entrer dans le CRM quand meme.
        ("", ""),
        ("   ", ""),
        ("telephone", ""),
        ("06 12 34", ""),
        (None, ""),
    ],
)
def test_telephone(saisie, attendu):
    assert normaliser_telephone(saisie) == attendu


@pytest.mark.parametrize(
    "saisie,attendu",
    [
        ("  Pierre.A@Gmail.COM ", "pierre.a@gmail.com"),
        ("mailto:contact@restaurant.fr", "contact@restaurant.fr"),
        ("CONTACT @ RESTAURANT.FR", "contact@restaurant.fr"),
        ("a@b", ""),
        ("a@@b.fr", ""),
        ("@b.fr", ""),
        ("a@.fr", ""),
        ("", ""),
        (None, ""),
    ],
)
def test_email(saisie, attendu):
    assert normaliser_email(saisie) == attendu


def test_email_ne_fusionne_pas_sur_les_points():
    """Chez Gmail « p.nom@ » et « pnom@ » sont la meme boite ; ailleurs ce sont
    deux personnes. Normaliser les points ecraserait la fiche d'un homonyme."""
    assert normaliser_email("p.nom@societe.fr") != normaliser_email("pnom@societe.fr")


@pytest.mark.parametrize(
    "a,b",
    [
        ("Jean-Luc O'Brien", "jean luc obrien"),
        ("O’Brien", "obrien"),
        ("St. Pierre", "st pierre"),
        ("Hôtellerie", "hotellerie"),
        ("  DUPONT   Jean  ", "dupont jean"),
    ],
)
def test_nom_meme_cle(a, b):
    assert normaliser_nom(a) == normaliser_nom(b)
    assert normaliser_nom(a) != ""


@pytest.mark.parametrize(
    "saisie,attendu",
    [
        ("552 032 534", "552032534"),
        ("552032534", "552032534"),
        # Un SIRET saisi a la place d'un SIREN : les 9 premiers chiffres.
        ("55203253400041", "552032534"),
        ("1234", ""),
        ("", ""),
    ],
)
def test_siren(saisie, attendu):
    assert normaliser_siren(saisie) == attendu


def test_cle_de_luhn():
    """Le dernier chiffre d'un SIREN est une cle : la verifier arrete la faute
    de frappe avant qu'elle ne cree une seconde fiche entreprise."""
    assert siren_valide("552032534") is True
    assert siren_valide("356000000") is True
    assert siren_valide("552032535") is False
    assert siren_valide("") is False
    assert siren_valide("12345") is False

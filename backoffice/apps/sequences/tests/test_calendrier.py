"""Quand un message a le droit de partir.

Un envoi groupe le dimanche matin, ou le 1er mai, signale une automatisation
a tout le monde — y compris au prospect qu'on voulait convaincre qu'un
formateur s'interesse a son cas.
"""

from datetime import date

import pytest

from apps.sequences.calendrier import est_ouvre, jours_feries, paques, prochain_jour_ouvre


@pytest.mark.parametrize(
    "annee,attendu",
    [
        (2024, date(2024, 3, 31)),
        (2025, date(2025, 4, 20)),
        (2026, date(2026, 4, 5)),
        (2027, date(2027, 3, 28)),
        (2030, date(2030, 4, 21)),
    ],
)
def test_paques(annee, attendu):
    """Les feries mobiles francais s'en deduisent tous : une erreur ici
    deplacerait l'Ascension et les deux lundis."""
    assert paques(annee) == attendu


def test_les_onze_feries_legaux():
    feries = jours_feries(2026)
    assert len(feries) == 11
    for jour in (
        date(2026, 1, 1),
        date(2026, 5, 1),
        date(2026, 7, 14),
        date(2026, 8, 15),
        date(2026, 12, 25),
    ):
        assert jour in feries
    # Ascension 2026 : Paques (5 avril) + 39 jours.
    assert date(2026, 5, 14) in feries


@pytest.mark.parametrize(
    "jour,ouvre",
    [
        (date(2026, 11, 10), True),  # mardi
        (date(2026, 11, 11), False),  # Armistice
        (date(2026, 11, 14), False),  # samedi
        (date(2026, 11, 15), False),  # dimanche
        (date(2026, 11, 16), True),  # lundi
        (date(2026, 5, 1), False),  # Fete du Travail
    ],
)
def test_jours_ouvres(jour, ouvre):
    assert est_ouvre(jour) is ouvre


def test_le_prochain_jour_ouvre_saute_le_week_end():
    assert prochain_jour_ouvre(date(2026, 11, 14)) == date(2026, 11, 16)


def test_il_saute_aussi_un_ferie_colle_au_week_end():
    """1er mai 2026 tombe un vendredi : le prochain ouvre est le lundi 4."""
    assert prochain_jour_ouvre(date(2026, 5, 1)) == date(2026, 5, 4)


def test_un_jour_deja_ouvre_est_rendu_tel_quel():
    assert prochain_jour_ouvre(date(2026, 11, 10)) == date(2026, 11, 10)

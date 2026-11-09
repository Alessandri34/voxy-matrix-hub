"""Quand un message peut partir.

Un envoi groupe le dimanche matin, ou le 1er mai, signale une automatisation
a tout le monde — y compris au prospect qu'on voulait convaincre qu'un
formateur s'interesse a son cas.

Les jours feries sont calcules, pas listes : une liste codee en dur se perime
au 31 decembre et personne ne s'en apercoit avant de l'avoir enfreinte.
"""

from __future__ import annotations

from datetime import date, timedelta


def paques(annee: int) -> date:
    """Dimanche de Paques, par l'algorithme de Butcher (comput gregorien)."""
    a = annee % 19
    b, c = divmod(annee, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    m = (32 + 2 * e + 2 * i - h - k) % 7
    n = (a + 11 * h + 22 * m) // 451
    mois, jour = divmod(h + m - 7 * n + 114, 31)
    return date(annee, mois, jour + 1)


def jours_feries(annee: int) -> set[date]:
    """Les onze jours feries legaux en France metropolitaine."""
    p = paques(annee)
    return {
        date(annee, 1, 1),  # Jour de l'an
        p + timedelta(days=1),  # Lundi de Paques
        date(annee, 5, 1),  # Fete du Travail
        date(annee, 5, 8),  # Victoire 1945
        p + timedelta(days=39),  # Ascension
        p + timedelta(days=50),  # Lundi de Pentecote
        date(annee, 7, 14),  # Fete nationale
        date(annee, 8, 15),  # Assomption
        date(annee, 11, 1),  # Toussaint
        date(annee, 11, 11),  # Armistice 1918
        date(annee, 12, 25),  # Noel
    }


def est_ouvre(jour: date) -> bool:
    """Ni samedi, ni dimanche, ni jour ferie."""
    return jour.weekday() < 5 and jour not in jours_feries(jour.year)


def prochain_jour_ouvre(jour: date) -> date:
    """Le jour meme s'il est ouvre, sinon le suivant qui l'est."""
    candidat = jour
    # 11 feries et 2 jours de week-end : jamais plus d'une poignee de jours.
    for _ in range(12):
        if est_ouvre(candidat):
            return candidat
        candidat += timedelta(days=1)
    return candidat

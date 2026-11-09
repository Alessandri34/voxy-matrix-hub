"""Quel financeur pour quel prospect.

L'arbitrage qui gelait ce module est tranche : **le Conseil de la Formation
des chambres de metiers n'existe plus depuis le 1er septembre 2022**, et le
FAFCEA est le guichet unique des artisans, formations transverses comprises
(loi n° 2022-172 du 14/02/2022, decret n° 2022-956 du 29/06/2022, arrete du
29/08/2022). Il n'y a donc plus deux guichets a departager : il y en a un
par statut.

**La regle tenue : on ne devine pas.** Quand l'inscription au Repertoire des
Metiers n'est pas etablie, le routage renvoie « indetermine » et non un
financeur par defaut. Un dossier parti au mauvais guichet revient refuse
apres plusieurs semaines — delai pendant lequel la fenetre de depot de
l'autre financeur peut s'etre fermee.
"""

from __future__ import annotations

from dataclasses import dataclass

FAFCEA = "fafcea"
AGEFICE = "agefice"
FIF_PL = "fifpl"
OPCO = "opco"
INDETERMINE = "indetermine"

#: Sections NAF des professions liberales les plus courantes chez nos
#: prospects. Volontairement court : le barème du FIF PL est propre a chaque
#: profession, et ce routage ne sert qu'a orienter, jamais a chiffrer.
SECTIONS_LIBERALES = frozenset({"M", "Q"})


@dataclass(frozen=True)
class Routage:
    financeur: str
    certitude: str  # "certain" | "probable" | "indetermine"
    motif: str
    a_verifier: str = ""


def router(
    *,
    inscrite_repertoire_metiers: bool | None,
    statut_contact: str = "",
    naf: str = "",
) -> Routage:
    """Determine le financeur. Ne tranche que sur ce qui est etabli."""
    if statut_contact == "salarie":
        return Routage(
            OPCO,
            "certain",
            "contact salarie : releve de l'OPCO de la branche, pas d'un fonds "
            "de chefs d'entreprise",
            a_verifier="identifier l'OPCO de la branche — hors routage automatique",
        )

    if inscrite_repertoire_metiers is True:
        return Routage(
            FAFCEA,
            "certain",
            "inscrite au Repertoire des Metiers : FAFCEA, guichet unique des "
            "artisans depuis le 01/09/2022",
        )

    section = (naf or "").strip()[:1].upper()
    if inscrite_repertoire_metiers is False:
        if section in SECTIONS_LIBERALES:
            return Routage(
                FIF_PL,
                "probable",
                f"non inscrite au Repertoire des Metiers, NAF en section "
                f"{section} : profession liberale probable",
                a_verifier="le bareme du FIF PL est propre a chaque profession "
                "et revu chaque annee : verifier la fiche du code NAF avant "
                "tout chiffrage",
            )
        return Routage(
            AGEFICE,
            "certain",
            "non inscrite au Repertoire des Metiers : ressortissante AGEFICE",
        )

    # inscrite_repertoire_metiers is None
    return Routage(
        INDETERMINE,
        "indetermine",
        "inscription au Repertoire des Metiers non etablie. L'API Recherche "
        "d'entreprises ne renseigne ce champ que lorsqu'une activite y est "
        "declaree : son absence ne prouve pas la non-inscription.",
        a_verifier="demander l'extrait D1 (Repertoire des Metiers) ou "
        "l'attestation de contribution URSSAF, qui nomme le fonds",
    )


def router_entreprise(entreprise, contact=None) -> Routage:
    """Routage a partir des objets du CRM."""
    return router(
        inscrite_repertoire_metiers=entreprise.inscrite_repertoire_metiers,
        statut_contact=getattr(contact, "statut", "") if contact else "",
        naf=entreprise.naf or "",
    )

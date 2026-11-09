"""Les baremes des financeurs. Un seul endroit, date et source.

**Pourquoi ce fichier existe.** Le site public a deja annonce la FAFCEA a
35 €/h alors que le numerique y est transverse a 25 €/h, et un parcours
individualise non mobilisable. Un taux recopie a trois endroits finit par
diverger : ici, il n'est ecrit qu'une fois, avec la source et la date de
lecture, et tout le reste du code le lit.

**Pourquoi des baremes dates.** Les taux changent — ceux du FAFCEA ont change
le 1er septembre 2026. Une formation qui commence avant cette date releve des
taux precedents. Un bareme sans date de validite donnerait des simulations
fausses pour toute formation a cheval sur un changement.

**Montants en centimes**, partout : 0,1 + 0,2 ne fait pas 0,3 en binaire, et
un reste a charge annonce a un client doit tomber juste.

⚠️ **Toute modification ici se fait sur un document officiel telecharge et
lu**, jamais sur un guide tiers : les guides consultes le 09/11/2026 se
contredisaient entre eux sur le seuil FAFCEA de 85 €.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


class Modalite:
    """Comment la formation se deroule. Le taux en depend — et pas de la
    meme facon selon le financeur, ce qui est le piege de ce module."""

    PRESENTIEL = "presentiel"
    DISTANCIEL_SYNCHRONE = "distanciel_synchrone"
    DISTANCIEL_ASYNCHRONE = "distanciel_asynchrone"
    E_LEARNING = "e_learning"

    CHOICES = [
        (PRESENTIEL, "Presentiel"),
        (DISTANCIEL_SYNCHRONE, "Distanciel synchrone (classe virtuelle, avec formateur)"),
        (DISTANCIEL_ASYNCHRONE, "Distanciel asynchrone (sans formateur en direct)"),
        (E_LEARNING, "E-learning (plateforme, en autonomie)"),
    ]

    #: Modalites ou un formateur est present en direct. Determinant pour le
    #: FAFCEA, qui paie « presentiel ET distanciel (avec formateur) » au meme
    #: taux, et tout le reste en « autres modalites ».
    AVEC_FORMATEUR = frozenset({PRESENTIEL, DISTANCIEL_SYNCHRONE})


class NatureFormation:
    """Au sens des financeurs, pas au notre.

    La definition de « transverse » est citee mot pour mot du document
    FAFCEA : « tout stage auquel les artisans de differentes professions
    peuvent assister et/ou toute action de formation dont le programme
    presente un contenu tous publics ». **Nos six offres sont transverses** :
    un plombier et une coiffeuse peuvent suivre la meme session. Ce n'est
    pas une appreciation, c'est la definition du financeur.
    """

    TECHNIQUE = "technique"
    TRANSVERSE = "transverse"

    CHOICES = [
        (TECHNIQUE, "Technique metier"),
        (TRANSVERSE, "Transverse ou gestion specifique metier"),
    ]


@dataclass(frozen=True)
class Bareme:
    """Les conditions d'un financeur a une date donnee."""

    financeur: str
    en_vigueur_du: date
    source: str
    valide_par: str
    lu_le: date

    #: (nature, modalite) -> centimes par heure. Absent = non finance.
    taux_horaire_centimes: dict = field(default_factory=dict)

    #: Plafond annuel par entreprise, en centimes, selon la contribution.
    plafond_annuel_centimes: int = 0
    plafond_annuel_faible_cfp_centimes: int = 0
    #: Au-dessus (strictement) de ce seuil de CFP, le plafond haut s'applique.
    seuil_cfp_centimes: int = 0
    #: Comparaison au seuil : « > » pour l'AGEFICE (cotisant >= 7 €),
    #: « >= » pour le FAFCEA (CFP > 85 €). Les deux financeurs ne placent
    #: pas la borne du meme cote, et une erreur d'un centime change le
    #: plafond d'un facteur cinq.
    seuil_inclusif: bool = False

    plafond_rncp_centimes: int = 0
    duree_max_heures_par_an: int = 0
    duree_min_heures: int = 0
    max_stagiaires_distanciel: int = 0
    max_participants: int = 0
    frais_annexes_par_stage_centimes: int = 0
    qualiopi_requis_depuis: date | None = None

    def taux(self, nature: str, modalite: str) -> int | None:
        """Centimes par heure, ou None si la combinaison n'est pas financee."""
        return self.taux_horaire_centimes.get((nature, modalite))

    def plafond(self, cfp_centimes: int, *, rncp: bool = False) -> int:
        """Plafond annuel applicable a cette entreprise, en centimes."""
        if self.seuil_inclusif:
            haut = cfp_centimes >= self.seuil_cfp_centimes
        else:
            haut = cfp_centimes > self.seuil_cfp_centimes
        if not haut:
            return self.plafond_annuel_faible_cfp_centimes
        if rncp and self.plafond_rncp_centimes:
            return self.plafond_rncp_centimes
        return self.plafond_annuel_centimes


# ---------------------------------------------------------------------------
# FAFCEA — artisans inscrits au Repertoire des Metiers
#
# Guichet UNIQUE depuis le 1er septembre 2022 : la loi n° 2022-172 du
# 14/02/2022 a supprime la ventilation de la contribution entre le FAFCEA et
# les conseils de la formation des chambres de metiers, le decret
# n° 2022-956 du 29/06/2022 a abroge les articles correspondants, et
# l'arrete du 29/08/2022 a agree le FAFCEA comme seul gestionnaire (hors
# parts CPF et CEP). La CMA reste un lieu de depot et de conseil, pas un
# financeur.
# ---------------------------------------------------------------------------

_T, _TR = NatureFormation.TECHNIQUE, NatureFormation.TRANSVERSE
_P, _DS = Modalite.PRESENTIEL, Modalite.DISTANCIEL_SYNCHRONE
_DA, _EL = Modalite.DISTANCIEL_ASYNCHRONE, Modalite.E_LEARNING

FAFCEA_2026_09 = Bareme(
    financeur="fafcea",
    en_vigueur_du=date(2026, 9, 1),
    source="https://www.fafcea.com/consulter-les-criteres-de-prise-en-charge/ "
    "— PDF par secteur (Batiment, Services et Fabrication : taux identiques)",
    valide_par="Conseil d'Administration du 31/07/2026",
    lu_le=date(2026, 11, 9),
    taux_horaire_centimes={
        # « Presentiel et distanciel (avec formateur) » : un seul taux pour
        # les deux. C'est la difference majeure avec l'AGEFICE, qui paie le
        # distanciel moins cher que le presentiel.
        (_T, _P): 3500,
        (_T, _DS): 3500,
        (_TR, _P): 2500,
        (_TR, _DS): 2500,
        # « Autres modalites (cf. annexe) » : FOAD sans formateur.
        (_T, _DA): 1500,
        (_T, _EL): 1500,
        (_TR, _DA): 1500,
        (_TR, _EL): 1500,
    },
    # Pas de plafond annuel en euros au-dela du seuil : c'est la duree qui
    # plafonne (100 h), pas un montant.
    plafond_annuel_centimes=0,
    plafond_annuel_faible_cfp_centimes=60000,  # 600 € si CFP <= 85 €
    seuil_cfp_centimes=8500,
    seuil_inclusif=False,  # le plafond haut s'applique si CFP > 85 €
    duree_max_heures_par_an=100,
    duree_min_heures=4,  # « action inferieure a 4 heures : pas de prise en charge »
    max_stagiaires_distanciel=12,
    frais_annexes_par_stage_centimes=20000,
    qualiopi_requis_depuis=date(2026, 7, 1),
)

# ---------------------------------------------------------------------------
# AGEFICE — commercants, dirigeants non artisans
# ---------------------------------------------------------------------------

AGEFICE_2026 = Bareme(
    financeur="agefice",
    en_vigueur_du=date(2026, 1, 1),
    source="https://communication-agefice.fr/wp-content/uploads/2025/12/"
    "Criteres-financiers-2026-Tableau-26-12-2025.pdf",
    valide_par="Tableau « Criteres de prise en charge 2026 » du 26/12/2025",
    lu_le=date(2026, 11, 9),
    taux_horaire_centimes={
        # L'AGEFICE ne distingue pas technique et transverse : son dispositif
        # general couvre « metiers ou transversales » au meme tarif. Les deux
        # natures sont donc declarees au meme taux plutot qu'une seule, pour
        # que le code appelant n'ait pas a connaitre cette particularite.
        (_T, _P): 4200,
        (_TR, _P): 4200,
        (_T, _DS): 3500,
        (_TR, _DS): 3500,
        (_T, _DA): 2000,
        (_TR, _DA): 2000,
        (_T, _EL): 2000,
        (_TR, _EL): 2000,
    },
    plafond_annuel_centimes=300000,  # 3 000 € si cotisant >= 7 €
    plafond_annuel_faible_cfp_centimes=60000,  # 600 € sinon
    seuil_cfp_centimes=700,
    seuil_inclusif=True,  # « cotisant >= 7 € »
    # ⚠️ Reserve aux titres RNCP. Une certification RS n'y donne PAS droit.
    plafond_rncp_centimes=500000,
    max_participants=25,
)

#: Tous les baremes connus, du plus recent au plus ancien par financeur.
BAREMES = {
    "fafcea": [FAFCEA_2026_09],
    "agefice": [AGEFICE_2026],
}


class BaremeIntrouvable(LookupError):
    """Aucun bareme connu pour ce financeur a cette date.

    Volontairement une erreur, pas un repli silencieux sur le bareme le plus
    proche : une simulation faite sur un bareme qui n'etait pas en vigueur
    donnerait un reste a charge faux annonce a un client.
    """


def bareme_applicable(financeur: str, date_debut: date) -> Bareme:
    """Le bareme en vigueur a la date de DEBUT de la formation.

    Date de debut et non date du devis : c'est celle-la que les financeurs
    retiennent (« pour les formations debutant a compter du... »).
    """
    candidats = [b for b in BAREMES.get(financeur, []) if b.en_vigueur_du <= date_debut]
    if not candidats:
        connus = ", ".join(
            f"{b.financeur} depuis le {b.en_vigueur_du:%d/%m/%Y}"
            for liste in BAREMES.values()
            for b in liste
        )
        raise BaremeIntrouvable(
            f"aucun bareme connu pour « {financeur} » au {date_debut:%d/%m/%Y}. "
            f"Baremes enregistres : {connus or 'aucun'}. "
            "Ajouter le bareme dans apps/financement/bareme.py, a partir du "
            "document officiel du financeur — jamais d'un guide tiers."
        )
    return max(candidats, key=lambda b: b.en_vigueur_du)

"""Combien d'heures une enveloppe couvre.

**Ce que ce module dit** : le plafond d'heures qu'un financeur prendra en
charge pour cette entreprise, cette annee, dans cette modalite. C'est un
calcul de tresorerie, utile avant de construire une proposition.

**Ce qu'il ne dit pas** : la duree de la formation. Le volume horaire d'une
action se justifie par ses objectifs pedagogiques et le niveau de depart de
l'apprenant — c'est ce que verifie un auditeur Qualiopi (indicateurs 4 et 8),
et c'est ce qu'exige la regle d'or du projet : les fonds de formation ne
financent que de la formation reelle.

Construire 100 heures parce que l'enveloppe permet 100 heures, et non parce
que l'apprenant en a besoin, est precisement ce que vise la loi anti-fraude
n° 2026-534. Le plafond est un plafond, pas une cible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from apps.financement.bareme import Bareme, Modalite, NatureFormation, bareme_applicable


@dataclass
class VolumeFinançable:
    """Le plafond d'heures, et d'ou il vient."""

    financeur: str
    bareme: Bareme
    taux_horaire_centimes: int
    heures: int
    montant_centimes: int
    limite: str
    details: list[str] = field(default_factory=list)

    @property
    def montant(self) -> Decimal:
        return (Decimal(self.montant_centimes) / 100).quantize(Decimal("0.01"))

    def resume(self) -> str:
        taux = (Decimal(self.taux_horaire_centimes) / 100).quantize(Decimal("0.01"))
        lignes = [
            f"{self.financeur.upper()} · {taux} €/h "
            f"(bareme du {self.bareme.en_vigueur_du:%d/%m/%Y})",
            f"  Plafond : {self.heures} h, soit {self.montant} € de prise en charge",
            f"  Limite atteinte : {self.limite}",
        ]
        lignes.extend(f"  {d}" for d in self.details)
        lignes.append(
            "  ⚠️ Ceci est un PLAFOND de financement, pas une duree de "
            "formation. La duree se justifie par les objectifs pedagogiques "
            "et le niveau de depart de l'apprenant."
        )
        return "\n".join(lignes)


def volume_financable(
    *,
    financeur: str,
    date_debut: date,
    modalite: str = Modalite.PRESENTIEL,
    nature: str = NatureFormation.TRANSVERSE,
    cfp_centimes: int | None = None,
    heures_deja_consommees: int = 0,
    montant_deja_consomme_centimes: int = 0,
    rncp: bool = False,
) -> VolumeFinançable:
    """Le nombre d'heures que l'enveloppe restante couvre."""
    bareme = bareme_applicable(financeur, date_debut)
    taux = bareme.taux(nature, modalite)
    details: list[str] = []

    if not taux:
        return VolumeFinançable(
            financeur=financeur,
            bareme=bareme,
            taux_horaire_centimes=0,
            heures=0,
            montant_centimes=0,
            limite=f"combinaison non financee ({nature} en {modalite})",
        )

    candidats: list[tuple[int, str]] = []

    if bareme.duree_max_heures_par_an:
        restantes = max(0, bareme.duree_max_heures_par_an - heures_deja_consommees)
        candidats.append((restantes, f"plafond de {bareme.duree_max_heures_par_an} h/an"))
        if heures_deja_consommees:
            details.append(f"{heures_deja_consommees} h deja consommees cette annee.")

    if cfp_centimes is None:
        plafond = bareme.plafond_annuel_faible_cfp_centimes or bareme.plafond_annuel_centimes
        details.append(
            "Contribution inconnue : plafond BAS retenu. Demander "
            "l'attestation URSSAF avant de chiffrer."
        )
    else:
        plafond = bareme.plafond(cfp_centimes, rncp=rncp)

    if plafond:
        reste = max(0, plafond - montant_deja_consomme_centimes)
        euros = (Decimal(plafond) / 100).quantize(Decimal("0.01"))
        candidats.append((reste // taux, f"plafond annuel de {euros} €"))
        if montant_deja_consomme_centimes:
            consomme = (Decimal(montant_deja_consomme_centimes) / 100).quantize(Decimal("0.01"))
            details.append(f"{consomme} € deja consommes cette annee.")

    if not candidats:
        return VolumeFinançable(
            financeur=financeur,
            bareme=bareme,
            taux_horaire_centimes=taux,
            heures=0,
            montant_centimes=0,
            limite="aucun plafond connu",
            details=details,
        )

    heures, limite = min(candidats, key=lambda c: c[0])

    if bareme.duree_min_heures and 0 < heures < bareme.duree_min_heures:
        details.append(
            f"⚠️ {heures} h reste(nt), mais le {financeur.upper()} ne prend "
            f"rien en charge en dessous de {bareme.duree_min_heures} h : "
            "l'enveloppe restante est inutilisable cette annee."
        )

    return VolumeFinançable(
        financeur=financeur,
        bareme=bareme,
        taux_horaire_centimes=taux,
        heures=heures,
        montant_centimes=heures * taux,
        limite=limite,
        details=details,
    )

"""Calcul de la prise en charge et du reste a charge.

**Le chiffre que ce module produit est annonce a un client.** Il doit donc
etre juste, et dire ce qu'il ne sait pas plutot que de deviner.

Trois choses que ce calcul fait et qu'une regle de trois ne fait pas.

1. **La TVA n'est pas financee.** Le document du FAFCEA porte la mention
   « Cout horaire maximum (Hors TVA - non financé) » en toutes lettres. Le
   financeur paie sur le montant HT ; le client, lui, paie le TTC. Pour un
   micro-entrepreneur non assujetti qui ne recupere rien, le reste a charge
   reel est donc tres superieur au « HT moins prise en charge » que `D1`
   calculait : sur un Integral a 2 900 € HT finance 2 520 € par l'AGEFICE,
   c'est **960 €** et non 380 €.

2. **Les plafonds sont annuels et par entreprise.** Une entreprise qui a
   deja consomme 60 heures chez le FAFCEA n'en a plus 100 : elle en a 40. Un
   calcul qui ignore le deja-consomme promet un financement qui sera refuse
   au depot.

3. **On ne finance jamais plus que le cout reel.** Evident, et pourtant :
   un plafond horaire eleve applique a une formation peu chere donnerait une
   prise en charge superieure a la facture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from apps.financement.bareme import Bareme, Modalite, NatureFormation, bareme_applicable

#: Taux de TVA de droit commun. Un organisme de formation peut en etre
#: exonere (art. 261-4-4° a du CGI) sur attestation delivree par la DREETS :
#: la demande de VFormations est en cours. Tant qu'elle n'a pas abouti, la
#: TVA s'applique et le reste a charge du client en depend directement.
TVA_TAUX = Decimal("0.20")


@dataclass
class Simulation:
    """Ce que le financeur prendra en charge, et ce qui restera au client."""

    financeur: str
    bareme: Bareme

    heures: int
    taux_horaire_centimes: int
    cout_ht_centimes: int
    tva_centimes: int
    cout_ttc_centimes: int

    prise_en_charge_centimes: int
    reste_a_charge_centimes: int

    #: Ce qui a limite la prise en charge, en clair. Vide si rien n'a limite.
    limites: list[str] = field(default_factory=list)
    #: Regles qui EMPECHENT le financement. Non vide = ne pas promettre.
    blocages: list[str] = field(default_factory=list)
    #: Points a verifier avant le depot, sans empecher le principe.
    avertissements: list[str] = field(default_factory=list)

    @property
    def finançable(self) -> bool:
        return not self.blocages and self.prise_en_charge_centimes > 0

    def en_euros(self, centimes: int) -> Decimal:
        return (Decimal(centimes) / 100).quantize(Decimal("0.01"))

    def resume(self) -> str:
        lignes = [
            f"Financeur : {self.financeur.upper()} "
            f"(bareme du {self.bareme.en_vigueur_du:%d/%m/%Y})",
            f"  {self.heures} h a {self.en_euros(self.taux_horaire_centimes)} €/h",
            f"  Cout            : {self.en_euros(self.cout_ht_centimes)} € HT"
            + (
                f" / {self.en_euros(self.cout_ttc_centimes)} € TTC"
                if self.tva_centimes
                else " (exonere de TVA)"
            ),
            f"  Prise en charge : {self.en_euros(self.prise_en_charge_centimes)} €",
            f"  Reste a charge  : {self.en_euros(self.reste_a_charge_centimes)} €",
        ]
        if self.limites:
            lignes.append("  Limite par : " + " · ".join(self.limites))
        if self.blocages:
            lignes.append("  ⛔ NON FINANCABLE : " + " · ".join(self.blocages))
        if self.avertissements:
            lignes.append("  ⚠️  " + " · ".join(self.avertissements))
        return "\n".join(lignes)


def simuler(
    *,
    financeur: str,
    date_debut: date,
    heures: int,
    prix_ht_centimes: int,
    modalite: str = Modalite.PRESENTIEL,
    nature: str = NatureFormation.TRANSVERSE,
    cfp_centimes: int | None = None,
    heures_deja_consommees: int = 0,
    montant_deja_consomme_centimes: int = 0,
    nb_stagiaires: int = 1,
    rncp: bool = False,
    exonere_tva: bool = False,
    organisme_qualiopi: bool = True,
    organisme_reference: bool = True,
) -> Simulation:
    """Calcule la prise en charge. Ne promet rien qu'une regle interdise.

    `cfp_centimes` a None signifie « contribution inconnue » : le calcul
    retient alors le plafond BAS et le dit. Retenir le plafond haut par
    defaut produirait des devis trop optimistes, qui se decouvrent au depot.
    """
    bareme = bareme_applicable(financeur, date_debut)
    blocages: list[str] = []
    avertissements: list[str] = []
    limites: list[str] = []

    # --- Regles qui empechent purement et simplement le financement -------
    if bareme.duree_min_heures and heures < bareme.duree_min_heures:
        blocages.append(
            f"action de {heures} h : le {financeur.upper()} ne prend pas en "
            f"charge en dessous de {bareme.duree_min_heures} h"
        )
    if (
        bareme.max_stagiaires_distanciel
        and modalite != Modalite.PRESENTIEL
        and nb_stagiaires > bareme.max_stagiaires_distanciel
    ):
        blocages.append(
            f"{nb_stagiaires} stagiaires en distanciel : le "
            f"{financeur.upper()} plafonne a {bareme.max_stagiaires_distanciel}"
        )
    if bareme.max_participants and nb_stagiaires > bareme.max_participants:
        blocages.append(
            f"{nb_stagiaires} participants : le {financeur.upper()} plafonne "
            f"a {bareme.max_participants}"
        )
    if (
        bareme.qualiopi_requis_depuis
        and date_debut >= bareme.qualiopi_requis_depuis
        and not organisme_qualiopi
    ):
        blocages.append(
            f"Qualiopi exige par le {financeur.upper()} depuis le "
            f"{bareme.qualiopi_requis_depuis:%d/%m/%Y}"
        )
    if not organisme_reference:
        avertissements.append(
            f"organisme non reference {financeur.upper()} : a verifier avant le depot"
        )

    taux = bareme.taux(nature, modalite)
    if taux is None:
        blocages.append(
            f"combinaison non financee : {nature} en {modalite} chez le {financeur.upper()}"
        )
        taux = 0

    # --- Couts -------------------------------------------------------------
    tva = 0 if exonere_tva else int(Decimal(prix_ht_centimes) * TVA_TAUX)
    ttc = prix_ht_centimes + tva
    if not exonere_tva:
        avertissements.append(
            "TVA a 20 % appliquee : le financeur ne la finance pas, elle "
            "reste entierement a la charge du client"
        )

    # --- Prise en charge ---------------------------------------------------
    heures_finançables = heures
    if bareme.duree_max_heures_par_an:
        restantes = bareme.duree_max_heures_par_an - heures_deja_consommees
        if restantes < heures:
            heures_finançables = max(0, restantes)
            limites.append(
                f"plafond de {bareme.duree_max_heures_par_an} h/an "
                f"({heures_deja_consommees} h deja consommees, "
                f"{max(0, restantes)} h restantes)"
            )

    prise_en_charge = heures_finançables * taux

    if cfp_centimes is None:
        plafond = bareme.plafond_annuel_faible_cfp_centimes or bareme.plafond_annuel_centimes
        avertissements.append(
            "contribution formation inconnue : plafond BAS retenu par "
            "prudence. Demander l'attestation URSSAF avant de chiffrer."
        )
    else:
        plafond = bareme.plafond(cfp_centimes, rncp=rncp)

    if plafond:
        reste_plafond = max(0, plafond - montant_deja_consomme_centimes)
        if prise_en_charge > reste_plafond:
            prise_en_charge = reste_plafond
            euros = (Decimal(plafond) / 100).quantize(Decimal("0.01"))
            limites.append(f"plafond annuel de {euros} €")

    # On ne finance jamais plus que la facture.
    if prise_en_charge > prix_ht_centimes:
        prise_en_charge = prix_ht_centimes
        limites.append("cout reel de la formation")

    if blocages:
        prise_en_charge = 0

    return Simulation(
        financeur=financeur,
        bareme=bareme,
        heures=heures,
        taux_horaire_centimes=taux,
        cout_ht_centimes=prix_ht_centimes,
        tva_centimes=tva,
        cout_ttc_centimes=ttc,
        prise_en_charge_centimes=prise_en_charge,
        reste_a_charge_centimes=ttc - prise_en_charge,
        limites=limites,
        blocages=blocages,
        avertissements=avertissements,
    )

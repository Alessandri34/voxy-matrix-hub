"""Simulation du reste a charge.

Les scenarios sont ceux du dossier, avec ses vrais chiffres — pas des cas
d'ecole. Le montant que ce module produit est annonce a un client.
"""

from datetime import date

from apps.financement.bareme import Modalite, NatureFormation
from apps.financement.simulation import simuler

DEBUT = date(2026, 12, 1)
TRANSVERSE = NatureFormation.TRANSVERSE


def euros(centimes: int) -> int:
    return centimes // 100


# --------------------------------------------------------------------------
# Le constat qui change l'offre
# --------------------------------------------------------------------------


def test_un_artisan_et_un_commercant_ne_sont_pas_loges_a_la_meme_enseigne():
    """21 h vendues : 525 € de FAFCEA contre 882 € d'AGEFICE. A prix de
    vente egal, l'artisan paie 357 € de plus. `D1` ne distingue pas les
    deux — Karim (BTP) et Lea (coiffure) ne sont pas dans la situation de
    Sophie (restauration)."""
    commun = dict(
        date_debut=DEBUT,
        heures=21,
        prix_ht_centimes=150000,
        modalite=Modalite.PRESENTIEL,
        nature=TRANSVERSE,
        exonere_tva=True,
    )
    artisan = simuler(financeur="fafcea", cfp_centimes=10000, **commun)
    commercant = simuler(financeur="agefice", cfp_centimes=10000, **commun)

    assert euros(artisan.prise_en_charge_centimes) == 525
    assert euros(commercant.prise_en_charge_centimes) == 882
    ecart = commercant.prise_en_charge_centimes - artisan.prise_en_charge_centimes
    assert euros(ecart) == 357


# --------------------------------------------------------------------------
# La TVA, que personne ne finance
# --------------------------------------------------------------------------


def test_la_tva_change_le_reste_a_charge_du_simple_au_triple():
    """Le document du FAFCEA porte « Cout horaire maximum (Hors TVA - non
    financé) » en toutes lettres. `D1` calculait les restes a charge en HT :
    pour un micro-entrepreneur non assujetti qui ne recupere rien, le reste
    a charge reel d'un Integral n'est pas 380 € mais 960 €."""
    commun = dict(
        financeur="agefice",
        date_debut=DEBUT,
        heures=60,
        prix_ht_centimes=290000,
        modalite=Modalite.PRESENTIEL,
        nature=TRANSVERSE,
        cfp_centimes=10000,
    )
    avec_tva = simuler(exonere_tva=False, **commun)
    sans_tva = simuler(exonere_tva=True, **commun)

    # 60 h x 42 €/h = 2 520 €, sous le plafond de 3 000 €.
    assert euros(avec_tva.prise_en_charge_centimes) == 2520
    assert euros(sans_tva.prise_en_charge_centimes) == 2520

    # 2 900 € HT -> 3 480 € TTC, moins 2 520 € = 960 €.
    assert euros(avec_tva.cout_ttc_centimes) == 3480
    assert euros(avec_tva.reste_a_charge_centimes) == 960
    # Avec l'exoneration DREETS, on retombe sur le chiffre de D1.
    assert euros(sans_tva.reste_a_charge_centimes) == 380


def test_la_tva_non_exoneree_est_signalee():
    simulation = simuler(
        financeur="agefice",
        date_debut=DEBUT,
        heures=21,
        prix_ht_centimes=150000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
        exonere_tva=False,
    )
    assert any("TVA" in a for a in simulation.avertissements)


# --------------------------------------------------------------------------
# Les regles qui EMPECHENT le financement
# --------------------------------------------------------------------------


def test_moins_de_quatre_heures_bloque_chez_le_fafcea():
    """Interdit de vendre un module de 3 h a un artisan en annoncant un
    financement."""
    simulation = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=3,
        prix_ht_centimes=30000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
    )
    assert simulation.blocages
    assert "4 h" in simulation.blocages[0]
    assert simulation.prise_en_charge_centimes == 0
    assert simulation.finançable is False


def test_quatre_heures_exactement_passent():
    simulation = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=4,
        prix_ht_centimes=40000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
        exonere_tva=True,
    )
    assert not simulation.blocages
    assert euros(simulation.prise_en_charge_centimes) == 100  # 4 x 25 €


def test_plus_de_douze_stagiaires_en_distanciel_bloque_le_fafcea():
    simulation = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=14,
        prix_ht_centimes=200000,
        modalite=Modalite.DISTANCIEL_SYNCHRONE,
        cfp_centimes=10000,
        nb_stagiaires=15,
    )
    assert simulation.blocages
    assert "12" in simulation.blocages[0]


def test_la_meme_session_passe_chez_l_agefice():
    """Les deux limites different : 12 pour le FAFCEA, 25 pour l'AGEFICE.
    Une session mixte doit respecter la plus basse."""
    simulation = simuler(
        financeur="agefice",
        date_debut=DEBUT,
        heures=14,
        prix_ht_centimes=200000,
        modalite=Modalite.DISTANCIEL_SYNCHRONE,
        cfp_centimes=10000,
        nb_stagiaires=15,
        exonere_tva=True,
    )
    assert not simulation.blocages


def test_le_presentiel_echappe_a_la_limite_de_douze():
    """La regle FAFCEA vise l'action « en distanciel » : en presentiel, elle
    ne s'applique pas."""
    simulation = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=14,
        prix_ht_centimes=200000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
        nb_stagiaires=15,
        exonere_tva=True,
    )
    assert not simulation.blocages


def test_sans_qualiopi_rien_n_est_finance():
    simulation = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=21,
        prix_ht_centimes=150000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
        organisme_qualiopi=False,
    )
    assert any("Qualiopi" in b for b in simulation.blocages)


# --------------------------------------------------------------------------
# Les plafonds
# --------------------------------------------------------------------------


def test_le_plafond_horaire_annuel_du_fafcea():
    """Une entreprise qui a deja consomme 90 h n'en a plus 100 : elle en a
    10. Ignorer le deja-consomme promet un financement refuse au depot."""
    simulation = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=21,
        prix_ht_centimes=150000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
        heures_deja_consommees=90,
        exonere_tva=True,
    )
    assert euros(simulation.prise_en_charge_centimes) == 250  # 10 h x 25 €
    assert any("100 h/an" in limite for limite in simulation.limites)


def test_le_plafond_de_600_euros_ne_finance_que_24_heures():
    """A 25 €/h, 600 € font 24 h : le palier IA « Sprint 14 h » passe, le
    « Median 28 h » ne passe pas en totalite."""
    simulation = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=28,
        prix_ht_centimes=200000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=8000,
        exonere_tva=True,
    )
    assert euros(simulation.prise_en_charge_centimes) == 600
    assert any("600" in limite for limite in simulation.limites)

    sprint = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=14,
        prix_ht_centimes=120000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=8000,
        exonere_tva=True,
    )
    assert euros(sprint.prise_en_charge_centimes) == 350  # 14 x 25, sous 600


def test_le_deja_consomme_entame_le_plafond_annuel():
    simulation = simuler(
        financeur="agefice",
        date_debut=DEBUT,
        heures=60,
        prix_ht_centimes=290000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
        montant_deja_consomme_centimes=250000,
        exonere_tva=True,
    )
    assert euros(simulation.prise_en_charge_centimes) == 500  # 3 000 - 2 500


def test_on_ne_finance_jamais_plus_que_la_facture():
    simulation = simuler(
        financeur="agefice",
        date_debut=DEBUT,
        heures=21,
        prix_ht_centimes=30000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
        exonere_tva=True,
    )
    assert simulation.prise_en_charge_centimes == 30000
    assert simulation.reste_a_charge_centimes == 0
    assert any("cout reel" in limite for limite in simulation.limites)


def test_une_cfp_inconnue_retient_le_plafond_bas():
    """Retenir le plafond haut par defaut produirait des devis trop
    optimistes, qui se decouvrent au depot."""
    simulation = simuler(
        financeur="agefice",
        date_debut=DEBUT,
        heures=60,
        prix_ht_centimes=290000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=None,
        exonere_tva=True,
    )
    assert euros(simulation.prise_en_charge_centimes) == 600
    assert any("inconnue" in a for a in simulation.avertissements)
    assert any("URSSAF" in a for a in simulation.avertissements)


def test_le_resume_est_lisible_sans_relire_le_code():
    simulation = simuler(
        financeur="fafcea",
        date_debut=DEBUT,
        heures=21,
        prix_ht_centimes=150000,
        modalite=Modalite.PRESENTIEL,
        cfp_centimes=10000,
    )
    texte = simulation.resume()
    assert "FAFCEA" in texte
    assert "25.00 €/h" in texte
    assert "Reste a charge" in texte

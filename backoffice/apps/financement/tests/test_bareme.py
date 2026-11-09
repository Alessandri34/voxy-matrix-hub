"""Les baremes doivent correspondre aux documents officiels.

Ces tests ne verifient pas une logique : ils verrouillent des CHIFFRES, et
c'est leur seul interet. Le site public a deja annonce la FAFCEA a 35 €/h
alors que le numerique y est transverse a 25 €/h. Un taux qui derive sans
que personne s'en apercoive produit des devis faux pendant des mois.

Sources, telechargees et lues le 09/11/2026 :
- FAFCEA, criteres 2026 par secteur, valides par le CA du 31/07/2026 ;
- AGEFICE, tableau « Criteres de prise en charge 2026 » du 26/12/2025.
"""

from datetime import date

import pytest

from apps.financement.bareme import (
    AGEFICE_2026,
    FAFCEA_2026_09,
    BaremeIntrouvable,
    Modalite,
    NatureFormation,
    bareme_applicable,
)

TECHNIQUE, TRANSVERSE = NatureFormation.TECHNIQUE, NatureFormation.TRANSVERSE


# --------------------------------------------------------------------------
# FAFCEA
# --------------------------------------------------------------------------


def test_fafcea_le_transverse_est_a_25_euros():
    """Le chiffre le plus important du dossier : nos six offres sont
    transverses au sens du FAFCEA (« tout stage auquel les artisans de
    differentes professions peuvent assister »), donc 25 €/h et pas 35."""
    assert FAFCEA_2026_09.taux(TRANSVERSE, Modalite.PRESENTIEL) == 2500


def test_fafcea_le_technique_est_a_35_euros():
    assert FAFCEA_2026_09.taux(TECHNIQUE, Modalite.PRESENTIEL) == 3500


def test_fafcea_paie_le_distanciel_synchrone_comme_le_presentiel():
    """« Presentiel et distanciel (avec formateur) » : une seule colonne.
    C'est la difference majeure avec l'AGEFICE, qui paie le distanciel
    moins cher — une classe virtuelle n'a donc pas le meme rendement selon
    le financeur du prospect."""
    for nature in (TECHNIQUE, TRANSVERSE):
        assert FAFCEA_2026_09.taux(nature, Modalite.PRESENTIEL) == FAFCEA_2026_09.taux(
            nature, Modalite.DISTANCIEL_SYNCHRONE
        )


def test_fafcea_les_autres_modalites_tombent_a_15_euros():
    """Basculer des heures en e-learning autonome pour reduire le cout de
    production divise leur financement par presque deux."""
    for nature in (TECHNIQUE, TRANSVERSE):
        for modalite in (Modalite.DISTANCIEL_ASYNCHRONE, Modalite.E_LEARNING):
            assert FAFCEA_2026_09.taux(nature, modalite) == 1500


def test_fafcea_cent_heures_par_an():
    assert FAFCEA_2026_09.duree_max_heures_par_an == 100


def test_fafcea_quatre_heures_minimum():
    """« Action inferieure a 4 heures : pas de prise en charge »."""
    assert FAFCEA_2026_09.duree_min_heures == 4


def test_fafcea_douze_stagiaires_maximum_en_distanciel():
    """A ne pas confondre avec les 25 participants de l'AGEFICE : une
    session mixte doit respecter la plus basse des deux limites."""
    assert FAFCEA_2026_09.max_stagiaires_distanciel == 12
    assert AGEFICE_2026.max_participants == 25


def test_fafcea_six_cents_euros_si_cfp_faible():
    """Le plafond s'applique a CFP <= 85 €, donc pas a 85 € exactement
    « au-dessus ». La borne est inclusive du cote bas."""
    assert FAFCEA_2026_09.plafond(8500) == 60000  # CFP = 85 € -> plafond bas
    assert FAFCEA_2026_09.plafond(8501) == 0  # CFP > 85 € -> pas de plafond en euros
    assert FAFCEA_2026_09.plafond(0) == 60000


def test_fafcea_qualiopi_exige_depuis_juillet_2026():
    assert FAFCEA_2026_09.qualiopi_requis_depuis == date(2026, 7, 1)


# --------------------------------------------------------------------------
# AGEFICE
# --------------------------------------------------------------------------


def test_agefice_les_trois_taux():
    assert AGEFICE_2026.taux(TRANSVERSE, Modalite.PRESENTIEL) == 4200
    assert AGEFICE_2026.taux(TRANSVERSE, Modalite.DISTANCIEL_SYNCHRONE) == 3500
    assert AGEFICE_2026.taux(TRANSVERSE, Modalite.DISTANCIEL_ASYNCHRONE) == 2000


def test_agefice_les_taux_ne_dependent_pas_du_plafond():
    """Le tableau officiel repete les memes plafonds horaires dans les trois
    colonnes : seul le plafond ANNUEL change selon la contribution."""
    for modalite in (Modalite.PRESENTIEL, Modalite.DISTANCIEL_SYNCHRONE):
        assert AGEFICE_2026.taux(TECHNIQUE, modalite) == AGEFICE_2026.taux(TRANSVERSE, modalite)


def test_agefice_plafonds_annuels():
    assert AGEFICE_2026.plafond(700) == 300000  # cotisant >= 7 € -> 3 000 €
    assert AGEFICE_2026.plafond(699) == 60000  # en dessous -> 600 €
    assert AGEFICE_2026.plafond(0) == 60000


def test_agefice_le_plafond_rncp_ne_vaut_que_pour_le_rncp():
    """⚠️ Une certification enregistree au RS n'est PAS un titre RNCP :
    annoncer 5 000 € sur une offre non RNCP serait faux."""
    assert AGEFICE_2026.plafond(700, rncp=True) == 500000
    assert AGEFICE_2026.plafond(700, rncp=False) == 300000
    # Et le plafond RNCP ne sauve pas un cotisant sous le seuil.
    assert AGEFICE_2026.plafond(500, rncp=True) == 60000


def test_les_deux_financeurs_ne_placent_pas_la_borne_du_meme_cote():
    """L'AGEFICE dit « cotisant >= 7 € », le FAFCEA « CFP > 85 € ». Une
    erreur d'un centime change le plafond d'un facteur cinq."""
    assert AGEFICE_2026.seuil_inclusif is True
    assert FAFCEA_2026_09.seuil_inclusif is False


# --------------------------------------------------------------------------
# Choix du bareme par date
# --------------------------------------------------------------------------


def test_le_bareme_depend_de_la_date_de_debut():
    assert bareme_applicable("fafcea", date(2026, 12, 1)) is FAFCEA_2026_09
    assert bareme_applicable("agefice", date(2026, 6, 1)) is AGEFICE_2026


def test_une_date_anterieure_leve_plutot_que_de_deviner():
    """Un repli silencieux sur le bareme le plus proche donnerait un reste a
    charge faux, annonce a un client."""
    with pytest.raises(BaremeIntrouvable, match="aucun bareme connu"):
        bareme_applicable("fafcea", date(2026, 1, 1))


def test_un_financeur_inconnu_leve():
    with pytest.raises(BaremeIntrouvable):
        bareme_applicable("opco_inconnu", date(2026, 12, 1))


def test_chaque_bareme_porte_sa_source_et_sa_date_de_lecture():
    """Sans source datee, un chiffre ne se reverifie pas — et c'est ainsi
    qu'un taux faux survit des mois."""
    for bareme in (FAFCEA_2026_09, AGEFICE_2026):
        assert bareme.source.startswith("http")
        assert bareme.valide_par
        assert bareme.lu_le == date(2026, 11, 9)

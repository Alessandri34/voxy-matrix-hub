"""Le plafond d'heures qu'une enveloppe couvre.

Ce calcul sert a preparer une proposition. Il ne decide pas de la duree de
la formation : celle-la se justifie par les objectifs pedagogiques, et c'est
ce que verifie un auditeur Qualiopi.
"""

from datetime import date

from apps.financement.bareme import Modalite
from apps.financement.volume import volume_financable

DEBUT = date(2026, 12, 1)


def test_fafcea_a_contribution_normale_plafonne_aux_heures():
    """Pas de plafond en euros au-dela de 85 € de CFP : c'est la duree qui
    plafonne, a 100 h."""
    v = volume_financable(financeur="fafcea", date_debut=DEBUT, cfp_centimes=10000)
    assert v.heures == 100
    assert v.montant_centimes == 100 * 2500
    assert "100 h/an" in v.limite


def test_fafcea_a_faible_contribution_plafonne_a_24_heures():
    """600 € a 25 €/h font 24 h. Le palier IA « Sprint 14 h » passe, le
    « Median 28 h » ne passe pas en totalite."""
    v = volume_financable(financeur="fafcea", date_debut=DEBUT, cfp_centimes=8000)
    assert v.heures == 24
    assert "600" in v.limite


def test_agefice_plafonne_par_l_enveloppe():
    """3 000 € a 42 €/h font 71 h (arrondi a l'heure inferieure)."""
    v = volume_financable(financeur="agefice", date_debut=DEBUT, cfp_centimes=10000)
    assert v.heures == 71
    assert v.montant_centimes == 71 * 4200


def test_le_distanciel_change_le_volume_chez_l_agefice():
    """A 20 €/h en asynchrone, la meme enveloppe couvre deux fois plus
    d'heures — et c'est un piege : la qualite pedagogique ne suit pas."""
    presentiel = volume_financable(
        financeur="agefice",
        date_debut=DEBUT,
        cfp_centimes=10000,
        modalite=Modalite.PRESENTIEL,
    )
    asynchrone = volume_financable(
        financeur="agefice",
        date_debut=DEBUT,
        cfp_centimes=10000,
        modalite=Modalite.DISTANCIEL_ASYNCHRONE,
    )
    assert presentiel.heures == 71
    assert asynchrone.heures == 150


def test_le_deja_consomme_reduit_le_volume():
    v = volume_financable(
        financeur="fafcea",
        date_debut=DEBUT,
        cfp_centimes=10000,
        heures_deja_consommees=70,
    )
    assert v.heures == 30
    assert "70 h deja consommees" in " ".join(v.details)


def test_une_enveloppe_residuelle_trop_petite_est_signalee():
    """Il reste 2 h, mais le FAFCEA ne finance rien sous 4 h : l'enveloppe
    est inutilisable, et le dire evite de batir une proposition dessus."""
    v = volume_financable(
        financeur="fafcea",
        date_debut=DEBUT,
        cfp_centimes=10000,
        heures_deja_consommees=98,
    )
    assert v.heures == 2
    assert any("inutilisable" in d for d in v.details)


def test_une_contribution_inconnue_retient_le_plafond_bas():
    v = volume_financable(financeur="agefice", date_debut=DEBUT, cfp_centimes=None)
    assert v.heures == 60000 // 4200  # 600 € a 42 €/h
    assert any("URSSAF" in d for d in v.details)


def test_le_plafond_rncp_ouvre_plus_d_heures():
    v = volume_financable(financeur="agefice", date_debut=DEBUT, cfp_centimes=10000, rncp=True)
    assert v.heures == 500000 // 4200  # 5 000 € a 42 €/h


def test_le_resume_rappelle_que_c_est_un_plafond():
    """La phrase compte autant que le chiffre : construire 100 h parce que
    l'enveloppe permet 100 h est ce que vise la loi anti-fraude."""
    v = volume_financable(financeur="fafcea", date_debut=DEBUT, cfp_centimes=10000)
    texte = v.resume()
    assert "PLAFOND de financement, pas une duree" in texte
    assert "objectifs pedagogiques" in texte

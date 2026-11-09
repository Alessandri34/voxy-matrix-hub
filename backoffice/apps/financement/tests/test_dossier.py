"""Dossiers de financement : fenetres de depot et regles de gestion."""

from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.crm.models import Entreprise
from apps.financement.bareme import Modalite
from apps.financement.models import Dossier, EtatDossier
from apps.financement.services import figer_calcul
from apps.pipeline.models import Opportunite

pytestmark = pytest.mark.django_db


@pytest.fixture
def affaire():
    entreprise = Entreprise.objects.create(
        denomination="BTP Benali", siren="552032534", inscrite_repertoire_metiers=True
    )
    return Opportunite.objects.create(entreprise=entreprise, intitule="Visibilite locale 21 h")


def dossier(affaire, **extra):
    donnees = dict(
        opportunite=affaire,
        financeur="fafcea",
        date_debut_formation=timezone.localdate() + timedelta(days=45),
        heures=21,
        modalite=Modalite.PRESENTIEL,
        prix_ht_centimes=150000,
        cfp_centimes=10000,
        exonere_tva=True,
    )
    donnees.update(extra)
    return Dossier.objects.create(**donnees)


# --------------------------------------------------------------------------
# Fenetres de depot
# --------------------------------------------------------------------------


def test_fenetre_agefice(affaire):
    """De 4 mois a 15 jours calendaires avant le demarrage."""
    debut = date(2027, 6, 1)
    d = dossier(affaire, financeur="agefice", date_debut_formation=debut)
    assert d.depot_ouvre_le == debut - timedelta(days=120)
    assert d.depot_ferme_le == debut - timedelta(days=15)


def test_fenetre_fafcea(affaire):
    """3 mois avant, jusqu'au jour du debut."""
    debut = date(2027, 6, 1)
    d = dossier(affaire, date_debut_formation=debut)
    assert d.depot_ouvre_le == debut - timedelta(days=90)
    assert d.depot_ferme_le == debut


def test_un_depot_agefice_en_retard_est_signale(affaire):
    """La fenetre AGEFICE se ferme 15 jours avant : une formation qui
    demarre dans 10 jours n'est plus deposable."""
    d = dossier(
        affaire,
        financeur="agefice",
        date_debut_formation=timezone.localdate() + timedelta(days=10),
        etat=EtatDossier.A_DEPOSER,
    )
    assert d.jours_avant_cloture < 0
    assert d.depot_en_retard is True


def test_la_meme_date_passe_encore_au_fafcea(affaire):
    """Le FAFCEA accepte jusqu'au jour du debut : le meme prospect peut
    encore etre finance, s'il est artisan."""
    d = dossier(
        affaire,
        date_debut_formation=timezone.localdate() + timedelta(days=10),
        etat=EtatDossier.A_DEPOSER,
    )
    assert d.depot_en_retard is False


def test_un_dossier_deja_depose_n_est_pas_en_retard(affaire):
    d = dossier(
        affaire,
        financeur="agefice",
        date_debut_formation=timezone.localdate() - timedelta(days=5),
        etat=EtatDossier.DEPOSE,
    )
    assert d.depot_en_retard is False


# --------------------------------------------------------------------------
# Regles de gestion
# --------------------------------------------------------------------------


def test_un_refus_porte_son_motif(affaire):
    """C'est le motif qui dit si le dossier etait mal monte ou le prospect
    ineligible — donc s'il faut corriger la methode ou le ciblage."""
    d = dossier(affaire)
    d.etat = EtatDossier.REFUSE
    with pytest.raises(ValidationError) as erreur:
        d.full_clean(exclude=["opportunite"])
    assert "motif_refus" in str(erreur.value)


def test_le_refus_sans_motif_est_refuse_par_la_base(affaire):
    d = dossier(affaire)
    with pytest.raises(IntegrityError), transaction.atomic():
        Dossier.objects.filter(pk=d.pk).update(etat=EtatDossier.REFUSE, motif_refus="")


def test_un_depot_agefice_exige_son_point_d_accueil(affaire):
    """Un dossier AGEFICE envoye au siege n'est pas instruit."""
    d = dossier(affaire, financeur="agefice")
    d.etat = EtatDossier.DEPOSE
    with pytest.raises(ValidationError) as erreur:
        d.full_clean(exclude=["opportunite"])
    assert "Point d'Accueil" in str(erreur.value)

    d.point_accueil = "CCI Herault — Montpellier"
    d.full_clean(exclude=["opportunite"])  # ne leve plus


def test_un_dossier_sans_heure_est_refuse(affaire):
    with pytest.raises(IntegrityError), transaction.atomic():
        dossier(affaire, heures=0)


# --------------------------------------------------------------------------
# Le calcul fige
# --------------------------------------------------------------------------


def test_figer_le_calcul_inscrit_tout_ce_qu_il_faut_pour_l_expliquer(affaire):
    d = dossier(affaire)
    simulation = figer_calcul(d)
    d.refresh_from_db()

    assert d.taux_horaire_centimes == 2500
    assert d.prise_en_charge_centimes == 52500  # 21 h x 25 €
    assert d.bareme_en_vigueur_du == date(2026, 9, 1)
    assert d.detail_calcul["source_bareme"].startswith("http")
    assert "31/07/2026" in d.detail_calcul["bareme_valide_par"]
    assert simulation.finançable is True


def test_le_bareme_est_fige_et_ne_bouge_plus(affaire):
    """Un dossier depose garde ses conditions. Recalculer a la lecture
    donnerait, six mois plus tard, un montant different de celui annonce au
    client et accepte par le financeur."""
    d = dossier(affaire)
    figer_calcul(d)
    d.refresh_from_db()
    fige = (d.bareme_en_vigueur_du, d.taux_horaire_centimes, d.prise_en_charge_centimes)

    d.etat = EtatDossier.DEPOSE
    d.save()
    d.refresh_from_db()
    assert (d.bareme_en_vigueur_du, d.taux_horaire_centimes, d.prise_en_charge_centimes) == fige


def test_le_calcul_laisse_une_activite_lisible(affaire):
    from apps.crm.models import Activite

    d = dossier(affaire)
    figer_calcul(d)
    activite = Activite.objects.filter(id_objet=str(d.pk)).first()
    assert activite is not None
    assert "FAFCEA" in activite.contenu
    assert "Reste a charge" in activite.contenu


def test_un_blocage_met_la_prise_en_charge_a_zero(affaire):
    d = dossier(affaire, heures=3, prix_ht_centimes=30000)
    simulation = figer_calcul(d)
    d.refresh_from_db()
    assert d.prise_en_charge_centimes == 0
    assert d.detail_calcul["blocages"]
    assert simulation.finançable is False

"""La chaine qui va de l'euro depense au client forme.

Une regie sait dire le cout par lead. Elle ne sait pas dire le cout par
CLIENT, parce qu'elle ignore ce qui se passe apres le formulaire. Ces tests
verrouillent ce calcul-la, qui est le seul sur lequel decider d'un budget.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.crm.models import Entreprise, Lead, SourceLead
from apps.financement.bareme import Modalite
from apps.financement.models import Dossier, EtatDossier
from apps.pipeline.models import Etape
from apps.publicite.attribution import (
    attribuer,
    creer_les_campagnes_manquantes,
    par_campagne,
    rapprocher_les_leads,
)
from apps.publicite.models import Campagne, Depense, Plateforme, SourceChiffre

pytestmark = pytest.mark.django_db


@pytest.fixture
def campagne():
    return Campagne.objects.create(
        plateforme=Plateforme.META,
        identifiant_externe="23851234567890123",
        nom="Visibilite locale — Herault",
        offre="OFFRE-3",
    )


@pytest.fixture
def entreprise():
    return Entreprise.objects.create(denomination="Le Comptoir", siren="552032534")


def lead_de(campagne, entreprise=None, **extra):
    donnees = dict(
        source=SourceLead.META_LEAD_ADS,
        campagne=campagne,
        meta_campagne_id=campagne.identifiant_externe,
        meta_campagne_nom=campagne.nom,
        entreprise=entreprise,
    )
    donnees.update(extra)
    return Lead.objects.create(**donnees)


# --------------------------------------------------------------------------
# Les depenses
# --------------------------------------------------------------------------


def test_une_depense_porte_sa_source(campagne):
    """Un montant saisi a la main et un montant rapatrie de l'API ne se
    discutent pas de la meme facon."""
    d = Depense.objects.create(
        campagne=campagne,
        mois=date(2026, 11, 1),
        montant_centimes=120000,
        impressions=50000,
        clics=800,
    )
    assert d.source == SourceChiffre.MANUELLE
    assert d.montant == Decimal("1200.00")
    assert d.cpc_centimes == 150  # 1 200 € / 800 clics
    assert d.cpm_centimes == 2400  # 1 200 € / 50 000 x 1000
    assert d.ctr == Decimal("1.60")


def test_une_periode_mensuelle_commence_le_premier(campagne):
    """Une periode qui commence le 15 rend tous les cumuls faux."""
    d = Depense(campagne=campagne, mois=date(2026, 11, 15), montant_centimes=1000)
    with pytest.raises(ValidationError, match="1er du mois"):
        d.full_clean(exclude=["campagne"])


def test_un_jour_doit_tomber_dans_son_mois(campagne):
    d = Depense(
        campagne=campagne,
        mois=date(2026, 11, 1),
        jour=date(2026, 10, 3),
        montant_centimes=1000,
    )
    with pytest.raises(ValidationError, match="dans le mois"):
        d.full_clean(exclude=["campagne"])


def test_plus_de_clics_que_d_impressions_est_refuse(campagne):
    """Un signe que les deux chiffres ne viennent pas de la meme source."""
    with pytest.raises(IntegrityError), transaction.atomic():
        Depense.objects.create(
            campagne=campagne,
            mois=date(2026, 11, 1),
            montant_centimes=1000,
            impressions=100,
            clics=200,
        )


def test_deux_depenses_mensuelles_sur_le_meme_mois_sont_refusees(campagne):
    """Non-regression.

    En SQL, NULL n'est pas egal a NULL : une contrainte unique sur
    (campagne, mois, jour) ne se declenche PAS entre deux lignes mensuelles,
    ou `jour` est nul. Les deux etaient acceptees, et toute la depense
    comptee en double — avec elle, tous les couts par client.
    """
    Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=1000)
    with pytest.raises(IntegrityError), transaction.atomic():
        Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=2000)


def test_deux_depenses_quotidiennes_le_meme_jour_sont_refusees(campagne):
    Depense.objects.create(
        campagne=campagne,
        mois=date(2026, 11, 1),
        jour=date(2026, 11, 3),
        montant_centimes=1000,
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        Depense.objects.create(
            campagne=campagne,
            mois=date(2026, 11, 1),
            jour=date(2026, 11, 3),
            montant_centimes=2000,
        )


def test_une_mensuelle_et_une_quotidienne_coexistent(campagne):
    """Elles ne sont pas en conflit : la quotidienne detaille, la mensuelle
    totalise. ⚠️ Les additionner compterait deux fois — c'est a l'appelant
    de choisir une maille."""
    Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=1000)
    Depense.objects.create(
        campagne=campagne,
        mois=date(2026, 11, 1),
        jour=date(2026, 11, 3),
        montant_centimes=50,
    )
    assert Depense.objects.count() == 2


# --------------------------------------------------------------------------
# La chaine complete
# --------------------------------------------------------------------------


def test_du_premier_euro_au_client_paye(campagne, entreprise):
    """Le scenario complet : 1 200 € depenses, 10 leads, 4 opportunites,
    2 dossiers deposes, 1 accord, 1 client paye a 1 950 €."""
    Depense.objects.create(
        campagne=campagne,
        mois=date(2026, 11, 1),
        montant_centimes=120000,
        impressions=50000,
        clics=800,
    )
    leads = [lead_de(campagne, entreprise) for _ in range(10)]

    from apps.pipeline.services import promouvoir_lead

    affaires = [promouvoir_lead(lead, intitule="Visibilite locale") for lead in leads[:4]]
    for affaire in affaires[:2]:
        Dossier.objects.create(
            opportunite=affaire,
            financeur="agefice",
            date_debut_formation=timezone.localdate() + timedelta(days=40),
            heures=21,
            modalite=Modalite.PRESENTIEL,
            prix_ht_centimes=195000,
            etat=EtatDossier.DEPOSE,
            point_accueil="CCI Herault",
        )
    Dossier.objects.filter(opportunite=affaires[0]).update(etat=EtatDossier.ACCORDE)
    affaires[0].etape = Etape.PAYE
    affaires[0].montant_estime_centimes = 195000
    affaires[0].save()

    a = attribuer(campagne)

    assert a.depense_centimes == 120000
    assert a.leads == 10
    assert a.opportunites == 4
    assert a.dossiers_deposes == 2
    assert a.accords == 1
    assert a.payes == 1
    assert a.chiffre_affaires_centimes == 195000

    # Les chiffres que la regie ne sait pas donner :
    assert a.cout_par_lead_centimes == 12000  # 1 200 € / 10
    assert a.cout_par_opportunite_centimes == 30000  # 1 200 € / 4
    assert a.cout_par_client_centimes == 120000  # 1 200 € / 1
    assert a.roas == Decimal("1.62")  # 1 950 / 1 200
    assert a.rentable is True


def test_une_campagne_qui_coute_plus_qu_elle_ne_rapporte(campagne, entreprise):
    Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=300000)
    lead = lead_de(campagne, entreprise)
    from apps.pipeline.services import promouvoir_lead

    affaire = promouvoir_lead(lead, intitule="Atelier")
    affaire.etape = Etape.PAYE
    affaire.montant_estime_centimes = 49000
    affaire.save()

    a = attribuer(campagne)
    assert a.roas == Decimal("0.16")
    assert a.rentable is False


def test_l_entonnoir_donne_les_taux_de_passage(campagne, entreprise):
    Depense.objects.create(
        campagne=campagne,
        mois=date(2026, 11, 1),
        montant_centimes=100000,
        impressions=100000,
        clics=2000,
    )
    for _ in range(20):
        lead_de(campagne, entreprise)

    a = attribuer(campagne)
    noms = [m.nom for m in a.maillons]
    assert noms[:3] == ["Impressions", "Clics", "Leads"]
    clics = next(m for m in a.maillons if m.nom == "Clics")
    leads = next(m for m in a.maillons if m.nom == "Leads")
    assert clics.taux == Decimal("2.00")  # 2 000 / 100 000
    assert leads.taux == Decimal("1.00")  # 20 / 2 000


def test_les_doublons_ne_comptent_pas(campagne, entreprise):
    """Un doublon gonflerait le volume et ferait croire a un cout par lead
    plus bas qu'il n'est."""
    Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=100000)
    original = lead_de(campagne, entreprise)
    lead_de(campagne, entreprise, doublon_de=original)

    a = attribuer(campagne)
    assert a.leads == 1
    assert a.cout_par_lead_centimes == 100000


def test_sans_depense_les_couts_sont_inconnus_pas_nuls(campagne, entreprise):
    """Zero serait un mensonge : on ne sait pas, ce n'est pas gratuit."""
    lead_de(campagne, entreprise)
    a = attribuer(campagne)
    assert a.cout_par_lead_centimes is None
    assert a.roas is None
    assert a.rentable is None
    assert any("aucune depense" in m for m in a.avertissements)


def test_de_la_depense_sans_lead_est_signalee(campagne):
    """Presque toujours un identifiant de campagne mal recopie."""
    Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=100000)
    a = attribuer(campagne)
    assert any("identifiant de campagne" in m for m in a.avertissements)


def test_les_leads_meta_sans_campagne_sont_signales(campagne, entreprise):
    Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=100000)
    lead_de(campagne, entreprise)
    Lead.objects.create(
        source=SourceLead.META_LEAD_ADS, meta_campagne_id="99999", nom_declare="Orphelin"
    )
    a = attribuer()
    assert any("sans campagne rattachee" in m for m in a.avertissements)


def test_le_classement_met_le_cout_par_client_le_plus_bas_en_tete(entreprise):
    """Une campagne a 200 leads et 90 € le client vaut mieux qu'une a 400
    leads et 300 € : le tableau doit le montrer d'un coup d'oeil."""
    from apps.pipeline.services import promouvoir_lead

    for nom, identifiant, depense_c, nb_payes in [
        ("Chere", "111", 300000, 1),
        ("Efficace", "222", 90000, 1),
    ]:
        c = Campagne.objects.create(
            plateforme=Plateforme.META, identifiant_externe=identifiant, nom=nom
        )
        Depense.objects.create(campagne=c, mois=date(2026, 11, 1), montant_centimes=depense_c)
        for _ in range(nb_payes):
            affaire = promouvoir_lead(lead_de(c, entreprise), intitule="x")
            affaire.etape = Etape.PAYE
            affaire.save()

    lignes = par_campagne()
    assert lignes[0].libelle == "Efficace"
    assert lignes[0].cout_par_client_centimes == 90000


# --------------------------------------------------------------------------
# Rapprochement
# --------------------------------------------------------------------------


def test_le_rapprochement_relie_les_leads_a_leur_campagne(campagne):
    Lead.objects.create(
        source=SourceLead.META_LEAD_ADS,
        meta_campagne_id=campagne.identifiant_externe,
        nom_declare="Sophie",
    )
    resultat = rapprocher_les_leads()
    assert resultat["rattaches"] == 1
    assert Lead.objects.get(nom_declare="Sophie").campagne_id == campagne.pk


def test_le_rapprochement_est_idempotent(campagne):
    Lead.objects.create(
        source=SourceLead.META_LEAD_ADS,
        meta_campagne_id=campagne.identifiant_externe,
        nom_declare="Sophie",
    )
    rapprocher_les_leads()
    assert rapprocher_les_leads()["rattaches"] == 0


def test_une_campagne_inconnue_est_signalee_pas_inventee(campagne):
    Lead.objects.create(
        source=SourceLead.META_LEAD_ADS,
        meta_campagne_id="inconnue-999",
        meta_campagne_nom="Campagne fantome",
        nom_declare="X",
    )
    resultat = rapprocher_les_leads()
    assert resultat["rattaches"] == 0
    assert "inconnue-999" in resultat["campagnes_inconnues"]


def test_on_peut_creer_les_campagnes_manquantes(campagne):
    """Sans depense elles n'apportent aucun cout, mais elles font apparaitre
    le volume de leads par campagne — ce qui suffit deja a voir laquelle
    produit."""
    Lead.objects.create(
        source=SourceLead.META_LEAD_ADS,
        meta_campagne_id="nouvelle-123",
        meta_campagne_nom="Prospection IA",
        nom_declare="X",
    )
    assert creer_les_campagnes_manquantes() == 1
    creee = Campagne.objects.get(identifiant_externe="nouvelle-123")
    assert creee.nom == "Prospection IA"
    assert rapprocher_les_leads()["rattaches"] == 1


def test_l_attribution_est_un_majorant_et_le_dit():
    """Un prospect qui voit une publicite sans cliquer, puis cherche sur
    Google deux semaines plus tard, apparait comme un lead sans campagne."""
    from apps.publicite import attribution

    texte = " ".join(attribution.__doc__.split())
    assert "MAJORANT" in texte
    assert "attribution au dernier clic declare" in texte


def test_une_campagne_saisie_au_mois_et_au_jour_n_est_pas_comptee_deux_fois(campagne):
    """Non-regression.

    La ligne mensuelle totalise, les quotidiennes detaillent. Les
    additionner doublerait la depense du mois, et avec elle tous les couts
    par client. Regle : des qu'un mois a des lignes quotidiennes, elles font
    foi et la mensuelle est ignoree.
    """
    Depense.objects.create(
        campagne=campagne,
        mois=date(2026, 11, 1),
        montant_centimes=100000,
        impressions=10000,
        clics=200,
    )
    for jour, montant in [(3, 30000), (4, 40000), (5, 30000)]:
        Depense.objects.create(
            campagne=campagne,
            mois=date(2026, 11, 1),
            jour=date(2026, 11, jour),
            montant_centimes=montant,
            impressions=3000,
            clics=60,
        )

    a = attribuer(campagne)
    # 30 000 + 40 000 + 30 000 = 100 000, et NON 200 000.
    assert a.depense_centimes == 100000
    assert a.impressions == 9000
    assert a.clics == 180


def test_un_mois_sans_detail_garde_sa_ligne_mensuelle(campagne):
    """Octobre n'a qu'une mensuelle, novembre a du detail : les deux
    comptent, chacun a sa maille."""
    Depense.objects.create(campagne=campagne, mois=date(2026, 10, 1), montant_centimes=80000)
    Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=100000)
    Depense.objects.create(
        campagne=campagne,
        mois=date(2026, 11, 1),
        jour=date(2026, 11, 3),
        montant_centimes=25000,
    )
    a = attribuer(campagne)
    assert a.depense_centimes == 80000 + 25000


def test_un_etage_a_zero_donne_une_barre_vide(campagne, entreprise):
    """Non-regression.

    La largeur de barre retombait sur 100 % quand le taux etait inconnu
    (etage precedent a zero) : un zero s'affichait avec une barre PLEINE,
    ce qui se lit exactement a l'envers.
    """
    Depense.objects.create(
        campagne=campagne,
        mois=date(2026, 11, 1),
        montant_centimes=100000,
        impressions=10000,
        clics=200,
    )
    lead_de(campagne, entreprise)

    a = attribuer(campagne)
    par_nom = {m.nom: m for m in a.maillons}
    assert par_nom["Impressions"].largeur == 100  # premier etage, plein
    assert par_nom["Clients payes"].valeur == 0
    assert par_nom["Clients payes"].largeur == 0  # et non 100
    assert par_nom["Accords financeur"].largeur == 0


def test_une_largeur_ne_depasse_jamais_cent(campagne, entreprise):
    """Un taux de passage superieur a 100 % (plus d'opportunites que de
    leads, apres une saisie manuelle) ne doit pas deborder du cadre."""
    Depense.objects.create(campagne=campagne, mois=date(2026, 11, 1), montant_centimes=1000)
    for _ in range(2):
        lead_de(campagne, entreprise)
    a = attribuer(campagne)
    for m in a.maillons:
        assert 0 <= m.largeur <= 100

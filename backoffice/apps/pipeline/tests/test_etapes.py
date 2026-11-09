"""Le motif de perte obligatoire est un critere de sortie de la phase 1.
Il est teste sur tous les chemins d'ecriture, pas seulement sur le formulaire :
une regle qui ne tient que dans un formulaire ne tient pas."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.crm.models import Activite, Entreprise, Lead, SourceLead
from apps.pipeline.models import Etape, Financeur, MotifPerte, Opportunite, PassageEtape
from apps.pipeline.services import changer_etape, promouvoir_lead

pytestmark = pytest.mark.django_db


@pytest.fixture
def entreprise():
    return Entreprise.objects.create(
        denomination="Le Comptoir", siren="552032534", code_postal="34000", commune="Montpellier"
    )


@pytest.fixture
def affaire(entreprise):
    return Opportunite.objects.create(
        entreprise=entreprise, intitule="Visibilite locale 21 h", etape=Etape.NOUVEAU
    )


def test_les_onze_etapes_sont_la():
    """Les onze etapes du cadrage, dans l'ordre. « Dossier depose » et
    « Accord financeur » restent distinctes : le delai entre les deux
    n'appartient pas a l'organisme."""
    assert Etape.values == [
        "nouveau",
        "contacte",
        "qualifie",
        "rdv_diagnostic",
        "proposition_envoyee",
        "dossier_depose",
        "accord_financeur",
        "inscrit",
        "forme",
        "paye",
        "perdu",
    ]


def test_perdu_sans_motif_est_refuse_par_la_base(affaire):
    """La contrainte CHECK, et non seulement `clean()` : l'administration
    Django, un import et une tache Celery contournent tous `clean()`."""
    with pytest.raises(IntegrityError), transaction.atomic():
        Opportunite.objects.filter(pk=affaire.pk).update(etape=Etape.PERDU, motif_de_perte="")


def test_perdu_sans_motif_est_refuse_par_le_service(affaire):
    with pytest.raises(ValidationError) as erreur:
        changer_etape(affaire, Etape.PERDU)
    assert "motif" in str(erreur.value)


def test_perdu_avec_motif_passe(affaire):
    changer_etape(affaire, Etape.PERDU, motif_de_perte=MotifPerte.RESTE_A_CHARGE)
    affaire.refresh_from_db()
    assert affaire.etape == Etape.PERDU
    assert affaire.motif_de_perte == MotifPerte.RESTE_A_CHARGE
    assert affaire.probabilite == 0
    assert affaire.date_cloture is not None
    assert affaire.est_close is True


def test_motif_autre_exige_une_explication(affaire):
    """Sans cela, « Autre » absorbe tous les cas et ne renseigne plus rien."""
    with pytest.raises(ValidationError) as erreur:
        changer_etape(affaire, Etape.PERDU, motif_de_perte=MotifPerte.AUTRE)
    assert "commentaire_perte" in str(erreur.value)
    changer_etape(
        affaire,
        Etape.PERDU,
        motif_de_perte=MotifPerte.AUTRE,
        commentaire_perte="Le client a vendu son fonds de commerce.",
    )
    affaire.refresh_from_db()
    assert affaire.etape == Etape.PERDU


def test_sortir_de_perdu_efface_le_motif(affaire):
    """Un motif de perte sur une affaire en cours fausserait le comptage des
    motifs, qui est la seule raison d'avoir ce champ."""
    changer_etape(affaire, Etape.PERDU, motif_de_perte=MotifPerte.PAS_LE_MOMENT)
    changer_etape(affaire, Etape.CONTACTE)
    affaire.refresh_from_db()
    assert affaire.motif_de_perte == ""
    assert affaire.date_cloture is None


def test_chaque_passage_est_date(affaire):
    """Une colonne `etape` dit ou en est l'affaire, jamais combien de temps
    elle a mis. Le temps par etape montre ou le pipeline se bouche."""
    debut = timezone.now() - timezone.timedelta(days=10)
    PassageEtape.objects.create(opportunite=affaire, etape=Etape.NOUVEAU, entree_le=debut)

    changer_etape(affaire, Etape.CONTACTE, maintenant=debut + timezone.timedelta(days=3))
    changer_etape(affaire, Etape.PROPOSITION_ENVOYEE, maintenant=debut + timezone.timedelta(days=7))

    passages = list(affaire.passages.order_by("entree_le"))
    assert [p.etape for p in passages] == [
        Etape.NOUVEAU,
        Etape.CONTACTE,
        Etape.PROPOSITION_ENVOYEE,
    ]
    assert passages[0].duree_jours == 3.0
    assert passages[1].duree_jours == 4.0
    # L'etape courante n'est pas encore sortie.
    assert passages[2].sortie_le is None


def test_changement_etape_laisse_une_activite(affaire):
    changer_etape(affaire, Etape.QUALIFIE)
    activite = Activite.objects.filter(id_objet=str(affaire.pk)).first()
    assert activite is not None
    assert "Nouveau → Qualifie" in activite.contenu


def test_etape_identique_ne_fait_rien(affaire):
    changer_etape(affaire, Etape.NOUVEAU)
    assert affaire.passages.count() == 0
    assert Activite.objects.count() == 0


def test_etape_inconnue_refusee(affaire):
    with pytest.raises(ValidationError):
        changer_etape(affaire, "etape_inventee")


def test_probabilite_ne_depasse_pas_cent(affaire):
    with pytest.raises(IntegrityError), transaction.atomic():
        Opportunite.objects.filter(pk=affaire.pk).update(probabilite=150)


def test_montant_en_centimes(entreprise):
    """Jamais de flottant : 0,1 + 0,2 ne fait pas 0,3 en binaire, et un devis
    doit tomber juste."""
    affaire = Opportunite.objects.create(
        entreprise=entreprise, intitule="Essentiel 35 h", montant_estime_centimes=195000
    )
    assert str(affaire.montant_estime) == "1950.00"


def test_financeur_est_informatif_en_phase_1(affaire):
    """Le routage automatique est gele : l'arbitrage CMA contre FAFCEA
    transverse n'est pas tranche sur sources primaires. Le champ existe,
    aucune regle ne le remplit."""
    assert affaire.financeur_probable == Financeur.INDETERMINE


def test_promouvoir_un_lead(entreprise):
    lead = Lead.objects.create(
        source=SourceLead.META_LEAD_ADS,
        nom_declare="Sophie Martin",
        formation_demandee="Visibilite locale",
        entreprise=entreprise,
    )
    affaire = promouvoir_lead(lead, formation="OFFRE-3")
    assert affaire.intitule == "Visibilite locale"
    assert affaire.etape == Etape.NOUVEAU
    assert affaire.passages.count() == 1
    # Deux appels ne creent pas deux affaires.
    assert promouvoir_lead(lead).pk == affaire.pk
    assert Opportunite.objects.count() == 1


def test_promouvoir_refuse_un_lead_sans_entreprise():
    """Sans entreprise, l'affaire ne peut etre ni devisee ni deposee chez un
    financeur : elle encombrerait le Kanban sans pouvoir avancer."""
    lead = Lead.objects.create(source=SourceLead.META_LEAD_ADS, nom_declare="Anonyme")
    with pytest.raises(ValidationError) as erreur:
        promouvoir_lead(lead)
    assert "entreprise" in str(erreur.value)


def test_promouvoir_refuse_un_doublon(entreprise):
    original = Lead.objects.create(
        source=SourceLead.META_LEAD_ADS, nom_declare="Sophie Martin", entreprise=entreprise
    )
    doublon = Lead.objects.create(
        source=SourceLead.IMPORT_CSV,
        nom_declare="Sophie Martin",
        entreprise=entreprise,
        doublon_de=original,
    )
    with pytest.raises(ValidationError) as erreur:
        promouvoir_lead(doublon)
    assert "doublon" in str(erreur.value)


def test_un_echec_ne_salit_pas_l_objet_en_memoire(affaire):
    """Non-regression.

    `transaction.atomic` annule la base, pas l'objet Python. Avant correction,
    un `changer_etape` refuse laissait l'instance portant deja la nouvelle
    etape : le second appel voyait « rien a changer » et ne faisait rien. Un
    utilisateur qui corrige son motif apres l'erreur voyait son changement
    disparaitre sans aucun message.
    """
    with pytest.raises(ValidationError):
        changer_etape(affaire, Etape.PERDU)  # sans motif

    # L'objet est revenu a son etat d'avant, pas reste sur « perdu ».
    assert affaire.etape == Etape.NOUVEAU
    assert affaire.motif_de_perte == ""
    assert affaire.date_cloture is None

    # Et la correction aboutit sur la meme instance.
    changer_etape(affaire, Etape.PERDU, motif_de_perte=MotifPerte.INJOIGNABLE)
    affaire.refresh_from_db()
    assert affaire.etape == Etape.PERDU
    assert affaire.motif_de_perte == MotifPerte.INJOIGNABLE


def test_un_echec_n_ecrit_aucun_passage(affaire):
    with pytest.raises(ValidationError):
        changer_etape(affaire, Etape.PERDU)
    assert PassageEtape.objects.count() == 0
    assert Activite.objects.count() == 0

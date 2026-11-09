"""Les pieces d'un dossier.

Un dossier se refuse pour une piece manquante, et la piece manquante se
decouvre au depot — quand la fenetre est sur le point de se fermer.
"""

from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.crm.models import Entreprise
from apps.documents.models import PIECES_PAR_FINANCEUR, EtatPiece, Piece, TypePiece
from apps.documents.services import controler, preparer_les_pieces
from apps.financement.bareme import Modalite
from apps.financement.models import Dossier
from apps.pipeline.models import Opportunite

pytestmark = pytest.mark.django_db


@pytest.fixture
def dossier():
    entreprise = Entreprise.objects.create(denomination="Le Comptoir", siren="552032534")
    affaire = Opportunite.objects.create(entreprise=entreprise, intitule="Visibilite locale")
    return Dossier.objects.create(
        opportunite=affaire,
        financeur="agefice",
        date_debut_formation=timezone.localdate() + timedelta(days=60),
        heures=21,
        modalite=Modalite.PRESENTIEL,
        prix_ht_centimes=150000,
    )


def test_la_liste_existe_avant_les_pieces(dossier):
    """Une case a cocher vide vaut mieux qu'une liste dans la tete de
    quelqu'un : c'est ce qui fait qu'une piece manquante se voit trois
    semaines avant le depot."""
    crees = preparer_les_pieces(dossier)
    assert crees == len(PIECES_PAR_FINANCEUR["agefice"]["avant_depot"])
    assert dossier.pieces.count() == crees
    assert all(p.etat == EtatPiece.ATTENDUE for p in dossier.pieces.all())


def test_preparer_deux_fois_ne_duplique_pas(dossier):
    preparer_les_pieces(dossier)
    assert preparer_les_pieces(dossier) == 0


def test_un_dossier_neuf_est_incomplet(dossier):
    preparer_les_pieces(dossier)
    controle = controler(dossier)
    assert controle.complet is False
    assert TypePiece.DEVIS in controle.manquantes
    assert "incomplet" in controle.resume()


def test_un_lien_externe_suffit(dossier):
    """Rien n'est stocke sur le VPS, et la piece compte comme fournie."""
    preparer_les_pieces(dossier)
    piece = dossier.pieces.get(type=TypePiece.DEVIS)
    piece.lien_externe = "https://drive.example.com/devis-123"
    piece.etat = EtatPiece.VALIDEE
    piece.save()

    piece.refresh_from_db()
    assert piece.fournie is True
    assert piece.ou == "lien externe"
    assert piece.recue_le is not None
    assert piece.validee_le is not None
    assert TypePiece.DEVIS not in controler(dossier).manquantes


def test_une_piece_recue_sans_support_est_refusee_par_la_base(dossier):
    """« Validee » sans fichier ni lien n'a rien valide."""
    with pytest.raises(IntegrityError), transaction.atomic():
        Piece.objects.create(dossier=dossier, type=TypePiece.RIB, etat=EtatPiece.VALIDEE)


def test_le_formulaire_le_dit_avant_la_base(dossier):
    piece = Piece(dossier=dossier, type=TypePiece.RIB, etat=EtatPiece.VALIDEE)
    with pytest.raises(ValidationError, match="fichier ou"):
        piece.full_clean(exclude=["dossier"])


def test_une_piece_autre_porte_un_libelle(dossier):
    piece = Piece(dossier=dossier, type=TypePiece.AUTRE)
    with pytest.raises(ValidationError, match="libelle"):
        piece.full_clean(exclude=["dossier"])


def test_une_piece_refusee_maintient_le_dossier_incomplet(dossier):
    preparer_les_pieces(dossier)
    for piece in dossier.pieces.all():
        piece.lien_externe = "https://drive.example.com/x"
        piece.etat = EtatPiece.VALIDEE
        piece.save()
    assert controler(dossier).complet is True

    rib = dossier.pieces.get(type=TypePiece.RIB)
    rib.etat = EtatPiece.REFUSEE
    rib.save()
    controle = controler(dossier)
    assert controle.complet is False
    assert TypePiece.RIB in controle.refusees


def test_une_piece_recue_remonte_a_verifier(dossier):
    preparer_les_pieces(dossier)
    devis = dossier.pieces.get(type=TypePiece.DEVIS)
    devis.lien_externe = "https://drive.example.com/devis"
    devis.etat = EtatPiece.RECUE
    devis.save()
    controle = controler(dossier)
    assert TypePiece.DEVIS in controle.a_verifier
    assert "À verifier" in controle.resume()


def test_les_deux_financeurs_n_exigent_pas_la_meme_chose(dossier):
    """Apres la formation, le FAFCEA demande une attestation d'assiduite
    la ou l'AGEFICE demande une attestation de fin."""
    agefice = set(PIECES_PAR_FINANCEUR["agefice"]["apres_formation"])
    fafcea = set(PIECES_PAR_FINANCEUR["fafcea"]["apres_formation"])
    assert agefice != fafcea
    assert TypePiece.ATTESTATION_ASSIDUITE in fafcea


def test_la_liste_est_signalee_comme_non_officielle(dossier):
    """Elle est etablie sur les procedures connues, pas extraite d'un
    document officiel : elle doit etre recoupee avant le premier depot."""
    assert controler(dossier).liste_non_officielle is True


def test_un_financeur_sans_liste_ne_bloque_pas(dossier):
    dossier.financeur = "fifpl"
    dossier.save()
    controle = controler(dossier)
    assert controle.attendues == []
    assert controle.complet is True

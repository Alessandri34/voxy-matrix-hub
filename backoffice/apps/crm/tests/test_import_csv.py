"""Import CSV.

Critere de sortie de la phase 1 : « import CSV de tes leads existants sans
doublon ». Les cas testes sont ceux d'un vrai fichier client, pas d'un CSV
d'ecole : encodage Windows, point-virgule, en-tetes approximatifs, lignes
vides, doublons internes au fichier.
"""

import pytest

from apps.crm.models import Lead, SourceLead
from apps.crm.services.import_csv import (
    associer_colonnes,
    decoder,
    deviner_separateur,
    importer,
)

pytestmark = pytest.mark.django_db

EXCEL_FR = (
    "Nom;Prénom;Société;Téléphone;Email;Intérêt\n"
    "Martin;Sophie;Le Comptoir;06 12 34 56 78;sophie@le-comptoir-34.fr;Visibilité\n"
    "Benali;Karim;BTP Bénali;04 67 11 22 33;karim@btp-benali.fr;Site web\n"
)


# --------------------------------------------------------------------------
# Lecture du fichier
# --------------------------------------------------------------------------


def test_un_export_excel_francais_est_lu():
    """`cp1252`, pas UTF-8 : lu en UTF-8, « Bénédicte » leve une exception
    ou devient illisible."""
    texte, encodage = decoder(EXCEL_FR.encode("cp1252"))
    assert encodage == "cp1252"
    assert "Prénom" in texte
    assert "Bénali" in texte


def test_un_fichier_utf8_avec_bom_est_lu_sans_bom():
    """Le BOM d'Excel collerait « ﻿ » au premier en-tete, qui ne serait
    plus reconnu."""
    texte, encodage = decoder(EXCEL_FR.encode("utf-8-sig"))
    assert encodage == "utf-8-sig"
    assert texte.startswith("Nom;")


@pytest.mark.parametrize(
    "entete,attendu",
    [
        ("Nom;Prénom;Email", ";"),
        ("Nom,Prénom,Email", ","),
        ("Nom\tPrénom\tEmail", "\t"),
        ("Nom|Prénom|Email", "|"),
        # Une seule colonne : on retombe sur le point-virgule, le plus
        # probable pour un export francais.
        ("Email", ";"),
    ],
)
def test_separateur_devine(entete, attendu):
    assert deviner_separateur(entete + "\nvaleur") == attendu


def test_le_separateur_est_devine_sur_l_entete_pas_sur_les_donnees():
    """Toute adresse postale contient une virgule : la deviner sur les
    donnees se tromperait sur un fichier a points-virgules."""
    texte = "Nom;Adresse;Email\nMartin;12, rue de la Loge, Montpellier;a@b.fr"
    assert deviner_separateur(texte) == ";"


@pytest.mark.parametrize(
    "entete,champ",
    [
        ("Email", "email_declare"),
        ("E-mail", "email_declare"),
        ("Courriel", "email_declare"),
        ("Téléphone", "telephone_declare"),
        ("Tel", "telephone_declare"),
        ("Tel portable", "telephone_declare"),
        ("MOBILE", "telephone_declare"),
        ("Société", "entreprise_declaree"),
        ("Raison sociale", "entreprise_declaree"),
        ("Enseigne", "entreprise_declaree"),
        ("Nom", "nom_declare"),
        ("Nom complet", "nom_declare"),
        ("SIRET", "siren"),
        ("Formation souhaitée", "formation_demandee"),
        ("Commentaire", "message"),
    ],
)
def test_entetes_approximatifs_reconnus(entete, champ):
    """Une correspondance rigide obligerait a retravailler le fichier a la
    main, ce que personne ne fait."""
    associations, _ = associer_colonnes([entete])
    assert associations.get(entete) == champ


def test_le_nom_d_entreprise_gagne_sur_le_nom():
    """« Nom société » ne doit pas alimenter le nom du contact."""
    associations, _ = associer_colonnes(["Nom société", "Nom"])
    assert associations["Nom société"] == "entreprise_declaree"
    assert associations["Nom"] == "nom_declare"


def test_une_seconde_colonne_du_meme_champ_est_ignoree_pas_ecrasante():
    associations, ignorees = associer_colonnes(["Email", "Email 2"])
    assert associations == {"Email": "email_declare"}
    assert "Email 2" in ignorees


# --------------------------------------------------------------------------
# L'import lui-meme
# --------------------------------------------------------------------------


def test_apercu_n_ecrit_rien_mais_dit_tout():
    """En apercu, tout le travail est fait puis annule : le rapport dit ce
    qui se passerait, pas une estimation."""
    rapport = importer(EXCEL_FR.encode("cp1252"))
    assert rapport.applique is False
    assert rapport.lignes_lues == 2
    assert rapport.crees == 2
    assert Lead.objects.count() == 0


def test_appliquer_ecrit_les_leads():
    rapport = importer(EXCEL_FR.encode("cp1252"), appliquer=True)
    assert rapport.crees == 2
    assert Lead.objects.count() == 2
    sophie = Lead.objects.get(email_normalise="sophie@le-comptoir-34.fr")
    assert sophie.telephone_normalise == "+33612345678"
    assert sophie.entreprise_declaree == "Le Comptoir"
    assert sophie.source == SourceLead.IMPORT_CSV


def test_le_meme_fichier_importe_deux_fois_ne_duplique_rien():
    """C'est le critere : « import CSV sans doublon »."""
    importer(EXCEL_FR.encode("cp1252"), appliquer=True)
    rapport = importer(EXCEL_FR.encode("cp1252"), appliquer=True)
    assert rapport.crees == 0
    assert rapport.fusionnes == 2
    assert Lead.objects.count() == 2


def test_un_doublon_interne_au_fichier_est_reconnu():
    """Un tableur tenu a la main contient presque toujours la meme personne
    deux fois, ecrite differemment."""
    fichier = (
        "Nom;Société;Téléphone;Email\n"
        "Martin;Le Comptoir;06 12 34 56 78;sophie@le-comptoir-34.fr\n"
        "S. Martin;Le Comptoir;+33 6 12 34 56 78;\n"
    )
    rapport = importer(fichier.encode("utf-8"), appliquer=True)
    assert rapport.crees == 1
    assert rapport.fusionnes == 1
    assert Lead.objects.count() == 1


def test_une_ligne_sans_moyen_de_contact_est_rejetee_avec_son_motif():
    """Un lead qu'on ne peut ni appeler ni dedoublonner n'encombrerait le
    CRM que pour gonfler un compteur."""
    fichier = (
        "Nom;Société;Téléphone;Email\n"
        "Martin;Le Comptoir;06 12 34 56 78;a@b.fr\n"
        "Durand;;pas un numero;\n"
        ";;;\n"
    )
    rapport = importer(fichier.encode("utf-8"), appliquer=True)
    assert rapport.crees == 1
    assert rapport.rejetes == 2
    assert rapport.lignes_lues == 3
    assert any("aucun moyen de contact" in motif for _, motif in rapport.motifs_de_rejet)
    # Le numero de ligne du fichier est donne : sans lui, « 2 rejets » est
    # inexploitable sur un fichier de 400 lignes.
    assert rapport.motifs_de_rejet[0][0] == 3


def test_un_couple_nom_plus_entreprise_suffit_sans_email_ni_telephone():
    """Il reste dedoublonnable et rattachable : c'est assez pour entrer."""
    fichier = "Nom;Société\nMartin Sophie;Le Comptoir\n"
    rapport = importer(fichier.encode("utf-8"), appliquer=True)
    assert rapport.crees == 1
    assert rapport.rejetes == 0


def test_le_siren_du_fichier_est_conserve_pour_la_resolution():
    """`siren` n'est pas un champ de Lead : il passe par le payload, ou la
    resolution SIREN le relira."""
    fichier = "Nom;SIREN;Email\nMartin;552 032 534;a@b.fr\n"
    importer(fichier.encode("utf-8"), appliquer=True)
    lead = Lead.objects.get()
    assert lead.payload_origine["siren"] == "552032534"
    assert lead.payload_origine["ligne_csv"] == 2


def test_un_fichier_sans_colonne_reconnue_est_refuse_clairement():
    """Mieux vaut un refus explicite qu'un import qui « reussit » en creant
    400 lignes vides."""
    rapport = importer(b"Col1;Col2\na;b\n", appliquer=True)
    assert rapport.crees == 0
    assert rapport.motifs_de_rejet
    assert "aucune colonne reconnue" in rapport.motifs_de_rejet[0][1]
    assert Lead.objects.count() == 0


def test_un_fichier_vide_ne_casse_pas():
    rapport = importer(b"", appliquer=True)
    assert rapport.lignes_lues == 0
    assert Lead.objects.count() == 0


def test_la_source_choisie_determine_la_base_legale():
    """Un formulaire vaut consentement, un tableur non : ecrire
    « consentement » partout rendrait la mention fausse."""
    from apps.crm.dedoublonnage import rattacher_contact
    from apps.crm.models import Entreprise

    importer(EXCEL_FR.encode("cp1252"), source=SourceLead.IMPORT_CSV, appliquer=True)
    entreprise = Entreprise.objects.create(denomination="Le Comptoir")
    contact = rattacher_contact(Lead.objects.first(), entreprise)
    assert contact.base_legale == "interet_legitime"


def test_le_rapport_est_lisible_sans_relire_le_fichier():
    rapport = importer(EXCEL_FR.encode("cp1252"))
    texte = rapport.resume()
    assert "APERCU" in texte
    assert "cp1252" in texte
    assert "colonnes reconnues" in texte
    assert "email_declare" in texte

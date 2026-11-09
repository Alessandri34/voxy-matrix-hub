"""L'opposition est consultee avant tout envoi et tout appel. Un contact qui
a demande a ne plus etre contacte et qui l'est quand meme est un manquement
concret, pas une imperfection de confort."""

import pytest
from django.db import IntegrityError, transaction

from apps.crm.models import CanalOpposition, Contact, Entreprise, Opposition

pytestmark = pytest.mark.django_db


@pytest.fixture
def entreprise():
    return Entreprise.objects.create(denomination="Le Comptoir", siren="552032534")


def test_opposition_normalise_ce_qu_on_lui_donne():
    """L'appelant ne doit pas avoir a savoir comment la table est ecrite,
    sinon la verification sera oubliee quelque part."""
    Opposition.objects.create(
        email_normalise="  Sophie@Exemple.FR ", canal=CanalOpposition.DESABONNEMENT
    )
    assert Opposition.est_oppose(email="sophie@exemple.fr") is True
    assert Opposition.est_oppose(email="SOPHIE@EXEMPLE.FR") is True


def test_opposition_par_telephone_quelle_que_soit_l_ecriture():
    Opposition.objects.create(telephone_normalise="06 12 34 56 78", canal=CanalOpposition.APPEL)
    assert Opposition.est_oppose(telephone="+33612345678") is True
    assert Opposition.est_oppose(telephone="0612345678") is True
    assert Opposition.est_oppose(telephone="0698765432") is False


def test_opposition_sur_un_siren_porte_sur_toute_l_entreprise():
    Opposition.objects.create(siren="552 032 534", canal=CanalOpposition.DEMANDE_DIRECTE)
    assert Opposition.est_oppose(siren="55203253400041") is True


def test_une_opposition_vide_est_refusee():
    """Une ligne qui ne porte sur rien bloquerait tout ou rien, selon la
    requete : la contrainte l'interdit en base."""
    with pytest.raises(IntegrityError), transaction.atomic():
        Opposition.objects.create(canal=CanalOpposition.DESABONNEMENT)


def test_rien_a_verifier_ne_vaut_pas_oppose():
    """Appelee sans argument exploitable, la verification doit repondre non,
    pas oui par precaution : sinon plus aucun envoi ne partirait."""
    Opposition.objects.create(email_normalise="a@b.fr", canal=CanalOpposition.DESABONNEMENT)
    assert Opposition.est_oppose() is False
    assert Opposition.est_oppose(email="", telephone="", siren="") is False
    assert Opposition.est_oppose(email="illisible") is False


def test_l_opposition_se_propage_aux_contacts_deja_en_base(entreprise):
    """Le champ `Contact.oppose` duplique la table par choix : une requete
    d'envoi peut oublier une jointure, pas une colonne. Encore faut-il que la
    colonne suive."""
    contact = Contact.objects.create(
        entreprise=entreprise, nom="Martin", prenom="Sophie", email="sophie@exemple.fr"
    )
    assert contact.oppose is False

    Opposition.objects.create(
        email_normalise="sophie@exemple.fr", canal=CanalOpposition.DESABONNEMENT
    )
    contact.refresh_from_db()
    assert contact.oppose is True


def test_l_opposition_par_siren_touche_tous_les_contacts(entreprise):
    a = Contact.objects.create(entreprise=entreprise, nom="Martin", email="a@comptoir.fr")
    b = Contact.objects.create(entreprise=entreprise, nom="Durand", email="b@comptoir.fr")
    autre = Entreprise.objects.create(denomination="Garage", siren="356000000")
    c = Contact.objects.create(entreprise=autre, nom="Benali", email="c@garage.fr")

    Opposition.objects.create(siren="552032534", canal=CanalOpposition.DEMANDE_DIRECTE)
    for contact in (a, b, c):
        contact.refresh_from_db()
    assert a.oppose is True
    assert b.oppose is True
    assert c.oppose is False


def test_une_opposition_survit_a_la_suppression_du_contact(entreprise):
    """C'est la raison d'etre d'une table separee : sans elle, supprimer la
    fiche effacerait l'opposition, et la personne serait recontactee au
    prochain import."""
    contact = Contact.objects.create(entreprise=entreprise, nom="Martin", email="sophie@exemple.fr")
    Opposition.objects.create(
        email_normalise="sophie@exemple.fr", canal=CanalOpposition.DESABONNEMENT
    )
    contact.delete()
    assert Opposition.est_oppose(email="sophie@exemple.fr") is True


def test_opposition_avant_toute_fiche():
    """Quelqu'un peut s'opposer sans etre en base : l'opposition doit pouvoir
    etre inscrite tout de suite, sinon elle est perdue."""
    Opposition.objects.create(
        email_normalise="inconnu@exemple.fr", canal=CanalOpposition.DEMANDE_DIRECTE
    )
    assert Opposition.est_oppose(email="inconnu@exemple.fr") is True

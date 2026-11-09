"""Le moteur de relance.

Les trois garde-fous que ces tests verrouillent :
l'opposition est verifiee avant CHAQUE envoi · toute relance s'arrete des que
la personne repond · rien ne part hors des jours et heures ouvrables.
"""

from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.crm.models import (
    CanalOpposition,
    Contact,
    Entreprise,
    Lead,
    Opposition,
    SourceLead,
)
from apps.sequences.models import (
    Canal,
    CibleSequence,
    Envoi,
    EtapeSequence,
    EtatEnvoi,
    EtatInscription,
    Inscription,
    MotifArret,
    Sequence,
)
from apps.sequences.moteur import (
    arreter,
    creneau,
    expedier,
    inscrire,
    preparer_prochain_envoi,
    rendre,
    traiter_echeances,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def sequence():
    s = Sequence.objects.create(
        nom="Visibilite locale — sourcing",
        cible=CibleSequence.SOURCING,
        active=True,
        plafond_quotidien=40,
    )
    EtapeSequence.objects.create(
        sequence=s,
        ordre=1,
        delai_jours=0,
        canal=Canal.EMAIL,
        objet="{entreprise} : une question sur votre visibilite",
        corps="Bonjour {prenom},\n\nJe vois que {entreprise} est a {ville}.",
    )
    EtapeSequence.objects.create(
        sequence=s,
        ordre=2,
        delai_jours=4,
        canal=Canal.EMAIL,
        objet="Relance — {entreprise}",
        corps="Bonjour {prenom}, je reviens vers vous.",
    )
    EtapeSequence.objects.create(
        sequence=s,
        ordre=3,
        delai_jours=6,
        canal=Canal.APPEL,
        objet="",
        corps="Appeler {prenom} chez {entreprise}.",
    )
    return s


@pytest.fixture
def entreprise():
    return Entreprise.objects.create(
        denomination="Le Comptoir", siren="552032534", commune="Montpellier"
    )


@pytest.fixture
def contact(entreprise):
    return Contact.objects.create(
        entreprise=entreprise,
        prenom="Sophie",
        nom="Martin",
        email="sophie@le-comptoir-34.fr",
        telephone="0612345678",
    )


# --------------------------------------------------------------------------
# Gabarits
# --------------------------------------------------------------------------


def test_les_variables_sont_remplacees(sequence, contact):
    inscription = inscrire(sequence, contact=contact)
    texte = rendre("Bonjour {prenom} {nom}, chez {entreprise} a {ville}.", inscription)
    assert texte == "Bonjour Sophie Martin, chez Le Comptoir a Montpellier."


def test_une_variable_inconnue_reste_telle_quelle(sequence, contact):
    """Un gabarit qui contient une faute de frappe doit produire un message
    imparfait, pas arreter la sequence en silence."""
    inscription = inscrire(sequence, contact=contact)
    assert rendre("Tarif : {prix}", inscription) == "Tarif : {prix}"


def test_un_gabarit_mal_forme_ne_fait_pas_echouer(sequence, contact):
    inscription = inscrire(sequence, contact=contact)
    assert rendre("50 % de { remise", inscription) == "50 % de { remise"


def test_le_nom_d_un_lead_sans_contact_est_decoupe(sequence):
    lead = Lead.objects.create(
        source=SourceLead.IMPORT_CSV,
        nom_declare="Karim Benali",
        email_declare="k@btp34.fr",
        entreprise_declaree="BTP Benali",
    )
    inscription = inscrire(sequence, lead=lead)
    assert rendre("{prenom}|{nom}|{entreprise}", inscription) == "Karim|Benali|BTP Benali"


# --------------------------------------------------------------------------
# Fenetre d'envoi
# --------------------------------------------------------------------------


def test_avant_l_ouverture_on_attend(sequence):
    tot = timezone.localtime(timezone.now()).replace(year=2026, month=11, day=10, hour=6, minute=30)
    assert creneau(tot, sequence).hour == sequence.heure_min


def test_apres_la_fermeture_on_passe_au_lendemain(sequence):
    tard = timezone.localtime(timezone.now()).replace(
        year=2026, month=11, day=10, hour=22, minute=0
    )
    resultat = creneau(tard, sequence)
    assert resultat.date().day == 11 or resultat.date().day == 12
    assert resultat.hour == sequence.heure_min


def test_le_week_end_est_saute(sequence):
    samedi = timezone.localtime(timezone.now()).replace(
        year=2026, month=11, day=14, hour=10, minute=0
    )
    assert creneau(samedi, sequence).date().weekday() == 0  # lundi


def test_un_ferie_est_saute(sequence):
    """11 novembre 2026 : Armistice."""
    ferie = timezone.localtime(timezone.now()).replace(
        year=2026, month=11, day=11, hour=10, minute=0
    )
    assert creneau(ferie, sequence).date().day == 12


def test_sans_jours_ouvres_le_samedi_passe(sequence):
    sequence.jours_ouvres_seulement = False
    sequence.save()
    samedi = timezone.localtime(timezone.now()).replace(
        year=2026, month=11, day=14, hour=10, minute=0
    )
    assert creneau(samedi, sequence).date().day == 14


# --------------------------------------------------------------------------
# Les raisons de s'arreter
# --------------------------------------------------------------------------


def test_une_personne_opposee_n_entre_meme_pas(sequence, contact):
    Opposition.objects.create(email_normalise=contact.email, canal=CanalOpposition.DESABONNEMENT)
    inscription = inscrire(sequence, contact=contact)
    assert inscription.etat == EtatInscription.ARRETEE
    assert inscription.motif_arret == MotifArret.OPPOSITION
    assert inscription.prochaine_echeance is None


def test_une_opposition_survenue_en_cours_de_sequence_arrete_la_relance(sequence, contact):
    """Le cas le plus frequent : c'est le PREMIER message qui declenche
    l'opposition. Verifier a l'inscription seulement enverrait la relance."""
    inscription = inscrire(sequence, contact=contact)
    premier = preparer_prochain_envoi(inscription)
    assert premier is not None

    Opposition.objects.create(email_normalise=contact.email, canal=CanalOpposition.DESABONNEMENT)
    inscription.refresh_from_db()
    assert preparer_prochain_envoi(inscription) is None
    inscription.refresh_from_db()
    assert inscription.etat == EtatInscription.ARRETEE
    assert inscription.motif_arret == MotifArret.OPPOSITION


def test_une_opposition_par_siren_arrete_aussi(sequence, contact, entreprise):
    Opposition.objects.create(siren=entreprise.siren, canal=CanalOpposition.DEMANDE_DIRECTE)
    inscription = inscrire(sequence, contact=contact)
    assert inscription.motif_arret == MotifArret.OPPOSITION


def test_une_reponse_arrete_la_relance(sequence, contact):
    inscription = inscrire(sequence, contact=contact)
    preparer_prochain_envoi(inscription)
    inscription.date_reponse = timezone.now()
    inscription.save()

    assert preparer_prochain_envoi(inscription) is None
    inscription.refresh_from_db()
    assert inscription.motif_arret == MotifArret.REPONSE


def test_un_lead_devenu_affaire_sort_de_la_prospection(sequence, entreprise):
    from apps.pipeline.services import promouvoir_lead

    lead = Lead.objects.create(
        source=SourceLead.SOURCING,
        nom_declare="Sophie Martin",
        email_declare="s@comptoir.fr",
        entreprise=entreprise,
    )
    inscription = inscrire(sequence, lead=lead)
    promouvoir_lead(lead, intitule="Visibilite locale")

    assert preparer_prochain_envoi(inscription) is None
    inscription.refresh_from_db()
    assert inscription.motif_arret == MotifArret.OPPORTUNITE


def test_un_doublon_ne_recoit_rien(sequence, entreprise):
    original = Lead.objects.create(
        source=SourceLead.SOURCING, nom_declare="Sophie", email_declare="a@b.fr"
    )
    doublon = Lead.objects.create(
        source=SourceLead.IMPORT_CSV,
        nom_declare="Sophie",
        email_declare="c@d.fr",
        doublon_de=original,
    )
    inscription = inscrire(sequence, lead=doublon)
    assert inscription.motif_arret == MotifArret.DOUBLON


def test_sans_moyen_de_contact_on_n_inscrit_pas(sequence):
    lead = Lead.objects.create(source=SourceLead.IMPORT_CSV, nom_declare="Anonyme")
    inscription = inscrire(sequence, lead=lead)
    assert inscription.motif_arret == MotifArret.SANS_CONTACT


def test_arreter_annule_les_envois_prevus(sequence, contact):
    inscription = inscrire(sequence, contact=contact)
    preparer_prochain_envoi(inscription)
    Envoi.objects.filter(inscription=inscription).update(etat=EtatEnvoi.PREVU)
    arreter(inscription, MotifArret.MANUEL, "test")
    assert Envoi.objects.filter(inscription=inscription, etat=EtatEnvoi.ANNULE).count() == 1


# --------------------------------------------------------------------------
# Avancement
# --------------------------------------------------------------------------


def test_la_sequence_avance_etape_par_etape(sequence, contact):
    inscription = inscrire(sequence, contact=contact)

    premier = preparer_prochain_envoi(inscription)
    assert premier.etape.ordre == 1
    assert "Le Comptoir" in premier.objet
    assert "Sophie" in premier.corps
    inscription.refresh_from_db()
    assert inscription.etape_courante == 1
    assert inscription.prochaine_echeance is not None

    second = preparer_prochain_envoi(inscription)
    assert second.etape.ordre == 2

    troisieme = preparer_prochain_envoi(inscription)
    assert troisieme.etape.ordre == 3
    assert troisieme.canal == Canal.APPEL
    # Une etape d'appel vise le telephone, pas l'email.
    assert troisieme.destinataire == contact.telephone_normalise

    inscription.refresh_from_db()
    assert inscription.prochaine_echeance is None
    assert preparer_prochain_envoi(inscription) is None
    inscription.refresh_from_db()
    assert inscription.etat == EtatInscription.TERMINEE


def test_un_passage_rejoue_ne_prepare_pas_deux_fois(sequence, contact):
    """Idempotence : une tache Celery rejouee ne doit pas doubler les envois."""
    inscription = inscrire(sequence, contact=contact)
    preparer_prochain_envoi(inscription)
    etape_apres = inscription.etape_courante

    # On remet l'inscription sur l'etape precedente, comme le ferait un
    # rejeu partiel, et on repasse.
    Inscription.objects.filter(pk=inscription.pk).update(etape_courante=etape_apres - 1)
    inscription.refresh_from_db()
    assert preparer_prochain_envoi(inscription) is None
    assert Envoi.objects.filter(inscription=inscription).count() == 1


def test_on_ne_s_inscrit_pas_deux_fois_a_la_meme_sequence(sequence, contact):
    inscrire(sequence, contact=contact)
    with pytest.raises(ValidationError, match="deja inscrit"):
        inscrire(sequence, contact=contact)


def test_une_sequence_sans_etape_active_refuse_les_inscriptions(contact):
    vide = Sequence.objects.create(nom="Vide", cible=CibleSequence.SOURCING, active=True)
    with pytest.raises(ValidationError, match="aucune etape active"):
        inscrire(vide, contact=contact)


def test_le_plafond_quotidien_reporte_sans_perdre(sequence, entreprise):
    sequence.plafond_quotidien = 2
    sequence.save()
    for i in range(5):
        contact = Contact.objects.create(
            entreprise=entreprise, nom=f"Prospect{i}", email=f"p{i}@exemple.fr"
        )
        inscrire(sequence, contact=contact)

    # Les echeances sont ramenees dans le passe : ce test porte sur le
    # plafond, pas sur la fenetre d'envoi. Sans cela il echouerait selon
    # l'heure a laquelle la suite tourne — le moteur reporte correctement
    # au lendemain tout ce qui arrive apres 18 h.
    Inscription.objects.filter(sequence=sequence).update(
        prochaine_echeance=timezone.now() - timedelta(minutes=1)
    )

    resultat = traiter_echeances()
    assert resultat["prepares"] == 2
    assert resultat["reportes_plafond"] == 3
    # Les trois reportes restent actifs : rien n'est perdu.
    assert Inscription.objects.filter(etat=EtatInscription.ACTIVE).count() == 5


def test_les_echeances_futures_ne_sont_pas_traitees(sequence, contact):
    inscription = inscrire(sequence, contact=contact)
    Inscription.objects.filter(pk=inscription.pk).update(
        prochaine_echeance=timezone.now() + timedelta(days=3)
    )
    assert traiter_echeances()["prepares"] == 0


def test_une_sequence_inactive_n_envoie_rien(sequence, contact):
    inscription = inscrire(sequence, contact=contact)
    Inscription.objects.filter(pk=inscription.pk).update(
        prochaine_echeance=timezone.now() - timedelta(minutes=1)
    )
    sequence.active = False
    sequence.save()
    assert traiter_echeances()["prepares"] == 0


def test_rien_ne_part_hors_de_la_fenetre_d_envoi(sequence, contact):
    """Non-regression : une inscription creee a 21 h a son echeance reportee
    au lendemain matin, et `traiter_echeances` ne la voit pas ce soir-la."""
    inscription = inscrire(sequence, contact=contact)
    assert inscription.prochaine_echeance is not None
    local = timezone.localtime(inscription.prochaine_echeance)
    assert sequence.heure_min <= local.hour < sequence.heure_max
    from apps.sequences.calendrier import est_ouvre

    assert est_ouvre(local.date())


# --------------------------------------------------------------------------
# Expedition
# --------------------------------------------------------------------------


def test_sans_autorisation_rien_ne_part(sequence, contact, settings):
    settings.SEQUENCES_ENVOI_REEL = False
    inscription = inscrire(sequence, contact=contact)
    envoi = preparer_prochain_envoi(inscription)
    assert expedier(envoi) is False
    envoi.refresh_from_db()
    assert envoi.etat == EtatEnvoi.A_ENVOYER
    assert "desactivee" in envoi.erreur


def test_avec_autorisation_le_message_part(sequence, contact, settings, mailoutbox):
    settings.SEQUENCES_ENVOI_REEL = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    inscription = inscrire(sequence, contact=contact)
    envoi = preparer_prochain_envoi(inscription)

    assert expedier(envoi) is True
    envoi.refresh_from_db()
    assert envoi.etat == EtatEnvoi.ENVOYE
    assert envoi.envoye_le is not None
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [contact.email_normalise]


def test_une_opposition_entre_preparation_et_expedition_annule(
    sequence, contact, settings, mailoutbox
):
    """Derniere verification, juste avant de partir : l'opposition a pu etre
    inscrite pendant que le message attendait dans la file."""
    settings.SEQUENCES_ENVOI_REEL = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    inscription = inscrire(sequence, contact=contact)
    envoi = preparer_prochain_envoi(inscription)

    Opposition.objects.create(email_normalise=contact.email, canal=CanalOpposition.DESABONNEMENT)
    assert expedier(envoi) is False
    envoi.refresh_from_db()
    assert envoi.etat == EtatEnvoi.ANNULE
    assert len(mailoutbox) == 0
    inscription.refresh_from_db()
    assert inscription.motif_arret == MotifArret.OPPOSITION


def test_le_contenu_envoye_est_conserve(sequence, contact):
    """Sans cela, on ne pourrait ni prouver ce qui a ete envoye, ni repondre
    a quelqu'un qui demande ce qu'on lui a ecrit."""
    inscription = inscrire(sequence, contact=contact)
    envoi = preparer_prochain_envoi(inscription)
    assert envoi.corps.startswith("Bonjour Sophie,")
    assert envoi.destinataire == contact.email_normalise

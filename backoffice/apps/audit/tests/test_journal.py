"""Regle 10 du cadrage : toute modification est inscrite au journal.

Le journal sert le jour ou un chiffre devient faux et ou il faut savoir qui
l'a change. Il sert aussi a repondre a une demande d'acces ou d'effacement
sans relire l'historique Git. Les deux usages veulent les valeurs, pas
seulement les noms de champs.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.audit.contexte import agir_en_tant_que
from apps.audit.models import Action, EntreeJournal
from apps.crm.models import Entreprise, Lead, SourceLead

pytestmark = pytest.mark.django_db


@pytest.fixture
def pierre():
    return get_user_model().objects.create_user(
        username="pierre", password="motdepasse-long-12", role="admin"
    )


def test_creation_inscrite():
    Entreprise.objects.create(denomination="Le Comptoir", siren="552032534")
    entree = EntreeJournal.objects.get(action=Action.CREATION)
    assert "Le Comptoir" in entree.libelle_objet
    assert entree.changements == {}


def test_modification_dit_de_quoi_vers_quoi():
    """« Le champ a change » sans dire de quoi vers quoi ne sert a rien le
    jour ou un montant devient faux."""
    entreprise = Entreprise.objects.create(denomination="Le Comptoir")
    EntreeJournal.objects.all().delete()

    entreprise.denomination = "Le Comptoir Montpelliérain"
    entreprise.save()

    entree = EntreeJournal.objects.get()
    assert entree.action == Action.MODIFICATION
    assert entree.changements["denomination"] == [
        "Le Comptoir",
        "Le Comptoir Montpelliérain",
    ]


def test_enregistrement_sans_changement_n_ecrit_rien():
    """Sinon le journal se remplit de lignes vides et devient illisible.

    Non-regression : `modifie_le` est un champ `auto_now`, il change a chaque
    enregistrement. Tant qu'il etait compare, toute sauvegarde produisait une
    ligne — y compris celles qui ne changeaient rien.
    """
    entreprise = Entreprise.objects.create(denomination="Le Comptoir")
    EntreeJournal.objects.all().delete()
    entreprise.save()
    assert EntreeJournal.objects.count() == 0

    # Et une vraie modification passe toujours.
    entreprise.commune = "Montpellier"
    entreprise.save()
    assert EntreeJournal.objects.count() == 1


def test_suppression_conserve_ce_qui_disparait():
    entreprise = Entreprise.objects.create(denomination="Le Comptoir", siren="552032534")
    EntreeJournal.objects.all().delete()
    entreprise.delete()

    entree = EntreeJournal.objects.get()
    assert entree.action == Action.SUPPRESSION
    # Le libelle survit a l'objet : c'est tout l'interet.
    assert "Le Comptoir" in entree.libelle_objet
    assert entree.changements["__supprime__"][0]["siren"] == "552032534"


def test_l_acteur_est_retenu(pierre):
    with agir_en_tant_que(acteur=pierre, origine="application", ip="192.0.2.10"):
        entreprise = Entreprise.objects.create(denomination="Le Comptoir")
    # La fixture `pierre` a elle aussi produit une creation au journal :
    # on vise celle de l'entreprise.
    entree = EntreeJournal.objects.get(
        action=Action.CREATION, id_objet=str(entreprise.pk), libelle_objet__contains="Comptoir"
    )
    assert entree.acteur == pierre
    assert entree.adresse_ip == "192.0.2.10"


def test_une_action_automatique_dit_son_origine():
    """Un lead arrive par webhook n'a pas d'acteur humain. Le journal doit
    dire « webhook-meta », pas laisser une ligne sans auteur ni explication."""
    with agir_en_tant_que(origine="webhook-meta"):
        Lead.objects.create(source=SourceLead.META_LEAD_ADS, nom_declare="Sophie")
    entree = EntreeJournal.objects.get(action=Action.CREATION)
    assert entree.acteur is None
    assert entree.origine == "webhook-meta"


def test_le_mot_de_passe_n_entre_jamais_au_journal(pierre):
    """Un journal qui recopie les empreintes de mots de passe devient une
    cible plus interessante que la table des utilisateurs."""
    pierre.set_password("un-autre-mot-de-passe-12")
    pierre.save()
    for entree in EntreeJournal.objects.all():
        assert "password" not in entree.changements
        assert "pbkdf2" not in str(entree.changements)


def test_un_payload_volumineux_n_est_pas_recopie():
    """On note que le payload a change, pas son contenu : il est deja
    conserve sur le lead, et le journal n'est pas une seconde base."""
    lead = Lead.objects.create(source=SourceLead.META_LEAD_ADS, nom_declare="Sophie")
    EntreeJournal.objects.all().delete()
    lead.payload_origine = {f"champ_{i}": "x" * 200 for i in range(20)}
    lead.save()

    entree = EntreeJournal.objects.get()
    avant, apres = entree.changements["payload_origine"]
    assert apres == "<dict de 20 element(s)>"
    assert len(str(entree.changements)) < 200


def test_une_entree_ne_se_modifie_pas():
    """Un journal reecrivable ne vaut rien en cas de contestation."""
    Entreprise.objects.create(denomination="Le Comptoir")
    entree = EntreeJournal.objects.first()
    entree.libelle_objet = "autre chose"
    with pytest.raises(ValueError, match="ne se modifie pas"):
        entree.save()


def test_seuls_les_modeles_declares_sont_surveilles():
    """Surveiller tout par defaut ferait du journal une copie de la base.
    `Activite` et `PassageEtape` sont deja des traces : les journaliser
    doublerait chaque ligne."""
    from django.conf import settings

    assert "crm.Activite" not in settings.AUDIT_MODELES
    assert "pipeline.PassageEtape" not in settings.AUDIT_MODELES
    assert "crm.Lead" in settings.AUDIT_MODELES


# --------------------------------------------------------------------------
# Le journal ne doit jamais faire echouer l'action qu'il trace
# --------------------------------------------------------------------------


def test_une_suppression_en_cascade_ne_casse_pas_sur_un_libelle_illisible():
    """Non-regression, trouvee en vidant les donnees de demonstration.

    `_ecrire` appelait `str(instance)` sans filet. Or `Inscription.__str__`
    lisait son contact, et pendant une suppression en cascade le contact
    pouvait deja avoir disparu : l'exception remontait depuis le signal et
    **faisait echouer la suppression entiere**. Le journal d'audit cassait
    l'operation dont il n'est que le temoin.

    Aucun des 501 tests ne le voyait, parce qu'aucun ne supprimait un contact
    dont une inscription partait dans la meme cascade. C'est exactement la
    classe de defaut que la vraie pile trouve et que les tests ne voient pas.
    """
    from apps.crm.models import Contact, Entreprise
    from apps.sequences.models import Canal, EtapeSequence, Inscription, Sequence
    from apps.sequences.moteur import inscrire

    entreprise = Entreprise.objects.create(denomination="Garage Bellefeuille", siren="552032534")
    contact = Contact.objects.create(
        entreprise=entreprise, nom="Bellefeuille", prenom="Karim", email="karim@exemple.fr"
    )
    sequence = Sequence.objects.create(nom="Relance a froid", active=True)
    EtapeSequence.objects.create(
        sequence=sequence, ordre=1, delai_jours=0, canal=Canal.EMAIL, objet="Bonjour", corps="…"
    )
    inscrire(sequence, contact=contact)

    # La cascade emporte le contact ET son inscription.
    entreprise.delete()

    assert not Inscription.objects.exists()
    assert not Contact.objects.exists()


def test_un_libelle_incalculable_laisse_quand_meme_une_trace_identifiante():
    """Le repli n'est pas un libelle vide : le modele et la cle primaire
    suffisent a retrouver l'objet dans une sauvegarde."""
    from apps.audit.signaux import _libelle
    from apps.crm.models import Entreprise

    entreprise = Entreprise.objects.create(denomination="Essai", siren="552032534")

    class Casse(Entreprise):
        class Meta:
            proxy = True

        def __str__(self):
            raise RuntimeError("relation disparue")

    casse = Casse.objects.get(pk=entreprise.pk)
    libelle = _libelle(casse)
    assert "Casse" in libelle or "crm." in libelle
    assert str(entreprise.pk) in libelle


def test_une_inscription_orpheline_reste_affichable():
    """Son `__str__` est lu par l'administration et par le journal : il doit
    tenir meme quand la relation n'est plus la."""
    from apps.crm.models import Contact, Entreprise
    from apps.sequences.models import Inscription, Sequence

    entreprise = Entreprise.objects.create(denomination="Essai", siren="552032534")
    contact = Contact.objects.create(entreprise=entreprise, nom="Durand", prenom="Lea")
    sequence = Sequence.objects.create(nom="Relance", active=True)
    inscription = Inscription.objects.create(sequence=sequence, contact=contact)

    # On reproduit l'etat transitoire d'une cascade : l'objet Python porte
    # encore un identifiant, la ligne visee n'est plus en base. On ne peut pas
    # y arriver en supprimant le contact, puisque la cascade emporterait aussi
    # l'inscription — c'est bien pour cela que le defaut etait invisible.
    orpheline = Inscription.objects.get(pk=inscription.pk)
    orpheline.contact_id = 999999
    orpheline._state.fields_cache.pop("contact", None)
    assert "supprime" in str(orpheline)
    assert "Relance" in str(orpheline)

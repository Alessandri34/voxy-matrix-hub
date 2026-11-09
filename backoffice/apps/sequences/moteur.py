"""Le moteur : qui recoit quoi, quand, et sous quelles conditions.

Il prepare les envois. Il ne les expedie que si `SEQUENCES_ENVOI_REEL` est
vrai dans les reglages — faux par defaut. Un moteur branche par erreur sur
une vraie base envoie des centaines de messages avant que quiconque s'en
apercoive, et un envoi ne se reprend pas.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.crm.models import Activite, Opposition, TypeActivite
from apps.sequences.calendrier import est_ouvre, prochain_jour_ouvre
from apps.sequences.models import (
    Canal,
    Envoi,
    EtatEnvoi,
    EtatInscription,
    Inscription,
    MotifArret,
    Sequence,
)

logger = logging.getLogger(__name__)


class _Variables(dict):
    """Une variable inconnue reste telle quelle.

    Un gabarit qui contient `{prix}` alors que la variable n'existe pas doit
    produire un message imparfait, pas une exception : l'alternative est une
    sequence qui s'arrete en silence sur une faute de frappe.
    """

    def __missing__(self, cle):
        return "{" + cle + "}"


def rendre(gabarit: str, inscription: Inscription) -> str:
    """Remplace les variables du gabarit par les donnees du prospect."""
    contact = inscription.contact
    lead = inscription.lead
    entreprise = None
    if contact is not None:
        entreprise = contact.entreprise
    elif lead is not None:
        entreprise = lead.entreprise

    prenom = (contact.prenom if contact else "") or ""
    nom = (contact.nom if contact else "") or ""
    if not (prenom or nom) and lead is not None:
        morceaux = (lead.nom_declare or "").strip().split(" ", 1)
        prenom = morceaux[0] if morceaux else ""
        nom = morceaux[1] if len(morceaux) > 1 else ""

    variables = _Variables(
        prenom=prenom,
        nom=nom,
        entreprise=(
            entreprise.denomination if entreprise else (lead.entreprise_declaree if lead else "")
        )
        or "",
        ville=(entreprise.commune if entreprise else "") or "",
        formation=(lead.formation_demandee if lead else "") or "",
    )
    try:
        return gabarit.format_map(variables)
    except (ValueError, IndexError):
        # Accolade seule ou mal fermee dans le gabarit : on sert le texte
        # brut plutot que de bloquer toute la sequence.
        logger.warning("Gabarit mal forme dans la sequence %s", inscription.sequence_id)
        return gabarit


def creneau(depuis: datetime, sequence: Sequence) -> datetime:
    """Le prochain moment ou cette sequence a le droit d'envoyer."""
    local = timezone.localtime(depuis)

    if local.hour < sequence.heure_min:
        local = local.replace(hour=sequence.heure_min, minute=0, second=0, microsecond=0)
    elif local.hour >= sequence.heure_max:
        local = (local + timedelta(days=1)).replace(
            hour=sequence.heure_min, minute=0, second=0, microsecond=0
        )

    if sequence.jours_ouvres_seulement and not est_ouvre(local.date()):
        jour = prochain_jour_ouvre(local.date())
        local = local.replace(
            year=jour.year,
            month=jour.month,
            day=jour.day,
            hour=sequence.heure_min,
            minute=0,
            second=0,
            microsecond=0,
        )
    return local


@dataclass(frozen=True)
class Arret:
    motif: str
    detail: str


def verifier_arret(inscription: Inscription) -> Arret | None:
    """Toutes les raisons de ne pas continuer. Verifie AVANT chaque envoi.

    L'opposition n'est pas verifiee qu'a l'inscription : une personne peut
    s'opposer entre deux etapes — c'est meme le cas le plus frequent, puisque
    c'est le premier message qui declenche l'opposition.
    """
    sequence = inscription.sequence

    if Opposition.est_oppose(
        email=inscription.email,
        telephone=inscription.telephone,
        siren=inscription.siren,
    ):
        return Arret(MotifArret.OPPOSITION, "inscrit au registre des oppositions")

    contact = inscription.contact
    if contact is not None and contact.oppose:
        return Arret(MotifArret.OPPOSITION, "contact marque oppose")

    lead = inscription.lead
    if lead is not None and lead.doublon_de_id is not None:
        return Arret(MotifArret.DOUBLON, f"doublon du lead #{lead.doublon_de_id}")

    if sequence.arret_si_reponse and inscription.date_reponse is not None:
        return Arret(MotifArret.REPONSE, "la personne a repondu")

    if sequence.arret_si_opportunite and lead is not None:
        opportunite = getattr(lead, "opportunite", None)
        if opportunite is not None:
            return Arret(MotifArret.OPPORTUNITE, f"affaire #{opportunite.pk} ouverte")

    if not (inscription.email or inscription.telephone):
        return Arret(MotifArret.SANS_CONTACT, "ni email ni telephone exploitable")

    return None


@transaction.atomic
def inscrire(sequence: Sequence, *, lead=None, contact=None, auteur=None) -> Inscription:
    """Inscrit un prospect. Refuse en silence ce qui ne doit pas y entrer."""
    if lead is None and contact is None:
        raise ValidationError("une inscription vise un lead ou un contact")

    inscription = Inscription(sequence=sequence, lead=lead, contact=contact, inscrit_par=auteur)
    arret = verifier_arret(inscription)
    if arret is not None:
        inscription.etat = EtatInscription.ARRETEE
        inscription.motif_arret = arret.motif
        inscription.detail_arret = arret.detail
        inscription.terminee_le = timezone.now()
    else:
        premiere = sequence.etapes.filter(active=True).order_by("ordre").first()
        if premiere is None:
            raise ValidationError(f"la sequence « {sequence.nom} » n'a aucune etape active")
        depart = timezone.now() + timedelta(days=premiere.delai_jours)
        inscription.prochaine_echeance = creneau(depart, sequence)

    try:
        inscription.save()
    except IntegrityError as erreur:
        raise ValidationError(
            "ce prospect est deja inscrit a cette sequence — l'inscrire deux "
            "fois enverrait tout en double"
        ) from erreur
    return inscription


def _tracer(inscription: Inscription, contenu: str) -> Activite:
    cible = inscription.lead or inscription.contact
    return Activite.objects.create(
        type=TypeActivite.SYSTEME,
        type_objet=ContentType.objects.get_for_model(cible.__class__),
        id_objet=str(cible.pk),
        contenu=contenu,
    )


@transaction.atomic
def arreter(inscription: Inscription, motif: str, detail: str = "") -> Inscription:
    inscription.etat = EtatInscription.ARRETEE
    inscription.motif_arret = motif
    inscription.detail_arret = detail[:250]
    inscription.prochaine_echeance = None
    inscription.terminee_le = timezone.now()
    inscription.save()
    Envoi.objects.filter(inscription=inscription, etat=EtatEnvoi.PREVU).update(
        etat=EtatEnvoi.ANNULE
    )
    _tracer(inscription, f"Sequence « {inscription.sequence.nom} » arretee : {detail or motif}.")
    return inscription


@transaction.atomic
def preparer_prochain_envoi(inscription: Inscription, maintenant=None) -> Envoi | None:
    """Prepare le message de l'etape suivante. Ne l'expedie pas.

    Renvoie None quand l'inscription s'arrete ou se termine. Idempotent : la
    contrainte `un_envoi_par_etape` empeche qu'une tache rejouee prepare deux
    fois le meme message.
    """
    maintenant = maintenant or timezone.now()
    if inscription.etat != EtatInscription.ACTIVE:
        return None

    arret = verifier_arret(inscription)
    if arret is not None:
        arreter(inscription, arret.motif, arret.detail)
        return None

    sequence = inscription.sequence
    etape = (
        sequence.etapes.filter(active=True, ordre__gt=inscription.etape_courante)
        .order_by("ordre")
        .first()
    )
    if etape is None:
        inscription.etat = EtatInscription.TERMINEE
        inscription.prochaine_echeance = None
        inscription.terminee_le = maintenant
        inscription.save()
        _tracer(
            inscription,
            f"Sequence « {sequence.nom} » terminee : toutes les etapes sont passees.",
        )
        return None

    destinataire = inscription.email if etape.canal == Canal.EMAIL else inscription.telephone
    if etape.canal == Canal.EMAIL and not destinataire:
        # Pas d'email : on saute l'etape plutot que d'arreter la sequence,
        # l'etape suivante peut etre un appel.
        inscription.etape_courante = etape.ordre
        inscription.prochaine_echeance = creneau(maintenant, sequence)
        inscription.save()
        return None

    envoi = Envoi(
        inscription=inscription,
        etape=etape,
        canal=etape.canal,
        destinataire=destinataire,
        objet=rendre(etape.objet, inscription),
        corps=rendre(etape.corps, inscription),
        etat=EtatEnvoi.A_ENVOYER,
        prevu_le=maintenant,
    )
    try:
        envoi.save()
    except IntegrityError:
        # Deja prepare par un passage precedent : rien a faire.
        return None

    inscription.etape_courante = etape.ordre
    suivante = sequence.etapes.filter(active=True, ordre__gt=etape.ordre).order_by("ordre").first()
    if suivante is None:
        inscription.prochaine_echeance = None
    else:
        inscription.prochaine_echeance = creneau(
            maintenant + timedelta(days=suivante.delai_jours), sequence
        )
    inscription.save()
    return envoi


def expedier(envoi: Envoi) -> bool:
    """Expedie reellement. Refuse tant que les reglages ne l'autorisent pas.

    Le garde-fou est volontairement dans le code et non seulement dans la
    configuration du serveur : un `.env` recopie d'une preproduction vers la
    production ne doit pas suffire a declencher une campagne.
    """
    if not getattr(settings, "SEQUENCES_ENVOI_REEL", False):
        envoi.erreur = (
            "expedition desactivee (SEQUENCES_ENVOI_REEL = False). Le message "
            "est prepare et consultable, rien n'est parti."
        )
        envoi.save(update_fields=["erreur"])
        return False

    if envoi.canal != Canal.EMAIL:
        return False

    # Derniere verification, juste avant de partir : l'opposition a pu etre
    # inscrite entre la preparation et l'expedition.
    arret = verifier_arret(envoi.inscription)
    if arret is not None:
        envoi.etat = EtatEnvoi.ANNULE
        envoi.erreur = f"annule avant expedition : {arret.detail}"
        envoi.save(update_fields=["etat", "erreur"])
        arreter(envoi.inscription, arret.motif, arret.detail)
        return False

    from django.core.mail import send_mail

    try:
        send_mail(
            subject=envoi.objet,
            message=envoi.corps,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[envoi.destinataire],
            fail_silently=False,
        )
    except Exception as erreur:  # noqa: BLE001 — toute panne SMTP compte pareil
        envoi.etat = EtatEnvoi.ECHOUE
        envoi.erreur = str(erreur)[:2000]
        envoi.save(update_fields=["etat", "erreur"])
        return False

    envoi.etat = EtatEnvoi.ENVOYE
    envoi.envoye_le = timezone.now()
    envoi.erreur = ""
    envoi.save(update_fields=["etat", "envoye_le", "erreur"])
    return True


def traiter_echeances(maintenant=None, limite: int = 500) -> dict:
    """Fait avancer toutes les inscriptions dont l'echeance est passee.

    Le plafond quotidien est applique PAR SEQUENCE : une campagne de masse ne
    doit pas noyer les relances d'une autre, ni degrader d'un coup la
    reputation du domaine qui porte aussi les convocations de formation.
    """
    maintenant = maintenant or timezone.now()
    dues = (
        Inscription.objects.filter(
            etat=EtatInscription.ACTIVE,
            prochaine_echeance__lte=maintenant,
            sequence__active=True,
        )
        .select_related("sequence", "lead", "contact")
        .order_by("prochaine_echeance")[:limite]
    )

    debut_jour = timezone.localtime(maintenant).replace(hour=0, minute=0, second=0, microsecond=0)
    deja_aujourdhui: dict[int, int] = {}
    prepares, arretes, plafonnes = 0, 0, 0

    for inscription in dues:
        sequence = inscription.sequence
        if sequence.pk not in deja_aujourdhui:
            deja_aujourdhui[sequence.pk] = Envoi.objects.filter(
                inscription__sequence=sequence, prevu_le__gte=debut_jour
            ).count()
        if deja_aujourdhui[sequence.pk] >= sequence.plafond_quotidien:
            plafonnes += 1
            continue

        avant = inscription.etat
        envoi = preparer_prochain_envoi(inscription, maintenant)
        if envoi is not None:
            prepares += 1
            deja_aujourdhui[sequence.pk] += 1
        elif avant == EtatInscription.ACTIVE:
            inscription.refresh_from_db()
            if inscription.etat == EtatInscription.ARRETEE:
                arretes += 1

    if plafonnes:
        logger.info("%s inscription(s) reportee(s) : plafond quotidien atteint.", plafonnes)
    return {
        "prepares": prepares,
        "arretes": arretes,
        "reportes_plafond": plafonnes,
        "examines": len(dues),
    }

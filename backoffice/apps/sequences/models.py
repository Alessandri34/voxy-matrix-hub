"""Sequences de relance : le moteur de nurturing.

**Ce que ce module fait et ne fait pas.** Il calcule *qui* doit recevoir
*quoi* et *quand*, et prepare les envois. Il ne les expedie pas tout seul :
l'expedition reelle demande `SEQUENCES_ENVOI_REEL = True` dans les reglages,
faux par defaut. Un moteur de relance branche par erreur sur une vraie base
de prospects envoie des centaines de messages avant que quiconque s'en
apercoive, et un envoi ne se reprend pas.

**Trois garde-fous qui ne sont pas negociables.**

1. **L'opposition est verifiee avant CHAQUE envoi**, pas a l'inscription.
   Une personne peut s'opposer entre deux etapes d'une sequence — c'est meme
   le cas le plus frequent, puisque c'est le premier message qui declenche
   l'opposition. Verifier a l'inscription seulement enverrait la relance.
2. **Toute relance s'arrete des que la personne repond.** Relancer quelqu'un
   qui a deja repondu est le defaut le plus visible d'un outil de
   prospection, et le plus couteux en image.
3. **Jours ouvres et plafond quotidien.** Un envoi groupe le dimanche matin
   signale une automatisation a tout le monde, et un pic de volume degrade
   la reputation du domaine expediteur — celui-la meme qui porte les
   convocations de formation.

**Base legale.** Prospection B2B vers une adresse professionnelle, au titre
de l'interet legitime (RGPD art. 6-1-f), sur une offre en rapport avec
l'activite du destinataire, avec un moyen de refus dans chaque message.
C'est la seule base que ce module admet pour une sequence de sourcing ; une
sequence vers un prospect entrant repose, elle, sur son consentement.
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone


class CibleSequence(models.TextChoices):
    """A qui la sequence s'adresse. Determine la base legale admise."""

    LEAD_ENTRANT = "lead_entrant", "Lead entrant (a rappele ou rempli un formulaire)"
    SOURCING = "sourcing", "Prospect sourcé (jamais entre en contact)"
    APRES_DEVIS = "apres_devis", "Apres l'envoi d'une proposition"
    APRES_FORMATION = "apres_formation", "Apres la formation (suivi a 90 jours)"


class Canal(models.TextChoices):
    EMAIL = "email", "Email"
    APPEL = "appel", "Appel a passer"
    COURRIER = "courrier", "Courrier"
    TACHE = "tache", "Tache interne (sans contact)"


class Sequence(models.Model):
    """Un enchainement d'etapes datees."""

    nom = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    cible = models.CharField(max_length=20, choices=CibleSequence.choices)
    active = models.BooleanField(default=False)

    arret_si_reponse = models.BooleanField(
        default=True,
        help_text="Relancer quelqu'un qui a deja repondu est le defaut le plus "
        "visible d'un outil de prospection. Ne desactiver qu'en connaissance "
        "de cause.",
    )
    arret_si_opportunite = models.BooleanField(
        default=True,
        help_text="Un prospect devenu affaire sort de la prospection : il est "
        "suivi par un commercial.",
    )
    jours_ouvres_seulement = models.BooleanField(default=True)
    heure_min = models.PositiveSmallIntegerField(
        default=9, help_text="Heure locale avant laquelle rien ne part."
    )
    heure_max = models.PositiveSmallIntegerField(
        default=18, help_text="Heure locale apres laquelle rien ne part."
    )
    plafond_quotidien = models.PositiveSmallIntegerField(
        default=40,
        help_text="Envois maximum par jour pour cette sequence. Un pic de "
        "volume degrade la reputation du domaine expediteur — celui qui porte "
        "aussi les convocations de formation.",
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "sequence"
        verbose_name_plural = "sequences"
        ordering = ("nom",)

    def __str__(self) -> str:
        return f"{self.nom} ({self.get_cible_display()})"

    def clean(self):
        super().clean()
        if self.heure_min >= self.heure_max:
            raise ValidationError(
                {"heure_max": "La fenetre d'envoi doit s'ouvrir avant de se fermer."}
            )
        if self.active and not self.etapes.filter(active=True).exists():
            raise ValidationError(
                "Une sequence sans etape active n'enverra jamais rien : "
                "ajouter au moins une etape avant de l'activer."
            )


class EtapeSequence(models.Model):
    """Une etape : un message, un delai depuis la precedente."""

    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name="etapes")
    ordre = models.PositiveSmallIntegerField()
    delai_jours = models.PositiveSmallIntegerField(
        help_text="Jours depuis l'etape precedente (ou depuis l'inscription "
        "pour la premiere). 0 = immediat."
    )
    canal = models.CharField(max_length=12, choices=Canal.choices, default=Canal.EMAIL)
    objet = models.CharField(max_length=200, blank=True)
    corps = models.TextField(
        help_text="Gabarit. Variables disponibles : {prenom}, {nom}, "
        "{entreprise}, {ville}, {formation}. Une variable inconnue reste "
        "telle quelle plutot que de faire echouer l'envoi."
    )
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "etape de sequence"
        verbose_name_plural = "etapes de sequence"
        ordering = ("sequence", "ordre")
        constraints = [
            models.UniqueConstraint(fields=["sequence", "ordre"], name="un_ordre_par_sequence")
        ]

    def __str__(self) -> str:
        return f"{self.sequence.nom} · etape {self.ordre} ({self.get_canal_display()})"

    def clean(self):
        super().clean()
        if self.canal == Canal.EMAIL and not self.objet.strip():
            raise ValidationError({"objet": "Un email sans objet part en indesirable."})


class EtatInscription(models.TextChoices):
    ACTIVE = "active", "En cours"
    TERMINEE = "terminee", "Terminee (toutes les etapes passees)"
    ARRETEE = "arretee", "Arretee"
    SUSPENDUE = "suspendue", "Suspendue"


class MotifArret(models.TextChoices):
    REPONSE = "reponse", "La personne a repondu"
    OPPOSITION = "opposition", "Opposition a la prospection"
    OPPORTUNITE = "opportunite", "Devenue une affaire"
    DOUBLON = "doublon", "Lead marque doublon"
    MANUEL = "manuel", "Arretee a la main"
    SANS_CONTACT = "sans_contact", "Aucun moyen de contact exploitable"


class Inscription(models.Model):
    """Un prospect dans une sequence."""

    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name="inscriptions")
    lead = models.ForeignKey(
        "crm.Lead",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="inscriptions",
    )
    contact = models.ForeignKey(
        "crm.Contact",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="inscriptions",
    )

    etat = models.CharField(
        max_length=12,
        choices=EtatInscription.choices,
        default=EtatInscription.ACTIVE,
        db_index=True,
    )
    etape_courante = models.PositiveSmallIntegerField(
        default=0, help_text="0 = aucune etape encore envoyee."
    )
    prochaine_echeance = models.DateTimeField(null=True, blank=True, db_index=True)
    motif_arret = models.CharField(max_length=15, choices=MotifArret.choices, blank=True)
    detail_arret = models.CharField(max_length=250, blank=True)

    date_reponse = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Renseignee quand la personne repond. ⚠️ Le moteur ne lit "
        "aucune boite mail : une reponse par email ne se detecte pas toute "
        "seule. Elle est inscrite soit a la main, soit parce qu'un humain a "
        "journalise un appel ou un echange sur ce lead.",
    )

    inscrit_le = models.DateTimeField(default=timezone.now)
    terminee_le = models.DateTimeField(null=True, blank=True)
    inscrit_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "inscription a une sequence"
        verbose_name_plural = "inscriptions aux sequences"
        ordering = ("prochaine_echeance",)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(lead__isnull=False) | models.Q(contact__isnull=False),
                name="inscription_vise_quelqu_un",
            ),
            # Un meme lead deux fois dans la meme sequence enverrait tout en
            # double, sans qu'aucune erreur ne le signale.
            models.UniqueConstraint(
                fields=["sequence", "lead"],
                condition=models.Q(lead__isnull=False),
                name="un_lead_par_sequence",
            ),
            models.UniqueConstraint(
                fields=["sequence", "contact"],
                condition=models.Q(contact__isnull=False),
                name="un_contact_par_sequence",
            ),
        ]
        indexes = [models.Index(fields=["etat", "prochaine_echeance"])]

    def __str__(self) -> str:
        # Les relations sont lues par identifiant, pas par dereferencement :
        # pendant une suppression en cascade, la ligne liee peut deja avoir
        # disparu, et un `__str__` qui lance une exception fait echouer la
        # suppression elle-meme (le journal d'audit l'appelle).
        qui = "inconnu"
        if self.contact_id:
            qui = str(self.contact) if self._relation_vivante("contact") else "contact supprime"
        elif self.lead_id:
            qui = str(self.lead) if self._relation_vivante("lead") else "lead supprime"
        sequence = self.sequence.nom if self._relation_vivante("sequence") else "sequence supprimee"
        return f"{qui} · {sequence} · etape {self.etape_courante}"

    def _relation_vivante(self, nom: str) -> bool:
        try:
            return getattr(self, nom) is not None
        except ObjectDoesNotExist:
            return False

    @property
    def email(self) -> str:
        if self.contact_id and self.contact.email_normalise:
            return self.contact.email_normalise
        if self.lead_id:
            return self.lead.email_normalise
        return ""

    @property
    def telephone(self) -> str:
        if self.contact_id and self.contact.telephone_normalise:
            return self.contact.telephone_normalise
        if self.lead_id:
            return self.lead.telephone_normalise
        return ""

    @property
    def siren(self) -> str:
        entreprise = None
        if self.contact_id:
            entreprise = self.contact.entreprise
        elif self.lead_id:
            entreprise = self.lead.entreprise
        return entreprise.siren if entreprise else ""


class EtatEnvoi(models.TextChoices):
    PREVU = "prevu", "Prevu"
    A_ENVOYER = "a_envoyer", "Pret a partir"
    ENVOYE = "envoye", "Envoye"
    ECHOUE = "echoue", "Echoue"
    ANNULE = "annule", "Annule"


class Envoi(models.Model):
    """Un message, prepare puis expedie.

    La ligne est ecrite AVANT l'expedition et porte le texte reellement
    produit. Sans cela, on ne pourrait ni prouver ce qui a ete envoye, ni
    repondre a quelqu'un qui demande ce qu'on lui a ecrit.
    """

    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, related_name="envois")
    etape = models.ForeignKey(EtapeSequence, on_delete=models.PROTECT, related_name="envois")

    canal = models.CharField(max_length=12, choices=Canal.choices)
    destinataire = models.CharField(max_length=254, blank=True)
    objet = models.CharField(max_length=200, blank=True)
    corps = models.TextField(blank=True)

    etat = models.CharField(
        max_length=10, choices=EtatEnvoi.choices, default=EtatEnvoi.PREVU, db_index=True
    )
    prevu_le = models.DateTimeField(db_index=True)
    envoye_le = models.DateTimeField(null=True, blank=True)
    erreur = models.TextField(blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "envoi"
        verbose_name_plural = "envois"
        ordering = ("-prevu_le",)
        constraints = [
            # Idempotence : une tache qui tourne deux fois ne doit pas
            # preparer deux fois le meme message.
            models.UniqueConstraint(fields=["inscription", "etape"], name="un_envoi_par_etape")
        ]
        indexes = [models.Index(fields=["etat", "prevu_le"])]

    def __str__(self) -> str:
        ou = self.destinataire or "—"
        return f"{self.get_canal_display()} · {ou} · {self.get_etat_display()}"

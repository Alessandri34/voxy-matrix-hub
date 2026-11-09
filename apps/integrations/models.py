"""Journal des receptions de webhooks.

Pourquoi conserver le corps brut : la charge utile d'un webhook Meta ne
contient que des identifiants ; les reponses du prospect demandent un second
appel au Graph API, qui peut echouer — jeton expire, permission revoquee,
limite de debit. Sans le corps brut conserve, ce lead serait perdu
definitivement, car Meta cesse de reemettre des qu'il a recu un 200.

Le corps est donc enregistre AVANT tout traitement, et le 200 n'est renvoye
qu'une fois l'enregistrement durable. Le traitement, lui, est rejouable.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class EtatReception(models.TextChoices):
    RECUE = "recue", "Recue, pas encore traitee"
    TRAITEE = "traitee", "Traitee"
    IGNOREE = "ignoree", "Ignoree (doublon ou hors sujet)"
    ECHOUEE = "echouee", "Echouee — rejouable"


class ReceptionWebhook(models.Model):
    source = models.CharField(max_length=30, default="meta", db_index=True)
    recue_le = models.DateTimeField(default=timezone.now, db_index=True)

    signature_valide = models.BooleanField(
        help_text="Faux signifie que la requete n'a pas ete traitee. La ligne "
        "est conservee quand meme : une serie de signatures invalides est le "
        "signe d'un secret desynchronise ou d'une tentative d'injection."
    )
    corps = models.TextField(help_text="Corps brut, tel que recu, non reinterprete.")
    entetes = models.JSONField(default=dict, blank=True)

    cle_idempotence = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
        help_text="Identifiant de l'evenement chez la source. Meta reemet "
        "jusqu'a recevoir un 200 : sans cette cle, un reessai creerait un "
        "second lead.",
    )
    etat = models.CharField(
        max_length=10, choices=EtatReception.choices, default=EtatReception.RECUE, db_index=True
    )
    traitee_le = models.DateTimeField(null=True, blank=True)
    erreur = models.TextField(blank=True)
    tentatives = models.PositiveSmallIntegerField(default=0)

    lead = models.ForeignKey(
        "crm.Lead",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="receptions",
    )

    class Meta:
        verbose_name = "reception de webhook"
        verbose_name_plural = "receptions de webhooks"
        ordering = ("-recue_le",)
        indexes = [
            models.Index(fields=["source", "etat", "-recue_le"]),
        ]

    def __str__(self) -> str:
        return f"{self.source} · {self.recue_le:%d/%m/%Y %H:%M:%S} · {self.get_etat_display()}"

    @property
    def delai_de_traitement_secondes(self) -> float | None:
        """Mesure le critere de sortie : « le lead apparait en moins d'1 minute ».

        Compte a partir de NOTRE reception, pas de l'envoi du formulaire :
        la documentation Meta annonce elle-meme un delai pouvant aller
        jusqu'a quelques minutes avant l'emission du ping. Pretendre mesurer
        le trajet complet serait mesurer le reseau de Meta.
        """
        if self.traitee_le is None:
            return None
        return round((self.traitee_le - self.recue_le).total_seconds(), 2)

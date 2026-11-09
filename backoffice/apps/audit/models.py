"""Journal d'audit.

Regle 10 du cadrage : toute modification est inscrite au journal. Le journal
sert deux usages differents, et c'est pourquoi il conserve les valeurs et pas
seulement les noms de champs :

- retrouver qui a change quoi, quand un chiffre devient faux ;
- repondre a une demande d'acces ou d'effacement sans relire l'historique Git.

Une entree n'est jamais modifiee ni supprimee par l'application.
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Action(models.TextChoices):
    CREATION = "creation", "Creation"
    MODIFICATION = "modification", "Modification"
    SUPPRESSION = "suppression", "Suppression"
    EXPORT = "export", "Export"
    CONNEXION = "connexion", "Connexion"


class EntreeJournal(models.Model):
    """Une ligne du journal. Jamais modifiee apres ecriture."""

    date = models.DateTimeField(auto_now_add=True, db_index=True)
    acteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="entrees_journal",
        help_text="Nul pour une action automatique (webhook, tache planifiee).",
    )
    origine = models.CharField(
        max_length=40,
        default="application",
        help_text="application, webhook-meta, import-csv, tache, commande.",
    )
    action = models.CharField(max_length=20, choices=Action.choices)

    type_objet = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    id_objet = models.CharField(max_length=40, blank=True, db_index=True)
    objet = GenericForeignKey("type_objet", "id_objet")
    libelle_objet = models.CharField(
        max_length=200,
        blank=True,
        help_text="Representation textuelle au moment de l'action : "
        "elle survit a la suppression de l'objet.",
    )

    changements = models.JSONField(
        default=dict,
        blank=True,
        help_text="{champ: [avant, apres]}. Vide pour une creation.",
    )
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "entree du journal"
        verbose_name_plural = "journal d'audit"
        ordering = ("-date",)
        indexes = [
            models.Index(fields=["type_objet", "id_objet"]),
            models.Index(fields=["-date", "acteur"]),
        ]

    def __str__(self) -> str:
        qui = self.acteur.get_username() if self.acteur else self.origine
        return f"{self.date:%d/%m/%Y %H:%M} · {qui} · {self.action} · {self.libelle_objet}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError(
                "Une entree du journal d'audit ne se modifie pas. "
                "Si une correction est necessaire, ecrire une nouvelle entree."
            )
        return super().save(*args, **kwargs)

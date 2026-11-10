"""Tracabilite de la donnee publicitaire.

**Le probleme que ce module resout.** Une regie publicitaire sait dire le
cout par clic et le cout par lead. Elle ne sait pas dire le **cout par
client**, parce qu'elle ignore ce qui se passe apres le formulaire : la
qualification, le dossier de financement, l'accord du financeur,
l'encaissement. C'est pourtant le seul chiffre sur lequel decider
d'augmenter un budget.

Le back-office, lui, connait toute la chaine. Il suffit de lui donner la
depense en face.

**Chaine de tracabilite, bout a bout :**

    depense → impressions → clics → leads → opportunites → dossiers
            → accords financeur → formes → payes

Chaque maillon est deja en base sauf le premier. Le lien se fait par
`meta_campagne_id`, que le webhook Meta inscrit sur chaque lead.

**Deux sources de depense, et c'est volontaire :**

- **saisie manuelle**, mensuelle ou quotidienne. Marche tout de suite, sans
  App Review, sans jeton. C'est la source de depart ;
- **API Marketing de Meta**, quand `ads_read` sera accorde. La permission
  demande une verification d'entreprise et une revue ou il faut **montrer
  les donnees publicitaires affichees dans l'application** — ce module est
  precisement ce qu'il faudra montrer.

Une depense porte sa source : un chiffre saisi a la main et un chiffre
rapatrie de l'API ne se discutent pas de la meme facon.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Plateforme(models.TextChoices):
    META = "meta", "Meta (Facebook, Instagram)"
    GOOGLE = "google", "Google Ads"
    LINKEDIN = "linkedin", "LinkedIn Ads"
    TIKTOK = "tiktok", "TikTok Ads"
    AUTRE = "autre", "Autre"


class SourceChiffre(models.TextChoices):
    """D'ou vient un chiffre. Un montant saisi a la main et un montant
    rapatrie de l'API ne se discutent pas de la meme facon."""

    MANUELLE = "manuelle", "Saisie manuelle"
    API = "api", "Rapatriee de l'API de la regie"
    IMPORT = "import", "Importee d'un fichier"


class Campagne(models.Model):
    """Une campagne publicitaire, telle que la regie la nomme."""

    plateforme = models.CharField(
        max_length=12, choices=Plateforme.choices, default=Plateforme.META
    )
    identifiant_externe = models.CharField(
        max_length=64,
        help_text="L'identifiant chez la regie. C'est LUI qui relie la "
        "depense aux leads : le webhook Meta l'inscrit sur chaque lead sous "
        "`meta_campagne_id`. Une faute ici casse tout le rapprochement.",
    )
    nom = models.CharField(max_length=200)
    objectif = models.CharField(
        max_length=120, blank=True, help_text="Ce que la campagne cherche, en clair."
    )
    offre = models.CharField(
        max_length=120,
        blank=True,
        help_text="Code du programme pousse : OFFRE-3, SITE, IA... Permet de "
        "comparer le rendement d'une offre a l'autre.",
    )

    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "campagne"
        verbose_name_plural = "campagnes"
        ordering = ("-date_debut", "nom")
        constraints = [
            models.UniqueConstraint(
                fields=["plateforme", "identifiant_externe"],
                name="un_identifiant_par_plateforme",
            )
        ]
        indexes = [models.Index(fields=["plateforme", "active"])]

    def __str__(self) -> str:
        return f"{self.nom} ({self.get_plateforme_display()})"


class Depense(models.Model):
    """Ce qu'une campagne a coute sur une periode, et ce qu'elle a produit
    au niveau de la regie.

    La granularite est le MOIS par defaut : c'est la maille a laquelle une
    facture de regie se lit, et celle a laquelle une decision de budget se
    prend. Une maille quotidienne est possible en renseignant `jour`.
    """

    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, related_name="depenses")
    mois = models.DateField(
        help_text="Le 1er du mois concerne. Une depense quotidienne porte aussi `jour`."
    )
    jour = models.DateField(null=True, blank=True, help_text="Facultatif : maille quotidienne.")

    montant_centimes = models.PositiveIntegerField(
        help_text="En centimes, TTC ou HT selon ce que facture la regie — "
        "indiquer lequel dans la note. Jamais en flottant."
    )
    impressions = models.PositiveIntegerField(default=0)
    clics = models.PositiveIntegerField(default=0)

    source = models.CharField(
        max_length=10, choices=SourceChiffre.choices, default=SourceChiffre.MANUELLE
    )
    note = models.CharField(max_length=250, blank=True)
    releve_le = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "depense publicitaire"
        verbose_name_plural = "depenses publicitaires"
        ordering = ("-mois", "campagne")
        constraints = [
            # Deux contraintes et non une : en SQL, NULL n'est pas egal a
            # NULL, donc une contrainte sur (campagne, mois, jour) ne se
            # declenche PAS entre deux lignes mensuelles, ou `jour` est nul.
            # Les deux auraient ete acceptees, et toute la depense comptee
            # en double — avec elle, tous les couts par client.
            models.UniqueConstraint(
                fields=["campagne", "mois"],
                condition=models.Q(jour__isnull=True),
                name="une_depense_mensuelle_par_campagne",
            ),
            models.UniqueConstraint(
                fields=["campagne", "jour"],
                condition=models.Q(jour__isnull=False),
                name="une_depense_quotidienne_par_campagne",
            ),
            models.CheckConstraint(
                condition=models.Q(clics__lte=models.F("impressions")) | models.Q(impressions=0),
                name="moins_de_clics_que_d_impressions",
            ),
        ]
        indexes = [models.Index(fields=["campagne", "-mois"])]

    def __str__(self) -> str:
        return f"{self.campagne.nom} · {self.mois:%m/%Y} · {self.montant} €"

    def clean(self):
        super().clean()
        if self.mois and self.mois.day != 1:
            raise ValidationError(
                {
                    "mois": "Indiquer le 1er du mois : une periode mensuelle qui "
                    "commence le 15 rend tous les cumuls faux."
                }
            )
        if (
            self.jour
            and self.mois
            and (self.jour.year != self.mois.year or self.jour.month != self.mois.month)
        ):
            raise ValidationError({"jour": "Le jour doit tomber dans le mois indique."})

    @property
    def montant(self) -> Decimal:
        return (Decimal(self.montant_centimes) / 100).quantize(Decimal("0.01"))

    @property
    def cpm_centimes(self) -> int | None:
        """Cout pour mille impressions."""
        if not self.impressions:
            return None
        return round(self.montant_centimes * 1000 / self.impressions)

    @property
    def cpc_centimes(self) -> int | None:
        if not self.clics:
            return None
        return round(self.montant_centimes / self.clics)

    @property
    def ctr(self) -> Decimal | None:
        if not self.impressions:
            return None
        return (Decimal(self.clics) * 100 / self.impressions).quantize(Decimal("0.01"))


def premier_du_mois(jour: date) -> date:
    return jour.replace(day=1)

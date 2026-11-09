"""Les dossiers de financement.

**Pourquoi un bareme fige sur le dossier.** Les taux changent — ceux du
FAFCEA ont change le 1er septembre 2026. Un dossier depose sous un bareme
doit garder ses conditions, meme si le bareme evolue ensuite. Recalculer a
la lecture donnerait, six mois plus tard, un montant different de celui qui
a ete annonce au client et accepte par le financeur.

**Pourquoi les montants en centimes.** Un reste a charge annonce doit tomber
juste : 0,1 + 0,2 ne fait pas 0,3 en binaire.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.financement.bareme import Modalite, NatureFormation


class EtatDossier(models.TextChoices):
    BROUILLON = "brouillon", "Brouillon"
    A_DEPOSER = "a_deposer", "A deposer"
    DEPOSE = "depose", "Depose"
    ACCORDE = "accorde", "Accord obtenu"
    REFUSE = "refuse", "Refuse"
    SOLDE = "solde", "Solde (rembourse)"
    ABANDONNE = "abandonne", "Abandonne"


#: Fenetres de depot, en jours avant le debut de la formation.
#: (au plus tot, au plus tard). Un « au plus tard » negatif signifie que le
#: depot reste possible apres le debut.
FENETRES_DEPOT = {
    # AGEFICE : de 4 mois a 15 jours calendaires avant le demarrage,
    # obligatoirement via un Point d'Accueil — un dossier envoye au siege
    # n'est pas instruit.
    "agefice": (120, 15),
    # FAFCEA : 3 mois avant, jusqu'au jour du debut.
    "fafcea": (90, 0),
    # FIF PL : jusqu'a 10 jours APRES le debut — le plus souple.
    "fifpl": (120, -10),
}


class Dossier(models.Model):
    """Une demande de financement, de sa preparation a son remboursement."""

    opportunite = models.ForeignKey(
        "pipeline.Opportunite", on_delete=models.CASCADE, related_name="dossiers"
    )
    financeur = models.CharField(max_length=20, db_index=True)
    etat = models.CharField(
        max_length=12,
        choices=EtatDossier.choices,
        default=EtatDossier.BROUILLON,
        db_index=True,
    )

    # --- Ce qui est demande ----------------------------------------------
    date_debut_formation = models.DateField(
        help_text="C'est elle qui determine le bareme applicable, pas la "
        "date du devis : les financeurs raisonnent en « formations debutant "
        "a compter du... »."
    )
    date_fin_formation = models.DateField(null=True, blank=True)
    heures = models.PositiveIntegerField()
    modalite = models.CharField(max_length=25, choices=Modalite.CHOICES)
    nature = models.CharField(
        max_length=12, choices=NatureFormation.CHOICES, default=NatureFormation.TRANSVERSE
    )
    nb_stagiaires = models.PositiveSmallIntegerField(default=1)

    prix_ht_centimes = models.PositiveIntegerField()
    exonere_tva = models.BooleanField(
        default=False,
        help_text="Exoneration au titre de l'art. 261-4-4° a du CGI, sur "
        "attestation DREETS. Tant qu'elle n'est pas obtenue, la TVA "
        "s'applique — et aucun financeur ne la finance.",
    )

    # --- Ce que le financeur dit -----------------------------------------
    cfp_centimes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Contribution formation professionnelle versee, lue sur "
        "l'attestation URSSAF. Nulle = inconnue : le calcul retient alors le "
        "plafond BAS, par prudence.",
    )
    heures_deja_consommees = models.PositiveIntegerField(default=0)
    montant_deja_consomme_centimes = models.PositiveIntegerField(default=0)

    # --- Le calcul, fige ---------------------------------------------------
    bareme_en_vigueur_du = models.DateField(
        null=True,
        blank=True,
        help_text="Date d'effet du bareme applique. Fige au calcul : un "
        "dossier garde ses conditions meme si le bareme evolue ensuite.",
    )
    taux_horaire_centimes = models.PositiveIntegerField(default=0)
    prise_en_charge_centimes = models.PositiveIntegerField(default=0)
    reste_a_charge_centimes = models.PositiveIntegerField(default=0)
    detail_calcul = models.JSONField(
        default=dict,
        blank=True,
        help_text="Limites, blocages et avertissements au moment du calcul. "
        "C'est ce qui permet d'expliquer un montant six mois plus tard.",
    )

    # --- Suivi -------------------------------------------------------------
    numero_dossier = models.CharField(
        max_length=60, blank=True, help_text="Reference donnee par le financeur."
    )
    date_depot = models.DateField(null=True, blank=True)
    date_decision = models.DateField(null=True, blank=True)
    montant_accorde_centimes = models.PositiveIntegerField(null=True, blank=True)
    motif_refus = models.TextField(blank=True)
    point_accueil = models.CharField(
        max_length=200,
        blank=True,
        help_text="AGEFICE : le depot passe OBLIGATOIREMENT par un Point "
        "d'Accueil. Un dossier envoye au siege n'est pas instruit.",
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dossiers",
    )

    class Meta:
        verbose_name = "dossier de financement"
        verbose_name_plural = "dossiers de financement"
        ordering = ("-date_debut_formation",)
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(etat="refuse") | ~models.Q(motif_refus=""),
                name="refus_exige_un_motif",
            ),
            models.CheckConstraint(
                condition=models.Q(heures__gt=0), name="dossier_au_moins_une_heure"
            ),
        ]
        indexes = [models.Index(fields=["etat", "date_debut_formation"])]

    def __str__(self) -> str:
        return f"{self.financeur.upper()} · {self.heures} h · {self.date_debut_formation:%d/%m/%Y}"

    # --- Fenetre de depot --------------------------------------------------

    @property
    def depot_ouvre_le(self):
        tot, _ = FENETRES_DEPOT.get(self.financeur, (None, None))
        return self.date_debut_formation - timedelta(days=tot) if tot is not None else None

    @property
    def depot_ferme_le(self):
        _, tard = FENETRES_DEPOT.get(self.financeur, (None, None))
        return self.date_debut_formation - timedelta(days=tard) if tard is not None else None

    @property
    def jours_avant_cloture(self) -> int | None:
        """Negatif = la fenetre est passee."""
        if self.depot_ferme_le is None:
            return None
        return (self.depot_ferme_le - timezone.localdate()).days

    @property
    def depot_en_retard(self) -> bool:
        """Vrai quand la fenetre est fermee et que rien n'a ete depose."""
        if self.etat not in (EtatDossier.BROUILLON, EtatDossier.A_DEPOSER):
            return False
        restants = self.jours_avant_cloture
        return restants is not None and restants < 0

    @property
    def prise_en_charge(self) -> Decimal:
        return (Decimal(self.prise_en_charge_centimes) / 100).quantize(Decimal("0.01"))

    @property
    def reste_a_charge(self) -> Decimal:
        return (Decimal(self.reste_a_charge_centimes) / 100).quantize(Decimal("0.01"))

    @property
    def montant_accorde(self) -> Decimal | None:
        if self.montant_accorde_centimes is None:
            return None
        return (Decimal(self.montant_accorde_centimes) / 100).quantize(Decimal("0.01"))

    @property
    def ecart_accorde(self) -> Decimal | None:
        """Ce que le financeur a accorde en moins (ou en plus) que demande.

        C'est la seule mesure qui dise si nos simulations sont justes. Un
        ecart recurrent signale un bareme mal lu, pas un financeur capricieux.
        """
        if self.montant_accorde_centimes is None:
            return None
        ecart = self.montant_accorde_centimes - self.prise_en_charge_centimes
        return (Decimal(ecart) / 100).quantize(Decimal("0.01"))

    def clean(self):
        super().clean()
        if self.etat == EtatDossier.REFUSE and not self.motif_refus.strip():
            raise ValidationError(
                {
                    "motif_refus": "Un refus porte son motif : c'est lui qui dit "
                    "si le dossier etait mal monte ou le prospect ineligible."
                }
            )
        if (
            self.financeur == "agefice"
            and self.etat in (EtatDossier.DEPOSE, EtatDossier.ACCORDE)
            and not self.point_accueil.strip()
        ):
            raise ValidationError(
                {
                    "point_accueil": "Le depot AGEFICE passe obligatoirement par "
                    "un Point d'Accueil : un dossier envoye au siege n'est pas "
                    "instruit. Indiquer lequel."
                }
            )

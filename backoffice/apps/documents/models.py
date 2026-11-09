"""Les pieces d'un dossier, en un seul endroit.

**Le probleme reel.** Un dossier de financement se refuse pour une piece
manquante, et la piece manquante se decouvre au depot — quand la fenetre est
sur le point de se fermer. La liste des pieces exigees n'est pas la meme chez
l'AGEFICE et chez le FAFCEA, et personne ne la retient.

**Deux facons de deposer une piece**, et c'est volontaire :

- **le fichier**, stocke sur le serveur. Simple, sauvegarde avec la base,
  mais il occupe le disque du VPS ;
- **un lien externe** (Drive, Nextcloud, n'importe quoi). Rien n'est stocke
  ici, le disque ne grossit pas, et le fichier reste la ou l'equipe le gere
  deja. En contrepartie, la sauvegarde chiffree du back-office ne le couvre
  pas, et un lien peut casser.

L'un ou l'autre suffit pour qu'une piece compte comme fournie.
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TypePiece(models.TextChoices):
    """Les pieces qu'un dossier de financement demande."""

    DEVIS = "devis", "Devis signe"
    PROGRAMME = "programme", "Programme de formation"
    CONVENTION = "convention", "Convention de formation"
    ATTESTATION_URSSAF = "urssaf", "Attestation de contribution URSSAF"
    KBIS = "kbis", "Extrait Kbis ou D1"
    RIB = "rib", "RIB de l'entreprise"
    AUTODIAGNOSTIC = "autodiagnostic", "Autodiagnostic prealable"
    FEUILLE_EMARGEMENT = "emargement", "Feuille d'emargement"
    ATTESTATION_ASSIDUITE = "assiduite", "Attestation d'assiduite"
    ATTESTATION_FIN = "attestation_fin", "Attestation de fin de formation"
    FACTURE = "facture", "Facture acquittee"
    EVALUATION = "evaluation", "Evaluation des acquis"
    QUALIOPI = "qualiopi", "Certificat Qualiopi de l'organisme"
    AUTRE = "autre", "Autre piece"


#: Pieces exigees selon le financeur, et a quel moment.
#: ⚠️ Liste de travail, etablie sur les procedures connues au 09/11/2026 :
#: elle n'est PAS extraite d'un document officiel et doit etre recoupee avec
#: le Point d'Accueil AGEFICE et le FAFCEA avant le premier depot reel.
PIECES_PAR_FINANCEUR = {
    "agefice": {
        "avant_depot": [
            TypePiece.DEVIS,
            TypePiece.PROGRAMME,
            TypePiece.ATTESTATION_URSSAF,
            TypePiece.KBIS,
            TypePiece.RIB,
        ],
        "apres_formation": [
            TypePiece.FEUILLE_EMARGEMENT,
            TypePiece.ATTESTATION_FIN,
            TypePiece.FACTURE,
        ],
    },
    "fafcea": {
        "avant_depot": [
            TypePiece.DEVIS,
            TypePiece.PROGRAMME,
            TypePiece.ATTESTATION_URSSAF,
            TypePiece.KBIS,
            TypePiece.RIB,
        ],
        "apres_formation": [
            TypePiece.FEUILLE_EMARGEMENT,
            TypePiece.ATTESTATION_ASSIDUITE,
            TypePiece.FACTURE,
        ],
    },
}


class EtatPiece(models.TextChoices):
    ATTENDUE = "attendue", "Attendue"
    RECUE = "recue", "Recue, a verifier"
    VALIDEE = "validee", "Validee"
    REFUSEE = "refusee", "Refusee, a refaire"


def chemin_piece(instance, nom_fichier: str) -> str:
    """Range par dossier. Un dossier = un repertoire, comme un classeur."""
    return f"dossiers/{instance.dossier_id}/{nom_fichier}"


class Piece(models.Model):
    """Une piece, deposee comme fichier ou pointee par un lien."""

    dossier = models.ForeignKey(
        "financement.Dossier", on_delete=models.CASCADE, related_name="pieces"
    )
    type = models.CharField(max_length=20, choices=TypePiece.choices)
    libelle = models.CharField(max_length=200, blank=True, help_text="Pour une piece « Autre ».")

    fichier = models.FileField(upload_to=chemin_piece, blank=True)
    lien_externe = models.URLField(
        blank=True,
        max_length=500,
        help_text="Drive, Nextcloud, n'importe quel stockage. Rien n'est "
        "stocke ici et le disque du VPS ne grossit pas — mais la sauvegarde "
        "chiffree du back-office ne couvre pas ce fichier.",
    )

    etat = models.CharField(
        max_length=10, choices=EtatPiece.choices, default=EtatPiece.ATTENDUE, db_index=True
    )
    obligatoire = models.BooleanField(default=True)
    note = models.TextField(blank=True)

    recue_le = models.DateTimeField(null=True, blank=True)
    validee_le = models.DateTimeField(null=True, blank=True)
    validee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "piece du dossier"
        verbose_name_plural = "pieces des dossiers"
        ordering = ("dossier", "type")
        constraints = [
            models.UniqueConstraint(
                fields=["dossier", "type", "libelle"], name="une_piece_par_type"
            ),
            # Une piece « validee » sans fichier ni lien n'a rien valide.
            models.CheckConstraint(
                condition=(
                    ~models.Q(etat__in=["recue", "validee"])
                    | ~(models.Q(fichier="") & models.Q(lien_externe=""))
                ),
                name="piece_fournie_a_un_support",
            ),
        ]
        indexes = [models.Index(fields=["dossier", "etat"])]

    def __str__(self) -> str:
        return f"{self.get_type_display()} — {self.get_etat_display()}"

    def save(self, *args, **kwargs):
        if self.fournie and self.recue_le is None:
            self.recue_le = timezone.now()
        if self.etat == EtatPiece.VALIDEE and self.validee_le is None:
            self.validee_le = timezone.now()
        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.etat in (EtatPiece.RECUE, EtatPiece.VALIDEE) and not self.fournie:
            raise ValidationError(
                "Une piece marquee recue ou validee doit porter un fichier ou "
                "un lien : sinon rien n'a ete fourni."
            )
        if self.type == TypePiece.AUTRE and not self.libelle.strip():
            raise ValidationError(
                {
                    "libelle": "Une piece « Autre » sans libelle est introuvable "
                    "le jour ou on la cherche."
                }
            )

    @property
    def fournie(self) -> bool:
        return bool(self.fichier) or bool(self.lien_externe)

    @property
    def ou(self) -> str:
        if self.fichier:
            return "sur le serveur"
        if self.lien_externe:
            return "lien externe"
        return "—"

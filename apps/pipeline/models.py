"""Le pipeline de vente.

Deux regles sont tenues par la base, pas seulement par le formulaire.

1. **Une opportunite perdue porte un motif.** Une contrainte `CHECK` le
   garantit. Mise dans le seul formulaire, la regle serait contournee par
   l'administration Django, par un import et par une tache Celery — et au
   bout de six mois la question « pourquoi perd-on ? » n'aurait plus de
   reponse, qui est la seule raison d'avoir ce champ.

2. **Chaque passage d'etape est date.** Une colonne `etape` seule dit ou en
   est l'affaire, jamais combien de temps elle a mis. Le temps passe par
   etape est ce qui montre ou le pipeline se bouche — ici, probablement entre
   « Proposition envoyee » et « Dossier depose », a cause des delais de depot
   des financeurs.
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.crm.models import Contact, Entreprise, Lead


class Etape(models.TextChoices):
    """Les onze etapes du pipeline de vente, dans l'ordre.

    « Dossier depose » et « Accord financeur » sont deux etapes distinctes
    parce que le delai entre les deux n'appartient pas a l'organisme : un
    dossier AGEFICE se depose au plus tard 15 jours calendaires avant le
    demarrage, via un Point d'Accueil, et l'instruction prend le temps
    qu'elle prend. Les confondre rendrait le pipeline impossible a lire.
    """

    NOUVEAU = "nouveau", "Nouveau"
    CONTACTE = "contacte", "Contacte"
    QUALIFIE = "qualifie", "Qualifie"
    RDV_DIAGNOSTIC = "rdv_diagnostic", "RDV diagnostic"
    PROPOSITION_ENVOYEE = "proposition_envoyee", "Proposition envoyee"
    DOSSIER_DEPOSE = "dossier_depose", "Dossier depose"
    ACCORD_FINANCEUR = "accord_financeur", "Accord financeur"
    INSCRIT = "inscrit", "Inscrit"
    FORME = "forme", "Forme"
    PAYE = "paye", "Paye"
    PERDU = "perdu", "Perdu"


#: Etapes dont on ne ressort pas : l'affaire est close.
ETAPES_FINALES = frozenset({Etape.PAYE, Etape.PERDU})

#: Probabilite par defaut a l'entree dans l'etape, en pourcentage.
#: Ce sont des valeurs de depart, pas des mesures : l'organisme n'a pas encore
#: d'historique. A recalculer sur les faits des que 30 affaires seront closes.
PROBABILITE_PAR_ETAPE = {
    Etape.NOUVEAU: 5,
    Etape.CONTACTE: 10,
    Etape.QUALIFIE: 20,
    Etape.RDV_DIAGNOSTIC: 35,
    Etape.PROPOSITION_ENVOYEE: 50,
    Etape.DOSSIER_DEPOSE: 70,
    Etape.ACCORD_FINANCEUR: 90,
    Etape.INSCRIT: 95,
    Etape.FORME: 100,
    Etape.PAYE: 100,
    Etape.PERDU: 0,
}


class Financeur(models.TextChoices):
    """Financeur pressenti.

    ⚠️ Champ d'information seulement en phase 1. Le routage automatique — quel
    financeur, quel taux, quel plafond — est **gele** : l'arbitrage CMA contre
    FAFCEA transverse n'est pas tranche sur sources primaires. Ecrire une regle
    de routage avant cet arbitrage reviendrait a figer dans le code un taux que
    le site a deja annonce faux une fois.
    """

    AGEFICE = "agefice", "AGEFICE"
    FAFCEA = "fafcea", "FAFCEA"
    FIF_PL = "fifpl", "FIF PL"
    OPCO_EP = "opco_ep", "OPCO EP"
    CONSTRUCTYS = "constructys", "Constructys"
    AUTRE_OPCO = "autre_opco", "Autre OPCO"
    FONDS_PROPRES = "fonds_propres", "Fonds propres (sans financement)"
    INDETERMINE = "indetermine", "A determiner"


class MotifPerte(models.TextChoices):
    """Pourquoi l'affaire est perdue. Liste fermee, pour etre comptable."""

    RESTE_A_CHARGE = "reste_a_charge", "Reste a charge juge trop eleve"
    PAS_DE_DROITS = "pas_de_droits", "Pas de droits ouverts chez le financeur"
    PLAFOND_ATTEINT = "plafond_atteint", "Plafond annuel deja atteint"
    DELAI_DEPOT = "delai_depot", "Delai de depot du financeur depasse"
    REFUS_FINANCEUR = "refus_financeur", "Refus du financeur"
    CONCURRENT = "concurrent", "Parti chez un concurrent"
    PAS_LE_MOMENT = "pas_le_moment", "Pas le moment (a relancer)"
    INJOIGNABLE = "injoignable", "Injoignable apres relances"
    HORS_CIBLE = "hors_cible", "Hors cible (particulier, hors zone)"
    BESOIN_PRESTATION = "besoin_prestation", "Voulait une prestation, pas une formation"
    AUTRE = "autre", "Autre (precise en commentaire)"


class Opportunite(models.Model):
    """Une affaire en cours. Nait d'un lead qualifie."""

    lead = models.OneToOneField(
        Lead,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="opportunite",
    )
    entreprise = models.ForeignKey(
        Entreprise, on_delete=models.PROTECT, related_name="opportunites"
    )
    contact = models.ForeignKey(
        Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name="opportunites"
    )

    intitule = models.CharField(
        max_length=200, help_text="Ce qui est vendu, en clair. Ex. « Visibilite locale 21 h »."
    )
    formation = models.CharField(
        max_length=120,
        blank=True,
        help_text="Code du programme B4 : OFFRE-3, SITE, IA, IAL...",
    )
    duree_heures = models.PositiveIntegerField(
        null=True, blank=True, help_text="Duree vendue, qui determine le plafond mobilisable."
    )

    etape = models.CharField(
        max_length=25, choices=Etape.choices, default=Etape.NOUVEAU, db_index=True
    )
    probabilite = models.PositiveSmallIntegerField(default=5)

    montant_estime_centimes = models.PositiveIntegerField(
        default=0,
        help_text="En centimes d'euro HT. Jamais en flottant : 0,1 + 0,2 ne "
        "fait pas 0,3 en binaire, et un devis doit tomber juste.",
    )
    financeur_probable = models.CharField(
        max_length=20, choices=Financeur.choices, default=Financeur.INDETERMINE
    )

    motif_de_perte = models.CharField(max_length=25, choices=MotifPerte.choices, blank=True)
    commentaire_perte = models.TextField(blank=True)

    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="opportunites",
    )

    date_entree_etape = models.DateTimeField(default=timezone.now, db_index=True)
    date_cloture_prevue = models.DateField(null=True, blank=True)
    date_cloture = models.DateTimeField(null=True, blank=True)

    rang = models.PositiveIntegerField(
        default=0,
        help_text="Position dans la colonne du Kanban. Permet un ordre choisi "
        "a la main plutot qu'un tri impose.",
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "opportunite"
        verbose_name_plural = "opportunites"
        ordering = ("rang", "-date_entree_etape")
        constraints = [
            models.CheckConstraint(
                condition=~Q(etape=Etape.PERDU) | ~Q(motif_de_perte=""),
                name="perdu_exige_un_motif",
            ),
            models.CheckConstraint(
                condition=Q(probabilite__lte=100), name="probabilite_au_plus_cent"
            ),
        ]
        indexes = [models.Index(fields=["etape", "rang"])]

    def __str__(self) -> str:
        return f"{self.intitule} — {self.entreprise.denomination}"

    @property
    def montant_estime(self):
        """Montant en euros, pour l'affichage seulement.

        Quantifie a deux decimales : sans cela, 195 000 centimes s'affichent
        « 1950 » et 195 050 s'affichent « 1950.5 ». Deux formats differents
        dans la meme colonne d'un tableau de bord se lisent mal.
        """
        from decimal import Decimal

        return (Decimal(self.montant_estime_centimes) / 100).quantize(Decimal("0.01"))

    @property
    def est_close(self) -> bool:
        return self.etape in ETAPES_FINALES

    def clean(self):
        """Double la contrainte CHECK, pour un message lisible dans un formulaire.

        La contrainte base protege de tous les chemins d'ecriture ; `clean()`
        explique a l'utilisateur ce qui manque au lieu d'afficher une erreur
        d'integrite.
        """
        super().clean()
        if self.etape == Etape.PERDU and not self.motif_de_perte:
            raise ValidationError(
                {
                    "motif_de_perte": "Une affaire perdue porte un motif. "
                    "Sans motif, la question « pourquoi perd-on ? » n'aura "
                    "pas de reponse dans six mois."
                }
            )
        if self.motif_de_perte == MotifPerte.AUTRE and not self.commentaire_perte.strip():
            raise ValidationError(
                {
                    "commentaire_perte": "Le motif « Autre » demande une "
                    "explication, sinon il absorbe tous les cas et ne "
                    "renseigne plus rien."
                }
            )


class PassageEtape(models.Model):
    """Combien de temps l'affaire est restee a une etape.

    Ecrit par `apps.pipeline.services.changer_etape`, jamais a la main.
    """

    opportunite = models.ForeignKey(Opportunite, on_delete=models.CASCADE, related_name="passages")
    etape = models.CharField(max_length=25, choices=Etape.choices)
    entree_le = models.DateTimeField()
    sortie_le = models.DateTimeField(null=True, blank=True)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "passage d'etape"
        verbose_name_plural = "passages d'etape"
        ordering = ("entree_le",)
        indexes = [models.Index(fields=["opportunite", "entree_le"])]

    def __str__(self) -> str:
        return f"{self.get_etape_display()} ({self.duree_jours} j)"

    @property
    def duree_jours(self) -> float | None:
        fin = self.sortie_le or timezone.now()
        return round((fin - self.entree_le).total_seconds() / 86400, 1)

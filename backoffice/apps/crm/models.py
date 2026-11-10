"""Entreprises, contacts, leads, activites, oppositions.

Trois partis pris structurent ce fichier.

1. **Les formes normalisees sont des colonnes, pas des proprietes.** Un
   dedoublonnage qui normalise a la lecture ne peut pas utiliser d'index :
   il relit toute la table a chaque lead entrant. Les colonnes
   `*_normalise` sont recalculees dans `save()` et indexees.

2. **Le payload d'origine est conserve tel quel.** Quand un lead Meta arrive
   mal interprete, la seule facon de corriger sans perdre l'information est de
   relire ce que Meta a reellement envoye.

3. **L'opposition est une table, pas une case a cocher.** Une personne qui
   s'oppose avant d'etre en base doit pouvoir etre inscrite quand meme, sinon
   son opposition est perdue jusqu'a ce qu'elle reapparaisse.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.crm.normalisation import (
    normaliser_email,
    normaliser_nom,
    normaliser_siren,
    normaliser_telephone,
    siren_valide,
)


def valider_siren(valeur: str) -> None:
    if valeur and not siren_valide(valeur):
        raise ValidationError(
            "Ce SIREN ne passe pas le controle de cle (Luhn) : "
            "verifier la saisie, un chiffre est probablement errone.",
            code="siren_invalide",
        )


class TrancheEffectif(models.TextChoices):
    """Codes INSEE, conserves tels quels pour rester comparables aux donnees
    de l'API Recherche d'entreprises."""

    NON_RENSEIGNE = "NN", "Non renseigne"
    ZERO_SALARIE = "00", "0 salarie"
    UN_DEUX = "01", "1 ou 2 salaries"
    TROIS_CINQ = "02", "3 a 5 salaries"
    SIX_NEUF = "03", "6 a 9 salaries"
    DIX_DIX_NEUF = "11", "10 a 19 salaries"
    VINGT_QUARANTE_NEUF = "12", "20 a 49 salaries"
    CINQUANTE_NONANTE_NEUF = "21", "50 a 99 salaries"
    CENT_ET_PLUS = "22", "100 salaries et plus"


class Entreprise(models.Model):
    """La personne morale. Le SIREN en est la cle metier.

    Le SIREN est unique et facultatif : un lead Meta arrive sans SIREN, il est
    resolu ensuite. Une contrainte unique classique interdirait deux fiches
    sans SIREN ; la contrainte est donc conditionnelle.
    """

    siren = models.CharField(
        max_length=9,
        blank=True,
        db_index=True,
        validators=[valider_siren],
        help_text="9 chiffres. Vide tant que la resolution n'a pas abouti.",
    )
    denomination = models.CharField(max_length=200)
    denomination_normalisee = models.CharField(max_length=200, blank=True, db_index=True)
    nom_commercial = models.CharField(max_length=200, blank=True)

    categorie_juridique = models.CharField(
        max_length=4, blank=True, help_text="Code INSEE, par ex. 5499 ou 1000."
    )
    categorie_juridique_libelle = models.CharField(max_length=200, blank=True)

    naf = models.CharField(
        max_length=6, blank=True, db_index=True, help_text="NAF en vigueur, ex. 56.10A."
    )
    naf_libelle = models.CharField(max_length=250, blank=True)
    naf_2025 = models.CharField(
        max_length=8,
        blank=True,
        help_text="Nomenclature NAF 2025. Conservee a part : le routage "
        "financeur s'appuie sur l'une ou l'autre selon la date du dossier.",
    )

    date_creation_entreprise = models.DateField(null=True, blank=True)
    tranche_effectif = models.CharField(
        max_length=2,
        choices=TrancheEffectif.choices,
        default=TrancheEffectif.NON_RENSEIGNE,
    )

    adresse = models.CharField(max_length=250, blank=True)
    code_postal = models.CharField(max_length=10, blank=True, db_index=True)
    commune = models.CharField(max_length=120, blank=True)
    departement = models.CharField(
        max_length=3, blank=True, db_index=True, help_text="Ex. 34 pour l'Herault."
    )

    etat_administratif = models.CharField(
        max_length=1,
        blank=True,
        choices=[("A", "Active"), ("C", "Cessee")],
        help_text="Etat de l'unite legale. Une entreprise cessee ne se vend "
        "pas une formation : le champ est lu avant tout devis.",
    )
    opposition_diffusion_commerciale = models.BooleanField(
        null=True,
        blank=True,
        help_text="Releve dans l'API Recherche d'entreprises. Vrai = l'unite "
        "legale s'est opposee a la reutilisation de ses donnees a des fins de "
        "prospection (RGPD art. 21 §2, art. R.123-320 du Code de commerce). "
        "Nul = unite legale absente du RNE, ce qui n'est pas une absence "
        "d'opposition.",
    )
    inscrite_repertoire_metiers = models.BooleanField(
        null=True,
        blank=True,
        help_text="Determine l'eligibilite FAFCEA. Nul = non verifie, ce qui "
        "n'est pas la meme chose que non inscrite.",
    )
    diffusible = models.BooleanField(
        default=True,
        help_text="Faux si l'INSEE marque l'unite legale non diffusible : "
        "ses donnees ne doivent alors ni etre publiees ni exportees.",
    )
    statut_diffusion = models.CharField(max_length=40, blank=True)

    source_resolution = models.CharField(
        max_length=60,
        blank=True,
        help_text="D'ou vient la fiche : recherche-entreprises, saisie, import.",
    )
    date_resolution = models.DateTimeField(null=True, blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "entreprise"
        verbose_name_plural = "entreprises"
        ordering = ("denomination",)
        constraints = [
            models.UniqueConstraint(
                fields=["siren"],
                condition=~Q(siren=""),
                name="siren_unique_si_renseigne",
            )
        ]

    def __str__(self) -> str:
        return f"{self.denomination} ({self.siren})" if self.siren else self.denomination

    def save(self, *args, **kwargs):
        self.siren = normaliser_siren(self.siren)
        self.denomination_normalisee = normaliser_nom(self.denomination)
        if self.code_postal and not self.departement:
            self.departement = self.code_postal[:2]
        return super().save(*args, **kwargs)


class StatutContact(models.TextChoices):
    """Le statut decide du financeur : un gerant majoritaire non salarie
    releve de l'AGEFICE ou du FAFCEA, un salarie releve de l'OPCO."""

    GERANT_MAJORITAIRE = "gerant_majoritaire", "Gerant majoritaire"
    GERANT_MINORITAIRE = "gerant_minoritaire", "Gerant minoritaire"
    SALARIE = "salarie", "Salarie"
    CONJOINT_COLLABORATEUR = "conjoint", "Conjoint collaborateur"
    INCONNU = "inconnu", "Inconnu"


class BaseLegale(models.TextChoices):
    """RGPD article 6. Inscrite a la collecte, pas devinee ensuite."""

    CONSENTEMENT = "consentement", "Consentement (formulaire rempli)"
    INTERET_LEGITIME = "interet_legitime", "Interet legitime (prospection B2B)"
    CONTRAT = "contrat", "Execution d'un contrat"


class Contact(models.Model):
    """La personne physique. Rattachee a une entreprise."""

    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name="contacts")
    civilite = models.CharField(max_length=10, blank=True)
    prenom = models.CharField(max_length=100, blank=True)
    nom = models.CharField(max_length=120)
    nom_normalise = models.CharField(max_length=220, blank=True, db_index=True)
    fonction = models.CharField(max_length=150, blank=True)
    statut = models.CharField(
        max_length=20, choices=StatutContact.choices, default=StatutContact.INCONNU
    )

    email = models.EmailField(blank=True)
    email_normalise = models.CharField(max_length=254, blank=True, db_index=True)
    telephone = models.CharField(max_length=40, blank=True)
    telephone_normalise = models.CharField(max_length=20, blank=True, db_index=True)

    email_devine = models.BooleanField(
        default=False,
        help_text="Vrai si l'adresse a ete reconstruite (prenom.nom@domaine) "
        "et non fournie. Un email devine ne doit pas servir de preuve de "
        "consentement et sa delivrabilite n'est pas garantie.",
    )
    base_legale = models.CharField(
        max_length=20, choices=BaseLegale.choices, default=BaseLegale.INTERET_LEGITIME
    )
    date_collecte = models.DateTimeField(default=timezone.now)
    origine_collecte = models.CharField(max_length=120, blank=True)

    oppose = models.BooleanField(
        default=False,
        help_text="Recopie depuis la table des oppositions. Redondant par "
        "choix : une requete d'envoi ne doit pas pouvoir oublier la jointure.",
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "contact"
        verbose_name_plural = "contacts"
        ordering = ("nom", "prenom")
        constraints = [
            models.UniqueConstraint(
                fields=["entreprise", "email_normalise"],
                condition=~Q(email_normalise=""),
                name="un_email_par_entreprise",
            )
        ]
        indexes = [models.Index(fields=["email_normalise", "telephone_normalise"])]

    def __str__(self) -> str:
        complet = f"{self.prenom} {self.nom}".strip()
        return f"{complet} — {self.entreprise.denomination}" if self.entreprise_id else complet

    def save(self, *args, **kwargs):
        self.email_normalise = normaliser_email(self.email)
        self.telephone_normalise = normaliser_telephone(self.telephone)
        self.nom_normalise = normaliser_nom(f"{self.prenom} {self.nom}")
        return super().save(*args, **kwargs)


class SourceLead(models.TextChoices):
    META_LEAD_ADS = "meta_lead_ads", "Meta Lead Ads"
    FORMULAIRE_SITE = "formulaire_site", "Formulaire du site"
    SAISIE_MANUELLE = "saisie_manuelle", "Saisie manuelle"
    IMPORT_CSV = "import_csv", "Import CSV"
    SOURCING = "sourcing", "Sourcing sortant"
    RECOMMANDATION = "recommandation", "Recommandation"
    APPEL_ENTRANT = "appel_entrant", "Appel entrant"


class EtapeAmont(models.TextChoices):
    """Les quatre etapes que suit un lead de sourcing avant d'entrer dans le
    pipeline de vente. Un lead entrant (Meta, formulaire) les saute."""

    IDENTIFIE = "identifie", "Identifie"
    ENRICHI = "enrichi", "Enrichi"
    EN_SEQUENCE = "en_sequence", "En sequence"
    A_REPONDU = "a_repondu", "A repondu"


class Lead(models.Model):
    """Une demande entrante ou une cible sortante, avant qualification.

    Un lead n'est pas une opportunite : il devient une opportunite quand il
    entre dans le pipeline de vente. Separer les deux evite de compter comme
    affaire en cours un formulaire rempli par erreur.
    """

    source = models.CharField(max_length=20, choices=SourceLead.choices)

    # --- Identite declaree, avant rattachement ---------------------------
    nom_declare = models.CharField(max_length=200, blank=True)
    email_declare = models.EmailField(blank=True)
    telephone_declare = models.CharField(max_length=40, blank=True)
    entreprise_declaree = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    formation_demandee = models.CharField(max_length=200, blank=True)

    # --- Formes normalisees, indexees : base du dedoublonnage ------------
    email_normalise = models.CharField(max_length=254, blank=True, db_index=True)
    telephone_normalise = models.CharField(max_length=20, blank=True, db_index=True)
    nom_normalise = models.CharField(max_length=220, blank=True, db_index=True)

    # --- Rattachement, une fois le SIREN resolu --------------------------
    entreprise = models.ForeignKey(
        Entreprise, null=True, blank=True, on_delete=models.SET_NULL, related_name="leads"
    )
    contact = models.ForeignKey(
        Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name="leads"
    )

    # --- Tracabilite Meta ------------------------------------------------
    # Sans ces cinq champs, une campagne ne peut pas etre jugee : on connait
    # le cout par lead mais pas le cout par inscrit, qui est le seul utile.
    meta_leadgen_id = models.CharField(
        max_length=64,
        blank=True,
        help_text="Identifiant du lead chez Meta. Garantit l'idempotence : "
        "Meta reemet le meme webhook jusqu'a recevoir un 200.",
    )
    meta_formulaire_id = models.CharField(max_length=64, blank=True)
    meta_formulaire_nom = models.CharField(max_length=200, blank=True)
    meta_campagne_id = models.CharField(max_length=64, blank=True, db_index=True)
    meta_campagne_nom = models.CharField(max_length=200, blank=True)
    meta_ensemble_id = models.CharField(max_length=64, blank=True)
    meta_ensemble_nom = models.CharField(max_length=200, blank=True)
    meta_publicite_id = models.CharField(max_length=64, blank=True)
    meta_publicite_nom = models.CharField(max_length=200, blank=True)

    campagne = models.ForeignKey(
        "publicite.Campagne",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
        help_text="Rattachement a la campagne qui a produit ce lead. Rempli "
        "par le rapprochement, a partir de `meta_campagne_id` — ou a la main "
        "pour une regie qui ne transmet pas d'identifiant. C'est ce lien qui "
        "permet de calculer un cout par client, et non seulement un cout par "
        "lead.",
    )

    payload_origine = models.JSONField(
        default=dict,
        blank=True,
        help_text="Ce que la source a reellement envoye. Jamais reecrit : "
        "c'est la seule facon de rattraper une interpretation fautive.",
    )

    score = models.IntegerField(
        default=0, help_text="Calcule par apps.pipeline.scoring. 0 = non score."
    )
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
    )
    etape_amont = models.CharField(
        max_length=20,
        choices=EtapeAmont.choices,
        blank=True,
        help_text="Renseignee pour un lead de sourcing seulement.",
    )

    candidats_siren = models.JSONField(
        default=list,
        blank=True,
        help_text="Candidats trouves par la resolution SIREN, avec leur note "
        "et les motifs de cette note. Conserves meme en cas de succes : c'est "
        "ce qui permet de corriger un rattachement faux sans relancer la "
        "recherche, et de savoir quel critere a mal juge.",
    )
    certitude_resolution = models.CharField(
        max_length=10,
        blank=True,
        choices=[
            ("certain", "Certain"),
            ("probable", "Probable"),
            ("ambigu", "Ambigu — plusieurs candidats"),
            ("aucun", "Aucun candidat"),
        ],
        help_text="Un rattachement « ambigu » n'est jamais applique seul : "
        "choisir au hasard entre deux homonymes mettrait un faux SIREN sur "
        "un dossier de financement.",
    )
    motif_resolution = models.CharField(max_length=300, blank=True)

    doublon_de = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="doublons",
        help_text="Renseigne au lieu de supprimer : le volume reel d'une "
        "campagne se compte doublons inclus, le pipeline les exclut.",
    )

    date_reception = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Date de l'evenement chez la source, pas de l'ecriture ici.",
    )
    date_premier_contact = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Premiere tentative de contact sortante. Nul = l'alerte des 24 h s'applique.",
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "lead"
        verbose_name_plural = "leads"
        ordering = ("-date_reception",)
        constraints = [
            models.UniqueConstraint(
                fields=["meta_leadgen_id"],
                condition=~Q(meta_leadgen_id=""),
                name="leadgen_meta_unique",
            )
        ]
        indexes = [
            models.Index(fields=["source", "-date_reception"]),
            models.Index(fields=["date_premier_contact", "-date_reception"]),
        ]

    def __str__(self) -> str:
        qui = self.nom_declare or self.email_declare or self.telephone_declare or "sans nom"
        return f"{qui} · {self.get_source_display()}"

    def save(self, *args, **kwargs):
        self.email_normalise = normaliser_email(self.email_declare)
        self.telephone_normalise = normaliser_telephone(self.telephone_declare)
        self.nom_normalise = normaliser_nom(self.nom_declare)
        return super().save(*args, **kwargs)

    @property
    def en_retard(self) -> bool:
        """Vrai au-dela de 24 h sans contact. Critere de sortie de la phase 1."""
        if self.date_premier_contact is not None:
            return False
        if self.doublon_de_id is not None:
            return False
        return (timezone.now() - self.date_reception) > timezone.timedelta(hours=24)


class TypeActivite(models.TextChoices):
    APPEL = "appel", "Appel"
    EMAIL = "email", "Email"
    NOTE = "note", "Note"
    RDV = "rdv", "Rendez-vous"
    CHANGEMENT_ETAPE = "changement_etape", "Changement d'etape"
    SYSTEME = "systeme", "Evenement automatique"


#: Types qui comptent comme une tentative de contact sortante : ce sont eux
#: qui arretent le compte a rebours des 24 h. Une note interne ne l'arrete pas.
TYPES_CONTACT = frozenset({TypeActivite.APPEL, TypeActivite.EMAIL, TypeActivite.RDV})


class Activite(models.Model):
    """Ce qui s'est passe, rattache a n'importe quel objet du CRM.

    Lien generique plutot que trois cles etrangeres : une activite se rattache
    aussi bien a un lead qu'a une opportunite ou a une session de formation,
    et la liste des objets concernes grandira aux phases suivantes.
    """

    type = models.CharField(max_length=20, choices=TypeActivite.choices)
    type_objet = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    id_objet = models.CharField(max_length=40, db_index=True)
    objet = GenericForeignKey("type_objet", "id_objet")

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activites",
    )
    date = models.DateTimeField(default=timezone.now, db_index=True)
    contenu = models.TextField(blank=True)
    duree_minutes = models.PositiveIntegerField(null=True, blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "activite"
        verbose_name_plural = "activites"
        ordering = ("-date",)
        indexes = [models.Index(fields=["type_objet", "id_objet", "-date"])]

    def __str__(self) -> str:
        return f"{self.get_type_display()} · {self.date:%d/%m/%Y %H:%M}"


class CanalOpposition(models.TextChoices):
    DESABONNEMENT = "desabonnement", "Lien de desabonnement"
    DEMANDE_DIRECTE = "demande_directe", "Demande directe (email, courrier)"
    APPEL = "appel", "Demande pendant un appel"
    BLOCTEL = "bloctel", "Bloctel"
    RETOUR_TECHNIQUE = "retour_technique", "Retour technique (adresse morte)"


class Opposition(models.Model):
    """Les gens qui ne veulent plus etre contactes.

    Consultee avant tout envoi et tout appel. Une table a part, et non une
    case sur le contact, pour trois raisons : une opposition peut arriver
    avant que la personne soit en base ; elle doit survivre a la suppression
    de sa fiche ; et elle peut porter sur un SIREN entier.
    """

    email_normalise = models.CharField(max_length=254, blank=True, db_index=True)
    telephone_normalise = models.CharField(max_length=20, blank=True, db_index=True)
    siren = models.CharField(max_length=9, blank=True, db_index=True)

    canal = models.CharField(max_length=20, choices=CanalOpposition.choices)
    date = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=250, blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "opposition"
        verbose_name_plural = "oppositions"
        ordering = ("-date",)
        constraints = [
            models.CheckConstraint(
                condition=~(Q(email_normalise="") & Q(telephone_normalise="") & Q(siren="")),
                name="opposition_porte_sur_quelque_chose",
            )
        ]

    def __str__(self) -> str:
        return self.email_normalise or self.telephone_normalise or self.siren

    def save(self, *args, **kwargs):
        self.email_normalise = normaliser_email(self.email_normalise)
        self.telephone_normalise = normaliser_telephone(self.telephone_normalise)
        self.siren = normaliser_siren(self.siren)
        return super().save(*args, **kwargs)

    @classmethod
    def est_oppose(cls, email: str = "", telephone: str = "", siren: str = "") -> bool:
        """A consulter avant tout envoi ou appel.

        Normalise ses arguments : l'appelant n'a pas a savoir comment la table
        est ecrite, sinon la verification sera oubliee quelque part.
        """
        criteres = Q(pk__in=[])
        if e := normaliser_email(email):
            criteres |= Q(email_normalise=e)
        if t := normaliser_telephone(telephone):
            criteres |= Q(telephone_normalise=t)
        if s := normaliser_siren(siren):
            criteres |= Q(siren=s)
        return cls.objects.filter(criteres).exists()

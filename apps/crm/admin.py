"""Administration du CRM.

Elle est enregistree sur `admin_site`, la version a double authentification :
sans cela, un mot de passe seul suffirait a lire toute la base de prospects.

Parti pris d'affichage : on montre d'abord ce qui bloque. Un lead utile n'est
pas « le dernier recu », c'est « celui que personne n'a rappele » ou « celui
dont l'entreprise n'est pas identifiee ».
"""

from django.contrib import admin
from django.utils.html import format_html

from apps.accounts.admin import admin_site
from apps.crm.models import Activite, Contact, Entreprise, Lead, Opposition


class ContactEnLigne(admin.TabularInline):
    model = Contact
    extra = 0
    fields = ("prenom", "nom", "fonction", "statut", "email", "telephone", "oppose")
    readonly_fields = ("oppose",)
    show_change_link = True


class AdminEntreprise(admin.ModelAdmin):
    list_display = (
        "denomination",
        "siren",
        "commune",
        "naf",
        "tranche_effectif",
        "etat_administratif",
        "signal_opposition",
    )
    list_filter = ("departement", "etat_administratif", "tranche_effectif", "diffusible")
    search_fields = ("denomination", "nom_commercial", "siren", "commune")
    readonly_fields = (
        "denomination_normalisee",
        "source_resolution",
        "date_resolution",
        "cree_le",
        "modifie_le",
    )
    inlines = [ContactEnLigne]
    fieldsets = (
        ("Identite", {"fields": ("siren", "denomination", "nom_commercial")}),
        (
            "Classement",
            {
                "fields": (
                    "categorie_juridique",
                    "categorie_juridique_libelle",
                    "naf",
                    "naf_libelle",
                    "naf_2025",
                    "date_creation_entreprise",
                    "tranche_effectif",
                )
            },
        ),
        ("Adresse", {"fields": ("adresse", "code_postal", "commune", "departement")}),
        (
            "Statut et prospection",
            {
                "fields": (
                    "etat_administratif",
                    "inscrite_repertoire_metiers",
                    "diffusible",
                    "statut_diffusion",
                    "opposition_diffusion_commerciale",
                ),
                "description": (
                    "« Opposition diffusion commerciale » vient du registre : "
                    "vrai signifie que l'entreprise s'est opposee a la "
                    "reutilisation de ses donnees a des fins de prospection "
                    "(RGPD art. 21 §2). Elle est alors inscrite "
                    "automatiquement au registre des oppositions."
                ),
            },
        ),
        (
            "Tracabilite",
            {"fields": ("source_resolution", "date_resolution", "cree_le", "modifie_le")},
        ),
    )

    @admin.display(description="Prospection", boolean=False)
    def signal_opposition(self, obj):
        if obj.opposition_diffusion_commerciale:
            return format_html('<b style="color:#b42318">opposee</b>')
        if obj.opposition_diffusion_commerciale is False:
            return "autorisee"
        return "inconnue (hors RNE)"


class AdminContact(admin.ModelAdmin):
    list_display = ("nom", "prenom", "entreprise", "fonction", "statut", "email", "oppose")
    list_filter = ("statut", "base_legale", "oppose", "email_devine")
    search_fields = ("nom", "prenom", "email", "telephone", "entreprise__denomination")
    readonly_fields = ("email_normalise", "telephone_normalise", "nom_normalise", "cree_le")
    autocomplete_fields = ("entreprise",)


class AdminLead(admin.ModelAdmin):
    list_display = (
        "date_reception",
        "nom_declare",
        "entreprise_affichee",
        "source",
        "certitude_resolution",
        "signal_retard",
        "doublon_de",
    )
    list_filter = (
        "source",
        "certitude_resolution",
        "etape_amont",
        ("date_premier_contact", admin.EmptyFieldListFilter),
        ("doublon_de", admin.EmptyFieldListFilter),
    )
    search_fields = (
        "nom_declare",
        "email_declare",
        "telephone_declare",
        "entreprise_declaree",
        "meta_leadgen_id",
        "meta_campagne_nom",
    )
    readonly_fields = (
        "email_normalise",
        "telephone_normalise",
        "nom_normalise",
        "candidats_siren",
        "motif_resolution",
        "payload_origine",
        "cree_le",
        "modifie_le",
    )
    autocomplete_fields = ("entreprise", "contact", "doublon_de", "proprietaire")
    date_hierarchy = "date_reception"
    fieldsets = (
        (
            "Ce que le prospect a declare",
            {
                "fields": (
                    "source",
                    "nom_declare",
                    "email_declare",
                    "telephone_declare",
                    "entreprise_declaree",
                    "formation_demandee",
                    "message",
                ),
            },
        ),
        (
            "Rattachement",
            {
                "fields": (
                    "entreprise",
                    "contact",
                    "certitude_resolution",
                    "motif_resolution",
                    "candidats_siren",
                ),
                "description": (
                    "Une certitude « ambigu » signifie que plusieurs entreprises "
                    "correspondaient. Le choix est laisse a un humain : un faux "
                    "SIREN sur un dossier de financement se decouvre au depot, "
                    "apres signature."
                ),
            },
        ),
        (
            "Suivi",
            {
                "fields": (
                    "proprietaire",
                    "etape_amont",
                    "score",
                    "date_reception",
                    "date_premier_contact",
                    "doublon_de",
                )
            },
        ),
        (
            "Tracabilite Meta",
            {
                "classes": ("collapse",),
                "fields": (
                    "meta_leadgen_id",
                    "meta_formulaire_id",
                    "meta_formulaire_nom",
                    "meta_campagne_id",
                    "meta_campagne_nom",
                    "meta_ensemble_id",
                    "meta_ensemble_nom",
                    "meta_publicite_id",
                    "meta_publicite_nom",
                    "payload_origine",
                ),
            },
        ),
    )

    @admin.display(description="Entreprise")
    def entreprise_affichee(self, obj):
        return (
            obj.entreprise.denomination if obj.entreprise_id else (obj.entreprise_declaree or "—")
        )

    @admin.display(description="Retard", boolean=True)
    def signal_retard(self, obj):
        return not obj.en_retard


class AdminOpposition(admin.ModelAdmin):
    list_display = ("__str__", "canal", "date", "note")
    list_filter = ("canal",)
    search_fields = ("email_normalise", "telephone_normalise", "siren")

    def has_delete_permission(self, request, obj=None):
        # Supprimer une opposition, c'est autoriser a nouveau un demarchage
        # refuse. Si c'est vraiment necessaire, cela passe par une commande
        # tracee, pas par un clic.
        return False


class AdminActivite(admin.ModelAdmin):
    list_display = ("date", "type", "auteur", "type_objet", "id_objet", "apercu")
    list_filter = ("type", "type_objet")
    search_fields = ("contenu", "id_objet")
    date_hierarchy = "date"

    @admin.display(description="Contenu")
    def apercu(self, obj):
        return (obj.contenu or "")[:110]


admin_site.register(Entreprise, AdminEntreprise)
admin_site.register(Contact, AdminContact)
admin_site.register(Lead, AdminLead)
admin_site.register(Opposition, AdminOpposition)
admin_site.register(Activite, AdminActivite)

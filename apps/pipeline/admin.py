"""Administration du pipeline."""

from django.contrib import admin

from apps.accounts.admin import admin_site
from apps.pipeline.models import Opportunite, PassageEtape


class PassageEnLigne(admin.TabularInline):
    model = PassageEtape
    extra = 0
    fields = ("etape", "entree_le", "sortie_le", "duree_jours", "auteur")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        # Les passages sont ecrits par `changer_etape`. Les saisir a la main
        # fausserait le temps par etape, qui est la seule mesure utile du
        # pipeline.
        return False


class AdminOpportunite(admin.ModelAdmin):
    list_display = (
        "intitule",
        "entreprise",
        "etape",
        "probabilite",
        "montant_estime",
        "financeur_probable",
        "motif_de_perte",
        "date_entree_etape",
    )
    list_filter = ("etape", "financeur_probable", "motif_de_perte", "formation")
    search_fields = ("intitule", "entreprise__denomination", "entreprise__siren")
    autocomplete_fields = ("entreprise", "contact", "lead", "proprietaire")
    readonly_fields = ("date_entree_etape", "date_cloture", "cree_le", "modifie_le")
    inlines = [PassageEnLigne]
    fieldsets = (
        (
            "Affaire",
            {
                "fields": (
                    "intitule",
                    "formation",
                    "duree_heures",
                    "entreprise",
                    "contact",
                    "lead",
                    "proprietaire",
                )
            },
        ),
        (
            "Avancement",
            {
                "fields": (
                    "etape",
                    "probabilite",
                    "rang",
                    "date_entree_etape",
                    "date_cloture_prevue",
                    "date_cloture",
                )
            },
        ),
        (
            "Montant et financement",
            {
                "fields": ("montant_estime_centimes", "financeur_probable"),
                "description": (
                    "Le montant est en CENTIMES d'euro HT. Le financeur est "
                    "informatif : le routage automatique est gele tant que "
                    "l'arbitrage CMA / FAFCEA transverse n'est pas tranche sur "
                    "sources primaires."
                ),
            },
        ),
        (
            "Perte",
            {
                "fields": ("motif_de_perte", "commentaire_perte"),
                "description": (
                    "Obligatoire des que l'etape est « Perdu » — tenu par une "
                    "contrainte en base, pas seulement par ce formulaire."
                ),
            },
        ),
    )


admin_site.register(Opportunite, AdminOpportunite)

"""Administration des receptions de webhooks."""

from django.contrib import admin

from apps.accounts.admin import admin_site
from apps.integrations.models import ReceptionWebhook


class AdminReception(admin.ModelAdmin):
    list_display = (
        "recue_le",
        "source",
        "signature_valide",
        "etat",
        "cle_idempotence",
        "delai_de_traitement_secondes",
        "tentatives",
        "lead",
    )
    list_filter = ("source", "etat", "signature_valide")
    search_fields = ("cle_idempotence", "corps", "erreur")
    date_hierarchy = "recue_le"
    readonly_fields = tuple(f.name for f in ReceptionWebhook._meta.fields) + (
        "delai_de_traitement_secondes",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Le corps brut est la preuve de ce que Meta a envoye : le rendre
        # modifiable lui oterait sa valeur.
        return False


admin_site.register(ReceptionWebhook, AdminReception)

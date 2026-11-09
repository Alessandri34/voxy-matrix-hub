"""Le journal se consulte, ne s'edite pas."""

from django.contrib import admin

from apps.audit.models import EntreeJournal


class AdminJournal(admin.ModelAdmin):
    list_display = ("date", "acteur", "origine", "action", "libelle_objet")
    list_filter = ("action", "origine", "type_objet")
    search_fields = ("libelle_objet", "id_objet")
    date_hierarchy = "date"
    readonly_fields = tuple(f.name for f in EntreeJournal._meta.fields) + ("objet",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Une purge legitime (duree de conservation) passe par une commande
        # de gestion tracee, pas par un clic dans l'administration.
        return False

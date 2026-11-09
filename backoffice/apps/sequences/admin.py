"""Administration des sequences."""

from django.contrib import admin
from django.utils.html import format_html

from apps.accounts.admin import admin_site
from apps.sequences.models import Envoi, EtapeSequence, Inscription, Sequence


class EtapeEnLigne(admin.TabularInline):
    model = EtapeSequence
    extra = 1
    fields = ("ordre", "delai_jours", "canal", "objet", "corps", "active")


class AdminSequence(admin.ModelAdmin):
    list_display = ("nom", "cible", "active", "nb_etapes", "nb_actives", "plafond_quotidien")
    list_filter = ("cible", "active")
    search_fields = ("nom", "description")
    inlines = [EtapeEnLigne]
    fieldsets = (
        ("Identite", {"fields": ("nom", "description", "cible", "active")}),
        (
            "Conditions d'arret",
            {
                "fields": ("arret_si_reponse", "arret_si_opportunite"),
                "description": (
                    "L'opposition a la prospection arrete TOUJOURS une "
                    "sequence : elle n'est pas reglable ici, et elle est "
                    "verifiee avant chaque envoi, pas seulement a "
                    "l'inscription."
                ),
            },
        ),
        (
            "Rythme",
            {
                "fields": ("jours_ouvres_seulement", "heure_min", "heure_max", "plafond_quotidien"),
                "description": (
                    "Un envoi groupe le dimanche matin signale une "
                    "automatisation a tout le monde, et un pic de volume "
                    "degrade la reputation du domaine — celui qui porte aussi "
                    "les convocations de formation."
                ),
            },
        ),
    )

    @admin.display(description="Etapes")
    def nb_etapes(self, obj):
        return obj.etapes.count()

    @admin.display(description="Actives")
    def nb_actives(self, obj):
        actives = obj.etapes.filter(active=True).count()
        if obj.active and not actives:
            return format_html('<b style="color:#b42318">aucune</b>')
        return actives


class AdminInscription(admin.ModelAdmin):
    list_display = (
        "__str__",
        "sequence",
        "etat",
        "etape_courante",
        "prochaine_echeance",
        "motif_arret",
    )
    list_filter = ("sequence", "etat", "motif_arret")
    search_fields = ("lead__nom_declare", "contact__nom", "contact__email")
    autocomplete_fields = ("lead", "contact")
    readonly_fields = ("inscrit_le", "terminee_le", "detail_arret")
    date_hierarchy = "inscrit_le"


class AdminEnvoi(admin.ModelAdmin):
    list_display = ("prevu_le", "canal", "destinataire", "objet", "etat", "envoye_le")
    list_filter = ("etat", "canal", "inscription__sequence")
    search_fields = ("destinataire", "objet", "corps")
    date_hierarchy = "prevu_le"
    readonly_fields = tuple(f.name for f in Envoi._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Le corps conserve est la preuve de ce qui a ete envoye : le rendre
        # modifiable lui oterait sa valeur.
        return False


admin_site.register(Sequence, AdminSequence)
admin_site.register(Inscription, AdminInscription)
admin_site.register(Envoi, AdminEnvoi)

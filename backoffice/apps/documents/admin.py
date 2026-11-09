"""Administration des pieces."""

from django.contrib import admin

from apps.accounts.admin import admin_site
from apps.documents.models import Piece


class AdminPiece(admin.ModelAdmin):
    list_display = ("dossier", "type", "libelle", "etat", "ou", "recue_le", "validee_par")
    list_filter = ("etat", "type", "dossier__financeur")
    search_fields = (
        "libelle",
        "note",
        "dossier__numero_dossier",
        "dossier__opportunite__entreprise__denomination",
    )
    autocomplete_fields = ("dossier", "validee_par")
    readonly_fields = ("recue_le", "validee_le", "cree_le", "modifie_le")
    fieldsets = (
        ("Piece", {"fields": ("dossier", "type", "libelle", "obligatoire", "etat")}),
        (
            "Ou elle se trouve",
            {
                "fields": ("fichier", "lien_externe"),
                "description": (
                    "Un fichier est sauvegarde avec la base, mais occupe le "
                    "disque du VPS. Un lien externe (Drive, Nextcloud) ne "
                    "pese rien ici, mais <b>la sauvegarde chiffree du "
                    "back-office ne le couvre pas</b> et un lien peut casser. "
                    "L'un ou l'autre suffit pour que la piece compte."
                ),
            },
        ),
        (
            "Suivi",
            {"fields": ("note", "recue_le", "validee_le", "validee_par", "cree_le", "modifie_le")},
        ),
    )


class PieceEnLigne(admin.TabularInline):
    model = Piece
    extra = 0
    fields = ("type", "libelle", "etat", "fichier", "lien_externe", "obligatoire")
    show_change_link = True


admin_site.register(Piece, AdminPiece)

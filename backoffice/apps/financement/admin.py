"""Administration des dossiers de financement."""

from django.contrib import admin
from django.utils.html import format_html

from apps.accounts.admin import admin_site
from apps.documents.admin import PieceEnLigne
from apps.financement.models import Dossier


class AdminDossier(admin.ModelAdmin):
    list_display = (
        "opportunite",
        "financeur",
        "etat",
        "date_debut_formation",
        "heures",
        "prise_en_charge",
        "reste_a_charge",
        "signal_fenetre",
    )
    list_filter = ("financeur", "etat", "modalite", "nature", "exonere_tva")
    search_fields = (
        "numero_dossier",
        "opportunite__intitule",
        "opportunite__entreprise__denomination",
        "opportunite__entreprise__siren",
    )
    autocomplete_fields = ("opportunite", "proprietaire")
    date_hierarchy = "date_debut_formation"
    readonly_fields = (
        "bareme_en_vigueur_du",
        "taux_horaire_centimes",
        "prise_en_charge_centimes",
        "reste_a_charge_centimes",
        "detail_calcul",
        "depot_ouvre_le",
        "depot_ferme_le",
        "jours_avant_cloture",
        "cree_le",
        "modifie_le",
    )
    fieldsets = (
        ("Affaire", {"fields": ("opportunite", "financeur", "etat", "proprietaire")}),
        (
            "Ce qui est vendu",
            {
                "fields": (
                    "date_debut_formation",
                    "date_fin_formation",
                    "heures",
                    "modalite",
                    "nature",
                    "nb_stagiaires",
                    "prix_ht_centimes",
                    "exonere_tva",
                ),
                "description": (
                    "Le prix est en CENTIMES d'euro HT. « Exonere de TVA » "
                    "suppose l'attestation DREETS obtenue (art. 261-4-4° a du "
                    "CGI) : sans elle, la TVA s'applique et <b>aucun financeur "
                    "ne la finance</b> — le reste a charge du client en depend "
                    "directement."
                ),
            },
        ),
        (
            "Situation du client chez le financeur",
            {
                "fields": (
                    "cfp_centimes",
                    "heures_deja_consommees",
                    "montant_deja_consomme_centimes",
                ),
                "description": (
                    "La contribution se lit sur l'attestation URSSAF. "
                    "Laissee vide, elle est traitee comme inconnue et le "
                    "calcul retient le plafond BAS, par prudence."
                ),
            },
        ),
        (
            "Calcul fige",
            {
                "fields": (
                    "bareme_en_vigueur_du",
                    "taux_horaire_centimes",
                    "prise_en_charge_centimes",
                    "reste_a_charge_centimes",
                    "detail_calcul",
                ),
                "description": (
                    "Fige au moment du calcul : un dossier garde ses "
                    "conditions meme si le financeur change ses taux ensuite."
                ),
            },
        ),
        (
            "Depot et decision",
            {
                "fields": (
                    "point_accueil",
                    "numero_dossier",
                    "depot_ouvre_le",
                    "depot_ferme_le",
                    "jours_avant_cloture",
                    "date_depot",
                    "date_decision",
                    "montant_accorde_centimes",
                    "motif_refus",
                ),
                "description": (
                    "AGEFICE : de 4 mois a 15 jours avant le demarrage, "
                    "<b>obligatoirement via un Point d'Accueil</b>. "
                    "FAFCEA : 3 mois avant, jusqu'au jour du debut."
                ),
            },
        ),
        ("Tracabilite", {"fields": ("cree_le", "modifie_le")}),
    )
    inlines = [PieceEnLigne]
    actions = ["recalculer", "preparer_les_pieces"]

    @admin.display(description="Fenetre de depot")
    def signal_fenetre(self, obj):
        restants = obj.jours_avant_cloture
        if restants is None:
            return "—"
        if obj.depot_en_retard:
            return format_html('<b style="color:#b42318">fermee depuis {} j</b>', -restants)
        if restants <= 7 and obj.etat in ("brouillon", "a_deposer"):
            return format_html('<b style="color:#b54708">{} j restants</b>', restants)
        return f"{restants} j"

    @admin.action(description="Preparer la liste des pieces attendues")
    def preparer_les_pieces(self, request, queryset):
        from apps.documents.services import preparer_les_pieces

        crees = sum(preparer_les_pieces(dossier) for dossier in queryset)
        self.message_user(request, f"{crees} piece(s) attendue(s) ajoutee(s).")

    @admin.action(description="Recalculer la prise en charge")
    def recalculer(self, request, queryset):
        from apps.financement.services import figer_calcul

        for dossier in queryset:
            figer_calcul(dossier, auteur=request.user)
        self.message_user(request, f"{queryset.count()} dossier(s) recalcule(s).")


admin_site.register(Dossier, AdminDossier)

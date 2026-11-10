"""Routes du pipeline. Le Kanban est la demonstration navigable de la phase 1."""

from django.urls import path

from apps.pipeline import vues

app_name = "pipeline"

urlpatterns = [
    path("", vues.accueil, name="accueil"),
    path("pipeline/", vues.kanban, name="kanban"),
    path("deplacer/<int:pk>/", vues.deplacer, name="deplacer"),
    path("leads/", vues.file_leads, name="leads"),
    path("financement/", vues.dossiers_financement, name="financement"),
    path("publicite/", vues.publicite, name="publicite"),
    path("sourcing/", vues.sourcing, name="sourcing"),
    path("sequences/", vues.sequences, name="sequences"),
    path("entreprises/", vues.entreprises, name="entreprises"),
    path("entreprises/<int:pk>/", vues.fiche_entreprise, name="fiche_entreprise"),
    path("leads/<int:pk>/", vues.fiche_lead, name="fiche_lead"),
    path("conformite/", vues.conformite, name="conformite"),
    path("journal/", vues.journal, name="journal"),
]

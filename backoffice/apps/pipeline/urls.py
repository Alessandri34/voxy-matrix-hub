"""Routes du pipeline. Le Kanban est la demonstration navigable de la phase 1."""

from django.urls import path

from apps.pipeline import vues

app_name = "pipeline"

urlpatterns = [
    path("", vues.kanban, name="kanban"),
    path("deplacer/<int:pk>/", vues.deplacer, name="deplacer"),
    path("leads/", vues.file_leads, name="leads"),
    path("financement/", vues.dossiers_financement, name="financement"),
]

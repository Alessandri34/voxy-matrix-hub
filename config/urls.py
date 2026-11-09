"""Routes. En phase 0, seule l'administration existe.

L'admin est remplace par une version qui exige la double authentification :
sans cela, un mot de passe seul suffirait a atteindre toutes les donnees.
"""

from django.urls import path

from apps.accounts.admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
]

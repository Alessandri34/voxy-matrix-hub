"""Routes.

L'admin est remplace par une version qui exige la double authentification :
sans cela, un mot de passe seul suffirait a atteindre toutes les donnees.

Le webhook Meta est hors de l'admin et sans session : son authentification
est la signature HMAC du corps, verifiee avant tout traitement.
"""

from django.urls import include, path

from apps.accounts.admin import admin_site
from apps.integrations.meta import vues as vues_meta

urlpatterns = [
    path("admin/", admin_site.urls),
    path("integrations/meta/webhook/", vues_meta.webhook, name="webhook-meta"),
    path("pipeline/", include("apps.pipeline.urls")),
]

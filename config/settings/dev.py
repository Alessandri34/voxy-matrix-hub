"""Developpement : base locale, erreurs visibles, aucun durcissement."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# WhiteNoise en mode manifeste exige un collectstatic prealable ; en
# developpement et sous pytest il n'a pas lieu d'etre.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# WhiteNoise previent quand STATIC_ROOT n'existe pas encore ; en
# developpement il sert les fichiers depuis les apps, sans collectstatic.
WHITENOISE_AUTOREFRESH = True

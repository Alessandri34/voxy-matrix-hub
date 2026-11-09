"""Reglages communs aux deux environnements.

Rien de secret ici : tout ce qui varie vient du .env, lu par django-environ.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-non-secret-a-remplacer")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 2FA : django_otp fournit les appareils, le middleware et la verification.
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "apps.accounts",
    "apps.audit",
    "apps.crm",
    "apps.pipeline",
    "apps.integrations",
    "apps.financement",
    "apps.sequences",
    "apps.sourcing",
    "apps.documents",
]

# Modeles dont chaque creation, modification et suppression est inscrite au
# journal d'audit (apps.audit.signaux). La liste est explicite : un modele
# surveille par defaut ferait du journal une seconde copie de la base.
AUDIT_MODELES = [
    "accounts.Utilisateur",
    "crm.Entreprise",
    "crm.Contact",
    "crm.Lead",
    "crm.Opposition",
    "pipeline.Opportunite",
    "financement.Dossier",
    "sequences.Sequence",
    "sequences.Inscription",
    "documents.Piece",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Doit suivre AuthenticationMiddleware : il pose request.user.is_verified().
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Apres AuthenticationMiddleware : il lui faut request.user.
    "apps.audit.middleware.middleware_acteur",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///" + str(BASE_DIR / "dev.sqlite3"))
}

AUTH_USER_MODEL = "accounts.Utilisateur"

# Departement de la zone commerciale. Sert a filtrer la resolution SIREN :
# l'API Recherche d'entreprises filtre sur les etablissements, donc une
# entreprise avec un etablissement ici est un prospect local meme si son
# siege est ailleurs. L'Herault est la cible annoncee du positionnement.
DEPARTEMENT_CIBLE = env("DEPARTEMENT_CIBLE", default="34")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Les dates sont stockees en UTC et affichees en Europe/Paris (regle 9 du PRD).
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Celery ---------------------------------------------------------------
CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# La resolution SIREN va sur sa propre file, servie par UN SEUL worker.
# L'API Recherche d'entreprises plafonne a 7 requetes/seconde par adresse IP
# et sa specification previent que les cloud publics l'atteignent. Une file a
# consommateur unique tient la cadence par construction ; un compteur local
# serait faux des qu'une seconde instance de worker demarre.
CELERY_TASK_ROUTES = {
    "apps.crm.taches.resoudre_siren_du_lead": {"queue": "siren"},
}

CELERY_BEAT_SCHEDULE = {
    "avancer-les-sequences": {
        "task": "apps.sequences.taches.faire_avancer_sequences",
        # Toutes les heures : le moteur refuse de toute facon d'envoyer hors
        # de la fenetre de chaque sequence, mais une etape « J+0 » doit
        # pouvoir partir dans l'heure qui suit l'inscription.
        "schedule": 3600.0,
    },
    "alerte-fenetres-de-depot": {
        "task": "apps.financement.taches.alerter_fenetres_de_depot",
        # Une fois par jour : une fenetre de depot se compte en jours, pas
        # en heures, et une alerte horaire deviendrait du bruit.
        "schedule": 86400.0,
        "kwargs": {"jours": 7},
    },
    "alerte-leads-sans-contact": {
        "task": "apps.crm.taches.alerter_leads_sans_contact",
        # Toutes les heures : un lead entre a 9 h 05 doit declencher l'alerte
        # a 10 h le lendemain au plus tard, pas 24 h apres un passage unique.
        "schedule": 3600.0,
        "kwargs": {"heures": 24},
    },
}

# --- Meta Lead Ads ---------------------------------------------------------
# Trois secrets, tous hors du depot (.env). Vides par defaut : la
# verification de signature echoue alors par defaut, ce qui est le
# comportement voulu — un webhook ouvert accepterait de faux leads.
META_APP_SECRET = env("META_APP_SECRET", default="")
META_VERIFY_TOKEN = env("META_VERIFY_TOKEN", default="")
META_PAGE_ACCESS_TOKEN = env("META_PAGE_ACCESS_TOKEN", default="")
# Version du Graph API. Citee par la documentation « Retrieving Leads »
# relevee le 09/11/2026. A relever quand Meta deprecie une version : les
# versions anciennes cessent de repondre sans preavis utile.
META_API_VERSION = env("META_API_VERSION", default="v27.0")

# --- Sequences de relance --------------------------------------------------
# 🔴 Faux par defaut, et le garde-fou est dans le CODE autant que dans la
# configuration : un moteur de relance branche par erreur sur une vraie base
# envoie des centaines de messages avant que quiconque s'en apercoive, et un
# envoi ne se reprend pas. Tant que ce reglage est faux, le moteur prepare
# les messages, les rend consultables, et n'expedie rien.
SEQUENCES_ENVOI_REEL = env.bool("SEQUENCES_ENVOI_REEL", default=False)

# --- Google Places (facultatif) --------------------------------------------
# Enrichit un prospect avec sa presence en ligne : note, nombre d'avis, site.
# ⚠️ Les conditions de Google Maps Platform n'autorisent a conserver
# durablement que le `place_id`. La note, les avis, le nom et l'adresse
# n'ont AUCUNE exception de cache : ils se demandent au moment de l'usage et
# ne doivent pas entrer en base. Le scraping de Maps est interdit.
# Sans cle, le sourcing fonctionne — avec les seules donnees publiques.
GOOGLE_PLACES_API_KEY = env("GOOGLE_PLACES_API_KEY", default="")

# --- Courriel -------------------------------------------------------------
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="")

LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "/admin/"

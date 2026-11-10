"""Production : le durcissement est ici, pas dans les reglages communs.

Caddy termine le TLS et transmet en clair a gunicorn sur le reseau interne :
d'ou SECURE_PROXY_SSL_HEADER, sans quoi Django se croirait en HTTP et
boucherait les redirections.
"""

from .base import *  # noqa: F403

DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
# Le point de sante est appele en HTTP sur 127.0.0.1, depuis le conteneur
# lui-meme (healthcheck Docker) et depuis le mandataire. Sans cette
# exemption, il recoit un 301 vers une URL HTTPS que rien ne sert sur cette
# interface : le conteneur serait marque « unhealthy » en permanence et le
# deploiement bloque. Exempter cette seule route ne reduit rien : elle ne
# porte ni session, ni cookie, ni donnee.
SECURE_REDIRECT_EXEMPT = [r"^sante/$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# --- Journalisation et remontee d'erreurs ----------------------------------
#
# **Pourquoi pas Sentry.** Une trace d'erreur de ce back-office contient des
# donnees de prospects : un nom dans une requete, un email dans un corps de
# formulaire. Les envoyer chez un tiers est une decision qui se prend, pas
# qui se subit — et elle demande au minimum `send_default_pii=False`, une
# mention dans la politique de confidentialite et un sous-traitant declare.
# Tant que le volume ne le justifie pas, Django sait faire sans : les erreurs
# partent par courriel vers ADMINS, et rien ne sort du VPS.
#
# **Pourquoi un fichier en plus de la console.** Les conteneurs sont
# redemarres ; `docker compose logs` ne remonte pas au-dela du dernier
# demarrage. Un fichier tournant garde quinze jours d'historique, ce qui est
# la duree pendant laquelle on cherche encore pourquoi un dossier est parti
# de travers.

ADMINS = [
    tuple(couple.split(":", 1))
    for couple in env.list("DJANGO_ADMINS", default=[])  # noqa: F405
    if ":" in couple
]
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)  # noqa: F405

REPERTOIRE_JOURNAUX = BASE_DIR / "journaux"  # noqa: F405
REPERTOIRE_JOURNAUX.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "complet": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        }
    },
    "filters": {
        "sauf_debug": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "complet"},
        "fichier": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(REPERTOIRE_JOURNAUX / "backoffice.log"),
            "when": "midnight",
            "backupCount": 15,
            "encoding": "utf-8",
            "formatter": "complet",
        },
        # Les erreurs arrivent dans la boite de Pierre. Sans cela, une panne
        # de production n'est connue de personne jusqu'a ce qu'un client
        # appelle.
        "courriel": {
            "class": "django.utils.log.AdminEmailHandler",
            "level": "ERROR",
            "filters": ["sauf_debug"],
            "include_html": False,
        },
    },
    "root": {"handlers": ["console", "fichier"], "level": "INFO"},
    "loggers": {
        # Les erreurs applicatives remontent par courriel ; les requetes
        # refusees (404, 400) non, elles feraient du bruit.
        "django.request": {
            "handlers": ["console", "fichier", "courriel"],
            "level": "ERROR",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "fichier", "courriel"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {"handlers": ["console", "fichier"], "level": "INFO", "propagate": False},
    },
}

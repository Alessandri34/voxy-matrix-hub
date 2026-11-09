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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

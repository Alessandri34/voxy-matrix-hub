from django.apps import AppConfig


class ConfigurationAudit(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = "Journal d'audit"

    def ready(self):
        from apps.audit.signaux import brancher

        brancher()

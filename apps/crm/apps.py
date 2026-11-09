from django.apps import AppConfig


class ConfigurationCrm(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.crm"
    verbose_name = "CRM"

    def ready(self):
        from apps.crm import signaux  # noqa: F401

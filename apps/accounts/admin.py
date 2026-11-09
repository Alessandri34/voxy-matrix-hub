"""Administration protegee par double authentification.

OTPAdminSite refuse la connexion tant que l'utilisateur n'a pas valide un
appareil : un mot de passe vole ne suffit donc pas a atteindre les donnees
des apprenants. C'est le critere de sortie n.2 de la phase 0.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import Utilisateur


class AdminSecurise(OTPAdminSite):
    site_header = "Back-office — centre de formation"
    site_title = "Back-office"
    index_title = "Administration"


admin_site = AdminSecurise(name="admin_securise")


@admin.register(Utilisateur, site=admin_site)
class UtilisateurAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Role", {"fields": ("role",)}),)


# Les appareils 2FA se gerent depuis la meme administration.
admin_site.register(TOTPDevice)
admin_site.register(StaticDevice)

"""Controle d'acces par module.

Le modele `Utilisateur` porte deja `peut_acceder(module)` : ce decorateur en
fait une barriere de vue. Sans lui, la regle existerait dans le modele et
serait oubliee dans les vues — ce qui est la facon habituelle dont une
matrice de droits devient decorative.

Deux exigences cumulees, et dans cet ordre :

1. **authentifie** — sinon on renvoie vers la connexion ;
2. **verifie par 2FA** — un mot de passe seul ne suffit pas a atteindre des
   donnees de prospects. `django_otp` pose `user.is_verified()`.

Un utilisateur connecte sans 2FA recoit 403 et non une redirection : le
rediriger en boucle vers une page de connexion ou il est deja connecte ne
lui dirait pas ce qui manque.
"""

from __future__ import annotations

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def exige_module(module: str):
    """Reserve la vue aux roles autorises sur ce module."""

    def decorateur(vue):
        @wraps(vue)
        def enveloppe(request, *args, **kwargs):
            utilisateur = getattr(request, "user", None)
            if utilisateur is None or not utilisateur.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not getattr(utilisateur, "is_verified", lambda: False)():
                raise PermissionDenied(
                    "Double authentification requise pour atteindre les donnees de prospects."
                )
            if not utilisateur.peut_acceder(module):
                raise PermissionDenied(
                    f"Le role « {utilisateur.get_role_display()} » n'a pas "
                    f"acces au module « {module} »."
                )
            return vue(request, *args, **kwargs)

        return enveloppe

    return decorateur

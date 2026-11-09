"""Utilisateurs et roles.

Le PRD fixe cinq roles. Ils vivent sur l'utilisateur plutot que dans des
groupes Django seuls : un role est une propriete de la personne, il se lit
dans une requete sans jointure, et un test peut l'affirmer en une ligne.
Les permissions fines restent celles de Django ; le role decide de ce qu'on
voit, les permissions de ce qu'on peut faire.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Administrateur"
    COMMERCIAL = "commercial", "Commercial"
    ADMINISTRATIF = "administratif", "Charge administratif"
    FORMATEUR = "formateur", "Formateur"
    LECTURE = "lecture", "Lecture seule"


# Ce que chaque role peut atteindre. Une seule table de verite : les vues et
# les tests la lisent, personne ne reecrit la regle ailleurs.
ACCES = {
    Role.ADMIN: {"crm", "pipeline", "financement", "formation", "sequences", "reporting", "audit"},
    Role.COMMERCIAL: {"crm", "pipeline", "sequences", "reporting"},
    Role.ADMINISTRATIF: {"crm", "financement", "formation", "reporting"},
    Role.FORMATEUR: {"formation"},
    Role.LECTURE: {"reporting"},
}


class Utilisateur(AbstractUser):
    role = models.CharField(
        "role",
        max_length=20,
        choices=Role.choices,
        default=Role.LECTURE,
        help_text="Decide des modules visibles. Le role le plus etroit par defaut.",
    )

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    def peut_acceder(self, module: str) -> bool:
        """Vrai si le role de cet utilisateur donne acces a ce module."""
        return module in ACCES.get(Role(self.role), set())

    @property
    def est_admin(self) -> bool:
        return self.role == Role.ADMIN

    def __str__(self) -> str:
        return f"{self.get_username()} ({self.get_role_display()})"

"""La navigation laterale, construite d'apres le role de l'utilisateur.

**Pourquoi la navigation est du code et non du gabarit.** Un menu ecrit dans
le HTML montre a tout le monde des rubriques que la moitie des roles ne peut
pas ouvrir : on clique, on prend un 403, on ne comprend pas. Ici, chaque
entree declare le module dont elle depend, et `apps.accounts.models.ACCES`
decide ce qui s'affiche. Une entree invisible est une entree inaccessible,
et reciproquement.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Entree:
    libelle: str
    route: str
    icone: str
    module: str
    #: Les routes qui doivent allumer cette entree, en plus de la sienne.
    aussi: tuple = ()
    #: Chemin direct plutot qu'un nom de route (l'administration Django).
    chemin: str = ""


@dataclass(frozen=True)
class Section:
    titre: str
    entrees: list = field(default_factory=list)


#: L'ordre compte : il suit le trajet d'un prospect, de la publicite qui le
#: fait venir jusqu'au dossier qui le finance.
NAVIGATION = [
    Section(
        "Pilotage",
        [
            Entree("Tableau de bord", "pipeline:accueil", "jauge", "reporting"),
        ],
    ),
    Section(
        "Acquisition",
        [
            Entree("Publicité", "pipeline:publicite", "megaphone", "reporting"),
            Entree("Sourcing", "pipeline:sourcing", "boussole", "crm"),
            Entree("Séquences", "pipeline:sequences", "envoi", "sequences"),
        ],
    ),
    Section(
        "Commercial",
        [
            Entree("Leads", "pipeline:leads", "entonnoir", "crm"),
            Entree("Pipeline", "pipeline:kanban", "colonnes", "pipeline"),
        ],
    ),
    Section(
        "Gestion",
        [
            Entree("Financement", "pipeline:financement", "euro", "financement"),
        ],
    ),
    Section(
        "Système",
        [
            Entree("Administration", "", "reglages", "crm", chemin="/admin/"),
        ],
    ),
]


def navigation_pour(utilisateur) -> list:
    """Les sections visibles par cet utilisateur. Une section vide disparait."""
    if utilisateur is None or not getattr(utilisateur, "is_authenticated", False):
        return []
    visibles = []
    for section in NAVIGATION:
        entrees = [e for e in section.entrees if utilisateur.peut_acceder(e.module)]
        if entrees:
            visibles.append(Section(section.titre, entrees))
    return visibles


def contexte_navigation(request):
    """Processeur de contexte : rend la navigation disponible partout."""
    return {"navigation": navigation_pour(getattr(request, "user", None))}

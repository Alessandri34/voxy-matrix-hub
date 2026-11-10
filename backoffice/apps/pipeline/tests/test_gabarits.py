"""Les gabarits et le squelette : deux defauts que le CSS ne signale jamais.

Le CSS echoue en silence. Une classe inconnue ne leve rien, elle ne fait
rien ; un selecteur redefini ne leve rien non plus, il ecrase. Les deux se
sont produits ici le meme jour, sur la meme page :

1. `conformite.html` posait `class="kpis"`, `class="etiquette"` et
   `class="detail"` — trois noms qui n'existent nulle part. Les cartes de
   chiffres s'empilaient en pleine largeur au lieu de former une rangee.
2. Le meme gabarit redefinissait `.barre`, qui est la **barre de titre du
   squelette**. Sur cette page seulement, l'en-tete perdait sa mise en page.

Aucun test fonctionnel ne pouvait le voir : les deux pages renvoyaient 200.
Ces deux tests lisent le CSS comme du texte, ce qui est grossier, mais
suffit a attraper exactement ces deux fautes.
"""

from __future__ import annotations

import re
from pathlib import Path

GABARITS = Path(__file__).resolve().parents[3] / "templates" / "pipeline"
SQUELETTE = GABARITS / "base.html"

#: Les classes que le squelette possede et qu'une page ne doit pas redefinir.
#: Une page qui les redefinit casse la mise en page partagee, chez elle seule.
STRUCTURELLES = {
    "rail",
    "zone",
    "barre",
    "marque",
    "logo",
    "entrees",
    "pied-rail",
    "bouton-rail",
    "cartes",
    "kpi",
    "panneau",
    "defile",
    "badge",
    "avis",
    "vide",
    "sous",
}


def _sans_commentaires(css: str) -> str:
    """Un commentaire CSS cite souvent la classe qu'il explique."""
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def _bloc_style(source: str) -> str:
    bloc = re.search(r"{%\s*block style\s*%}(.*?){%\s*endblock\s*%}", source, re.S)
    return _sans_commentaires(bloc.group(1)) if bloc else ""


def _classes_definies(css: str) -> set[str]:
    return set(re.findall(r"\.([a-zA-Z][\w-]*)", _sans_commentaires(css)))


def _classes_utilisees(source: str) -> set[str]:
    utilisees: set[str] = set()
    for attribut in re.findall(r'class="([^"]*)"', source):
        # Un `class="{% if … %}actif{% endif %}"` : on garde les mots nus.
        nettoye = re.sub(r"{[%{].*?[%}]}", " ", attribut)
        utilisees.update(mot for mot in nettoye.split() if re.fullmatch(r"[a-zA-Z][\w-]*", mot))
    return utilisees


def _pages() -> list[Path]:
    return sorted(p for p in GABARITS.glob("*.html") if p.name != "base.html")


def test_aucune_page_ne_redefinit_une_classe_du_squelette():
    """Non-regression.

    `conformite.html` redefinissait `.barre` pour ses lignes de comptage.
    `.barre` est la barre de titre : la page perdait son en-tete, et rien
    ne le signalait.
    """
    for page in _pages():
        definies = _classes_definies(_bloc_style(page.read_text()))
        collisions = definies & STRUCTURELLES
        assert not collisions, (
            f"{page.name} redefinit {sorted(collisions)}, qui appartient au squelette. "
            "Renommer la classe de la page : le squelette est partage."
        )


def test_aucune_classe_inventee_dans_les_pages():
    """Non-regression.

    `class="kpis"` au lieu de `class="cartes"` : aucune erreur, aucune
    mise en page. Une classe doit etre definie, soit par le squelette, soit
    par le bloc `style` de la page qui s'en sert.
    """
    connues = _classes_definies(SQUELETTE.read_text())
    for page in _pages():
        source = page.read_text()
        autorisees = connues | _classes_definies(_bloc_style(source))
        inconnues = _classes_utilisees(source) - autorisees
        assert not inconnues, (
            f"{page.name} utilise {sorted(inconnues)}, qui n'est defini ni par le "
            "squelette ni par la page. Une classe inconnue ne fait rien et ne "
            "leve rien."
        )


def test_aucun_identifiant_en_double_entre_une_page_et_le_squelette():
    """Non-regression.

    Le Kanban posait `id="rail"` sur sa bande de colonnes, alors que le
    squelette le porte deja sur la barre laterale. `getElementById` rend le
    premier venu : le bouton de repli de la barre pouvait agir sur l'un ou
    sur l'autre selon l'ordre du document. Un identifiant en double est du
    HTML invalide qu'aucun navigateur ne signale.
    """
    identifiants_squelette = set(re.findall(r'id="([\w-]+)"', SQUELETTE.read_text()))
    for page in _pages():
        doublons = set(re.findall(r'id="([\w-]+)"', page.read_text())) & identifiants_squelette
        assert not doublons, f"{page.name} reutilise l'identifiant {sorted(doublons)} du squelette."

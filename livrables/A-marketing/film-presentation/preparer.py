"""Prepare les elements de marque du film, a partir des logos du site.

- decoupe le sigle en ses trois barres (une image par barre, meme cadre),
  pour pouvoir les animer une a une sans redessiner la marque ;
- isole le mot « VFORMATIONS » du logo complet ;
- fabrique un grain fixe, pose en surimpression : sans lui, les degrades
  sombres se cassent en bandes a l'encodage H.264 (8 bits).

Rien n'est retouche : les images produites sont des decoupes exactes des
fichiers de `livrables/C-site/img/`.
"""

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ICI = Path(__file__).resolve().parent
SITE = ICI.parent.parent / "C-site" / "img"
SORTIE = ICI / "ressources"
SORTIE.mkdir(exist_ok=True)


def barres(couleur: str) -> None:
    sigle = Image.open(SITE / f"logo-mark-{couleur}.png").convert("RGBA")
    alpha = np.array(sigle)[:, :, 3] > 40
    etiquettes, nombre = ndimage.label(alpha)
    # Les trois plus grandes composantes, de gauche a droite.
    tailles = ndimage.sum(alpha, etiquettes, range(1, nombre + 1))
    gardees = sorted(np.argsort(tailles)[-3:] + 1, key=lambda e: np.where(etiquettes == e)[1].mean())
    assert len(gardees) == 3, "le sigle doit compter trois barres"
    pixels = np.array(sigle)
    for rang, etiquette in enumerate(gardees, start=1):
        calque = pixels.copy()
        # Dilatation d'un pixel : garde le lisse du bord de chaque barre.
        masque = ndimage.binary_dilation(etiquettes == etiquette, iterations=2)
        calque[~masque] = 0
        Image.fromarray(calque).save(SORTIE / f"sigle-{couleur}-{rang}.png")
    print(f"sigle {couleur} : 3 barres, cadre {sigle.size}")


def mot(couleur: str) -> None:
    logo = Image.open(SITE / f"logo-vformations-{couleur}.png").convert("RGBA")
    alpha = np.array(logo)[:, :, 3] > 40
    lignes = alpha.any(axis=1)
    # Le mot est le dernier bloc de lignes pleines, sous le sigle.
    pleines = np.where(lignes)[0]
    coupures = np.where(np.diff(pleines) > 6)[0]
    haut = pleines[coupures[-1] + 1] if len(coupures) else pleines[0]
    bas = pleines[-1]
    colonnes = np.where(alpha[haut : bas + 1].any(axis=0))[0]
    boite = (max(colonnes[0] - 4, 0), max(haut - 4, 0), min(colonnes[-1] + 5, logo.width), min(bas + 5, logo.height))
    logo.crop(boite).save(SORTIE / f"mot-{couleur}.png")
    print(f"mot {couleur} : {boite}")


def grain() -> None:
    alea = np.random.default_rng(34)
    bruit = alea.normal(128, 26, (540, 960)).clip(0, 255).astype(np.uint8)
    Image.fromarray(bruit, "L").save(SORTIE / "grain.png")


if __name__ == "__main__":
    for couleur in ("blue", "white"):
        barres(couleur)
        mot(couleur)
    grain()

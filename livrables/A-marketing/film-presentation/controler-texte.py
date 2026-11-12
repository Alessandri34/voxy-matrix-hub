#!/usr/bin/env python3
"""Relit tout le texte a l'ecran du film, avant de le rendre.

Un film publicitaire d'organisme de formation est tenu par les memes regles
que les scripts : pas de « gratuit », pas de « finance a 100 % », pas de
resultat promis, pas de prix, pas de « formation obligatoire ». Les listes
reprennent celles de `../controle-scripts.py`, qui ne s'importe pas (il lit
un fichier des son chargement).

S'y ajoutent deux controles propres a l'image :
- **pas de logo Qualiopi**. La marque est interdite « dans une publicite pour
  une action de formation en particulier » (CLAUDE.md §8sexies). La mention
  ecrite, elle, est permise, a condition de porter la categorie d'action ;
- **pas de montant en euros** : aucun prix n'est publie (decision D9).

    python3 controler-texte.py        code de sortie 1 s'il y a une erreur
"""

import html
import re
import sys
import unicodedata
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "film.html"

BANNIES = ["100 % finance", "100% finance", "sans reste a charge", "machine a cash", "paravent",
           "sans depenser un centime", "ne vous coute rien", "entierement finance", "formation offerte",
           "reste a charge nul", "gratuit", "offert", "formation obligatoire", "obligatoire"]  # fmt: skip
PROMESSES = [r"\bgaranti", r"vous (?:gagnerez|aurez|obtiendrez|doublerez)", r"\+\s*\d+\s*%", r"x\s*\d+\s+(?:vos|votre|plus)",
             r"(?:premiere|1re) place", r"(?:plus|davantage) de (?:clients|chiffre|revenus?|ventes)\b",
             r"(?:augmente|fera augmenter|fait augmenter) (?:votre|ton) (?:ca|chiffre)", r"(?:usine|machine) a ",
             r"\bdomination\b", r"\btop 1 ?%", r"\bhack\b"]  # fmt: skip


def plat(texte: str) -> str:
    return unicodedata.normalize("NFD", texte.lower()).encode("ascii", "ignore").decode()


def texte_a_l_ecran(source: str) -> str:
    corps = source[source.index("<body") : source.index("<script src=")]
    corps = re.sub(r"<!--.*?-->|<svg.*?</svg>", " ", corps, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", corps))).strip()


def controler() -> list[str]:
    source = SOURCE.read_text(encoding="utf8")
    texte = texte_a_l_ecran(source)
    bas = plat(texte)
    erreurs = [f"formulation bannie : « {m} »" for m in BANNIES if m in bas]
    erreurs += [f"promesse de resultat : motif « {motif} »" for motif in PROMESSES if re.search(motif, bas)]
    if "€" in texte or re.search(r"\b\d+\s*euros?\b", bas):
        erreurs.append("un montant en euros apparait a l'ecran (aucun prix n'est publie : D9)")
    if re.search(r"qualiopi[\w-]*\.(?:png|svg|jpg)|mag-qualiopi", source, re.I):
        erreurs.append("le logo Qualiopi (ou une image qui le montre) est utilise dans le film")
    if "qualiopi" in bas and "au titre des actions de formation" not in bas:
        erreurs.append("Qualiopi est cite sans la categorie d'action (« au titre des actions de formation »)")
    return erreurs


if __name__ == "__main__":
    erreurs = controler()
    mots = len(texte_a_l_ecran(SOURCE.read_text(encoding="utf8")).split())
    for e in erreurs:
        print("ERREUR", e)
    print(f"{mots} mots a l'ecran relus · {len(erreurs)} erreur(s)")
    sys.exit(1 if erreurs else 0)

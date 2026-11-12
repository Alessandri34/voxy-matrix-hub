#!/usr/bin/env python3
"""Recupere les bruitages de la banque, un par un, dans `sons/`.

    python3 telecharger-sons.py

Pourquoi ce script existe. La licence des sons (Mixkit Sound Effects Free
License, lue le 12/11/2026) permet de les utiliser dans une publicite, sans
credit, mais interdit de les redistribuer seuls « ou avec des fichiers
source ». Ce depot est public : y deposer les fichiers serait les
redistribuer. Ils restent donc hors Git, et ce script les recupere.

⚠️ Les conditions d'utilisation de Mixkit interdisent le telechargement
**en masse** par script (« use scripts or bots to mass download Items »).
Ce script ne recupere que les douze sons nommes dans `sons/banque.json`,
une fois, avec une pause entre chacun. La lecture stricte reste de les
telecharger a la main depuis la page de chaque son : `banque.json` donne la
page et le titre. Les deux chemins produisent les memes fichiers, que
l'empreinte verifie.
"""

import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent / "sons"
TABLE = json.loads((DOSSIER / "banque.json").read_text())


def recuperer(adresse: str) -> bytes:
    requete = urllib.request.Request(adresse, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return reponse.read()


def principal() -> int:
    erreurs = 0
    for cle, son in TABLE["sons"].items():
        fichier = DOSSIER / son["local"]
        if fichier.exists():
            contenu, origine = fichier.read_bytes(), "deja la"
        else:
            contenu, origine = recuperer(son["fichier"]), "recupere"
            time.sleep(1.5)
        if contenu[:4] != b"RIFF":
            print(f"ERREUR  {cle:15} la source n'a pas rendu un fichier WAV ({son['fichier']})")
            erreurs += 1
            continue
        if hashlib.sha256(contenu).hexdigest() != son["sha256"]:
            # Un son remplace sous le meme nom n'est plus celui qui a ete choisi et mesure.
            print(f"ERREUR  {cle:15} l'empreinte ne correspond pas : fichier change a la source. Non enregistre.")
            erreurs += 1
            continue
        fichier.write_bytes(contenu)
        print(f"ok      {cle:15} {son['titre']:36} {len(contenu) // 1024:5} Ko  ({origine})")
    print(f"\n{TABLE['banque']} — {TABLE['licence']} — {TABLE['url_licence']} (lue le {TABLE['lue_le']})")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(principal())

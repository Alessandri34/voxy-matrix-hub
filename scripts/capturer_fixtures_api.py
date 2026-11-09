#!/usr/bin/env python3
"""Capture des reponses reelles de l'API Recherche d'entreprises comme fixtures.

A relancer quand l'API change de forme : des fixtures captees contiennent les
champs tels que l'API les envoie, y compris ceux qu'on n'avait pas prevus —
et c'est precisement la qu'un client se casse.

    python scripts/capturer_fixtures_api.py

Les fichiers vont dans `apps/crm/tests/fixtures/`. La limite de debit de
l'API est de 7 requetes/seconde par IP : le script attend entre deux appels.
"""

from __future__ import annotations

import json
import pathlib
import sys
import time

import httpx

URL_BASE = "https://recherche-entreprises.api.gouv.fr"
AGENT = "vformations-backoffice/1.0 (+https://vformations.fr)"
DOSSIER = pathlib.Path(__file__).resolve().parent.parent / "apps/crm/tests/fixtures"

#: Chaque cas couvre une branche du code de resolution.
CAS = {
    # Un seul candidat net : le chemin nominal.
    "un_resultat_local": {
        "q": "ENSANTE",
        "departement": "34",
        "etat_administratif": "A",
        "per_page": 10,
        "limite_matching_etablissements": 3,
    },
    # Un nom tres partage : plusieurs candidats comparables, donc « ambigu ».
    "plusieurs_homonymes": {
        "q": "le comptoir",
        "departement": "34",
        "etat_administratif": "A",
        "per_page": 5,
        "limite_matching_etablissements": 3,
    },
    # Une entreprise opposee a la prospection commerciale.
    "avec_opposition": {"q": "503120578", "per_page": 5, "limite_matching_etablissements": 3},
    # Recherche sans resultat.
    "aucun_resultat": {"q": "zzqxwvu entreprise inexistante", "departement": "34", "per_page": 10},
}


def appeler(client: httpx.Client, params: dict, essais: int = 4) -> dict | None:
    for tentative in range(essais):
        try:
            reponse = client.get("/search", params=params)
            if reponse.status_code == 200:
                return reponse.json()
            print(f"    HTTP {reponse.status_code}", file=sys.stderr)
        except httpx.RequestError as erreur:
            print(f"    reseau : {type(erreur).__name__}", file=sys.stderr)
        time.sleep(1.5 * (tentative + 1))
    return None


def main() -> int:
    DOSSIER.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(
        base_url=URL_BASE,
        timeout=httpx.Timeout(connect=5, read=20, write=5, pool=5),
        headers={"User-Agent": AGENT},
    )
    echecs = 0
    try:
        for nom, params in CAS.items():
            donnees = appeler(client, params)
            if donnees is None:
                print(f"ECHEC  {nom}")
                echecs += 1
                continue
            if nom == "plusieurs_homonymes":
                donnees["results"] = donnees.get("results", [])[:5]
            (DOSSIER / f"{nom}.json").write_text(
                json.dumps(donnees, ensure_ascii=False, indent=1), encoding="utf8"
            )
            resultats = donnees.get("results") or []
            print(
                f"OK     {nom:22} {donnees.get('total_results', 0):>6} resultats, "
                f"{len(resultats)} conserve(s)"
            )
            time.sleep(0.5)
    finally:
        client.close()
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())

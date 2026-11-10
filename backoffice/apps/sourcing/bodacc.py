"""Veille BODACC : les creations d'entreprise comme signal de prospection.

**Pourquoi cette source vaut mieux qu'un fichier achete.** Une entreprise
qui vient d'etre immatriculee, c'est un dirigeant qui n'a encore ni site, ni
avis, ni fichier clients — et qui a des droits a formation ouverts. C'est le
moment precis ou l'offre de VFormations repond a un besoin reel, et non le
moment ou on derange quelqu'un d'installe.

**Source**, verifiee le 10/11/2026 :
`https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records`
publiee par la DILA. Libre d'acces, sans cle, sans quota annonce.
51 358 443 annonces au total ; 1 667 creations dans l'Herault depuis le
1er octobre 2026, soit une quarantaine par jour.

**Deux etapes, et c'est le point de conception.** Le BODACC donne
l'EVENEMENT (quelqu'un vient de s'immatriculer) mais pas la qualification :
les premiers resultats d'une requete heraultaise sont des societes civiles
immobilieres, qui ne sont pas des clients. C'est l'API Recherche
d'entreprises qui donne le NAF, l'effectif et — surtout — l'opposition a la
prospection. Le BODACC declenche, l'autre qualifie.

⚠️ **Le BODACC ne dit rien de l'opposition a la prospection.** Une annonce
publiee au Journal officiel est publique ; cela ne vaut pas consentement a
etre demarche. Tout prospect issu de cette veille passe donc par la meme
qualification que le reste, et les opposees sont ecartees.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import date, timedelta

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

URL = (
    "https://bodacc-datadila.opendatasoft.com/api/explore/v2.1"
    "/catalog/datasets/annonces-commerciales/records"
)
AGENT = "vformations-backoffice/1.0 (+https://vformations.fr)"
DELAIS = httpx.Timeout(connect=10.0, read=40.0, write=10.0, pool=10.0)

#: L'API renvoie 100 enregistrements au maximum par appel.
PAR_PAGE = 100

#: Formes juridiques sans interet pour une offre de formation
#: professionnelle : des structures patrimoniales, pas des entreprises qui
#: exploitent. Les ecarter ici evite autant d'appels de qualification.
FORMES_ECARTEES = (
    "civile immobili",
    "syndicat de copropri",
    "association",
    "fonds de dotation",
)


class ErreurBodacc(RuntimeError):
    """Le BODACC n'a pas repondu utilement. Se reessaie."""


@dataclass
class Immatriculation:
    """Une creation d'entreprise, telle que le BODACC l'annonce."""

    siren: str
    denomination: str
    ville: str
    code_postal: str
    departement: str
    date_parution: str
    forme_juridique: str
    identifiant_annonce: str
    url: str

    @property
    def ecartee_par_forme(self) -> bool:
        forme = (self.forme_juridique or "").lower()
        return any(motif in forme for motif in FORMES_ECARTEES)


@dataclass
class Veille:
    """Ce qu'une passe de veille a trouve."""

    immatriculations: list = field(default_factory=list)
    lues: int = 0
    ecartees_forme: int = 0
    sans_siren: int = 0
    total_annonce: int = 0
    erreurs: list = field(default_factory=list)

    def resume(self) -> str:
        return "\n".join(
            [
                f"{self.total_annonce} creation(s) annoncee(s) sur la periode",
                f"  {self.lues} lue(s)",
                f"  {len(self.immatriculations)} retenue(s)",
                f"  {self.ecartees_forme} ecartee(s) — forme juridique sans objet",
                f"  {self.sans_siren} sans SIREN exploitable",
            ]
            + ([f"  {len(self.erreurs)} erreur(s) : {self.erreurs[0]}"] if self.erreurs else [])
        )


def _forme(enregistrement: dict) -> str:
    """La forme juridique, enfouie dans un JSON encode en chaine."""
    brut = enregistrement.get("listepersonnes")
    if not brut:
        return ""
    try:
        personnes = json.loads(brut).get("personne")
    except (TypeError, ValueError):
        return ""
    if isinstance(personnes, list):
        personnes = personnes[0] if personnes else {}
    if not isinstance(personnes, dict):
        return ""
    return str(personnes.get("formeJuridique") or "")


def _siren(enregistrement: dict) -> str:
    """Le registre porte le SIREN, avec et sans espaces."""
    from apps.crm.normalisation import normaliser_siren

    for valeur in enregistrement.get("registre") or []:
        propre = normaliser_siren(str(valeur))
        if propre:
            return propre
    return ""


#: Un service public gratuit coupe parfois une connexion sans raison. Trois
#: tentatives a retardement croissant suffisent, et evitent qu'une commande
#: lancee a la main echoue sur un alea reseau — la tache Celery, elle, a sa
#: propre politique de reprise par-dessus.
TENTATIVES = 3

#: Secondes d'attente de base entre deux tentatives, multipliees par le rang
#: de la tentative. Mises a zero dans les tests, ou attendre ne verifie rien.
RETARD_REESSAI = 1.5


def appeler(parametres: dict, *, client: httpx.Client | None = None) -> dict:
    """Un appel, avec quelques reessais sur aleas reseau."""
    ferme = client is None
    client = client or httpx.Client(timeout=DELAIS, headers={"User-Agent": AGENT})
    derniere = ""
    try:
        for tentative in range(TENTATIVES):
            try:
                reponse = client.get(URL, params=parametres)
            except httpx.RequestError as erreur:
                derniere = f"appel impossible : {erreur}"
                logger.info("BODACC injoignable (tentative %s) : %s", tentative + 1, erreur)
                time.sleep(RETARD_REESSAI * (tentative + 1))
                continue

            if reponse.status_code == 200:
                try:
                    return reponse.json()
                except ValueError as erreur:
                    raise ErreurBodacc("reponse illisible (JSON invalide)") from erreur

            # 4xx : la requete est fautive, la reessayer ne changera rien.
            if 400 <= reponse.status_code < 500:
                raise ErreurBodacc(
                    f"le BODACC a refuse la requete ({reponse.status_code}) : {reponse.text[:200]}"
                )
            derniere = f"le BODACC a repondu {reponse.status_code}"
            time.sleep(RETARD_REESSAI * (tentative + 1))
    finally:
        if ferme:
            client.close()

    raise ErreurBodacc(f"{derniere} (apres {TENTATIVES} tentatives)")


def veiller(
    *,
    departement: str = "",
    depuis: date | None = None,
    pages_max: int = 5,
    client: httpx.Client | None = None,
) -> Veille:
    """Les immatriculations publiees depuis une date, dans un departement."""
    departement = departement or getattr(settings, "DEPARTEMENT_CIBLE", "34")
    depuis = depuis or (date.today() - timedelta(days=7))
    veille = Veille()
    vus: set[str] = set()

    for page in range(pages_max):
        parametres = {
            "where": (
                f'familleavis="creation" AND numerodepartement="{departement}" '
                f"AND dateparution>=date'{depuis.isoformat()}'"
            ),
            "limit": PAR_PAGE,
            "offset": page * PAR_PAGE,
            "order_by": "dateparution DESC",
        }
        try:
            donnees = appeler(parametres, client=client)
        except ErreurBodacc as erreur:
            veille.erreurs.append(f"page {page + 1} : {erreur}")
            break

        veille.total_annonce = donnees.get("total_count") or veille.total_annonce
        resultats = donnees.get("results") or []
        if not resultats:
            break

        for enregistrement in resultats:
            veille.lues += 1
            siren = _siren(enregistrement)
            if not siren:
                veille.sans_siren += 1
                continue
            if siren in vus:
                continue
            vus.add(siren)

            immat = Immatriculation(
                siren=siren,
                denomination=(enregistrement.get("commercant") or "").strip(),
                ville=(enregistrement.get("ville") or "").strip(),
                code_postal=(enregistrement.get("cp") or "").strip(),
                departement=str(enregistrement.get("numerodepartement") or ""),
                date_parution=str(enregistrement.get("dateparution") or ""),
                forme_juridique=_forme(enregistrement),
                identifiant_annonce=str(enregistrement.get("id") or ""),
                url=str(enregistrement.get("url_complete") or ""),
            )
            if immat.ecartee_par_forme:
                veille.ecartees_forme += 1
                continue
            veille.immatriculations.append(immat)

        if len(resultats) < PAR_PAGE:
            break
        # Courtoisie envers un service public gratuit : rien n'oblige a
        # l'interroger aussi vite que la machine le permet.
        time.sleep(0.3)

    return veille

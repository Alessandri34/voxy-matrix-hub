"""Client du Graph API, pour aller chercher ce que le webhook ne dit pas.

Fait verifie sur la documentation officielle (guide « Retrieving Leads »,
releve le 09/11/2026) : **la charge utile du webhook ne contient aucune
reponse du prospect**, seulement `leadgen_id`, `page_id`, `form_id`,
`adgroup_id`, `ad_id` et `created_time`. Les reponses se recuperent par

    GET https://graph.facebook.com/<version>/<LEAD_ID>?access_token=<jeton>

qui renvoie `created_time`, `id`, `ad_id`, `form_id` et `field_data`, une
liste d'objets `{"name": ..., "values": [...]}`.

Permissions requises, citees par la documentation : `leads_retrieval` et
`pages_manage_ads`, a soumettre en App Review. Un jeton de Page est
recommande plutot qu'un jeton d'utilisateur.

⚠️ **Point a confirmer avec un vrai jeton** : les noms de campagne et
d'ensemble de publicites ne sont PAS dans le webhook. Ils demandent un appel
supplementaire sur le noeud `Ad` avec expansion de champs. La forme employee
ici (`fields=name,campaign{id,name},adset{id,name}`) est celle de la
Marketing API, mais elle n'a pas pu etre verifiee sur la reference officielle
depuis cette session — la documentation de Meta refuse les clients non
navigateurs. Le code degrade proprement : si l'enrichissement echoue, le lead
entre quand meme, avec ses identifiants mais sans les libelles.
"""

from __future__ import annotations

import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

URL_BASE = "https://graph.facebook.com"
DELAIS = httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)

#: Champs standard d'un formulaire Meta, vers nos champs de lead. Les
#: questions personnalisees ne sont pas traduites : elles restent dans le
#: payload d'origine, qui est conserve entier.
CORRESPONDANCES = {
    "full_name": "nom_declare",
    # « first_name » n'est PAS ici : il est traite plus bas avec
    # « last_name ». Le mettre ici remplissait `nom_declare` avec le seul
    # prenom, apres quoi le recollage ne s'executait plus et le nom de
    # famille etait perdu.
    "email": "email_declare",
    "phone_number": "telephone_declare",
    "company_name": "entreprise_declaree",
    "job_title": "fonction_declaree",
}


class ErreurGraph(RuntimeError):
    """Le Graph API n'a pas repondu utilement. Rejouable."""


def _version() -> str:
    return getattr(settings, "META_API_VERSION", "v27.0")


def _jeton() -> str:
    return getattr(settings, "META_PAGE_ACCESS_TOKEN", "")


def appeler(chemin: str, parametres: dict, *, client: httpx.Client | None = None) -> dict:
    jeton = _jeton()
    if not jeton:
        raise ErreurGraph(
            "aucun jeton de Page configure (META_PAGE_ACCESS_TOKEN). Le lead "
            "est conserve : il sera rejoue des que le jeton sera en place."
        )
    ferme = client is None
    client = client or httpx.Client(base_url=URL_BASE, timeout=DELAIS)
    try:
        reponse = client.get(
            f"/{_version()}/{chemin.lstrip('/')}", params={**parametres, "access_token": jeton}
        )
    except httpx.RequestError as erreur:
        raise ErreurGraph(f"appel a {chemin} impossible : {erreur}") from erreur
    finally:
        if ferme:
            client.close()

    if reponse.status_code != 200:
        # Le message d'erreur de Meta est utile et ne contient pas le jeton,
        # qui voyage en parametre : il est donc sur a journaliser.
        raise ErreurGraph(f"Graph a repondu {reponse.status_code} : {reponse.text[:300]}")
    try:
        return reponse.json()
    except ValueError as erreur:
        raise ErreurGraph("reponse illisible (JSON invalide)") from erreur


def recuperer_lead(leadgen_id: str, *, client: httpx.Client | None = None) -> dict:
    """Les reponses du prospect, que le webhook ne transmet pas."""
    return appeler(leadgen_id, {}, client=client)


def recuperer_contexte_publicite(ad_id: str, *, client: httpx.Client | None = None) -> dict:
    """Les libelles de campagne et d'ensemble, absents du webhook.

    Sans eux, on connait le cout par lead mais pas le cout par inscrit — qui
    est la seule mesure sur laquelle decider d'augmenter un budget.
    """
    if not ad_id:
        return {}
    return appeler(ad_id, {"fields": "name,campaign{id,name},adset{id,name}"}, client=client)


def aplatir_field_data(field_data: list) -> dict:
    """`[{"name": "email", "values": ["a@b.fr"]}]` devient `{"email": "a@b.fr"}`.

    Une valeur multiple (case a cocher multiple) est jointe par « ; » plutot
    que tronquee : perdre silencieusement la deuxieme reponse d'un prospect
    serait pire que de la presenter mal.
    """
    plat = {}
    for champ in field_data or []:
        nom = (champ.get("name") or "").strip()
        if not nom:
            continue
        valeurs = [str(v) for v in (champ.get("values") or []) if v not in (None, "")]
        plat[nom] = " ; ".join(valeurs)
    return plat


def vers_donnees_lead(reponse_lead: dict, contexte: dict, evenement: dict) -> dict:
    """Assemble ce que les trois sources disent en un jeu de champs de lead."""
    plat = aplatir_field_data(reponse_lead.get("field_data"))
    campagne = (contexte or {}).get("campaign") or {}
    ensemble = (contexte or {}).get("adset") or {}

    donnees = {
        "source": "meta_lead_ads",
        "meta_leadgen_id": str(evenement.get("leadgen_id") or reponse_lead.get("id") or ""),
        "meta_formulaire_id": str(evenement.get("form_id") or reponse_lead.get("form_id") or ""),
        "meta_publicite_id": str(evenement.get("ad_id") or reponse_lead.get("ad_id") or ""),
        "meta_publicite_nom": (contexte or {}).get("name") or "",
        "meta_campagne_id": str(campagne.get("id") or ""),
        "meta_campagne_nom": campagne.get("name") or "",
        "meta_ensemble_id": str(ensemble.get("id") or evenement.get("adgroup_id") or ""),
        "meta_ensemble_nom": ensemble.get("name") or "",
        # Le payload d'origine garde TOUT : les questions personnalisees du
        # formulaire, et ce que Meta ajoutera plus tard sans nous le dire.
        "payload_origine": {
            "evenement_webhook": evenement,
            "reponse_graph": reponse_lead,
            "contexte_publicite": contexte,
        },
    }
    for nom_meta, champ in CORRESPONDANCES.items():
        if plat.get(nom_meta) and champ in {
            "nom_declare",
            "email_declare",
            "telephone_declare",
            "entreprise_declaree",
        }:
            donnees.setdefault(champ, plat[nom_meta])

    # « first_name » + « last_name » quand le formulaire ne demande pas le
    # nom complet : les recoller plutot que de n'en garder qu'un. Un
    # formulaire qui ne demande que le prenom laisse donc le prenom seul,
    # ce qui est juste.
    if not donnees.get("nom_declare"):
        morceaux = [plat.get("first_name", ""), plat.get("last_name", "")]
        recolle = " ".join(m for m in morceaux if m).strip()
        if recolle:
            donnees["nom_declare"] = recolle

    # Les reponses libres du formulaire, reunies en message lisible.
    connus = set(CORRESPONDANCES) | {"first_name", "last_name"}
    libres = [f"{nom} : {valeur}" for nom, valeur in plat.items() if nom not in connus]
    if libres:
        donnees["message"] = "\n".join(libres)
    return donnees

"""Enrichissement Google Places — et ce qu'il est interdit d'en garder.

**Pourquoi ce module ne stocke presque rien.** Les conditions de Google Maps
Platform, relevees le 09/11/2026, n'autorisent a conserver durablement que le
`place_id`. Les coordonnees peuvent etre mises en cache **30 jours** au plus.
Le nom affiche, l'adresse, la note et les avis **n'ont aucune exception de
cache** : ils doivent etre redemandes. Et les conditions interdisent
explicitement d'extraire ou de scraper le contenu de Maps hors des Services.

Ce module interroge donc l'API **au moment ou on en a besoin**, rend les
signaux de qualification a l'ecran, et n'inscrit en base que le `place_id`.
C'est moins pratique qu'un fichier, et c'est la seule forme defendable.

**Pourquoi s'en donner la peine.** Ces signaux sont les meilleurs arguments
de VFormations : une entreprise avec douze avis et aucun site web est
exactement la cible de l'offre « visibilite locale » et de l'offre « site
internet ». L'API Recherche d'entreprises, elle, ne dit rien de la presence
en ligne.

⚠️ Demande une cle Google Cloud facturable (`GOOGLE_PLACES_API_KEY`). Sans
elle, le module renvoie None et le dit — il ne se rabat sur aucun
contournement.

Documentation : https://developers.google.com/maps/documentation/places/web-service/policies
"""

from __future__ import annotations

import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

URL = "https://places.googleapis.com/v1/places:searchText"
DELAIS = httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)

#: Le SEUL champ que les conditions autorisent a conserver durablement.
CHAMP_STOCKABLE = "place_id"

#: Champs demandes. Tout le reste est hors de ce dont on a besoin, et chaque
#: champ demande est facture.
CHAMPS = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.rating",
        "places.userRatingCount",
        "places.websiteUri",
        "places.nationalPhoneNumber",
        "places.businessStatus",
    ]
)


class PlacesIndisponible(RuntimeError):
    """Pas de cle, ou l'API n'a pas repondu."""


def qualifier(nom: str, commune: str = "", *, client: httpx.Client | None = None) -> dict | None:
    """Les signaux de presence en ligne d'un etablissement.

    ⚠️ Le resultat est a usage **immediat**. Seul `place_id` peut etre
    conserve ; la note, le nombre d'avis et le site ne doivent pas entrer en
    base. Les afficher a l'ecran au moment de la qualification est conforme ;
    les stocker ne l'est pas.
    """
    cle = getattr(settings, "GOOGLE_PLACES_API_KEY", "")
    if not cle:
        raise PlacesIndisponible(
            "aucune cle GOOGLE_PLACES_API_KEY configuree. L'enrichissement "
            "Places est facultatif : le sourcing fonctionne sans lui, avec "
            "les seules donnees de l'API Recherche d'entreprises."
        )
    requete = " ".join(part for part in (nom, commune) if part).strip()
    if not requete:
        return None

    ferme = client is None
    client = client or httpx.Client(timeout=DELAIS)
    try:
        reponse = client.post(
            URL,
            json={"textQuery": requete, "languageCode": "fr", "regionCode": "FR"},
            headers={"X-Goog-Api-Key": cle, "X-Goog-FieldMask": CHAMPS},
        )
    except httpx.RequestError as erreur:
        raise PlacesIndisponible(f"appel impossible : {erreur}") from erreur
    finally:
        if ferme:
            client.close()

    if reponse.status_code != 200:
        raise PlacesIndisponible(f"Places a repondu {reponse.status_code}")

    lieux = (reponse.json() or {}).get("places") or []
    if not lieux:
        return None
    lieu = lieux[0]
    return {
        # Conservable.
        "place_id": lieu.get("id", ""),
        # À usage immediat seulement — ne pas ecrire en base.
        "nom": (lieu.get("displayName") or {}).get("text", ""),
        "adresse": lieu.get("formattedAddress", ""),
        "note": lieu.get("rating"),
        "nb_avis": lieu.get("userRatingCount"),
        "site_web": lieu.get("websiteUri", ""),
        "telephone": lieu.get("nationalPhoneNumber", ""),
        "statut": lieu.get("businessStatus", ""),
    }


def argument_commercial(signaux: dict | None) -> str:
    """Traduit les signaux en accroche, sans rien conserver.

    C'est l'usage legitime de ces donnees : elles servent a preparer un
    appel, pas a constituer un fichier.
    """
    if not signaux:
        return ""
    avis = signaux.get("nb_avis") or 0
    note = signaux.get("note")
    site = signaux.get("site_web")

    if not site and avis >= 5:
        return (
            f"{avis} avis sur Google et aucun site web : l'offre « site "
            "internet professionnel » repond directement."
        )
    if not site:
        return "Aucun site web : offre « site internet professionnel »."
    if avis < 10:
        return (
            f"Seulement {avis} avis : l'offre « visibilite locale » porte "
            "justement sur la collecte d'avis."
        )
    if note is not None and note < 4.0:
        return f"Note de {note}/5 sur {avis} avis : la reputation en ligne est un sujet ouvert."
    return f"{avis} avis, note {note}/5, site en ligne : prospect deja avance."

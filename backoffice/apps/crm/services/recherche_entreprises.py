"""Client de l'API Recherche d'entreprises (DINUM / annuaire-entreprises).

Documentation officielle : https://recherche-entreprises.api.gouv.fr/openapi.json
Portail : https://api.gouv.fr/les-api/api-recherche-entreprises

Tout ce qui suit a ete releve dans cette specification le 09/11/2026, et non
suppose. Quatre points en sont tires, et chacun change le code.

1. **7 requetes/seconde par adresse IP, 30/s par ASN.** La specification
   previent explicitement : « Il est donc probable de faire face a cette
   limite sur les cloud publics. » Le VPS en est un. D'ou la file Celery
   dediee a consommateur unique (voir `apps.crm.taches`) plutot qu'un
   compteur local, qu'une seconde instance de worker rendrait faux.

2. **`code_postal` et `departement` filtrent sur les ETABLISSEMENTS, pas sur
   le siege.** Une entreprise dont le siege est a Lyon mais qui exploite un
   etablissement a Montpellier repond a `departement=34`. C'est voulu : c'est
   un prospect local legitime. Mais c'est la personne morale — le SIREN — qui
   compte pour un dossier financeur, pas l'etablissement. Les deux sont donc
   conserves separement.

3. **`opposition_diffusion_commerciale: true` signifie que l'entreprise S'EST
   OPPOSEE** a la reutilisation de ses donnees a des fins de prospection
   (RGPD art. 21 §2, art. R.123-320 du Code de commerce). `null` = unite
   legale absente du RNE. Se tromper sur ce booleen conduirait a prospecter
   exactement les entreprises qui l'ont refuse : il alimente donc
   automatiquement la table des oppositions.

4. **`activite_principale_naf25` est un champ temporaire, supprime au
   1er janvier 2027** (dit par la specification elle-meme). Le code ne doit
   pas en dependre apres cette date.

A noter aussi : les unites legales non diffusibles **ne figurent pas** dans
l'API. Un SIREN absent n'est donc pas forcement un SIREN inexistant.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import httpx
from django.conf import settings

from apps.crm.normalisation import normaliser_nom, normaliser_siren, siren_valide

logger = logging.getLogger(__name__)

URL_BASE = "https://recherche-entreprises.api.gouv.fr"

#: Plafond annonce par la specification. Jamais atteint volontairement : la
#: file Celery dediee tient le rythme bien en dessous.
LIMITE_API_PAR_SECONDE = 7

#: Identifie l'appelant sans transmettre d'adresse personnelle. L'API est
#: ouverte et ne demande aucune identification ; en donner une est une
#: courtoisie, pas une obligation, et l'email du client n'y a pas sa place.
AGENT = "vformations-backoffice/1.0 (+https://vformations.fr)"

#: Connexion courte, lecture plus longue : l'API repond en general en moins
#: d'une seconde, mais une recherche textuelle large peut prendre plusieurs.
DELAIS = httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)

#: Fournisseurs de messagerie grand public : le domaine n'y dit rien de
#: l'entreprise, et chercher « gmail » renverrait n'importe quoi.
DOMAINES_GENERIQUES = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "hotmail.com",
        "hotmail.fr",
        "outlook.com",
        "outlook.fr",
        "live.fr",
        "live.com",
        "msn.com",
        "yahoo.com",
        "yahoo.fr",
        "orange.fr",
        "wanadoo.fr",
        "free.fr",
        "sfr.fr",
        "neuf.fr",
        "laposte.net",
        "bbox.fr",
        "icloud.com",
        "me.com",
        "aol.com",
        "protonmail.com",
        "proton.me",
        "gmx.fr",
        "numericable.fr",
        "club-internet.fr",
        "voila.fr",
        "aliceadsl.fr",
    }
)

CERTAIN = "certain"
PROBABLE = "probable"
AMBIGU = "ambigu"
AUCUN = "aucun"


class ErreurApi(RuntimeError):
    """L'API n'a pas repondu utilement. Distinguee d'une absence de resultat :
    l'une se reessaie, l'autre non."""


@dataclass
class Resolution:
    """Ce que la resolution a trouve, avec de quoi en juger.

    `candidats` est rempli meme en cas de succes : c'est ce qui permet a un
    humain de corriger un rattachement douteux sans relancer la recherche.
    """

    siren: str = ""
    certitude: str = AUCUN
    motif: str = ""
    donnees: dict = field(default_factory=dict)
    candidats: list[dict] = field(default_factory=list)
    requete: str = ""

    def __bool__(self) -> bool:
        return bool(self.siren)


def _client() -> httpx.Client:
    return httpx.Client(
        base_url=URL_BASE, timeout=DELAIS, headers={"User-Agent": AGENT}, follow_redirects=True
    )


def appeler(chemin: str, parametres: dict, *, client: httpx.Client | None = None) -> dict:
    """Un appel, sans reessai : les reessais sont le travail de la tache Celery.

    Melanger la politique de reessai dans le client rend le comportement
    impossible a tester et double les delais quand la tache reessaie aussi.
    """
    propre = {c: v for c, v in parametres.items() if v not in (None, "", [])}
    ferme = client is None
    client = client or _client()
    try:
        reponse = client.get(chemin, params=propre)
    except httpx.RequestError as erreur:
        raise ErreurApi(f"appel a {chemin} impossible : {erreur}") from erreur
    finally:
        if ferme:
            client.close()

    if reponse.status_code == 429:
        raise ErreurApi(
            "limite de debit atteinte (429). La specification annonce "
            f"{LIMITE_API_PAR_SECONDE} requetes/seconde par IP ; "
            f"Retry-After = {reponse.headers.get('Retry-After', 'non precise')}."
        )
    if reponse.status_code >= 500:
        raise ErreurApi(f"l'API a repondu {reponse.status_code}")
    if reponse.status_code != 200:
        raise ErreurApi(f"reponse inattendue {reponse.status_code} : {reponse.text[:200]}")
    try:
        return reponse.json()
    except ValueError as erreur:
        raise ErreurApi("reponse illisible (JSON invalide)") from erreur


def rechercher(
    termes: str,
    *,
    departement: str = "",
    code_postal: str = "",
    actives_seulement: bool = True,
    limite: int = 10,
    client: httpx.Client | None = None,
) -> list[dict]:
    """Recherche textuelle. `departement` et `code_postal` filtrent sur les
    etablissements, pas sur le siege (point 2 de l'en-tete)."""
    if not (termes or "").strip():
        return []
    donnees = appeler(
        "/search",
        {
            "q": termes.strip(),
            "departement": departement or None,
            "code_postal": code_postal or None,
            "etat_administratif": "A" if actives_seulement else None,
            "per_page": min(limite, 25),
            "limite_matching_etablissements": 3,
        },
        client=client,
    )
    return donnees.get("results") or []


def par_siren(siren: str, *, client: httpx.Client | None = None) -> dict | None:
    """Recherche directe par SIREN. L'API accepte un SIREN dans `q`."""
    propre = normaliser_siren(siren)
    if not propre:
        return None
    for resultat in rechercher(propre, actives_seulement=False, limite=5, client=client):
        if resultat.get("siren") == propre:
            return resultat
    return None


def _departement_du_resultat(resultat: dict) -> set[str]:
    """Tous les departements ou l'entreprise est presente, siege inclus."""
    departements = set()
    siege = resultat.get("siege") or {}
    if siege.get("departement"):
        departements.add(str(siege["departement"]))
    for etablissement in resultat.get("matching_etablissements") or []:
        if etablissement.get("departement"):
            departements.add(str(etablissement["departement"]))
        elif etablissement.get("code_postal"):
            departements.add(str(etablissement["code_postal"])[:2])
    return departements


def noter(resultat: dict, termes: str, departement_cible: str) -> tuple[int, list[str]]:
    """Note un candidat de 0 a 100, et dit pourquoi.

    La liste de motifs n'est pas decorative : quand un rattachement se revele
    faux, c'est elle qui dit quel critere a mal juge. Sans elle, la note est
    un nombre sans recours.
    """
    note, motifs = 0, []
    cherche = normaliser_nom(termes)
    noms = {
        normaliser_nom(resultat.get("nom_complet") or ""),
        normaliser_nom(resultat.get("nom_raison_sociale") or ""),
        normaliser_nom((resultat.get("siege") or {}).get("nom_commercial") or ""),
        normaliser_nom(resultat.get("sigle") or ""),
    } - {""}

    if cherche and cherche in noms:
        note += 60
        motifs.append("denomination identique")
    elif cherche and any(cherche in nom or nom in cherche for nom in noms):
        note += 30
        motifs.append("denomination incluse")
    elif cherche and any(set(cherche.split()) <= set(nom.split()) for nom in noms):
        note += 20
        motifs.append("tous les mots cherches presents")

    departements = _departement_du_resultat(resultat)
    if departement_cible and departement_cible in departements:
        siege = resultat.get("siege") or {}
        if str(siege.get("departement") or "") == departement_cible:
            note += 25
            motifs.append(f"siege dans le {departement_cible}")
        else:
            note += 15
            motifs.append(f"etablissement dans le {departement_cible}")

    if resultat.get("etat_administratif") == "A":
        note += 10
        motifs.append("unite legale active")
    else:
        note -= 40
        motifs.append("unite legale cessee")

    # Une TPE est la cible ; un grand groupe homonyme ne l'est pas.
    if resultat.get("categorie_entreprise") in (None, "PME"):
        note += 5
        motifs.append("taille compatible avec la cible")

    return max(0, min(100, note)), motifs


def _resume(resultat: dict, note: int, motifs: list[str]) -> dict:
    """Ce qu'on garde d'un candidat pour qu'un humain puisse choisir."""
    siege = resultat.get("siege") or {}
    return {
        "siren": resultat.get("siren", ""),
        "denomination": resultat.get("nom_complet") or resultat.get("nom_raison_sociale") or "",
        "code_postal": siege.get("code_postal") or "",
        "commune": siege.get("libelle_commune") or "",
        "naf": resultat.get("activite_principale") or "",
        "etat": resultat.get("etat_administratif") or "",
        "note": note,
        "motifs": motifs,
    }


def resoudre(
    *,
    siren_declare: str = "",
    denomination: str = "",
    email: str = "",
    departement_cible: str = "",
    client: httpx.Client | None = None,
) -> Resolution:
    """Trouve le SIREN d'un prospect a partir de ce qu'il a declare.

    Trois chemins, par ordre de fiabilite :

    1. un SIREN declare et valide — on verifie seulement qu'il existe ;
    2. une raison sociale — recherche textuelle filtree sur le departement ;
    3. a defaut, le domaine de l'email, s'il n'est pas celui d'un
       fournisseur grand public. Un formulaire Meta ne demande pas toujours
       le nom de l'entreprise, et `contact@le-comptoir-34.fr` le dit quand
       meme. C'est une heuristique, declaree comme telle dans la certitude.

    Ne rattache jamais seule : renvoie une certitude, et `AMBIGU` quand
    plusieurs candidats se valent. Choisir au hasard entre deux homonymes
    mettrait un faux SIREN sur un dossier de financement.
    """
    departement_cible = departement_cible or getattr(settings, "DEPARTEMENT_CIBLE", "")

    propre = normaliser_siren(siren_declare)
    if propre:
        if not siren_valide(propre):
            return Resolution(
                certitude=AUCUN,
                motif=f"le SIREN declare {propre} ne passe pas le controle de cle",
                requete=propre,
            )
        resultat = par_siren(propre, client=client)
        if resultat:
            note, motifs = noter(resultat, denomination or "", departement_cible)
            return Resolution(
                siren=propre,
                certitude=CERTAIN,
                motif="SIREN declare, trouve dans l'API",
                donnees=resultat,
                candidats=[_resume(resultat, note, motifs)],
                requete=propre,
            )
        return Resolution(
            certitude=AUCUN,
            motif=f"SIREN {propre} absent de l'API — il peut s'agir d'une "
            "unite legale non diffusible, qui n'y figure pas",
            requete=propre,
        )

    termes, origine = (denomination or "").strip(), "raison sociale declaree"
    if not termes:
        termes, origine = _termes_depuis_email(email), "domaine de l'email"
    if not termes:
        return Resolution(
            certitude=AUCUN, motif="ni SIREN, ni raison sociale, ni domaine exploitable"
        )

    resultats = rechercher(termes, departement=departement_cible, client=client)
    if not resultats and departement_cible:
        # Hors departement cible : le prospect peut etre ailleurs. On
        # elargit, mais la note le sanctionnera.
        resultats = rechercher(termes, client=client)

    notes = sorted(
        ((*noter(r, termes, departement_cible), r) for r in resultats),
        key=lambda t: t[0],
        reverse=True,
    )
    candidats = [_resume(r, note, motifs) for note, motifs, r in notes[:5]]
    if not notes:
        return Resolution(
            certitude=AUCUN, motif=f"aucun resultat pour « {termes} » ({origine})", requete=termes
        )

    meilleure, motifs_meilleur, resultat = notes[0]
    second = notes[1][0] if len(notes) > 1 else 0
    base = f"« {termes} » ({origine}) : " + ", ".join(motifs_meilleur)

    if meilleure >= 80 and meilleure - second >= 25:
        certitude = CERTAIN
    elif meilleure >= 55 and meilleure - second >= 15:
        certitude = PROBABLE
    elif meilleure >= 55:
        certitude = AMBIGU
        base += f" — mais {len(notes)} candidats se valent (second a {second}/100)"
    else:
        certitude = AUCUN
        base += f" — note trop faible ({meilleure}/100)"

    return Resolution(
        siren=resultat.get("siren", "") if certitude in (CERTAIN, PROBABLE) else "",
        certitude=certitude,
        motif=base,
        donnees=resultat if certitude in (CERTAIN, PROBABLE) else {},
        candidats=candidats,
        requete=termes,
    )


def _termes_depuis_email(email: str) -> str:
    """« contact@le-comptoir-34.fr » devient « le comptoir 34 ».

    Les chiffres sont conserves : a Montpellier, « 34 » fait partie de bien
    des raisons sociales, et le retirer degraderait la recherche.
    """
    if "@" not in (email or ""):
        return ""
    domaine = email.rsplit("@", 1)[1].strip().lower()
    if not domaine or domaine in DOMAINES_GENERIQUES:
        return ""
    etiquette = domaine.split(".")[0]
    if len(etiquette) < 3:
        return ""
    return etiquette.replace("-", " ").replace("_", " ")

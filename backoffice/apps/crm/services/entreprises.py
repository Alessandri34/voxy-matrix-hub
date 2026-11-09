"""Conversion d'un resultat de l'API Recherche d'entreprises en fiche.

La correspondance des champs est tiree de la specification officielle
(https://recherche-entreprises.api.gouv.fr/openapi.json, relevee le
09/11/2026) et non devinee. Les noms de l'API sont cites tels quels dans les
commentaires : le jour ou l'API bougera, c'est ici qu'il faudra regarder.
"""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from apps.crm.models import CanalOpposition, Entreprise, Opposition, TrancheEffectif
from apps.crm.normalisation import normaliser_siren

logger = logging.getLogger(__name__)

#: Codes INSEE de tranche d'effectif connus du modele. L'API en renvoie
#: d'autres (31, 32, 41, 42, 51, 52, 53) pour les entreprises plus grandes,
#: hors cible : elles sont repliees sur « 100 salaries et plus ».
_TRANCHES_CONNUES = set(TrancheEffectif.values)
_GRANDES = {"31", "32", "41", "42", "51", "52", "53"}


def _tranche(code) -> str:
    code = str(code or "").strip()
    if code in _TRANCHES_CONNUES:
        return code
    if code in _GRANDES:
        return TrancheEffectif.CENT_ET_PLUS
    return TrancheEffectif.NON_RENSEIGNE


def _date(valeur) -> str | None:
    """L'API renvoie « 2013-07-01 », parfois « 2013-07 » ou « 2013 »."""
    texte = str(valeur or "").strip()
    if len(texte) == 10:
        return texte
    if len(texte) == 7:
        return texte + "-01"
    if len(texte) == 4:
        return texte + "-01-01"
    return None


def champs_depuis_api(donnees: dict) -> dict:
    """Traduit un resultat de l'API en champs du modele `Entreprise`."""
    siege = donnees.get("siege") or {}
    return {
        "denomination": (donnees.get("nom_complet") or donnees.get("nom_raison_sociale") or "")[
            :200
        ],
        "nom_commercial": (siege.get("nom_commercial") or "")[:200],
        # `nature_juridique` est le code de categorie juridique INSEE.
        "categorie_juridique": (donnees.get("nature_juridique") or "")[:4],
        "naf": (donnees.get("activite_principale") or "")[:6],
        "naf_libelle": (donnees.get("libelle_activite_principale") or "")[:250],
        # Champ TEMPORAIRE : la specification annonce sa suppression au
        # 1er janvier 2027. Ne rien y accrocher de durable.
        "naf_2025": (donnees.get("activite_principale_naf25") or "")[:8],
        "date_creation_entreprise": _date(donnees.get("date_creation")),
        "tranche_effectif": _tranche(donnees.get("tranche_effectif_salarie")),
        "adresse": (siege.get("adresse") or siege.get("geo_adresse") or "")[:250],
        "code_postal": (siege.get("code_postal") or "")[:10],
        "commune": (siege.get("libelle_commune") or "")[:120],
        "departement": str(siege.get("departement") or "")[:3],
        "etat_administratif": (donnees.get("etat_administratif") or "")[:1],
        # Present au Registre des Metiers => inscrite. L'absence de valeur ne
        # prouve pas la non-inscription : on laisse nul plutot que faux, car
        # l'eligibilite FAFCEA en depend.
        "inscrite_repertoire_metiers": (
            True if siege.get("activite_principale_registre_metier") else None
        ),
        # « O » = diffusible, « P » = diffusion partielle (opposition
        # demandee). Les unites non diffusibles ne figurent pas dans l'API.
        "statut_diffusion": (donnees.get("statut_diffusion") or "")[:40],
        "diffusible": (donnees.get("statut_diffusion") or "O") == "O",
        "opposition_diffusion_commerciale": donnees.get("opposition_diffusion_commerciale"),
        "source_resolution": "recherche-entreprises",
        "date_resolution": timezone.now(),
    }


@transaction.atomic
def enregistrer_depuis_api(donnees: dict) -> tuple[Entreprise, bool]:
    """Cree ou met a jour la fiche entreprise. Renvoie `(entreprise, creee)`.

    Les champs deja renseignes a la main **ne sont pas ecrases** : une
    correction faite par un humain vaut mieux qu'une donnee d'API, surtout
    pour l'adresse d'un etablissement qui n'est pas le siege.
    """
    siren = normaliser_siren(donnees.get("siren", ""))
    if not siren:
        raise ValueError("resultat d'API sans SIREN exploitable")

    champs = champs_depuis_api(donnees)
    entreprise = Entreprise.objects.filter(siren=siren).first()
    creee = entreprise is None

    if creee:
        entreprise = Entreprise(siren=siren, **champs)
    else:
        for champ, valeur in champs.items():
            if champ in ("source_resolution", "date_resolution"):
                setattr(entreprise, champ, valeur)
                continue
            actuelle = getattr(entreprise, champ)
            # On remplit ce qui est vide, on ne remplace pas ce qui est la.
            if valeur not in (None, "", TrancheEffectif.NON_RENSEIGNE) and actuelle in (
                None,
                "",
                TrancheEffectif.NON_RENSEIGNE,
            ):
                setattr(entreprise, champ, valeur)
        # Exception : ces trois-la viennent toujours de la source et doivent
        # suivre. Un etat administratif perime ferait vendre une formation a
        # une entreprise cessee ; une opposition perimee la ferait prospecter.
        for champ in ("etat_administratif", "diffusible", "opposition_diffusion_commerciale"):
            if champs[champ] not in (None, ""):
                setattr(entreprise, champ, champs[champ])
    entreprise.save()

    inscrire_opposition_legale(entreprise)
    return entreprise, creee


def inscrire_opposition_legale(entreprise: Entreprise) -> Opposition | None:
    """Reporte dans la table des oppositions ce que l'INSEE et le RNE disent.

    Pourquoi automatiquement : `opposition_diffusion_commerciale` est une
    opposition formelle au sens du RGPD, enregistree par l'entreprise aupres
    du registre. La connaitre et ne pas l'appliquer serait pire que de ne pas
    la connaitre. Le statut de diffusion « P » vaut la meme chose.

    Idempotent : une seconde resolution ne cree pas une seconde ligne.
    """
    oppose = bool(entreprise.opposition_diffusion_commerciale) or (
        entreprise.statut_diffusion == "P"
    )
    if not (oppose and entreprise.siren):
        return None
    existante = Opposition.objects.filter(
        siren=entreprise.siren, canal=CanalOpposition.DEMANDE_DIRECTE
    ).first()
    if existante:
        return existante
    logger.info(
        "Opposition legale relevee pour le SIREN %s (%s) : inscrite au registre des oppositions.",
        entreprise.siren,
        entreprise.denomination,
    )
    return Opposition.objects.create(
        siren=entreprise.siren,
        canal=CanalOpposition.DEMANDE_DIRECTE,
        note="Opposition a la prospection commerciale declaree au registre "
        "(RGPD art. 21 §2, art. R.123-320 du Code de commerce). Relevee "
        "automatiquement par la resolution SIREN.",
    )

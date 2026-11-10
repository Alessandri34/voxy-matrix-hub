"""Limitation de debit sur les points d'entree publics.

**Pourquoi ecrit a la main plutot qu'avec une bibliotheque.** Il y a
exactement un point d'entree public dans cette application : le webhook
Meta. Une bibliotheque de limitation apporterait une syntaxe generale, des
reglages a apprendre et une dependance de plus sur le chemin critique
d'authentification — pour une regle qui tient en trente lignes.

**Pourquoi il en faut une.** Le webhook est joignable par tout internet et
ne porte aucune session : c'est voulu, il s'authentifie par la signature
HMAC de son corps. Mais la verification de signature coute un calcul, et
l'enregistrement de la reception coute une ecriture en base. Sans plafond,
n'importe qui peut saturer la base avec des requetes mal signees.

**Le compteur vit dans le cache partage** (Redis en production). Un
compteur en memoire de processus serait remis a zero a chaque redemarrage
et compterait separement dans chaque worker gunicorn — soit trois fois le
plafond annonce.

⚠️ **Deux plafonds differents, et c'est le point important.** Une requete
BIEN signee vient de Meta, qui peut legitimement envoyer des rafales : son
plafond est large. Une requete MAL signee ne vient pas de Meta : son
plafond est serre, parce qu'il n'existe aucune raison legitime d'en
envoyer beaucoup.
"""

from __future__ import annotations

import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

#: Requetes correctement signees, par minute et par adresse. Large : Meta
#: regroupe et peut reemettre.
PLAFOND_SIGNEES = 300

#: Requetes mal signees, par minute et par adresse. Serre : il n'y a aucune
#: raison legitime d'en envoyer plus de quelques-unes.
PLAFOND_NON_SIGNEES = 20

FENETRE_SECONDES = 60


def _cle(prefixe: str, adresse: str) -> str:
    return f"debit:{prefixe}:{adresse}"


def compter(prefixe: str, adresse: str, plafond: int) -> tuple[bool, int]:
    """Incremente et dit si le plafond est depasse.

    Renvoie `(autorise, compte)`. En cas de panne du cache, **autorise** :
    un limiteur qui tombe ne doit pas faire tomber la reception des leads
    avec lui. La perte d'un plafond vaut mieux que la perte des demandes
    d'un client.
    """
    cle = _cle(prefixe, adresse)
    try:
        # `add` ne pose la valeur que si la cle n'existe pas : c'est lui qui
        # cree la fenetre et son expiration. `incr` la fait ensuite avancer
        # sans toucher a l'expiration, donc la fenetre reste glissante par
        # tranche et ne se prolonge pas indefiniment sous la charge.
        cache.add(cle, 0, FENETRE_SECONDES)
        compte = cache.incr(cle)
    except Exception as erreur:  # noqa: BLE001 — cache indisponible
        logger.warning("Limitation de debit inoperante (cache) : %s", erreur)
        return True, 0
    return compte <= plafond, compte


def adresse_client(request) -> str:
    """L'adresse du client, derriere le mandataire.

    ⚠️ `X-Forwarded-For` est fourni par le client et donc falsifiable — sauf
    si un mandataire de confiance la reecrit, ce que fait nginx ici. On ne
    retient que la PREMIERE valeur, celle que nginx a posee.
    """
    transmise = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if transmise:
        return transmise.split(",")[0].strip()[:45]
    return (request.META.get("REMOTE_ADDR") or "inconnue")[:45]

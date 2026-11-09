"""Verification de la signature des webhooks Meta.

Specification officielle (developers.facebook.com/docs/graph-api/webhooks/
getting-started, relevee le 09/11/2026) :

- en-tete **`X-Hub-Signature-256`**, valeur prefixee de **`sha256=`** ;
- signature **SHA256** calculee « using the payload and your app's App Secret » ;
- la documentation precise : « You don't have to validate the payload, but
  you should. »

La documentation de Meta ne nomme ni HMAC ni l'encodage de sortie. La
convention `X-Hub-Signature` vient de PubSubHubbub et designe un **HMAC** en
**hexadecimal minuscule** ; c'est ce qu'implementent les bibliotheques
officielles de Meta et tous les clients observes. C'est donc ce qui est fait
ici, et c'est signale comme une deduction, pas comme une citation.

Deux choix de securite :

1. **Comparaison a temps constant** (`hmac.compare_digest`). Un `==` sur des
   chaines s'arrete au premier octet different : le temps de reponse revele
   alors combien d'octets etaient justes, ce qui permet de reconstruire la
   signature octet par octet.
2. **Fermeture par defaut.** Sans secret configure, la verification echoue au
   lieu de passer. Un webhook ouvert accepterait de faux leads de n'importe
   qui, et ces faux leads entreraient dans le pipeline commercial.
"""

from __future__ import annotations

import hashlib
import hmac

ENTETE = "HTTP_X_HUB_SIGNATURE_256"
PREFIXE = "sha256="


class SignatureInvalide(Exception):
    """La requete n'a pas ete signee par l'application Meta attendue."""


def calculer(corps: bytes, secret: str) -> str:
    """La signature attendue, prefixe inclus."""
    empreinte = hmac.new(secret.encode("utf-8"), corps, hashlib.sha256).hexdigest()
    return PREFIXE + empreinte


def verifier(corps: bytes, signature_recue: str | None, secret: str) -> None:
    """Leve `SignatureInvalide` si la requete n'est pas authentique.

    `corps` doit etre le corps **brut**. Re-serialiser le JSON avant de
    signer donnerait une empreinte differente pour la meme donnee : un espace
    ou un ordre de cles suffit.
    """
    if not secret:
        raise SignatureInvalide(
            "aucun secret d'application configure (META_APP_SECRET) : la "
            "verification echoue par defaut plutot que de laisser passer. "
            "Un webhook ouvert accepterait de faux leads de n'importe qui."
        )
    if not signature_recue:
        raise SignatureInvalide(f"en-tete {ENTETE} absent")
    if not signature_recue.startswith(PREFIXE):
        raise SignatureInvalide(
            f"prefixe inattendu : attendu « {PREFIXE} », recu « {signature_recue[:12]}… »"
        )
    if not hmac.compare_digest(calculer(corps, secret), signature_recue):
        raise SignatureInvalide("signature non concordante")

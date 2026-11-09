"""Point d'entree du webhook Meta.

Deux methodes sur la meme URL, comme Meta l'exige :

- **GET** : la poignee de main de verification. Meta envoie `hub.mode=subscribe`,
  `hub.verify_token` et `hub.challenge` ; il faut renvoyer le challenge tel
  quel, en texte brut, apres avoir verifie le jeton.
- **POST** : la notification. Signature verifiee, corps brut enregistre, 200
  renvoye, traitement differe.

Pourquoi `csrf_exempt` : un webhook n'a pas de session et ne peut pas porter
de jeton CSRF. Ce n'est pas un trou, parce que l'authentification de la
requete est assuree par la signature HMAC, qui est plus forte qu'un jeton
CSRF — elle prouve l'origine ET l'integrite du corps.
"""

from __future__ import annotations

import hmac
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.integrations.meta.signature import ENTETE, SignatureInvalide, verifier
from apps.integrations.models import EtatReception, ReceptionWebhook

logger = logging.getLogger(__name__)

#: En-tetes conserves pour le diagnostic. Volontairement restreint : garder
#: tous les en-tetes reviendrait a stocker des cookies et des jetons.
ENTETES_UTILES = (
    "HTTP_X_HUB_SIGNATURE_256",
    "HTTP_USER_AGENT",
    "HTTP_CONTENT_TYPE",
    "CONTENT_TYPE",
    "CONTENT_LENGTH",
)


def _cle_idempotence(corps: str) -> str:
    """L'identifiant du premier evenement leadgen, s'il y en a un.

    Sert a reconnaitre un reessai de Meta : il reemet jusqu'a recevoir un
    200, et sans cette cle un reessai creerait un second lead.
    """
    from apps.integrations.meta.taches import evenements_leadgen

    evenements = evenements_leadgen(corps)
    if not evenements:
        return ""
    return str(evenements[0].get("leadgen_id") or "")[:120]


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _verifier_abonnement(request)
    return _recevoir(request)


def _verifier_abonnement(request: HttpRequest) -> HttpResponse:
    """La poignee de main de Meta.

    `hub.challenge` est renvoye en texte brut, sans guillemets JSON : Meta
    compare la reponse caractere par caractere.
    """
    mode = request.GET.get("hub.mode", "")
    jeton = request.GET.get("hub.verify_token", "")
    challenge = request.GET.get("hub.challenge", "")
    attendu = getattr(settings, "META_VERIFY_TOKEN", "")

    if not attendu:
        logger.error("Verification du webhook refusee : META_VERIFY_TOKEN n'est pas configure.")
        return HttpResponseForbidden("verify token non configure")
    # Comparaison a temps constant : le jeton de verification est un secret.
    if mode != "subscribe" or not hmac.compare_digest(jeton, attendu):
        logger.warning("Verification du webhook refusee (mode=%r).", mode)
        return HttpResponseForbidden("verification refusee")
    return HttpResponse(challenge, content_type="text/plain")


def _recevoir(request: HttpRequest) -> HttpResponse:
    # `request.body` AVANT toute lecture de POST : re-serialiser le JSON
    # donnerait une empreinte differente pour la meme donnee.
    corps_brut = request.body
    signature = request.META.get(ENTETE)
    entetes = {c: request.META.get(c) for c in ENTETES_UTILES if request.META.get(c)}

    try:
        verifier(corps_brut, signature, getattr(settings, "META_APP_SECRET", ""))
    except SignatureInvalide as erreur:
        # La ligne est conservee : une serie de signatures invalides signale
        # un secret desynchronise ou une tentative d'injection de faux leads.
        ReceptionWebhook.objects.create(
            source="meta",
            signature_valide=False,
            corps=corps_brut.decode("utf-8", errors="replace")[:100_000],
            entetes=entetes,
            etat=EtatReception.IGNOREE,
            erreur=f"signature refusee : {erreur}",
        )
        logger.warning("Webhook Meta refuse : %s", erreur)
        return HttpResponseForbidden("signature invalide")

    corps = corps_brut.decode("utf-8", errors="replace")
    cle = _cle_idempotence(corps)

    if cle:
        deja = ReceptionWebhook.objects.filter(
            source="meta", cle_idempotence=cle, etat=EtatReception.TRAITEE
        ).first()
        if deja:
            # Meta reemet apres un 200 perdu en route. Reconnaitre le
            # reessai evite un second lead, et le 200 arrete la serie.
            logger.info("Reessai Meta pour le lead %s deja traite (reception %s).", cle, deja.pk)
            return JsonResponse({"recu": True, "deja_traite": True})

    reception = ReceptionWebhook.objects.create(
        source="meta",
        signature_valide=True,
        corps=corps[:100_000],
        entetes=entetes,
        cle_idempotence=cle,
        etat=EtatReception.RECUE,
    )

    # Le 200 ne part qu'une fois le corps enregistre : sinon Meta
    # considererait le lead livre alors qu'il serait perdu.
    from apps.integrations.meta.taches import traiter_reception

    try:
        traiter_reception.delay(reception.pk)
    except Exception as erreur:  # noqa: BLE001 — courtier injoignable
        # Le lead n'est PAS perdu : la reception est en base, l'etat « recue »
        # la rend rejouable par la commande `rejouer_receptions`.
        logger.error(
            "Reception %s enregistree mais non mise en file (%s). "
            "Rejouable : manage.py rejouer_receptions",
            reception.pk,
            erreur,
        )
    return JsonResponse({"recu": True, "reception": reception.pk})

"""Rend l'utilisateur de la requete visible aux signaux du journal."""

from apps.audit.contexte import agir_en_tant_que


def _ip_client(request) -> str | None:
    transmise = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if transmise:
        # Caddy ajoute l'adresse du client en tete de liste.
        return transmise.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def middleware_acteur(get_response):
    def middleware(request):
        utilisateur = getattr(request, "user", None)
        if utilisateur is not None and not utilisateur.is_authenticated:
            utilisateur = None
        with agir_en_tant_que(acteur=utilisateur, origine="application", ip=_ip_client(request)):
            return get_response(request)

    return middleware

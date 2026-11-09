"""Le Kanban et la file des leads.

C'est la demonstration navigable de la phase 1 : « Kanban fonctionnel, motif
de perte obligatoire, alerte a 24 h sans contact ».

Choix d'implementation : des gabarits Django rendus par le serveur, avec un
glisser-deposer qui poste en `fetch`. Pas de cadre JavaScript. Le back-office
sera utilise par deux ou trois personnes sur quelques centaines d'affaires ;
une application monopage couterait un chantier de plus a maintenir pour un
gain nul a cette echelle, et la page se recharge en moins d'une seconde.
"""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.permissions import exige_module
from apps.crm.models import Lead
from apps.pipeline.models import ETAPES_FINALES, Etape, MotifPerte, Opportunite
from apps.pipeline.services import changer_etape


@exige_module("pipeline")
def kanban(request):
    affaires = Opportunite.objects.select_related("entreprise", "contact", "proprietaire")
    par_etape = {etape: [] for etape, _ in Etape.choices}
    for affaire in affaires:
        par_etape.setdefault(affaire.etape, []).append(affaire)

    totaux = {
        ligne["etape"]: ligne
        for ligne in affaires.values("etape").annotate(
            nombre=Count("id"), montant=Sum("montant_estime_centimes")
        )
    }

    colonnes = []
    for etape, libelle in Etape.choices:
        ligne = totaux.get(etape, {})
        colonnes.append(
            {
                "code": etape,
                "libelle": libelle,
                "affaires": par_etape.get(etape, []),
                "nombre": ligne.get("nombre", 0),
                # Converti ici, pas dans le gabarit : un filtre de division
                # dans un gabarit Django donne un flottant, et un total de
                # devis affiche en flottant finit par ne plus tomber juste.
                "montant": (Decimal(ligne.get("montant") or 0) / 100).quantize(Decimal("0.01")),
                "finale": etape in ETAPES_FINALES,
            }
        )

    return render(
        request,
        "pipeline/kanban.html",
        {
            "colonnes": colonnes,
            "motifs": MotifPerte.choices,
            "etape_perdu": Etape.PERDU,
            "leads_en_retard": _leads_en_retard().count(),
        },
    )


@require_POST
@exige_module("pipeline")
def deplacer(request, pk: int):
    """Deplace une affaire. Refuse « Perdu » sans motif, avec un message.

    La vue ne duplique pas la regle : elle laisse `changer_etape` la tenir et
    se contente de traduire l'erreur. Deux copies d'une meme regle finissent
    toujours par divercher.
    """
    affaire = get_object_or_404(Opportunite, pk=pk)
    cible = request.POST.get("etape", "")
    try:
        changer_etape(
            affaire,
            cible,
            auteur=request.user,
            motif_de_perte=request.POST.get("motif_de_perte", ""),
            commentaire_perte=request.POST.get("commentaire_perte", ""),
        )
    except Exception as erreur:  # ValidationError et ses messages de champ
        messages = getattr(erreur, "message_dict", None) or {"__all__": [str(erreur)]}
        premier = next(iter(messages.values()))[0]
        return JsonResponse({"ok": False, "erreur": premier}, status=400)

    return JsonResponse(
        {
            "ok": True,
            "etape": affaire.etape,
            "libelle": affaire.get_etape_display(),
            "probabilite": affaire.probabilite,
        }
    )


def _leads_en_retard(heures: int = 24):
    limite = timezone.now() - timezone.timedelta(hours=heures)
    return Lead.objects.filter(
        date_premier_contact__isnull=True,
        doublon_de__isnull=True,
        date_reception__lt=limite,
    )


@exige_module("crm")
def file_leads(request):
    """Les leads pas encore entres dans le pipeline.

    Les trois colonnes repondent aux trois raisons pour lesquelles un lead
    reste en attente : personne ne l'a appele, son entreprise n'est pas
    identifiee, ou c'est peut-etre un doublon.
    """
    base = Lead.objects.select_related("entreprise", "contact", "doublon_de")
    return render(
        request,
        "pipeline/leads.html",
        {
            "en_retard": list(
                _leads_en_retard().select_related("entreprise").order_by("date_reception")[:50]
            ),
            "a_resoudre": list(
                base.filter(entreprise__isnull=True, doublon_de__isnull=True).order_by(
                    "-date_reception"
                )[:50]
            ),
            "doublons": list(
                base.filter(doublon_de__isnull=False).order_by("-date_reception")[:50]
            ),
            "recents": list(base.filter(doublon_de__isnull=True).order_by("-date_reception")[:20]),
        },
    )


@exige_module("financement")
def dossiers_financement(request):
    """Les dossiers, tries par urgence de depot.

    L'ordre est volontaire : une fenetre fermee d'abord, puis ce qui se
    ferme bientot. Trier par date de creation mettrait en haut ce qui n'est
    pas urgent.
    """
    from apps.financement.models import Dossier, EtatDossier

    dossiers = Dossier.objects.select_related(
        "opportunite__entreprise", "opportunite__contact"
    ).order_by("date_debut_formation")

    en_cours = [d for d in dossiers if d.etat in (EtatDossier.BROUILLON, EtatDossier.A_DEPOSER)]
    fermes = [d for d in en_cours if d.depot_en_retard]
    urgents = [
        d
        for d in en_cours
        if not d.depot_en_retard
        and d.jours_avant_cloture is not None
        and d.jours_avant_cloture <= 7
    ]
    autres = [d for d in en_cours if d not in fermes and d not in urgents]

    return render(
        request,
        "pipeline/financement.html",
        {
            "fermes": fermes,
            "urgents": urgents,
            "autres": autres,
            "deposes": [
                d for d in dossiers if d.etat not in (EtatDossier.BROUILLON, EtatDossier.A_DEPOSER)
            ][:30],
        },
    )

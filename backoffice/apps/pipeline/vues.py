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

from datetime import datetime
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


# ==========================================================================
# Tableau de bord
# ==========================================================================


@exige_module("reporting")
def accueil(request):
    """Ce qu'il faut savoir en ouvrant l'outil.

    L'ordre est volontaire : d'abord ce qui bloque, ensuite ce qui avance.
    Un tableau de bord qui ouvre sur les totaux du mois laisse passer le
    dossier dont la fenetre de depot se ferme demain.
    """
    from apps.financement.models import Dossier, EtatDossier
    from apps.publicite.attribution import attribuer
    from apps.sequences.models import EtatInscription, Inscription

    maintenant = timezone.now()
    debut_mois = timezone.localdate().replace(day=1)

    leads_mois = Lead.objects.filter(doublon_de__isnull=True, date_reception__date__gte=debut_mois)
    affaires = Opportunite.objects.exclude(etape__in=ETAPES_FINALES)
    dossiers = Dossier.objects.filter(
        etat__in=[EtatDossier.BROUILLON, EtatDossier.A_DEPOSER]
    ).select_related("opportunite__entreprise")

    fenetres_fermees = [d for d in dossiers if d.depot_en_retard]
    fenetres_urgentes = [
        d
        for d in dossiers
        if not d.depot_en_retard
        and d.jours_avant_cloture is not None
        and d.jours_avant_cloture <= 7
    ]

    pipeline_centimes = affaires.aggregate(total=Sum("montant_estime_centimes"))["total"] or 0
    publicite = attribuer(depuis=debut_mois)

    return render(
        request,
        "pipeline/accueil.html",
        {
            "leads_mois": leads_mois.count(),
            "leads_en_retard": _leads_en_retard().count(),
            "affaires_ouvertes": affaires.count(),
            "pipeline": (Decimal(pipeline_centimes) / 100).quantize(Decimal("0.01")),
            "fenetres_fermees": fenetres_fermees,
            "fenetres_urgentes": fenetres_urgentes,
            "a_resoudre": Lead.objects.filter(
                entreprise__isnull=True, doublon_de__isnull=True
            ).count(),
            "inscriptions_actives": Inscription.objects.filter(etat=EtatInscription.ACTIVE).count(),
            "publicite": publicite,
            "colonnes": _repartition_pipeline(),
            "derniers_leads": list(
                Lead.objects.filter(doublon_de__isnull=True)
                .select_related("entreprise", "campagne")
                .order_by("-date_reception")[:8]
            ),
            "maintenant": maintenant,
        },
    )


def _repartition_pipeline():
    """Le nombre et le montant par etape, pour la barre de repartition."""
    lignes = (
        Opportunite.objects.values("etape")
        .annotate(nombre=Count("id"), montant=Sum("montant_estime_centimes"))
        .order_by()
    )
    par_etape = {ligne["etape"]: ligne for ligne in lignes}
    total = sum(ligne["nombre"] for ligne in lignes) or 1
    resultat = []
    for etape, libelle in Etape.choices:
        ligne = par_etape.get(etape, {})
        nombre = ligne.get("nombre", 0)
        resultat.append(
            {
                "code": etape,
                "libelle": libelle,
                "nombre": nombre,
                "part": round(nombre * 100 / total, 1),
                "montant": (Decimal(ligne.get("montant") or 0) / 100).quantize(Decimal("0.01")),
                "finale": etape in ETAPES_FINALES,
            }
        )
    return resultat


# ==========================================================================
# Publicité
# ==========================================================================


@exige_module("reporting")
def publicite(request):
    """La chaine complete, de l'euro depense au client forme.

    C'est le chiffre que la regie ne sait pas donner : elle ignore ce qui se
    passe apres le formulaire.
    """
    from apps.publicite.attribution import attribuer, par_campagne
    from apps.publicite.models import Campagne, Depense

    debut = request.GET.get("depuis") or ""
    depuis = None
    if debut:
        try:
            depuis = datetime.strptime(debut, "%Y-%m-%d").date()
        except ValueError:
            depuis = None

    total = attribuer(depuis=depuis)
    lignes = [
        ligne for ligne in par_campagne(depuis=depuis) if ligne.leads or ligne.depense_centimes
    ]

    return render(
        request,
        "pipeline/publicite.html",
        {
            "total": total,
            "lignes": lignes,
            "depuis": debut,
            "nb_campagnes": Campagne.objects.count(),
            "nb_depenses": Depense.objects.count(),
            "dernieres_depenses": list(
                Depense.objects.select_related("campagne").order_by("-mois", "-jour")[:10]
            ),
            "leads_sans_campagne": Lead.objects.filter(
                doublon_de__isnull=True, campagne__isnull=True, source="meta_lead_ads"
            ).count(),
        },
    )


# ==========================================================================
# Sourcing et séquences
# ==========================================================================


@exige_module("crm")
def sourcing(request):
    """Les prospects issus du sourcing, et ce que la derniere campagne a donne."""
    from apps.sourcing.ciblage import FAMILLES_NAF

    sources = Lead.objects.filter(source="sourcing").select_related("entreprise")
    return render(
        request,
        "pipeline/sourcing.html",
        {
            "total": sources.count(),
            "rattaches": sources.filter(entreprise__isnull=False).count(),
            "en_sequence": sources.filter(inscriptions__isnull=False).distinct().count(),
            "recents": list(sources.order_by("-date_reception")[:40]),
            # Une liste de couples plutot qu'un dictionnaire : un gabarit
            # Django ne sait pas chercher une cle dynamique.
            "familles": [
                {"nom": nom, "codes": len(codes)} for nom, codes in sorted(FAMILLES_NAF.items())
            ],
        },
    )


@exige_module("sequences")
def sequences(request):
    """L'etat des sequences : ce qui part, ce qui s'est arrete, et pourquoi."""
    from django.conf import settings

    from apps.sequences.models import (
        Envoi,
        EtatEnvoi,
        EtatInscription,
        Inscription,
        Sequence,
    )

    liste = []
    for sequence in Sequence.objects.prefetch_related("etapes"):
        inscriptions = Inscription.objects.filter(sequence=sequence)
        liste.append(
            {
                "sequence": sequence,
                "etapes": sequence.etapes.filter(active=True).count(),
                "actives": inscriptions.filter(etat=EtatInscription.ACTIVE).count(),
                "terminees": inscriptions.filter(etat=EtatInscription.TERMINEE).count(),
                "arretees": inscriptions.filter(etat=EtatInscription.ARRETEE).count(),
                "envois": Envoi.objects.filter(inscription__sequence=sequence).count(),
            }
        )

    motifs = (
        Inscription.objects.filter(etat=EtatInscription.ARRETEE)
        .exclude(motif_arret="")
        .values("motif_arret")
        .annotate(nombre=Count("id"))
        .order_by("-nombre")
    )

    return render(
        request,
        "pipeline/sequences.html",
        {
            "lignes": liste,
            "motifs": list(motifs),
            "envoi_reel": getattr(settings, "SEQUENCES_ENVOI_REEL", False),
            "prets": Envoi.objects.filter(etat=EtatEnvoi.A_ENVOYER).count(),
            "envoyes": Envoi.objects.filter(etat=EtatEnvoi.ENVOYE).count(),
            "derniers": list(
                Envoi.objects.select_related("inscription__sequence").order_by("-prevu_le")[:15]
            ),
        },
    )

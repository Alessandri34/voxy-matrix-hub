"""Les operations du pipeline, en un seul endroit.

Un changement d'etape touche quatre choses a la fois : l'etape, la date
d'entree, le passage precedent a fermer, l'activite a tracer. Laisse a
l'appelant, l'une des quatre serait oubliee quelque part — et le temps par
etape, qui est la seule mesure utile du pipeline, deviendrait faux sans que
personne s'en apercoive.
"""

from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.crm.models import Activite, Lead, TypeActivite
from apps.pipeline.models import (
    ETAPES_FINALES,
    PROBABILITE_PAR_ETAPE,
    Etape,
    Opportunite,
    PassageEtape,
)


def _tracer(opportunite: Opportunite, contenu: str, auteur=None) -> Activite:
    return Activite.objects.create(
        type=TypeActivite.CHANGEMENT_ETAPE,
        type_objet=ContentType.objects.get_for_model(Opportunite),
        id_objet=str(opportunite.pk),
        auteur=auteur,
        contenu=contenu,
    )


@transaction.atomic
def changer_etape(
    opportunite: Opportunite,
    nouvelle_etape: str,
    *,
    auteur=None,
    motif_de_perte: str = "",
    commentaire_perte: str = "",
    maintenant=None,
) -> Opportunite:
    """Deplace une affaire, en datant le passage et en tracant l'activite."""
    maintenant = maintenant or timezone.now()
    ancienne = opportunite.etape
    if nouvelle_etape == ancienne:
        return opportunite
    if nouvelle_etape not in Etape.values:
        raise ValidationError(f"Etape inconnue : {nouvelle_etape!r}")

    # `transaction.atomic` annule la base, pas l'objet Python. Sans cette
    # sauvegarde, un echec de validation laisserait l'instance en memoire
    # portant la nouvelle etape : l'appel suivant verrait `nouvelle_etape ==
    # ancienne`, croirait n'avoir rien a faire et ne ferait rien. Un
    # utilisateur qui corrige son motif apres l'erreur verrait son changement
    # disparaitre sans message.
    CHAMPS_TOUCHES = (
        "etape",
        "probabilite",
        "date_entree_etape",
        "date_cloture",
        "motif_de_perte",
        "commentaire_perte",
    )
    avant = {champ: getattr(opportunite, champ) for champ in CHAMPS_TOUCHES}
    try:
        return _appliquer_etape(
            opportunite,
            nouvelle_etape,
            ancienne,
            auteur=auteur,
            motif_de_perte=motif_de_perte,
            commentaire_perte=commentaire_perte,
            maintenant=maintenant,
        )
    except Exception:
        for champ, valeur in avant.items():
            setattr(opportunite, champ, valeur)
        raise


def _appliquer_etape(
    opportunite: Opportunite,
    nouvelle_etape: str,
    ancienne: str,
    *,
    auteur,
    motif_de_perte: str,
    commentaire_perte: str,
    maintenant,
) -> Opportunite:
    """Le corps du changement d'etape. Appele sous transaction par
    `changer_etape`, qui se charge de restaurer l'objet en cas d'echec."""
    if nouvelle_etape == Etape.PERDU:
        opportunite.motif_de_perte = motif_de_perte or opportunite.motif_de_perte
        opportunite.commentaire_perte = commentaire_perte or opportunite.commentaire_perte
    else:
        # Une affaire qui ressort de « Perdu » n'a plus de motif de perte :
        # le laisser ferait apparaitre un motif sur une affaire en cours.
        opportunite.motif_de_perte = ""
        opportunite.commentaire_perte = ""

    opportunite.etape = nouvelle_etape
    opportunite.probabilite = PROBABILITE_PAR_ETAPE.get(nouvelle_etape, opportunite.probabilite)
    opportunite.date_entree_etape = maintenant
    opportunite.date_cloture = maintenant if nouvelle_etape in ETAPES_FINALES else None
    # `full_clean` avant d'ecrire : le message d'erreur reste lisible, et la
    # contrainte CHECK n'est pas atteinte par surprise.
    opportunite.full_clean(exclude=["lead", "entreprise", "contact", "proprietaire"])
    opportunite.save()

    PassageEtape.objects.filter(
        opportunite=opportunite, etape=ancienne, sortie_le__isnull=True
    ).update(sortie_le=maintenant)
    PassageEtape.objects.create(
        opportunite=opportunite, etape=nouvelle_etape, entree_le=maintenant, auteur=auteur
    )

    libelles = dict(Etape.choices)
    detail = ""
    if nouvelle_etape == Etape.PERDU:
        detail = f" — motif : {opportunite.get_motif_de_perte_display()}"
        if opportunite.commentaire_perte:
            detail += f" ({opportunite.commentaire_perte})"
    _tracer(
        opportunite,
        f"{libelles.get(ancienne, ancienne)} → {libelles[nouvelle_etape]}{detail}",
        auteur,
    )
    return opportunite


@transaction.atomic
def promouvoir_lead(
    lead: Lead,
    *,
    intitule: str = "",
    formation: str = "",
    auteur=None,
    montant_estime_centimes: int = 0,
) -> Opportunite:
    """Fait entrer un lead dans le pipeline.

    Exige un rattachement a une entreprise : sans SIREN ni entreprise, une
    opportunite ne peut etre ni devisee ni deposee chez un financeur, et
    encombrerait le Kanban sans pouvoir avancer.
    """
    if lead.doublon_de_id is not None:
        raise ValidationError(
            "Ce lead est marque comme doublon du lead "
            f"#{lead.doublon_de_id}. Trancher le doublon avant de le promouvoir."
        )
    if lead.entreprise_id is None:
        raise ValidationError(
            "Ce lead n'est rattache a aucune entreprise. Resoudre le SIREN "
            "ou creer la fiche entreprise d'abord."
        )
    if hasattr(lead, "opportunite") and lead.opportunite is not None:
        return lead.opportunite

    maintenant = timezone.now()
    opportunite = Opportunite.objects.create(
        lead=lead,
        entreprise=lead.entreprise,
        contact=lead.contact,
        intitule=intitule or (lead.formation_demandee or "Demande a qualifier"),
        formation=formation,
        etape=Etape.NOUVEAU,
        probabilite=PROBABILITE_PAR_ETAPE[Etape.NOUVEAU],
        montant_estime_centimes=montant_estime_centimes,
        proprietaire=lead.proprietaire or auteur,
        date_entree_etape=maintenant,
    )
    PassageEtape.objects.create(
        opportunite=opportunite, etape=Etape.NOUVEAU, entree_le=maintenant, auteur=auteur
    )
    _tracer(opportunite, f"Opportunite ouverte depuis le lead #{lead.pk}.", auteur)
    return opportunite

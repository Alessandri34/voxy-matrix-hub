"""Propagation d'une opposition sur les contacts deja en base.

Le champ `Contact.oppose` duplique l'information de la table des oppositions.
C'est volontaire : une requete d'envoi mal ecrite peut oublier une jointure,
elle n'oubliera pas une colonne. Encore faut-il que la colonne suive.
"""

from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.crm.models import Contact, Opposition


@receiver(post_save, sender=Opposition, dispatch_uid="crm_propager_opposition")
def propager_opposition(sender, instance: Opposition, created, **kwargs):
    if not created:
        return
    criteres = Q(pk__in=[])
    if instance.email_normalise:
        criteres |= Q(email_normalise=instance.email_normalise)
    if instance.telephone_normalise:
        criteres |= Q(telephone_normalise=instance.telephone_normalise)
    if instance.siren:
        criteres |= Q(entreprise__siren=instance.siren)
    # `update()` et non une boucle de `save()` : une opposition portant sur un
    # SIREN peut toucher dix contacts, et le journal d'audit conserve de toute
    # facon la creation de l'opposition, qui est l'acte a tracer.
    Contact.objects.filter(criteres).exclude(oppose=True).update(oppose=True)

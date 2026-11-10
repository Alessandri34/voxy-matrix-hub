"""Ecriture automatique du journal.

Le choix fait ici : des recepteurs branches sans `sender`, qui filtrent sur une
liste de modeles declaree dans les reglages (`AUDIT_MODELES`). Brancher par
`sender` obligerait a importer les modeles au chargement de l'application, ce
qui cree des dependances circulaires des que deux applications se surveillent.

Les valeurs avant/apres sont relues en base dans `pre_save`. C'est une requete
supplementaire par enregistrement : assumee, parce qu'un journal qui dit
« le champ a change » sans dire de quoi vers quoi ne sert a rien le jour ou un
montant devient faux.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save

from apps.audit.contexte import acteur_courant, ip_courante, origine_courante
from apps.audit.models import Action, EntreeJournal

#: Champs jamais recopies dans le journal, quelle que soit l'application.
CHAMPS_MASQUES = {"password", "secret", "token", "cle_api", "cle_privee"}

#: Au-dela, la valeur est tronquee : le journal n'est pas une copie de la base.
LONGUEUR_MAX = 500


def _modeles_surveilles() -> set[str]:
    return {m.lower() for m in getattr(settings, "AUDIT_MODELES", ())}


def _surveille(sender) -> bool:
    try:
        etiquette = sender._meta.label.lower()
    except AttributeError:
        return False
    return etiquette in _modeles_surveilles()


logger = logging.getLogger(__name__)


def _lisible(valeur):
    """Rend une valeur de champ comparable et stockable en JSON."""
    if valeur is None or isinstance(valeur, bool | int | float):
        return valeur
    if isinstance(valeur, dict | list):
        # Un payload d'origine Meta peut peser plusieurs kilo-octets : on note
        # qu'il a change, pas son contenu, qui est deja conserve sur l'objet.
        return f"<{type(valeur).__name__} de {len(valeur)} element(s)>"
    texte = str(valeur)
    return texte if len(texte) <= LONGUEUR_MAX else texte[:LONGUEUR_MAX] + "…"


def _valeurs(instance) -> dict:
    valeurs = {}
    for champ in instance._meta.concrete_fields:
        if champ.name in CHAMPS_MASQUES:
            continue
        # Un champ `auto_now` change a chaque enregistrement : le garder
        # ferait du journal une ligne par `save()`, meme quand rien d'autre
        # n'a bouge — exactement le bruit qui rend un journal illisible. La
        # date de l'action est de toute facon portee par l'entree elle-meme.
        if getattr(champ, "auto_now", False):
            continue
        if isinstance(champ, models.ForeignKey):
            valeurs[champ.name] = _lisible(getattr(instance, champ.attname))
        else:
            valeurs[champ.name] = _lisible(getattr(instance, champ.name, None))
    return valeurs


def _libelle(instance) -> str:
    """Le `__str__` de l'objet, ou un repli si on ne peut pas le calculer.

    Un `__str__` de modele Django traverse librement ses relations. Pendant
    une suppression en cascade, la ligne liee peut deja avoir disparu :
    `Inscription.__str__` lit son contact, et le contact n'est plus la. Sans
    ce garde-fou, l'exception remonte depuis le signal et **fait echouer la
    suppression entiere** — le journal d'audit casse l'operation qu'il a pour
    seul role d'enregistrer. Trouve en vidant les donnees de demonstration ;
    aucun des 501 tests ne le voyait, parce qu'aucun ne supprimait une
    inscription dont le contact partait dans la meme cascade.

    Le repli reste identifiant : le nom du modele et la cle primaire suffisent
    a retrouver ce dont il s'agit.
    """
    try:
        return _lisible(instance)[:200]
    except Exception:  # noqa: BLE001 — aucune exception ne doit passer
        logger.warning(
            "Libelle illisible pour %s#%s : la trace est ecrite sans lui.",
            instance._meta.label,
            instance.pk,
            exc_info=True,
        )
        return f"{instance._meta.label}#{instance.pk}"


def _ecrire(instance, action: str, changements: dict | None = None) -> None:
    EntreeJournal.objects.create(
        acteur=acteur_courant(),
        origine=origine_courante(),
        action=action,
        type_objet=ContentType.objects.get_for_model(instance.__class__),
        id_objet=str(instance.pk) if instance.pk is not None else "",
        libelle_objet=_libelle(instance),
        changements=changements or {},
        adresse_ip=ip_courante(),
    )


def avant_enregistrement(sender, instance, **kwargs):
    if not _surveille(sender) or instance.pk is None:
        return
    try:
        ancien = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Creation avec cle primaire imposee : rien a comparer.
        instance._valeurs_avant = None
        return
    instance._valeurs_avant = _valeurs(ancien)


def apres_enregistrement(sender, instance, created, **kwargs):
    if not _surveille(sender):
        return
    if created:
        _ecrire(instance, Action.CREATION)
        return
    avant = getattr(instance, "_valeurs_avant", None)
    if avant is None:
        return
    apres = _valeurs(instance)
    changements = {
        champ: [avant.get(champ), apres.get(champ)]
        for champ in apres
        if avant.get(champ) != apres.get(champ)
    }
    if not changements:
        # Un `save()` qui ne change rien n'a pas sa place au journal : sinon
        # le journal se remplit de lignes vides et devient illisible.
        return
    _ecrire(instance, Action.MODIFICATION, changements)


def apres_suppression(sender, instance, **kwargs):
    if not _surveille(sender):
        return
    _ecrire(instance, Action.SUPPRESSION, {"__supprime__": [_valeurs(instance), None]})


def brancher() -> None:
    pre_save.connect(avant_enregistrement, dispatch_uid="audit_avant")
    post_save.connect(apres_enregistrement, dispatch_uid="audit_apres")
    post_delete.connect(apres_suppression, dispatch_uid="audit_suppression")

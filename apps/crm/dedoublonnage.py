"""Reconnaitre un prospect deja connu.

Le probleme reel : la meme personne arrive par Meta lundi, remplit le
formulaire du site jeudi, et figure dans le CSV de l'ancien tableur. Trois
lignes, un seul client. Compte trois fois, le cout par lead d'une campagne est
divise par trois et la decision d'investissement devient fausse.

La regle tenue ici : **on ne fusionne que sur un signal fort, on ne cree
jamais en silence sur un signal fort.** Deux niveaux de certitude, et un
traitement different pour chacun.

- **Certain** — meme identifiant Meta, meme email, ou meme telephone. On
  n'ecrit pas de second lead : on enrichit le premier.
- **Probable** — meme SIREN et meme nom, ou meme nom et meme raison sociale.
  On ecrit le lead mais on le marque `doublon_de` : il reste visible, hors
  pipeline, et un humain tranche.

Ce qui n'est **jamais** un critere : le nom seul (les homonymes existent), le
domaine de l'email seul (dix salaries partagent `@restaurant-x.fr`), la
raison sociale seule (« Le Comptoir » existe quatre fois a Montpellier).
"""

from __future__ import annotations

from dataclasses import dataclass

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q

from apps.crm.models import Activite, Contact, Entreprise, Lead, TypeActivite
from apps.crm.normalisation import (
    normaliser_email,
    normaliser_nom,
    normaliser_siren,
    normaliser_telephone,
)

CERTAIN = "certain"
PROBABLE = "probable"
AUCUN = "aucun"

#: Champs qu'un second passage peut remplir s'ils sont vides, jamais ecraser.
CHAMPS_ENRICHISSABLES = (
    "nom_declare",
    "email_declare",
    "telephone_declare",
    "entreprise_declaree",
    "formation_demandee",
    "meta_leadgen_id",
    "meta_formulaire_id",
    "meta_formulaire_nom",
    "meta_campagne_id",
    "meta_campagne_nom",
    "meta_ensemble_id",
    "meta_ensemble_nom",
    "meta_publicite_id",
    "meta_publicite_nom",
)


@dataclass(frozen=True)
class Verdict:
    """Ce que le dedoublonnage a trouve, et sur quoi il s'appuie."""

    lead: Lead | None
    certitude: str
    motif: str

    def __bool__(self) -> bool:
        return self.lead is not None


def chercher_doublon(
    *,
    email: str = "",
    telephone: str = "",
    nom: str = "",
    siren: str = "",
    entreprise: str = "",
    meta_leadgen_id: str = "",
    exclure: int | None = None,
) -> Verdict:
    """Cherche un lead deja connu. Ne modifie rien.

    L'ordre des criteres est l'ordre de fiabilite : le premier qui repond
    gagne. Les doublons deja marques sont exclus de la recherche, sinon une
    chaine de doublons pointerait sur un doublon et non sur l'original.
    """
    base = Lead.objects.filter(doublon_de__isnull=True)
    if exclure is not None:
        base = base.exclude(pk=exclure)

    if identifiant := (meta_leadgen_id or "").strip():
        trouve = base.filter(meta_leadgen_id=identifiant).first()
        if trouve:
            return Verdict(trouve, CERTAIN, f"identifiant Meta {identifiant} deja recu")

    if e := normaliser_email(email):
        trouve = base.filter(email_normalise=e).first()
        if trouve:
            return Verdict(trouve, CERTAIN, f"email {e}")

    if t := normaliser_telephone(telephone):
        trouve = base.filter(telephone_normalise=t).first()
        if trouve:
            return Verdict(trouve, CERTAIN, f"telephone {t}")

    n = normaliser_nom(nom)
    if n and (s := normaliser_siren(siren)):
        trouve = base.filter(nom_normalise=n, entreprise__siren=s).first()
        if trouve:
            return Verdict(trouve, PROBABLE, f"nom « {n} » chez le SIREN {s}")

    if n and (raison := normaliser_nom(entreprise)):
        trouve = base.filter(
            Q(nom_normalise=n)
            & (
                Q(entreprise_declaree__iexact=entreprise.strip())
                | Q(entreprise__denomination_normalisee=raison)
            )
        ).first()
        if trouve:
            return Verdict(trouve, PROBABLE, f"nom « {n} » chez « {raison} »")

    return Verdict(None, AUCUN, "")


def _enrichir(lead: Lead, donnees: dict) -> dict:
    """Remplit les champs vides du lead existant. Ne remplace jamais.

    Renvoie ce qui a reellement ete ajoute : sans cela, l'activite ecrite
    ensuite dirait « enrichi » pour une arrivee qui n'apportait rien.
    """
    ajouts = {}
    for champ in CHAMPS_ENRICHISSABLES:
        nouvelle = (donnees.get(champ) or "").strip() if champ in donnees else ""
        if nouvelle and not (getattr(lead, champ) or ""):
            setattr(lead, champ, nouvelle)
            ajouts[champ] = nouvelle
    if ajouts:
        lead.save()
    return ajouts


def _tracer(lead: Lead, type_activite: str, contenu: str, auteur=None) -> Activite:
    return Activite.objects.create(
        type=type_activite,
        type_objet=ContentType.objects.get_for_model(Lead),
        id_objet=str(lead.pk),
        auteur=auteur,
        contenu=contenu,
    )


@transaction.atomic
def enregistrer_lead(donnees: dict, *, auteur=None) -> tuple[Lead, bool, Verdict]:
    """Point d'entree unique pour tout lead, d'ou qu'il vienne.

    Le webhook Meta, le formulaire du site, l'import CSV et la saisie manuelle
    passent tous par ici. C'est la condition pour que le dedoublonnage soit
    reellement applique : un seul chemin d'ecriture, teste une fois.

    Renvoie `(lead, cree, verdict)`. `cree` est faux quand un lead existant a
    ete enrichi au lieu d'en ecrire un second.
    """
    verdict = chercher_doublon(
        email=donnees.get("email_declare", ""),
        telephone=donnees.get("telephone_declare", ""),
        nom=donnees.get("nom_declare", ""),
        siren=donnees.get("siren", ""),
        entreprise=donnees.get("entreprise_declaree", ""),
        meta_leadgen_id=donnees.get("meta_leadgen_id", ""),
    )

    if verdict.certitude == CERTAIN:
        ajouts = _enrichir(verdict.lead, donnees)
        detail = ", ".join(sorted(ajouts)) if ajouts else "rien de nouveau"
        _tracer(
            verdict.lead,
            TypeActivite.SYSTEME,
            f"Seconde arrivee du meme prospect ({verdict.motif}), "
            f"source {donnees.get('source', 'inconnue')}. Apporte : {detail}. "
            f"Aucun second lead n'a ete cree.",
            auteur,
        )
        return verdict.lead, False, verdict

    champs = {c.name for c in Lead._meta.concrete_fields}
    lead = Lead(**{c: v for c, v in donnees.items() if c in champs})
    if verdict.certitude == PROBABLE:
        lead.doublon_de = verdict.lead
    lead.save()

    if verdict.certitude == PROBABLE:
        _tracer(
            lead,
            TypeActivite.SYSTEME,
            f"Doublon probable du lead #{verdict.lead.pk} ({verdict.motif}). "
            "Ecrit hors pipeline : a trancher a la main. Si ce n'est pas un "
            "doublon, vider le champ « doublon de ».",
            auteur,
        )
    return lead, True, verdict


def rattacher_contact(lead: Lead, entreprise: Entreprise, *, auteur=None) -> Contact:
    """Cree ou retrouve le contact du lead dans cette entreprise.

    `get_or_create` sur l'email normalise : la contrainte
    `un_email_par_entreprise` interdit le doublon en base, autant ne pas
    attendre l'exception pour s'en apercevoir.
    """
    email = normaliser_email(lead.email_declare)
    telephone = normaliser_telephone(lead.telephone_declare)
    morceaux = (lead.nom_declare or "").strip().split(" ", 1)
    prenom, nom = (morceaux[0], morceaux[1]) if len(morceaux) == 2 else ("", morceaux[0])

    contact = None
    if email:
        contact = Contact.objects.filter(entreprise=entreprise, email_normalise=email).first()
    if contact is None and telephone:
        contact = Contact.objects.filter(
            entreprise=entreprise, telephone_normalise=telephone
        ).first()
    if contact is None:
        contact = Contact.objects.create(
            entreprise=entreprise,
            prenom=prenom,
            nom=nom or "Inconnu",
            email=lead.email_declare,
            telephone=lead.telephone_declare,
            base_legale="consentement"
            if lead.source in {"meta_lead_ads", "formulaire_site"}
            else "interet_legitime",
            origine_collecte=lead.get_source_display(),
            date_collecte=lead.date_reception,
        )
    lead.entreprise = entreprise
    lead.contact = contact
    lead.save()
    return contact

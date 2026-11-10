"""Du signal BODACC au lead qualifie.

Le BODACC dit qu'une entreprise vient d'etre immatriculee. Il ne dit ni son
secteur, ni sa taille, ni — surtout — si elle s'est opposee a la
prospection commerciale. L'API Recherche d'entreprises dit les trois.

**L'ordre compte et il coute.** Chaque immatriculation demande un appel de
qualification, et cette API plafonne a 7 requetes par seconde par adresse.
On ecarte donc d'abord ce qui se voit sans appeler (forme juridique,
SIREN deja connu), puis on qualifie le reste.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import date

import httpx
from django.db import transaction

from apps.crm.models import SourceLead
from apps.sourcing.bodacc import Immatriculation, Veille, veiller

logger = logging.getLogger(__name__)

#: Pause entre deux qualifications. L'API Recherche d'entreprises plafonne a
#: 7 requetes par seconde et par adresse : 4/s laisse de la marge pour les
#: autres usages. Mise a zero dans les tests, ou elle ne protegerait rien et
#: couterait des secondes a chaque passage.
PAUSE_QUALIFICATION = 0.25

#: Sections NAF sans objet pour une offre de formation a la communication :
#: administration publique, activites extra-territoriales, menages
#: employeurs. Les ecarter evite des appels et des leads inexploitables.
SECTIONS_ECARTEES = frozenset({"O", "T", "U"})


@dataclass
class Resultat:
    retenus: list = field(default_factory=list)
    qualifies: int = 0
    opposees: int = 0
    deja_connues: int = 0
    hors_cible: int = 0
    introuvables: int = 0
    leads_crees: int = 0
    applique: bool = False
    veille: Veille | None = None

    def resume(self) -> str:
        lignes = []
        if self.veille is not None:
            lignes.append(self.veille.resume())
        lignes += [
            f"  {self.qualifies} qualifiee(s) aupres de Recherche d'entreprises",
            f"  {self.opposees} ecartee(s) — opposees a la prospection",
            f"  {self.deja_connues} deja en base",
            f"  {self.hors_cible} hors cible (section NAF)",
            f"  {self.introuvables} introuvable(s) dans l'API "
            "(unite non diffusible, ou publication plus rapide que l'INSEE)",
            f"  → {len(self.retenus)} prospect(s) retenu(s), "
            f"{self.leads_crees} lead(s) {'cree(s)' if self.applique else 'a creer'}",
        ]
        return "\n".join(lignes)


def _qualifier(immat: Immatriculation, client) -> dict | None:
    from apps.crm.services.recherche_entreprises import par_siren

    return par_siren(immat.siren, client=client)


@transaction.atomic
def veiller_et_integrer(
    *,
    departement: str = "",
    depuis: date | None = None,
    pages_max: int = 3,
    appliquer: bool = False,
    client_bodacc: httpx.Client | None = None,
    client_entreprises: httpx.Client | None = None,
) -> Resultat:
    """Releve les creations, les qualifie, et cree les leads retenus.

    Apercu par defaut : on ne verse pas quarante prospects par jour dans le
    CRM sans avoir regarde ce que le filtre laisse passer.
    """
    from apps.crm.dedoublonnage import enregistrer_lead
    from apps.crm.models import Entreprise, EtapeAmont, Opposition
    from apps.crm.services.entreprises import enregistrer_depuis_api

    class Annuler(Exception):
        pass

    resultat = Resultat(applique=appliquer)
    resultat.veille = veiller(
        departement=departement, depuis=depuis, pages_max=pages_max, client=client_bodacc
    )
    connues = set(Entreprise.objects.exclude(siren="").values_list("siren", flat=True))

    def travailler():
        for immat in resultat.veille.immatriculations:
            if immat.siren in connues:
                resultat.deja_connues += 1
                continue

            donnees = _qualifier(immat, client_entreprises)
            resultat.qualifies += 1
            if PAUSE_QUALIFICATION:
                time.sleep(PAUSE_QUALIFICATION)

            if donnees is None:
                # Une immatriculation publiee au BODACC peut precéder sa
                # parution dans la base SIRENE, et une unite non diffusible
                # n'y figure jamais.
                resultat.introuvables += 1
                continue

            section = str(donnees.get("section_activite_principale") or "")
            if section in SECTIONS_ECARTEES:
                resultat.hors_cible += 1
                continue

            if (
                donnees.get("opposition_diffusion_commerciale") is True
                or donnees.get("statut_diffusion") == "P"
                or Opposition.est_oppose(siren=immat.siren)
            ):
                resultat.opposees += 1
                continue

            resultat.retenus.append((immat, donnees))
            connues.add(immat.siren)

            entreprise, _ = enregistrer_depuis_api(donnees)
            _, nouveau, _ = enregistrer_lead(
                {
                    "source": SourceLead.SOURCING,
                    "entreprise": entreprise,
                    "entreprise_declaree": immat.denomination or entreprise.denomination,
                    "etape_amont": EtapeAmont.IDENTIFIE,
                    "payload_origine": {
                        "origine": "bodacc",
                        "siren": immat.siren,
                        "annonce": immat.identifiant_annonce,
                        "date_parution": immat.date_parution,
                        "url": immat.url,
                    },
                    "message": (
                        f"Immatriculation publiee au BODACC le "
                        f"{immat.date_parution} — {immat.denomination or '—'}, "
                        f"{immat.ville} ({immat.code_postal}). "
                        f"NAF {donnees.get('activite_principale', '—')}. "
                        "Entreprise nouvellement creee : droits a formation "
                        "ouverts, aucun site ni avis en ligne a ce stade."
                    ),
                }
            )
            if nouveau:
                resultat.leads_crees += 1

    if appliquer:
        travailler()
    else:
        try:
            with transaction.atomic():
                travailler()
                raise Annuler
        except Annuler:
            pass
    return resultat

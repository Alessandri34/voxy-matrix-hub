"""Constitution d'une liste de prospection, sur l'API officielle.

**Pourquoi pas un scraper.** Trois raisons, verifiees le 09/11/2026 :

1. **Google interdit explicitement le scraping de Maps.** Ses conditions ne
   laissent conserver durablement que le `place_id` ; les coordonnees 30
   jours ; le nom, l'adresse, la note et les avis n'ont **aucune exception
   de cache**. Un fichier de profils Maps n'est pas conservable.
2. **`societe.com` et Pappers vendent une API** pour les memes donnees que
   l'API publique Recherche d'entreprises, que ce projet utilise deja —
   gratuite, sans credits, documentee.
3. **Seule l'API officielle porte `opposition_diffusion_commerciale`**, le
   drapeau qui dit qu'une entreprise s'est formellement opposee a la
   prospection (RGPD art. 21 §2). Sur l'echantillon heraultais, **34 %** des
   TPE des NAF cibles le portent. Une liste constituee autrement ne le sait
   pas, et demarche ces 34 % sans le savoir.

Ce module fait donc ce qu'un scraper ferait, en mieux : il cible, il filtre
les opposes, et il cree des leads dedoublonnes.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import httpx
from django.conf import settings

from apps.crm.services.recherche_entreprises import appeler, noter

logger = logging.getLogger(__name__)

#: Les codes NAF des cibles de VFormations, par famille. Modifiable sans
#: toucher au code : c'est une liste de travail, pas une regle.
FAMILLES_NAF = {
    "restauration": ["56.10A", "56.10C", "56.30Z"],
    "coiffure_esthetique": ["96.02A", "96.02B"],
    "batiment": ["43.21A", "43.22A", "43.32A", "43.34Z", "43.31Z", "41.20A"],
    "commerce": ["47.11B", "47.19B", "47.71Z", "47.76Z", "47.78C"],
    "automobile": ["45.20A", "45.20B"],
    "services": ["81.21Z", "49.32Z", "96.01B", "93.13Z"],
    "conseil_numerique": ["62.01Z", "70.22Z", "73.11Z"],
}


@dataclass
class Cible:
    """Ce qu'on cherche."""

    departement: str = ""
    codes_naf: list[str] = field(default_factory=list)
    tranches_effectif: list[str] = field(default_factory=list)
    actives_seulement: bool = True
    #: Exclure les entreprises opposees a la prospection. Par defaut oui :
    #: les garder dans une liste de demarchage n'a aucun usage legitime.
    exclure_opposees: bool = True
    #: Exclure celles dont le siege est hors du departement. L'API filtre sur
    #: les ETABLISSEMENTS : sans ce reglage, un groupe national avec une
    #: agence a Montpellier remonte comme une TPE locale.
    siege_dans_le_departement: bool = True
    pages_max: int = 4

    def __post_init__(self):
        if not self.departement:
            self.departement = getattr(settings, "DEPARTEMENT_CIBLE", "34")


@dataclass
class Prospect:
    """Une entreprise retenue, avec de quoi juger."""

    siren: str
    denomination: str
    naf: str
    naf_libelle: str
    code_postal: str
    commune: str
    tranche_effectif: str
    inscrite_repertoire_metiers: bool | None
    opposee: bool | None
    note: int
    donnees: dict


@dataclass
class Moisson:
    """Le resultat d'une recherche, et ce qui en a ete retire."""

    prospects: list[Prospect] = field(default_factory=list)
    examines: int = 0
    hors_departement: int = 0
    opposees: int = 0
    deja_connues: int = 0
    erreurs: list[str] = field(default_factory=list)

    def resume(self) -> str:
        lignes = [
            f"{self.examines} entreprise(s) examinee(s)",
            f"  {len(self.prospects)} retenue(s)",
            f"  {self.hors_departement} ecartee(s) — siege hors departement",
            f"  {self.opposees} ecartee(s) — opposees a la prospection",
            f"  {self.deja_connues} deja en base",
        ]
        if self.erreurs:
            lignes.append(f"  {len(self.erreurs)} erreur(s) : {self.erreurs[0]}")
        return "\n".join(lignes)


def _prospect(resultat: dict, departement: str) -> Prospect:
    siege = resultat.get("siege") or {}
    note, _ = noter(resultat, resultat.get("nom_complet") or "", departement)
    return Prospect(
        siren=resultat.get("siren", ""),
        denomination=resultat.get("nom_complet") or resultat.get("nom_raison_sociale") or "",
        naf=resultat.get("activite_principale") or "",
        naf_libelle=resultat.get("libelle_activite_principale") or "",
        code_postal=siege.get("code_postal") or "",
        commune=siege.get("libelle_commune") or "",
        tranche_effectif=str(resultat.get("tranche_effectif_salarie") or ""),
        inscrite_repertoire_metiers=(
            True if siege.get("activite_principale_registre_metier") else None
        ),
        opposee=resultat.get("opposition_diffusion_commerciale"),
        note=note,
        donnees=resultat,
    )


def moissonner(cible: Cible, *, client: httpx.Client | None = None) -> Moisson:
    """Interroge l'API et renvoie les entreprises retenues.

    Respecte la cadence de l'API : sa specification annonce 7 requetes par
    seconde par adresse IP et previent que les cloud publics l'atteignent.
    On reste volontairement en dessous.
    """
    from apps.crm.models import Entreprise, Opposition

    moisson = Moisson()
    sirens_connus = set(Entreprise.objects.exclude(siren="").values_list("siren", flat=True))

    for naf in cible.codes_naf or [""]:
        for page in range(1, cible.pages_max + 1):
            parametres = {
                "departement": cible.departement,
                "activite_principale": naf or None,
                "etat_administratif": "A" if cible.actives_seulement else None,
                "tranche_effectif_salarie": ",".join(cible.tranches_effectif) or None,
                "per_page": 25,
                "page": page,
                "limite_matching_etablissements": 1,
            }
            try:
                donnees = appeler("/search", parametres, client=client)
            except Exception as erreur:  # noqa: BLE001 — une panne ne doit pas tout perdre
                moisson.erreurs.append(f"{naf or 'tous NAF'} page {page} : {erreur}")
                break

            resultats = donnees.get("results") or []
            if not resultats:
                break

            for resultat in resultats:
                moisson.examines += 1
                siege = resultat.get("siege") or {}
                if (
                    cible.siege_dans_le_departement
                    and str(siege.get("departement") or "") != cible.departement
                ):
                    moisson.hors_departement += 1
                    continue

                prospect = _prospect(resultat, cible.departement)

                if cible.exclure_opposees and (
                    prospect.opposee is True
                    or resultat.get("statut_diffusion") == "P"
                    or Opposition.est_oppose(siren=prospect.siren)
                ):
                    moisson.opposees += 1
                    continue

                if prospect.siren in sirens_connus:
                    moisson.deja_connues += 1
                    continue

                moisson.prospects.append(prospect)
                sirens_connus.add(prospect.siren)

            # 4 appels/seconde : la marge sous le plafond de 7 absorbe les
            # autres usages de la meme adresse IP.
            time.sleep(0.25)

    moisson.prospects.sort(key=lambda p: p.note, reverse=True)
    return moisson

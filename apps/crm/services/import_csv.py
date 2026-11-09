"""Import des leads existants depuis un tableur.

Critere de sortie de la phase 1 : « import CSV de tes leads existants sans
doublon ». Tout passe par `enregistrer_lead`, donc par le dedoublonnage :
c'est la seule facon que la regle s'applique vraiment, plutot que d'etre
reecrite ici avec une nuance de moins.

Trois pieges d'un vrai fichier client, traites explicitement.

1. **L'encodage.** Un export Excel francais sort en `cp1252`, pas en UTF-8.
   Lu en UTF-8, « Bénédicte » devient illisible ou leve une exception. On
   essaie plusieurs encodages, dans l'ordre du plus probable.
2. **Le separateur.** Excel francais ecrit des points-virgules, parce que la
   virgule est le separateur decimal. Un fichier lu avec le mauvais
   separateur donne une seule colonne, et l'import « reussit » en creant des
   lignes vides.
3. **Les en-tetes.** « Tel », « Téléphone », « tel portable », « Mobile »
   designent la meme chose. Une correspondance rigide obligerait a
   retravailler le fichier a la main, ce que personne ne fait.

Et un choix : **l'apercu est le mode par defaut.** On n'importe pas le
tableur d'un client en aveugle.
"""

from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass, field

from django.db import transaction

from apps.crm.dedoublonnage import PROBABLE, enregistrer_lead
from apps.crm.models import SourceLead
from apps.crm.normalisation import (
    normaliser_email,
    normaliser_nom,
    normaliser_siren,
    normaliser_telephone,
    sans_accent,
)

logger = logging.getLogger(__name__)

#: Dans l'ordre du plus probable pour un export francais.
ENCODAGES = ("utf-8-sig", "cp1252", "latin-1")

#: Un en-tete est reconnu si sa forme normalisee contient l'un de ces mots.
#: L'ordre compte : le premier modele qui correspond gagne, donc les plus
#: specifiques d'abord (« nom entreprise » avant « nom »).
MODELES_COLONNES = (
    (
        "entreprise_declaree",
        ("raison sociale", "nom entreprise", "societe", "entreprise", "enseigne"),
    ),
    ("siren", ("siren", "siret")),
    ("email_declare", ("email", "mail", "courriel", "e mail")),
    ("telephone_declare", ("telephone", "tel", "mobile", "portable", "gsm")),
    ("nom_declare", ("nom complet", "nom et prenom", "contact", "nom", "prenom")),
    ("formation_demandee", ("formation", "offre", "produit", "interet")),
    ("message", ("message", "commentaire", "note", "remarque", "besoin")),
)


@dataclass
class Rapport:
    """Ce que l'import a fait, ou ferait. Lisible sans relire le fichier."""

    lignes_lues: int = 0
    crees: int = 0
    fusionnes: int = 0
    doublons_probables: int = 0
    rejetes: int = 0
    encodage: str = ""
    separateur: str = ""
    colonnes_reconnues: dict = field(default_factory=dict)
    colonnes_ignorees: list = field(default_factory=list)
    motifs_de_rejet: list = field(default_factory=list)
    applique: bool = False

    def resume(self) -> str:
        etat = "APPLIQUE" if self.applique else "APERCU — rien n'a ete ecrit"
        lignes = [
            f"{etat}",
            f"  fichier lu en {self.encodage}, separateur « {self.separateur} »",
            f"  {self.lignes_lues} ligne(s) de donnees",
            f"  {self.crees} lead(s) nouveau(x)",
            f"  {self.fusionnes} deja connu(s) — enrichi(s), pas dupliqué(s)",
            f"  {self.doublons_probables} doublon(s) probable(s) — ecrit(s) hors pipeline",
            f"  {self.rejetes} ligne(s) rejetee(s)",
        ]
        if self.colonnes_reconnues:
            lignes.append("  colonnes reconnues :")
            for entete, champ in self.colonnes_reconnues.items():
                lignes.append(f"    « {entete} » → {champ}")
        if self.colonnes_ignorees:
            lignes.append(f"  colonnes ignorees : {', '.join(self.colonnes_ignorees)}")
        if self.motifs_de_rejet:
            lignes.append("  rejets :")
            lignes.extend(f"    ligne {n} : {motif}" for n, motif in self.motifs_de_rejet[:20])
            if len(self.motifs_de_rejet) > 20:
                lignes.append(f"    … et {len(self.motifs_de_rejet) - 20} autre(s)")
        return "\n".join(lignes)


def decoder(octets: bytes) -> tuple[str, str]:
    """Renvoie `(texte, encodage)`. Leve `UnicodeDecodeError` en dernier recours."""
    derniere = None
    for encodage in ENCODAGES:
        try:
            return octets.decode(encodage), encodage
        except UnicodeDecodeError as erreur:
            derniere = erreur
    raise derniere


def deviner_separateur(texte: str) -> str:
    """Le point-virgule d'abord : c'est ce qu'ecrit Excel en francais.

    `csv.Sniffer` se trompe sur un fichier dont un champ contient une
    virgule — ce qui est le cas de toute adresse postale. On compte donc les
    candidats sur la ligne d'en-tete, qui, elle, n'en contient pas.
    """
    premiere = texte.splitlines()[0] if texte.splitlines() else ""
    comptes = {candidat: premiere.count(candidat) for candidat in (";", ",", "\t", "|")}
    meilleur = max(comptes, key=lambda c: comptes[c])
    return meilleur if comptes[meilleur] else ";"


def associer_colonnes(entetes: list[str]) -> tuple[dict, list]:
    """Associe chaque en-tete du fichier a un champ de lead.

    Un champ deja associe n'est pas reassocie : si le fichier porte
    « Email » et « Email 2 », seule la premiere colonne alimente le champ,
    la seconde est signalee comme ignoree plutot que d'ecraser la premiere.
    """
    associations, ignorees, pris = {}, [], set()
    for entete in entetes:
        propre = " ".join(sans_accent(entete or "").lower().replace("_", " ").split())
        if not propre:
            continue
        trouve = None
        for champ, mots in MODELES_COLONNES:
            if champ in pris:
                continue
            if any(mot in propre for mot in mots):
                trouve = champ
                break
        if trouve:
            associations[entete] = trouve
            pris.add(trouve)
        else:
            ignorees.append(entete)
    return associations, ignorees


def _ligne_vers_donnees(ligne: dict, associations: dict) -> dict:
    donnees = {}
    for entete, champ in associations.items():
        valeur = (ligne.get(entete) or "").strip()
        if valeur:
            donnees[champ] = valeur
    return donnees


def _exploitable(donnees: dict) -> str:
    """Une ligne doit porter au moins un moyen de recontacter la personne.

    Sans email, sans telephone et sans nom d'entreprise, le lead ne peut etre
    ni appele, ni dedoublonne, ni rattache : il n'encombrerait le CRM que
    pour gonfler un compteur.
    """
    if normaliser_email(donnees.get("email_declare", "")):
        return ""
    if normaliser_telephone(donnees.get("telephone_declare", "")):
        return ""
    if normaliser_nom(donnees.get("entreprise_declaree", "")) and normaliser_nom(
        donnees.get("nom_declare", "")
    ):
        return ""
    return (
        "aucun moyen de contact exploitable (ni email, ni telephone valide, "
        "ni couple nom + entreprise)"
    )


def importer(
    octets: bytes,
    *,
    source: str = SourceLead.IMPORT_CSV,
    appliquer: bool = False,
    proprietaire=None,
) -> Rapport:
    """Lit le fichier et, si `appliquer`, ecrit les leads.

    En apercu, tout le travail est fait — lecture, normalisation,
    dedoublonnage — puis la transaction est annulee. Le rapport dit donc
    exactement ce qui se passerait, et non une estimation.
    """
    texte, encodage = decoder(octets)
    separateur = deviner_separateur(texte)
    lecteur = csv.DictReader(io.StringIO(texte), delimiter=separateur)
    entetes = lecteur.fieldnames or []
    associations, ignorees = associer_colonnes(entetes)

    rapport = Rapport(
        encodage=encodage,
        separateur=separateur,
        colonnes_reconnues=associations,
        colonnes_ignorees=ignorees,
        applique=appliquer,
    )
    if not associations:
        rapport.motifs_de_rejet.append(
            (1, f"aucune colonne reconnue parmi : {', '.join(entetes) or '(fichier vide)'}")
        )
        return rapport

    class Annuler(Exception):
        pass

    def travailler():
        for numero, ligne in enumerate(lecteur, start=2):
            rapport.lignes_lues += 1
            donnees = _ligne_vers_donnees(ligne, associations)
            motif = _exploitable(donnees)
            if motif:
                rapport.rejetes += 1
                rapport.motifs_de_rejet.append((numero, motif))
                continue

            siren = normaliser_siren(donnees.pop("siren", ""))
            charge = {**donnees, "source": source}
            if siren:
                # Le SIREN du fichier n'est pas un champ de Lead : il passe
                # par le payload, ou la resolution SIREN le relira.
                charge["payload_origine"] = {"siren": siren, "ligne_csv": numero}
            if proprietaire is not None:
                charge["proprietaire"] = proprietaire

            _, cree, verdict = enregistrer_lead(charge)
            if not cree:
                rapport.fusionnes += 1
            elif verdict.certitude == PROBABLE:
                rapport.doublons_probables += 1
            else:
                rapport.crees += 1

    if appliquer:
        with transaction.atomic():
            travailler()
    else:
        try:
            with transaction.atomic():
                travailler()
                raise Annuler
        except Annuler:
            pass
    return rapport

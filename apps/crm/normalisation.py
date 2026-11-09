"""Formes normalisees des identifiants, pour comparer ce qui est comparable.

Un meme prospect arrive par trois chemins — un formulaire Meta, le formulaire
du site, un fichier CSV — et s'ecrit trois fois differemment :
« 06 12 34 56 78 », « +33 6 12 34 56 78 », « 0612345678 ». Sans forme
normalisee stockee en colonne, le dedoublonnage ne peut pas s'appuyer sur un
index et devient faux des que le fichier grossit.

Ces fonctions ne valident pas : elles normalisent. Une entree inexploitable
renvoie une chaine vide, jamais une exception — un lead qui arrive de Meta avec
un telephone mal saisi doit entrer dans le CRM, pas disparaitre.
"""

from __future__ import annotations

import re
import unicodedata

#: Indicatifs acceptes pour la France metropolitaine et les DOM.
#: La liste est volontairement courte : la cible est l'Herault.
_INDICATIF_FR = "33"


def _chiffres(valeur: str) -> str:
    return re.sub(r"\D", "", valeur or "")


def sans_accent(valeur: str) -> str:
    """« Hôtellerie » devient « Hotellerie » : deux saisies, une seule cle."""
    decompose = unicodedata.normalize("NFKD", valeur or "")
    return "".join(c for c in decompose if not unicodedata.combining(c))


def normaliser_siren(valeur: str) -> str:
    """9 chiffres, ou chaine vide. Accepte un SIRET et en extrait le SIREN."""
    chiffres = _chiffres(valeur)
    if len(chiffres) == 14:
        chiffres = chiffres[:9]
    return chiffres if len(chiffres) == 9 else ""


def siren_valide(valeur: str) -> bool:
    """Controle de Luhn.

    Un SIREN n'est pas un numero libre : son dernier chiffre est une cle.
    Verifier la cle arrete les fautes de frappe avant qu'elles ne creent une
    deuxieme fiche entreprise pour le meme client.
    """
    siren = normaliser_siren(valeur)
    if not siren:
        return False
    total = 0
    for position, caractere in enumerate(siren):
        chiffre = int(caractere)
        # Les rangs pairs vus de la gauche (2e, 4e, 6e, 8e) sont doubles.
        if position % 2 == 1:
            chiffre *= 2
            if chiffre > 9:
                chiffre -= 9
        total += chiffre
    return total % 10 == 0


def normaliser_email(valeur: str) -> str:
    """Minuscules, sans espace, sans prefixe « mailto: ».

    Volontairement conservateur : les points de la partie locale ne sont PAS
    retires. Chez Gmail « p.alessandri@ » et « palessandri@ » sont la meme
    boite, mais ailleurs ce sont deux personnes differentes. Fusionner sur
    cette base ecraserait la fiche d'un homonyme.
    """
    brut = (valeur or "").strip().lower()
    brut = re.sub(r"^mailto:", "", brut)
    brut = re.sub(r"\s+", "", brut)
    if brut.count("@") != 1:
        return ""
    locale, _, domaine = brut.partition("@")
    if not locale or "." not in domaine or domaine.startswith(".") or domaine.endswith("."):
        return ""
    return brut


def normaliser_telephone(valeur: str) -> str:
    """Forme E.164 (« +33612345678 »), ou chaine vide.

    Les formulaires Meta renvoient parfois le numero sans le zero initial :
    neuf chiffres commencant par 1-9 sont donc traites comme un numero
    francais ampute de son zero. C'est une hypothese, assumee pour une cible
    100 % heraultaise, et elle est inscrite dans les tests.
    """
    brut = (valeur or "").strip()
    international = brut.startswith("+") or brut.startswith("00")
    chiffres = _chiffres(brut)
    if not chiffres:
        return ""
    if chiffres.startswith("00"):
        chiffres = chiffres[2:]
    if chiffres.startswith(_INDICATIF_FR) and len(chiffres) == 11:
        return "+" + chiffres
    if chiffres.startswith(_INDICATIF_FR + "0") and len(chiffres) == 12:
        # « +33 06 12 34 56 78 » : indicatif ET zero national, saisi par des
        # clients qui recopient leur numero apres l'avoir compose.
        return "+" + _INDICATIF_FR + chiffres[3:]
    if chiffres.startswith("0") and len(chiffres) == 10:
        return "+" + _INDICATIF_FR + chiffres[1:]
    if len(chiffres) == 9 and chiffres[0] != "0":
        return "+" + _INDICATIF_FR + chiffres
    if international and 8 <= len(chiffres) <= 15:
        # Numero etranger : conserve tel quel, sans chercher a l'interpreter.
        return "+" + chiffres
    return ""


def normaliser_nom(valeur: str) -> str:
    """Majuscules, sans accent, sans ponctuation, espaces reduits.

    Sert de cle secondaire quand il n'y a ni email ni telephone exploitable :
    « Jean-Luc O'Brien » et « jean luc obrien » donnent la meme cle.
    """
    texte = sans_accent(valeur or "").upper()
    # L'apostrophe et le point disparaissent sans laisser d'espace : « O'BRIEN »
    # et « OBRIEN » doivent donner la meme cle, « ST. PIERRE » et « ST PIERRE »
    # aussi. Le tiret, lui, devient un espace : « JEAN-LUC » vaut « JEAN LUC ».
    texte = re.sub(r"['\u2019.]+", "", texte)
    texte = re.sub(r"[^A-Z0-9 ]+", " ", texte)
    return re.sub(r"\s+", " ", texte).strip()

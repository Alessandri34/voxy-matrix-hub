"""Ce qui manque a un dossier, et depuis combien de temps."""

from __future__ import annotations

from dataclasses import dataclass, field

from django.db import transaction

from apps.documents.models import PIECES_PAR_FINANCEUR, EtatPiece, Piece, TypePiece


@dataclass
class Controle:
    """L'etat des pieces d'un dossier."""

    financeur: str
    moment: str
    attendues: list = field(default_factory=list)
    manquantes: list = field(default_factory=list)
    a_verifier: list = field(default_factory=list)
    refusees: list = field(default_factory=list)
    liste_non_officielle: bool = True

    @property
    def complet(self) -> bool:
        return not self.manquantes and not self.refusees

    def resume(self) -> str:
        if self.complet:
            texte = f"Dossier {self.financeur.upper()} complet pour « {self.moment} »."
        else:
            texte = (
                f"Dossier {self.financeur.upper()} incomplet : "
                f"{len(self.manquantes)} piece(s) manquante(s)"
            )
            if self.refusees:
                texte += f", {len(self.refusees)} refusee(s)"
            texte += ".\n  Manque : " + ", ".join(
                dict(TypePiece.choices)[t] for t in self.manquantes
            )
        if self.a_verifier:
            texte += f"\n  À verifier : {len(self.a_verifier)} piece(s) recue(s)."
        return texte


def controler(dossier, moment: str = "avant_depot") -> Controle:
    """Compare les pieces presentes a celles qu'exige le financeur."""
    exigees = PIECES_PAR_FINANCEUR.get(dossier.financeur, {}).get(moment, [])
    presentes = {p.type: p for p in dossier.pieces.all()}

    controle = Controle(financeur=dossier.financeur, moment=moment, attendues=list(exigees))
    for type_piece in exigees:
        piece = presentes.get(type_piece)
        if piece is None or not piece.fournie:
            controle.manquantes.append(type_piece)
        elif piece.etat == EtatPiece.REFUSEE:
            controle.refusees.append(type_piece)
        elif piece.etat == EtatPiece.RECUE:
            controle.a_verifier.append(type_piece)
    return controle


@transaction.atomic
def preparer_les_pieces(dossier, moment: str = "avant_depot") -> int:
    """Cree les lignes « attendues » pour que la liste existe avant la piece.

    Une case a cocher vide vaut mieux qu'une liste dans la tete de quelqu'un :
    c'est ce qui fait qu'une piece manquante se voit trois semaines avant le
    depot et non la veille.
    """
    exigees = PIECES_PAR_FINANCEUR.get(dossier.financeur, {}).get(moment, [])
    deja = set(dossier.pieces.values_list("type", flat=True))
    crees = 0
    for type_piece in exigees:
        if type_piece in deja:
            continue
        Piece.objects.create(dossier=dossier, type=type_piece, obligatoire=True)
        crees += 1
    return crees

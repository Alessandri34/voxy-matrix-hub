"""Constitue une liste de prospection ciblee. Apercu par defaut."""

from django.core.management.base import BaseCommand, CommandError

from apps.audit.contexte import agir_en_tant_que
from apps.sourcing.ciblage import FAMILLES_NAF, Cible, moissonner
from apps.sourcing.integration import integrer


class Command(BaseCommand):
    help = (
        "Cherche des prospects sur l'API Recherche d'entreprises, ecarte les "
        "entreprises opposees a la prospection, et cree des leads dedoublonnes."
    )

    def add_arguments(self, parseur):
        parseur.add_argument(
            "--famille",
            action="append",
            choices=sorted(FAMILLES_NAF),
            help="Famille de metiers a cibler. Repetable. Par defaut : toutes.",
        )
        parseur.add_argument("--naf", action="append", help="Code NAF precis. Repetable.")
        parseur.add_argument("--departement", default="", help="Par defaut, DEPARTEMENT_CIBLE.")
        parseur.add_argument(
            "--effectif",
            action="append",
            help="Tranche INSEE (00, 01, 02, 03, 11, 12...). Repetable.",
        )
        parseur.add_argument(
            "--pages", type=int, default=2, help="Pages par code NAF (25 par page)."
        )
        parseur.add_argument(
            "--inclure-opposees",
            action="store_true",
            help="⚠️ Garde les entreprises opposees a la prospection. Aucun "
            "usage legitime en demarchage : reserve a une etude de marche.",
        )
        parseur.add_argument(
            "--appliquer",
            action="store_true",
            help="Cree reellement les leads. Sans ce drapeau, la commande dit ce qu'elle ferait.",
        )

    def handle(self, *args, **options):
        codes = list(options["naf"] or [])
        for famille in options["famille"] or ([] if codes else sorted(FAMILLES_NAF)):
            codes.extend(FAMILLES_NAF[famille])
        if not codes:
            raise CommandError("aucun code NAF a chercher")

        cible = Cible(
            departement=options["departement"],
            codes_naf=sorted(set(codes)),
            tranches_effectif=options["effectif"] or [],
            exclure_opposees=not options["inclure_opposees"],
            pages_max=options["pages"],
        )
        self.stdout.write(
            f"Departement {cible.departement} · {len(cible.codes_naf)} code(s) NAF · "
            f"{cible.pages_max} page(s) chacun"
        )

        with agir_en_tant_que(origine="sourcing"):
            moisson = moissonner(cible)
            self.stdout.write(moisson.resume())

            if moisson.prospects:
                self.stdout.write("\nLes dix mieux notes :")
                for p in moisson.prospects[:10]:
                    rm = {True: "artisan", None: "RM inconnu"}[p.inscrite_repertoire_metiers]
                    self.stdout.write(
                        f"  {p.note:>3}/100  {p.siren}  {p.denomination[:38]:38} "
                        f"{p.commune[:18]:18} {p.naf:8} {rm}"
                    )

            compte = integrer(moisson, appliquer=options["appliquer"])

        self.stdout.write(
            f"\n{compte['entreprises']} entreprise(s), {compte['leads']} lead(s) "
            f"nouveau(x), {compte['deja_connus']} deja connu(s)."
        )
        if options["inclure_opposees"]:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️ Les entreprises opposees a la prospection ont ete GARDEES. "
                    "Ne pas les demarcher : RGPD art. 21 §2."
                )
            )
        if not options["appliquer"]:
            self.stdout.write(
                self.style.WARNING("\nRien n'a ete ecrit. Relancer avec --appliquer.")
            )

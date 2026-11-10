"""Releve les creations d'entreprise et en fait des leads qualifies."""

from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.audit.contexte import agir_en_tant_que
from apps.sourcing.veille import veiller_et_integrer


class Command(BaseCommand):
    help = (
        "Releve au BODACC les entreprises immatriculees recemment, les "
        "qualifie aupres de Recherche d'entreprises, ecarte les opposees, "
        "et cree des leads dedoublonnes. Apercu par defaut."
    )

    def add_arguments(self, parseur):
        parseur.add_argument(
            "--jours", type=int, default=7, help="Profondeur de la veille, en jours (defaut 7)."
        )
        parseur.add_argument("--departement", default="", help="Par defaut, DEPARTEMENT_CIBLE.")
        parseur.add_argument(
            "--pages", type=int, default=3, help="Pages BODACC au maximum (100 annonces par page)."
        )
        parseur.add_argument("--appliquer", action="store_true", help="Cree reellement les leads.")

    def handle(self, *args, **options):
        depuis = date.today() - timedelta(days=options["jours"])
        self.stdout.write(
            f"Creations publiees depuis le {depuis:%d/%m/%Y}"
            f"{' dans le ' + options['departement'] if options['departement'] else ''}…"
        )
        with agir_en_tant_que(origine="veille-bodacc"):
            resultat = veiller_et_integrer(
                departement=options["departement"],
                depuis=depuis,
                pages_max=options["pages"],
                appliquer=options["appliquer"],
            )
        self.stdout.write(resultat.resume())

        if resultat.retenus:
            self.stdout.write("\nLes dix premiers :")
            for immat, donnees in resultat.retenus[:10]:
                self.stdout.write(
                    f"  {immat.date_parution}  {immat.siren}  "
                    f"{(immat.denomination or '—')[:32]:32} {immat.ville[:16]:16} "
                    f"{donnees.get('activite_principale', '—')}"
                )
        if not options["appliquer"]:
            self.stdout.write(
                self.style.WARNING("\nRien n'a ete ecrit. Relancer avec --appliquer.")
            )

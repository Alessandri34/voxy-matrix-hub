"""Import d'un fichier de leads. Apercu par defaut, ecriture sur demande."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.audit.contexte import agir_en_tant_que
from apps.crm.models import SourceLead
from apps.crm.services.import_csv import importer


class Command(BaseCommand):
    help = (
        "Importe des leads depuis un CSV, en passant par le dedoublonnage. "
        "Sans --appliquer, rien n'est ecrit : la commande dit ce qu'elle ferait."
    )

    def add_arguments(self, parseur):
        parseur.add_argument("fichier", type=str, help="Chemin du fichier CSV.")
        parseur.add_argument(
            "--appliquer",
            action="store_true",
            help="Ecrit reellement. Sans ce drapeau, la commande se contente "
            "d'un apercu — on n'importe pas le tableur d'un client en aveugle.",
        )
        parseur.add_argument(
            "--source",
            default=SourceLead.IMPORT_CSV,
            choices=SourceLead.values,
            help="Source a inscrire sur les leads. Elle determine la base "
            "legale du contact : un formulaire vaut consentement, un tableur non.",
        )

    def handle(self, *args, **options):
        chemin = Path(options["fichier"])
        if not chemin.is_file():
            raise CommandError(f"fichier introuvable : {chemin}")

        with agir_en_tant_que(origine="import-csv"):
            rapport = importer(
                chemin.read_bytes(),
                source=options["source"],
                appliquer=options["appliquer"],
            )

        self.stdout.write(rapport.resume())
        if not options["appliquer"]:
            self.stdout.write(
                self.style.WARNING("\nRien n'a ete ecrit. Relancer avec --appliquer pour importer.")
            )
        elif rapport.crees or rapport.fusionnes:
            self.stdout.write(self.style.SUCCESS("\nImport termine."))

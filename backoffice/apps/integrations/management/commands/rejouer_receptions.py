"""Rejoue les receptions qui n'ont pas abouti.

Pourquoi cette commande existe : Meta cesse de reemettre des qu'il a recu un
200, et le 200 part des que le corps brut est enregistre. Si le traitement
echoue ensuite — jeton expire, Redis tombe, Graph API indisponible — le lead
est en base mais pas dans le CRM. Sans cette commande, il faudrait le
ressaisir a la main depuis le corps brut.
"""

from django.core.management.base import BaseCommand

from apps.integrations.models import EtatReception, ReceptionWebhook


class Command(BaseCommand):
    help = "Remet en file les receptions a l'etat « recue » ou « echouee »."

    def add_arguments(self, parseur):
        parseur.add_argument(
            "--etat",
            default="tous",
            choices=["recue", "echouee", "tous"],
            help="Quelles receptions rejouer. Par defaut les deux.",
        )
        parseur.add_argument("--limite", type=int, default=200)
        parseur.add_argument(
            "--appliquer",
            action="store_true",
            help="Sans ce drapeau, la commande liste ce qu'elle rejouerait.",
        )

    def handle(self, *args, **options):
        etats = (
            [EtatReception.RECUE, EtatReception.ECHOUEE]
            if options["etat"] == "tous"
            else [options["etat"]]
        )
        receptions = ReceptionWebhook.objects.filter(
            etat__in=etats, signature_valide=True
        ).order_by("recue_le")[: options["limite"]]

        if not receptions:
            self.stdout.write("Aucune reception a rejouer.")
            return

        from apps.integrations.meta.taches import traiter_reception

        for reception in receptions:
            ligne = (
                f"#{reception.pk}  {reception.recue_le:%d/%m/%Y %H:%M:%S}  "
                f"{reception.get_etat_display()}  tentatives={reception.tentatives}"
            )
            if reception.erreur:
                ligne += f"\n    derniere erreur : {reception.erreur[:160]}"
            self.stdout.write(ligne)
            if options["appliquer"]:
                traiter_reception.delay(reception.pk)

        if options["appliquer"]:
            self.stdout.write(
                self.style.SUCCESS(f"\n{len(receptions)} reception(s) remise(s) en file.")
            )
        else:
            self.stdout.write(
                self.style.WARNING("\nRien n'a ete rejoue. Relancer avec --appliquer.")
            )

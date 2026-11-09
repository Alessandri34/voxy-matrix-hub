"""Jeu de donnees de demonstration, pour voir le pipeline fonctionner.

Les entreprises sont des TPE heraultaises plausibles, pas des « Societe A ».
Une demonstration faite sur des noms abstraits ne montre pas si l'ecran est
lisible une fois rempli de vrais libelles.

Reservee au developpement : la commande refuse de s'executer si DEBUG est
faux, parce que des leads fictifs dans la base de production fausseraient
tous les comptages de campagne.
"""

from __future__ import annotations

import random

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.audit.contexte import agir_en_tant_que
from apps.crm.dedoublonnage import enregistrer_lead, rattacher_contact
from apps.crm.models import Entreprise, Lead, SourceLead
from apps.pipeline.models import Etape, Financeur, MotifPerte, Opportunite
from apps.pipeline.services import changer_etape, promouvoir_lead

#: Le dernier champ dit l'inscription au Repertoire des Metiers, qui decide
#: du financeur : artisan -> FAFCEA a 25 €/h, commercant -> AGEFICE a 42 €/h.
#: `None` represente le cas le plus frequent dans la realite — l'API ne dit
#: rien, et nul ne vaut pas « non inscrit ».
ENTREPRISES = [
    ("Le Comptoir de la Loge", "552032534", "34000", "Montpellier", "56.10A", "Resto", False),
    ("Coiffure Melanie", "356000000", "34070", "Montpellier", "96.02A", "Coiffure", True),
    ("BTP Benali & Fils", "843105230", "34080", "Montpellier", "43.32A", "Menuiserie", True),
    ("Garage des Arceaux", "812841324", "34000", "Montpellier", "45.20A", "Reparation auto", True),
    ("Fleurs de Sete", "519986157", "34200", "Sete", "47.76Z", "Fleuriste", None),
    ("Studio Pilates Lattes", "878998562", "34970", "Lattes", "93.13Z", "Sport", False),
    ("Boulangerie du Peyrou", "487703602", "34000", "Montpellier", "10.71C", "Boulangerie", True),
    ("Taxi Herault Transfert", "792377236", "34400", "Lunel", "49.32Z", "Taxi", None),
]

CONTACTS = [
    ("Sophie", "Martin", "06 12 34 56 78"),
    ("Melanie", "Roux", "06 23 45 67 89"),
    ("Karim", "Benali", "06 34 56 78 90"),
    ("Thomas", "Delmas", "04 67 11 22 33"),
    ("Veronique", "Pages", "06 45 67 89 01"),
    ("Lea", "Fabre", "06 56 78 90 12"),
    ("Julien", "Cazals", "04 67 44 55 66"),
    ("Mehdi", "Amrani", "06 67 89 01 23"),
]

OFFRES = [
    ("Developper sa visibilite locale par la video — 21 h", "OFFRE-3", 21),
    ("Utiliser l'IA generative dans son entreprise — 14 h", "IA", 14),
    ("Creer un site internet professionnel — 21 h", "SITE", 21),
    ("Structurer sa prospection commerciale B2B — 35 h", "OFFRE-2", 35),
]

PARCOURS = [
    [Etape.CONTACTE, Etape.QUALIFIE, Etape.RDV_DIAGNOSTIC, Etape.PROPOSITION_ENVOYEE],
    [Etape.CONTACTE, Etape.QUALIFIE],
    [
        Etape.CONTACTE,
        Etape.QUALIFIE,
        Etape.RDV_DIAGNOSTIC,
        Etape.PROPOSITION_ENVOYEE,
        Etape.DOSSIER_DEPOSE,
        Etape.ACCORD_FINANCEUR,
        Etape.INSCRIT,
    ],
    [Etape.CONTACTE],
    [Etape.CONTACTE, Etape.QUALIFIE, Etape.RDV_DIAGNOSTIC],
    [Etape.CONTACTE, Etape.QUALIFIE, Etape.PERDU],
    [
        Etape.CONTACTE,
        Etape.QUALIFIE,
        Etape.RDV_DIAGNOSTIC,
        Etape.PROPOSITION_ENVOYEE,
        Etape.DOSSIER_DEPOSE,
    ],
    [],
]


class Command(BaseCommand):
    help = "Peuple la base d'un jeu de demonstration (developpement seulement)."

    def add_arguments(self, parseur):
        parseur.add_argument("--vider", action="store_true", help="Efface d'abord les donnees CRM.")

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "refuse de s'executer hors DEBUG : des leads fictifs en "
                "production fausseraient tous les comptages de campagne."
            )
        hasard = random.Random(34)

        with agir_en_tant_que(origine="peupler-demo"):
            if options["vider"]:
                Opportunite.objects.all().delete()
                Lead.objects.all().delete()
                Entreprise.objects.all().delete()
                self.stdout.write("Donnees CRM effacees.")

            maintenant = timezone.now()
            for index, (nom, siren, cp, commune, naf, activite, artisan) in enumerate(ENTREPRISES):
                entreprise, _ = Entreprise.objects.get_or_create(
                    siren=siren,
                    defaults={
                        "denomination": nom,
                        "code_postal": cp,
                        "commune": commune,
                        "naf": naf,
                        "naf_libelle": activite,
                        "etat_administratif": "A",
                        "tranche_effectif": hasard.choice(["00", "01", "02", "03"]),
                        "inscrite_repertoire_metiers": artisan,
                        "source_resolution": "peupler-demo",
                    },
                )
                prenom, patronyme, telephone = CONTACTS[index]
                intitule, code, heures = OFFRES[index % len(OFFRES)]

                # Un lead d'autant plus ancien que l'affaire est avancee.
                age = timezone.timedelta(days=3 + index * 4, hours=hasard.randint(0, 20))
                lead, cree, _ = enregistrer_lead(
                    {
                        "source": hasard.choice(
                            [SourceLead.META_LEAD_ADS, SourceLead.FORMULAIRE_SITE]
                        ),
                        "nom_declare": f"{prenom} {patronyme}",
                        "email_declare": f"{prenom.lower()}@{nom.split()[0].lower()}-34.fr",
                        "telephone_declare": telephone,
                        "entreprise_declaree": nom,
                        "formation_demandee": intitule,
                        "meta_campagne_nom": "Visibilite locale — Herault",
                        "meta_ensemble_nom": f"{activite} 34",
                        "date_reception": maintenant - age,
                    }
                )
                if not cree:
                    continue
                rattacher_contact(lead, entreprise)

                parcours = PARCOURS[index]
                # Les deux derniers leads restent sans contact : ils
                # declenchent l'alerte des 24 h, qu'il faut pouvoir voir.
                if parcours:
                    lead.date_premier_contact = lead.date_reception + timezone.timedelta(hours=2)
                    lead.save()

                if not parcours:
                    continue

                affaire = promouvoir_lead(
                    lead,
                    intitule=intitule,
                    formation=code,
                    montant_estime_centimes=hasard.choice([49000, 118000, 195000, 290000]),
                )
                affaire.duree_heures = heures
                affaire.financeur_probable = hasard.choice(
                    [Financeur.AGEFICE, Financeur.FAFCEA, Financeur.INDETERMINE]
                )
                affaire.save()

                instant = lead.date_reception + timezone.timedelta(hours=4)
                for etape in parcours:
                    instant += timezone.timedelta(days=hasard.randint(1, 6))
                    changer_etape(
                        affaire,
                        etape,
                        motif_de_perte=MotifPerte.RESTE_A_CHARGE if etape == Etape.PERDU else "",
                        maintenant=min(instant, maintenant),
                    )

            self._dossiers(hasard)

        self.stdout.write(
            self.style.SUCCESS(
                f"{Entreprise.objects.count()} entreprises, {Lead.objects.count()} leads, "
                f"{Opportunite.objects.count()} affaires. "
                f"{Lead.objects.filter(date_premier_contact__isnull=True).count()} lead(s) "
                "sans contact — l'alerte des 24 h doit apparaitre."
            )
        )

    def _dossiers(self, hasard):
        """Quelques dossiers de financement, dont un dont la fenetre est
        fermee : c'est le cas qu'il faut pouvoir voir a l'ecran."""
        from apps.financement.bareme import Modalite
        from apps.financement.models import Dossier, EtatDossier
        from apps.financement.routage import router_entreprise
        from apps.financement.services import figer_calcul

        aujourd_hui = timezone.localdate()
        cas = [
            # (jours avant le debut, etat, exonere_tva)
            (45, EtatDossier.A_DEPOSER, True),
            (5, EtatDossier.A_DEPOSER, False),  # AGEFICE : fenetre fermee
            (90, EtatDossier.BROUILLON, True),
            (20, EtatDossier.DEPOSE, True),
        ]
        affaires = list(Opportunite.objects.select_related("entreprise")[: len(cas)])
        for affaire, (jours, etat, exonere) in zip(affaires, cas, strict=False):
            routage = router_entreprise(affaire.entreprise)
            connus = ("fafcea", "agefice")
            financeur = routage.financeur if routage.financeur in connus else "agefice"
            dossier = Dossier.objects.create(
                opportunite=affaire,
                financeur=financeur,
                etat=etat,
                date_debut_formation=aujourd_hui + timezone.timedelta(days=jours),
                heures=affaire.duree_heures or 21,
                modalite=Modalite.PRESENTIEL,
                nb_stagiaires=hasard.choice([1, 1, 2]),
                prix_ht_centimes=affaire.montant_estime_centimes or 150000,
                cfp_centimes=hasard.choice([None, 9000, 12000, 500]),
                exonere_tva=exonere,
                point_accueil="CCI Herault — Montpellier" if etat == EtatDossier.DEPOSE else "",
                date_depot=aujourd_hui - timezone.timedelta(days=3)
                if etat == EtatDossier.DEPOSE
                else None,
            )
            figer_calcul(dossier)

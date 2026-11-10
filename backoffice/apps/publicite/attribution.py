"""La chaine qui va de l'euro depense au client forme.

Une regie sait dire le cout par clic et le cout par lead. Elle ne sait pas
dire le **cout par client**, parce qu'elle ignore tout ce qui se passe apres
le formulaire. Le back-office, lui, connait la suite.

⚠️ **Ce que ces chiffres ne sont pas.** C'est une attribution au dernier
clic declare : le lead porte l'identifiant de campagne que Meta a transmis.
Un prospect qui voit une publicite, n'y clique pas, puis cherche
« formation video Montpellier » sur Google deux semaines plus tard apparait
comme un lead sans campagne. Le cout par client calcule ici est donc un
MAJORANT : la publicite produit au moins ce qui lui est attribue, et
probablement un peu plus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from django.db.models import Count, Sum

from apps.crm.models import Lead
from apps.pipeline.models import Etape, Opportunite
from apps.publicite.models import Campagne, Depense


def _euros(centimes: int | None) -> Decimal | None:
    if centimes is None:
        return None
    return (Decimal(centimes) / 100).quantize(Decimal("0.01"))


@dataclass
class Maillon:
    """Un etage de l'entonnoir."""

    nom: str
    valeur: int
    #: Taux de passage depuis l'etage precedent, en pourcentage.
    taux: Decimal | None = None
    #: Cout unitaire a cet etage, en centimes.
    cout_centimes: int | None = None

    @property
    def cout(self) -> Decimal | None:
        return _euros(self.cout_centimes)

    @property
    def largeur(self) -> Decimal:
        """Largeur de la barre, en pourcentage de l'etage precedent.

        Calculee ici et non dans le gabarit : un etage a zero doit donner
        une barre vide. Un `{% if %}` qui retombait sur 100 % affichait une
        barre PLEINE en face d'un zero, ce qui se lit exactement a
        l'envers.
        """
        if not self.valeur:
            return Decimal(0)
        if self.taux is None:
            return Decimal(100)
        return min(self.taux, Decimal(100))


@dataclass
class Attribution:
    """Ce qu'une campagne — ou toutes — a coute et rapporte."""

    libelle: str
    depense_centimes: int = 0
    impressions: int = 0
    clics: int = 0
    leads: int = 0
    opportunites: int = 0
    dossiers_deposes: int = 0
    accords: int = 0
    payes: int = 0
    chiffre_affaires_centimes: int = 0
    perdus: int = 0
    maillons: list[Maillon] = field(default_factory=list)
    avertissements: list[str] = field(default_factory=list)

    # --- Couts unitaires -------------------------------------------------

    def _cout(self, quantite: int) -> int | None:
        if not quantite or not self.depense_centimes:
            return None
        return round(self.depense_centimes / quantite)

    @property
    def cpm_centimes(self) -> int | None:
        if not self.impressions:
            return None
        return round(self.depense_centimes * 1000 / self.impressions)

    @property
    def cpc_centimes(self) -> int | None:
        return self._cout(self.clics)

    @property
    def cout_par_lead_centimes(self) -> int | None:
        return self._cout(self.leads)

    @property
    def cout_par_opportunite_centimes(self) -> int | None:
        return self._cout(self.opportunites)

    @property
    def cout_par_client_centimes(self) -> int | None:
        return self._cout(self.payes)

    @property
    def ctr(self) -> Decimal | None:
        if not self.impressions:
            return None
        return (Decimal(self.clics) * 100 / self.impressions).quantize(Decimal("0.01"))

    @property
    def roas(self) -> Decimal | None:
        """Retour sur depense publicitaire. 3,0 = 3 € encaisses par euro depense."""
        if not self.depense_centimes:
            return None
        return (Decimal(self.chiffre_affaires_centimes) / self.depense_centimes).quantize(
            Decimal("0.01")
        )

    @property
    def depense(self) -> Decimal:
        return _euros(self.depense_centimes)

    # Les gabarits lisent des euros, jamais des centimes : « 13010 c. »
    # affiche a un utilisateur n'est pas un montant, c'est une fuite de
    # representation interne.
    @property
    def cout_par_lead(self) -> Decimal | None:
        return _euros(self.cout_par_lead_centimes)

    @property
    def cout_par_opportunite(self) -> Decimal | None:
        return _euros(self.cout_par_opportunite_centimes)

    @property
    def cout_par_client(self) -> Decimal | None:
        return _euros(self.cout_par_client_centimes)

    @property
    def cpc(self) -> Decimal | None:
        return _euros(self.cpc_centimes)

    @property
    def cpm(self) -> Decimal | None:
        return _euros(self.cpm_centimes)

    @property
    def chiffre_affaires(self) -> Decimal:
        return _euros(self.chiffre_affaires_centimes)

    @property
    def rentable(self) -> bool | None:
        roas = self.roas
        return None if roas is None else roas >= 1


def _totaliser(depenses) -> dict:
    """Totalise la depense sans jamais compter un mois deux fois.

    Une campagne peut etre saisie au mois ET au jour : la ligne mensuelle
    totalise, les lignes quotidiennes detaillent. Les additionner doublerait
    la depense de ce mois-la, et avec elle tous les couts par client.

    Regle : **des qu'un mois a des lignes quotidiennes, elles font foi** et
    la ligne mensuelle de ce mois est ignoree. Le detail l'emporte sur le
    total, parce qu'il est plus recent et plus precis.
    """
    mois_detailles = set(depenses.filter(jour__isnull=False).values_list("campagne_id", "mois"))
    retenues = [
        d
        for d in depenses.only(
            "campagne_id", "mois", "jour", "montant_centimes", "impressions", "clics"
        )
        if d.jour is not None or (d.campagne_id, d.mois) not in mois_detailles
    ]
    return {
        "depense": sum(d.montant_centimes for d in retenues),
        "impressions": sum(d.impressions for d in retenues),
        "clics": sum(d.clics for d in retenues),
        "mois_detailles": len(mois_detailles),
    }


def _construire_maillons(a: Attribution) -> None:
    """L'entonnoir, avec les taux de passage d'un etage a l'autre."""
    etages = [
        ("Impressions", a.impressions, None),
        ("Clics", a.clics, a.cpc_centimes),
        ("Leads", a.leads, a.cout_par_lead_centimes),
        ("Opportunites", a.opportunites, a.cout_par_opportunite_centimes),
        ("Dossiers deposes", a.dossiers_deposes, a._cout(a.dossiers_deposes)),
        ("Accords financeur", a.accords, a._cout(a.accords)),
        ("Clients payes", a.payes, a.cout_par_client_centimes),
    ]
    precedent = None
    for nom, valeur, cout in etages:
        taux = None
        if precedent:
            taux = (Decimal(valeur) * 100 / precedent).quantize(Decimal("0.01"))
        a.maillons.append(Maillon(nom=nom, valeur=valeur, taux=taux, cout_centimes=cout))
        precedent = valeur or None


def attribuer(
    campagne: Campagne | None = None,
    *,
    depuis: date | None = None,
    jusqu_a: date | None = None,
) -> Attribution:
    """Calcule la chaine complete pour une campagne, ou pour toutes."""
    depenses = Depense.objects.all()
    leads = Lead.objects.filter(doublon_de__isnull=True)

    if campagne is not None:
        depenses = depenses.filter(campagne=campagne)
        leads = leads.filter(campagne=campagne)
        libelle = campagne.nom
    else:
        # Sans campagne : tout ce qui est rattache a une campagne. Les leads
        # sans campagne ne sont pas attribuables a une depense.
        leads = leads.filter(campagne__isnull=False)
        libelle = "Toutes campagnes"

    if depuis:
        depenses = depenses.filter(mois__gte=depuis.replace(day=1))
        leads = leads.filter(date_reception__date__gte=depuis)
    if jusqu_a:
        depenses = depenses.filter(mois__lte=jusqu_a)
        leads = leads.filter(date_reception__date__lte=jusqu_a)

    totaux = _totaliser(depenses)
    a = Attribution(
        libelle=libelle,
        depense_centimes=totaux["depense"] or 0,
        impressions=totaux["impressions"] or 0,
        clics=totaux["clics"] or 0,
        leads=leads.count(),
    )

    affaires = Opportunite.objects.filter(lead__in=leads)
    a.opportunites = affaires.count()
    a.perdus = affaires.filter(etape=Etape.PERDU).count()
    a.payes = affaires.filter(etape=Etape.PAYE).count()
    a.chiffre_affaires_centimes = (
        affaires.filter(etape=Etape.PAYE).aggregate(ca=Sum("montant_estime_centimes"))["ca"] or 0
    )

    from apps.financement.models import Dossier, EtatDossier

    dossiers = Dossier.objects.filter(opportunite__in=affaires)
    a.dossiers_deposes = dossiers.exclude(
        etat__in=[EtatDossier.BROUILLON, EtatDossier.A_DEPOSER]
    ).count()
    a.accords = dossiers.filter(etat__in=[EtatDossier.ACCORDE, EtatDossier.SOLDE]).count()

    if a.depense_centimes and not a.leads:
        a.avertissements.append(
            "De la depense, aucun lead rattache. Verifier que l'identifiant "
            "de campagne du back-office est bien celui de la regie : c'est "
            "lui qui fait tout le rapprochement."
        )
    if a.leads and not a.depense_centimes:
        a.avertissements.append(
            "Des leads, aucune depense saisie. Les couts unitaires ne peuvent pas etre calcules."
        )
    non_attribues = Lead.objects.filter(
        doublon_de__isnull=True, campagne__isnull=True, source="meta_lead_ads"
    ).count()
    if campagne is None and non_attribues:
        a.avertissements.append(
            f"{non_attribues} lead(s) Meta sans campagne rattachee : lancer le "
            "rapprochement, ou creer la campagne manquante."
        )

    _construire_maillons(a)
    return a


def par_campagne(*, depuis: date | None = None, jusqu_a: date | None = None) -> list:
    """Une ligne par campagne, la plus rentable en tete.

    Classees par cout par client plutot que par volume : une campagne qui
    produit 200 leads a 90 € le client vaut mieux qu'une qui en produit 400
    a 300 €, et le tableau doit le montrer d'un coup d'oeil.
    """
    lignes = [
        attribuer(campagne, depuis=depuis, jusqu_a=jusqu_a) for campagne in Campagne.objects.all()
    ]
    return sorted(
        lignes,
        key=lambda a: (
            a.cout_par_client_centimes is None,
            a.cout_par_client_centimes or 0,
            -(a.leads or 0),
        ),
    )


def rapprocher_les_leads() -> dict:
    """Relie les leads Meta a leur campagne, par identifiant.

    Idempotent : ne touche que les leads sans campagne.
    """
    connues = {c.identifiant_externe: c for c in Campagne.objects.exclude(identifiant_externe="")}
    a_traiter = Lead.objects.filter(campagne__isnull=True).exclude(meta_campagne_id="")

    rattaches, inconnues = 0, {}
    for lead in a_traiter.only("pk", "meta_campagne_id", "meta_campagne_nom"):
        campagne = connues.get(lead.meta_campagne_id)
        if campagne is None:
            inconnues.setdefault(lead.meta_campagne_id, lead.meta_campagne_nom or "")
            continue
        Lead.objects.filter(pk=lead.pk).update(campagne=campagne)
        rattaches += 1

    return {
        "rattaches": rattaches,
        "campagnes_inconnues": inconnues,
    }


def creer_les_campagnes_manquantes() -> int:
    """Cree les campagnes vues dans les leads mais absentes du referentiel.

    Sans depense, elles n'apportent aucun cout — mais elles font apparaitre
    le volume de leads par campagne, ce qui suffit deja a voir laquelle
    produit.
    """
    connues = set(Campagne.objects.values_list("identifiant_externe", flat=True))
    vues = (
        Lead.objects.exclude(meta_campagne_id="")
        .values("meta_campagne_id", "meta_campagne_nom")
        .annotate(n=Count("id"))
    )
    crees = 0
    for ligne in vues:
        identifiant = ligne["meta_campagne_id"]
        if identifiant in connues:
            continue
        Campagne.objects.create(
            plateforme="meta",
            identifiant_externe=identifiant,
            nom=ligne["meta_campagne_nom"] or f"Campagne Meta {identifiant}",
        )
        connues.add(identifiant)
        crees += 1
    return crees

"""Routage vers le bon financeur.

L'arbitrage est tranche : le Conseil de la Formation des chambres de metiers
n'existe plus depuis le 1er septembre 2022, et le FAFCEA est le guichet
unique des artisans, formations transverses comprises.

La regle que ces tests verrouillent : **on ne devine pas**. Un dossier parti
au mauvais guichet revient refuse apres plusieurs semaines, delai pendant
lequel la fenetre de depot de l'autre financeur peut s'etre fermee.
"""

import pytest

from apps.financement.routage import (
    AGEFICE,
    FAFCEA,
    FIF_PL,
    INDETERMINE,
    OPCO,
    router,
    router_entreprise,
)


def test_un_artisan_va_au_fafcea():
    r = router(inscrite_repertoire_metiers=True)
    assert r.financeur == FAFCEA
    assert r.certitude == "certain"
    assert "01/09/2022" in r.motif


def test_un_commercant_va_a_l_agefice():
    r = router(inscrite_repertoire_metiers=False, naf="56.10A")
    assert r.financeur == AGEFICE
    assert r.certitude == "certain"


def test_une_inscription_non_etablie_ne_route_pas():
    """Le defaut a eviter : l'API Recherche d'entreprises ne renseigne le
    Registre des Metiers que lorsqu'une activite y est declaree. Son absence
    ne prouve pas la non-inscription — et sur l'echantillon heraultais,
    32 % seulement portaient cette information."""
    r = router(inscrite_repertoire_metiers=None)
    assert r.financeur == INDETERMINE
    assert r.certitude == "indetermine"
    assert "ne prouve pas" in r.motif
    assert "URSSAF" in r.a_verifier or "D1" in r.a_verifier


def test_un_salarie_releve_de_l_opco_quel_que_soit_le_reste():
    """Un fonds de chefs d'entreprise ne finance pas un salarie, meme chez
    un artisan."""
    r = router(inscrite_repertoire_metiers=True, statut_contact="salarie")
    assert r.financeur == OPCO


@pytest.mark.parametrize("naf", ["M70.22Z", "M69.10Z", "Q86.21Z"])
def test_une_profession_liberale_est_orientee_fif_pl_avec_reserve(naf):
    """Le bareme du FIF PL est propre a chaque profession et revu chaque
    annee : le routage oriente, il ne chiffre pas."""
    r = router(inscrite_repertoire_metiers=False, naf=naf)
    assert r.financeur == FIF_PL
    assert r.certitude == "probable"
    assert "propre a chaque profession" in r.a_verifier


@pytest.mark.django_db
def test_routage_depuis_les_objets_du_crm():
    from apps.crm.models import Contact, Entreprise

    artisan = Entreprise.objects.create(
        denomination="BTP Benali",
        siren="552032534",
        inscrite_repertoire_metiers=True,
        naf="43.32A",
    )
    assert router_entreprise(artisan).financeur == FAFCEA

    restaurant = Entreprise.objects.create(
        denomination="Le Comptoir",
        siren="356000000",
        inscrite_repertoire_metiers=False,
        naf="56.10A",
    )
    assert router_entreprise(restaurant).financeur == AGEFICE

    inconnue = Entreprise.objects.create(denomination="A qualifier")
    assert router_entreprise(inconnue).financeur == INDETERMINE

    salarie = Contact.objects.create(entreprise=artisan, nom="Durand", statut="salarie")
    assert router_entreprise(artisan, salarie).financeur == OPCO

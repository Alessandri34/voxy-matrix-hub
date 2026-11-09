"""Permissions sur les vues du pipeline.

La matrice des roles vit dans `apps.accounts.models.ACCES`. Ces tests
verifient qu'elle est reellement APPLIQUEE : une matrice de droits qui
n'existe que dans le modele devient decorative des la troisieme vue ecrite.

Deux exigences cumulees, et dans cet ordre : authentifie, puis verifie par
2FA. Un mot de passe seul ne doit pas suffire a lire des donnees de
prospects — c'est la raison d'etre de l'admin a double authentification de
la phase 0.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.models import ACCES, Role
from apps.crm.models import Entreprise
from apps.pipeline.models import Opportunite

pytestmark = pytest.mark.django_db


def utilisateur(role, **extra):
    return get_user_model().objects.create_user(
        username=f"essai-{role}", password="motdepasse-long-12", role=role, **extra
    )


class ClientVerifie:
    """Simule une session passee par la double authentification.

    `django_otp` pose `request.user.is_verified()` a partir de
    `user.otp_device`. On enregistre un appareil TOTP et on le declare
    verifie, ce qui est exactement ce que fait une connexion reelle.
    """

    @staticmethod
    def connecter(client, utilisateur, *, avec_2fa=True):
        client.force_login(utilisateur)
        if not avec_2fa:
            return client
        from django_otp.plugins.otp_static.models import StaticDevice

        appareil = StaticDevice.objects.create(user=utilisateur, name="essai")
        session = client.session
        session["otp_device_id"] = appareil.persistent_id
        session.save()
        return client


@pytest.fixture
def affaire():
    entreprise = Entreprise.objects.create(denomination="Le Comptoir", siren="552032534")
    return Opportunite.objects.create(entreprise=entreprise, intitule="Visibilite locale 21 h")


def test_un_visiteur_anonyme_est_renvoye_vers_la_connexion(client):
    reponse = client.get(reverse("pipeline:kanban"))
    assert reponse.status_code == 302
    assert "/login" in reponse["Location"] or "next=" in reponse["Location"]


def test_un_mot_de_passe_sans_2fa_ne_suffit_pas(client):
    """403 et non une redirection : le renvoyer vers une page de connexion
    ou il est deja connecte ne lui dirait pas ce qui manque."""
    ClientVerifie.connecter(client, utilisateur(Role.ADMIN), avec_2fa=False)
    assert client.get(reverse("pipeline:kanban")).status_code == 403


@pytest.mark.parametrize(
    "role,attendu",
    [
        (Role.ADMIN, 200),
        (Role.COMMERCIAL, 200),
        # L'administratif gere les dossiers de financement, pas la vente.
        (Role.ADMINISTRATIF, 403),
        (Role.FORMATEUR, 403),
        (Role.LECTURE, 403),
    ],
)
def test_acces_au_kanban_par_role(client, role, attendu):
    ClientVerifie.connecter(client, utilisateur(role))
    assert client.get(reverse("pipeline:kanban")).status_code == attendu


@pytest.mark.parametrize(
    "role,attendu",
    [
        (Role.ADMIN, 200),
        (Role.COMMERCIAL, 200),
        (Role.ADMINISTRATIF, 200),
        # Un formateur n'a pas a lire la file des prospects.
        (Role.FORMATEUR, 403),
        (Role.LECTURE, 403),
    ],
)
def test_acces_a_la_file_des_leads_par_role(client, role, attendu):
    ClientVerifie.connecter(client, utilisateur(role))
    assert client.get(reverse("pipeline:leads")).status_code == attendu


def test_le_formateur_ne_peut_pas_deplacer_une_affaire(client, affaire):
    """Le deplacement est verifie separement de l'affichage : une vue qui
    ecrit et qui ne verifie rien est le trou classique."""
    ClientVerifie.connecter(client, utilisateur(Role.FORMATEUR))
    reponse = client.post(reverse("pipeline:deplacer", args=[affaire.pk]), {"etape": "qualifie"})
    assert reponse.status_code == 403
    affaire.refresh_from_db()
    assert affaire.etape == "nouveau"


def test_la_lecture_seule_ne_peut_pas_deplacer(client, affaire):
    ClientVerifie.connecter(client, utilisateur(Role.LECTURE))
    reponse = client.post(reverse("pipeline:deplacer", args=[affaire.pk]), {"etape": "qualifie"})
    assert reponse.status_code == 403


def test_une_requete_get_ne_deplace_rien(client, affaire):
    """Un deplacement par GET serait declenchable par un simple lien, ou par
    un pre-chargement de navigateur."""
    ClientVerifie.connecter(client, utilisateur(Role.ADMIN))
    reponse = client.get(reverse("pipeline:deplacer", args=[affaire.pk]))
    assert reponse.status_code == 405


def test_un_commercial_deplace_et_cela_se_voit(client, affaire):
    ClientVerifie.connecter(client, utilisateur(Role.COMMERCIAL))
    reponse = client.post(
        reverse("pipeline:deplacer", args=[affaire.pk]), {"etape": "rdv_diagnostic"}
    )
    assert reponse.status_code == 200
    assert reponse.json()["ok"] is True
    affaire.refresh_from_db()
    assert affaire.etape == "rdv_diagnostic"
    assert affaire.probabilite == 35
    assert affaire.passages.count() == 1


def test_perdu_sans_motif_renvoie_un_message_lisible(client, affaire):
    """La vue ne duplique pas la regle : elle laisse le service la tenir et
    traduit l'erreur. Deux copies d'une meme regle finissent par divercher."""
    ClientVerifie.connecter(client, utilisateur(Role.COMMERCIAL))
    reponse = client.post(reverse("pipeline:deplacer", args=[affaire.pk]), {"etape": "perdu"})
    assert reponse.status_code == 400
    assert "motif" in reponse.json()["erreur"].lower()
    affaire.refresh_from_db()
    assert affaire.etape == "nouveau"


def test_perdu_avec_motif_passe_par_la_vue(client, affaire):
    ClientVerifie.connecter(client, utilisateur(Role.COMMERCIAL))
    reponse = client.post(
        reverse("pipeline:deplacer", args=[affaire.pk]),
        {"etape": "perdu", "motif_de_perte": "reste_a_charge"},
    )
    assert reponse.status_code == 200
    affaire.refresh_from_db()
    assert affaire.etape == "perdu"
    assert affaire.motif_de_perte == "reste_a_charge"


def test_la_matrice_des_roles_couvre_tous_les_roles():
    """Un role ajoute sans entree dans ACCES n'aurait acces a rien — ce qui
    est sur, mais silencieux. Mieux vaut que le test le dise."""
    assert set(ACCES) == set(Role)


def test_chaque_module_cite_dans_acces_est_connu():
    """Une faute de frappe dans un nom de module donnerait un droit qui ne
    s'applique a aucune vue, sans jamais lever d'erreur."""
    modules_connus = {
        "crm",
        "pipeline",
        "financement",
        "formation",
        "sequences",
        "reporting",
        "audit",
    }
    for role, modules in ACCES.items():
        inconnus = modules - modules_connus
        assert not inconnus, f"{role} reference des modules inconnus : {inconnus}"


# --------------------------------------------------------------------------
# Protection CSRF
# --------------------------------------------------------------------------


def test_le_kanban_fournit_un_jeton_csrf_au_javascript():
    """Non-regression.

    Le client de test Django desactive la verification CSRF : tous les tests
    de deplacement passaient alors que, dans un vrai navigateur, le `fetch`
    etait refuse en 403 — le gabarit ne lisait `csrf_token` nulle part, donc
    `get_token()` n'etait jamais appele et le cookie n'existait pas.
    """
    from django.test import Client

    client = Client()
    ClientVerifie.connecter(client, utilisateur(Role.ADMIN))
    reponse = client.get(reverse("pipeline:kanban"))
    assert reponse.status_code == 200
    assert b'id="jeton-csrf"' in reponse.content
    # get_token() a bien ete appele : le cookie part avec la reponse.
    assert "csrftoken" in reponse.cookies


def test_un_deplacement_sans_jeton_csrf_est_refuse(affaire):
    """Verifie avec la protection CSRF reellement active."""
    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    ClientVerifie.connecter(client, utilisateur(Role.ADMIN))
    reponse = client.post(reverse("pipeline:deplacer", args=[affaire.pk]), {"etape": "qualifie"})
    assert reponse.status_code == 403
    affaire.refresh_from_db()
    assert affaire.etape == "nouveau"


def test_un_deplacement_avec_le_jeton_du_gabarit_passe(affaire):
    """Le parcours reel : on lit le jeton sur la page, on le renvoie en
    en-tete, exactement comme le fait le JavaScript du Kanban."""
    import re

    from django.test import Client

    client = Client(enforce_csrf_checks=True)
    ClientVerifie.connecter(client, utilisateur(Role.ADMIN))
    page = client.get(reverse("pipeline:kanban")).content.decode()
    jeton = re.search(r'id="jeton-csrf" value="([^"]+)"', page).group(1)

    reponse = client.post(
        reverse("pipeline:deplacer", args=[affaire.pk]),
        {"etape": "qualifie"},
        HTTP_X_CSRFTOKEN=jeton,
    )
    assert reponse.status_code == 200
    affaire.refresh_from_db()
    assert affaire.etape == "qualifie"


@pytest.mark.parametrize("route", ["pipeline:kanban", "pipeline:leads"])
def test_aucune_balise_de_gabarit_ne_fuit_dans_la_page(client, route):
    """Non-regression.

    La syntaxe `{# … #}` de Django ne vaut que pour UNE ligne. Ecrit sur
    plusieurs, le commentaire n'est pas reconnu et s'affiche en clair aux
    utilisateurs — ce qui etait le cas du Kanban, visible seulement en
    ouvrant la page.
    """
    ClientVerifie.connecter(client, utilisateur(Role.ADMIN))
    contenu = client.get(reverse(route)).content.decode()
    # On regarde le corps rendu, pas le JavaScript, qui contient des
    # accolades legitimes.
    corps = contenu.split("<main>", 1)[-1]
    for balise in ("{#", "#}", "{%", "%}", "{{", "}}"):
        assert balise not in corps, f"« {balise} » apparait dans la page rendue"

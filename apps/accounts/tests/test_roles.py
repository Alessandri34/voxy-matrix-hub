"""Les cinq roles existent et donnent exactement les acces prevus."""

import pytest

from apps.accounts.models import ACCES, Role, Utilisateur


def test_les_cinq_roles_du_prd_existent():
    assert {r.value for r in Role} == {
        "admin",
        "commercial",
        "administratif",
        "formateur",
        "lecture",
    }


def test_chaque_role_a_une_table_d_acces():
    assert set(ACCES) == set(Role)


@pytest.mark.django_db
def test_le_role_par_defaut_est_le_plus_etroit():
    u = Utilisateur.objects.create_user(username="nouveau", password="motdepasse-long-12")
    assert u.role == Role.LECTURE
    assert u.peut_acceder("reporting")
    assert not u.peut_acceder("financement")


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "autorise", "interdit"),
    [
        (Role.ADMIN, "audit", None),
        (Role.COMMERCIAL, "pipeline", "financement"),
        (Role.ADMINISTRATIF, "financement", "sequences"),
        (Role.FORMATEUR, "formation", "crm"),
        (Role.LECTURE, "reporting", "crm"),
    ],
)
def test_acces_par_role(role, autorise, interdit):
    u = Utilisateur.objects.create_user(
        username=f"u-{role}", password="motdepasse-long-12", role=role
    )
    assert u.peut_acceder(autorise)
    if interdit:
        assert not u.peut_acceder(interdit)


@pytest.mark.django_db
def test_seul_l_admin_voit_l_audit():
    for role in Role:
        u = Utilisateur.objects.create_user(
            username=f"audit-{role}", password="motdepasse-long-12", role=role
        )
        assert u.peut_acceder("audit") is (role == Role.ADMIN)

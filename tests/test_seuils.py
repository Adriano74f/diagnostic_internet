import pytest

from modele import Statut
from seuils import (classer, classer_debit, classer_signal, pire,
                    LATENCE_BOX_MS)


@pytest.mark.parametrize("valeur, attendu", [
    (5, Statut.OK),
    (10, Statut.OK),          # pile sur la limite OK
    (10.1, Statut.ATTENTION),
    (30, Statut.ATTENTION),   # pile sur la limite ATTENTION
    (31, Statut.PROBLEME),
])
def test_classer_latence_box(valeur, attendu):
    assert classer(valeur, LATENCE_BOX_MS) == attendu


@pytest.mark.parametrize("dbm, attendu", [
    (-50, Statut.OK),
    (-60, Statut.OK),
    (-65, Statut.ATTENTION),
    (-70, Statut.ATTENTION),
    (-71, Statut.PROBLEME),
])
def test_classer_signal(dbm, attendu):
    assert classer_signal(dbm) == attendu


@pytest.mark.parametrize("mbps, abonnement, attendu", [
    (150, 300, Statut.OK),          # 50 % de l'abonnement
    (100, 300, Statut.ATTENTION),
    (60, 300, Statut.ATTENTION),    # 20 % de l'abonnement
    (50, 300, Statut.PROBLEME),
    (20, None, Statut.OK),          # sans abonnement : seuils absolus
    (10, None, Statut.ATTENTION),
    (4, None, Statut.PROBLEME),
])
def test_classer_debit(mbps, abonnement, attendu):
    assert classer_debit(mbps, abonnement) == attendu


def test_pire_renvoie_le_statut_le_plus_grave():
    assert pire(Statut.OK, Statut.PROBLEME, Statut.ATTENTION) == Statut.PROBLEME
    assert pire(Statut.OK, Statut.OK) == Statut.OK
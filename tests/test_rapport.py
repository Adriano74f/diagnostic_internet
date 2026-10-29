from arbre_decision import diagnostiquer
from modele import Statut
from rapport import generer_html
from tests.test_arbre import avec, resultat, resultats_sains


def test_rapport_contient_diagnostic_et_mesures():
    r = resultats_sains()
    page = generer_html(r, diagnostiquer(r), attendu=300)
    assert "Votre connexion fonctionne normalement" in page
    assert "Latence Internet" in page
    assert "300 Mbit/s" in page


def test_rapport_echappe_le_html():
    r = avec(dns=resultat("DNS", Statut.PROBLEME, message="<script>alert(1)</script>"))
    page = generer_html(r, diagnostiquer(r))
    assert "<script>" not in page
    assert "&lt;script&gt;" in page
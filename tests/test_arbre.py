import pytest

from arbre_decision import diagnostiquer
from explications import EXPLICATIONS
from modele import ResultatTest, Statut


def resultat(nom, statut=Statut.OK, valeur=None, unite="", details=None, message=""):
    return ResultatTest(nom, statut, valeur, unite, details or {},
                        message or f"{nom} : {statut.value}")


def resultats_sains():
    return {
        "interface": resultat("Wi-Fi", valeur=-55, unite="dBm", details={"type": "wifi"}),
        "passerelle": resultat("Box (passerelle)", valeur=3, unite="ms"),
        "acces_internet": resultat("Accès Internet"),
        "dns": resultat("DNS", valeur=20, unite="ms"),
        "latence": resultat("Latence Internet", valeur=15, unite="ms"),
        "perte": resultat("Perte de paquets", valeur=0, unite="%",
                          details={"box": 0, "internet": 0}),
        "traceroute": resultat("Traceroute", valeur=8, unite="sauts",
                               details={"degradation": None}),
        "debit": resultat("Débit", valeur=300, unite="Mbit/s"),
    }


def avec(**changements):
    """Connexion saine dans laquelle on remplace certains résultats."""
    r = resultats_sains()
    r.update(changements)
    return r


def degradation_au_saut(numero):
    return resultat("Traceroute", Statut.ATTENTION, 10, "sauts",
                    {"degradation": {"saut": numero, "ip": "203.0.113.1", "hausse": 80}})


P = Statut.PROBLEME

CAS = [
    pytest.param(resultats_sains(), "connexion_saine", id="connexion saine"),
    pytest.param(avec(interface=resultat("Connexion réseau", P)),
                 "pas_connexion", id="pas de connexion"),
    pytest.param(avec(interface=resultat("Wi-Fi", P, -80, "dBm", {"type": "wifi"})),
                 "wifi_faible", id="wifi faible"),
    pytest.param(avec(passerelle=resultat("Box (passerelle)", P, 85, "ms")),
                 "box_ou_reseau_local", id="box lente"),
    pytest.param(avec(perte=resultat("Perte de paquets", P, 10, "%",
                                     {"box": 10, "internet": 10})),
                 "box_ou_reseau_local", id="perte des la box"),
    pytest.param(avec(acces_internet=resultat("Accès Internet", P)),
                 "panne_fai", id="panne fournisseur"),
    pytest.param(avec(dns=resultat("DNS", P)),
                 "dns", id="dns en panne"),
    pytest.param(avec(latence=resultat("Latence Internet", P, 300, "ms"),
                      traceroute=degradation_au_saut(3)),
                 "fai_sature", id="fournisseur sature"),
    pytest.param(avec(latence=resultat("Latence Internet", P, 300, "ms"),
                      traceroute=degradation_au_saut(8)),
                 "internet_lointain", id="probleme lointain"),
    pytest.param(avec(latence=resultat("Latence Internet", P, 300, "ms")),
                 "fai_sature", id="latence sans degradation visible"),
    pytest.param(avec(debit=resultat("Débit", P, 10, "Mbit/s")),
                 "debit_insuffisant", id="debit insuffisant"),
]


@pytest.mark.parametrize("resultats, cause_attendue", CAS)
def test_cause_principale(resultats, cause_attendue):
    assert diagnostiquer(resultats).cause == cause_attendue


# ---------- Règles particulières ----------

def test_le_plus_proche_est_prioritaire():
    # Wi-Fi faible ET DNS en panne : on accuse le Wi-Fi, plus proche
    r = avec(interface=resultat("Wi-Fi", P, -80, "dBm", {"type": "wifi"}),
             dns=resultat("DNS", P))
    assert diagnostiquer(r).cause == "wifi_faible"


def test_pas_de_problemes_secondaires_en_cascade():
    # Sans connexion, tout échoue : on ne liste pas ces conséquences
    r = avec(interface=resultat("Connexion réseau", P),
             acces_internet=resultat("Accès Internet", P),
             dns=resultat("DNS", P))
    assert diagnostiquer(r).secondaires == []


def test_problemes_secondaires_listes():
    r = avec(debit=resultat("Débit", P, 10, "Mbit/s"),
             dns=resultat("DNS", Statut.ATTENTION, 150, "ms"))
    diag = diagnostiquer(r)
    assert diag.cause == "debit_insuffisant"
    assert any("DNS" in s for s in diag.secondaires)


def test_certitude_moyenne_sans_degradation_visible():
    r = avec(latence=resultat("Latence Internet", P, 300, "ms"))
    assert diagnostiquer(r).confiance == "moyenne"


def test_test_en_echec_signale_comme_non_realise():
    r = avec(debit=resultat("Débit", Statut.ECHEC))
    diag = diagnostiquer(r)
    assert diag.cause == "connexion_saine"
    assert diag.non_realises == ["Débit"]


def test_preuves_presentes():
    diag = diagnostiquer(avec(dns=resultat("DNS", P, message="DNS muet")))
    assert diag.preuves == ["DNS : DNS muet"]


# ---------- Explications ----------

TOUTES_LES_CAUSES = ["pas_connexion", "wifi_faible", "box_ou_reseau_local", "panne_fai",
                     "dns", "fai_sature", "internet_lointain", "debit_insuffisant",
                     "connexion_saine"]


@pytest.mark.parametrize("cause", TOUTES_LES_CAUSES)
def test_chaque_cause_a_une_explication(cause):
    texte = EXPLICATIONS[cause]
    assert texte["titre"]
    assert texte["explication"]
    assert len(texte["conseils"]) >= 2
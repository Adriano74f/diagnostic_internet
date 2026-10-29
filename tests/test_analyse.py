import re
from pathlib import Path

import pytest

from outils import analyser_ping, decoder
from tests_reseau.latence import statistiques
from tests_reseau.traceroute import analyser_tracert, trouver_degradation

FIXTURES = Path(__file__).parent / "fixtures"


def lire(nom):
    """Lit une sortie enregistrée, avec le même décodage que le programme."""
    return decoder((FIXTURES / nom).read_bytes())


# ---------- Décodage ----------

def test_decoder_utf8_avec_espace_insecable():
    # Le bug du J5 : netsh répond en UTF-8 avec une espace insécable
    texte = "Signal\u00a0: 85%"
    assert decoder(texte.encode("utf-8")) == texte


def test_decoder_encodage_console():
    # ping répond dans l'encodage de la console Windows (cp850 en français)
    assert decoder("Réponse de 1.1.1.1".encode("cp850")) == "Réponse de 1.1.1.1"


# ---------- Ping ----------

PING_FR = ("Réponse de 1.1.1.1 : octets=32 temps=14 ms TTL=57\n"
           "Réponse de 1.1.1.1 : octets=32 temps<1ms TTL=57\n")
PING_EN = ("Reply from 1.1.1.1: bytes=32 time=14ms TTL=57\n"
           "Reply from 1.1.1.1: bytes=32 time<1ms TTL=57\n")


@pytest.mark.parametrize("sortie", [PING_FR, PING_EN], ids=["français", "anglais"])
def test_analyser_ping_francais_et_anglais(sortie):
    assert analyser_ping(sortie) == [14, 1]


def test_hote_injoignable_n_est_pas_une_reponse():
    sortie = "Réponse de 192.168.1.10 : Impossible de joindre l'hôte de destination.\n"
    assert analyser_ping(sortie) == []


def test_ping_reel_reussi():
    sortie = lire("ping_internet_ok.txt")
    temps = analyser_ping(sortie)
    # On compare avec le nombre de réponses annoncé par Windows lui-même
    recus = int(re.search(r"(?:reçus|Received)\s*=\s*(\d+)", sortie).group(1))
    assert len(temps) == recus
    assert all(t >= 0 for t in temps)


def test_ping_reel_echec():
    assert analyser_ping(lire("ping_echec.txt")) == []


# ---------- Statistiques ----------

def test_statistiques_completes():
    stats = statistiques([10, 20, 10, 20], nb=4)
    assert stats["moyenne"] == 15
    assert stats["min"] == 10
    assert stats["max"] == 20
    assert stats["gigue"] == 10
    assert stats["perte"] == 0


def test_statistiques_avec_perte():
    assert statistiques([10, 10], nb=4)["perte"] == 50


def test_statistiques_aucune_reponse():
    stats = statistiques([], nb=4)
    assert stats["recus"] == 0
    assert stats["perte"] == 100
    assert "moyenne" not in stats


# ---------- Traceroute ----------

TRACERT = """
Détermination de l'itinéraire vers 1.1.1.1 avec un maximum de 15 sauts.

  1    <1 ms    <1 ms     1 ms  192.168.1.1
  2     5 ms     4 ms     6 ms  10.0.0.1
  3     *        *        *     Délai d'attente de la demande dépassé.
  4    12 ms    11 ms    13 ms  1.1.1.1

Itinéraire déterminé.
"""


def test_analyser_tracert_exemple():
    sauts = analyser_tracert(TRACERT)
    assert [s["numero"] for s in sauts] == [1, 2, 3, 4]
    assert sauts[0]["temps"] == [1, 1, 1]
    assert sauts[2]["latence"] is None          # saut sans réponse
    assert sauts[3]["ip"] == "1.1.1.1"


def test_analyser_tracert_reel():
    sauts = analyser_tracert(lire("tracert_ok.txt"))
    assert sauts, "aucun saut reconnu dans la sortie réelle"
    assert sauts[0]["numero"] == 1


def sauts_avec_latences(*latences):
    return [{"numero": i, "ip": None, "temps": [], "latence": l}
            for i, l in enumerate(latences, 1)]


def test_degradation_persistante_detectee():
    degradation = trouver_degradation(sauts_avec_latences(1, 5, 10, 80, 85, 90))
    assert degradation["saut"] == 4
    assert degradation["hausse"] == 70


def test_pic_isole_ignore():
    # Un routeur lent à répondre, mais la latence redescend ensuite
    assert trouver_degradation(sauts_avec_latences(1, 5, 200, 10, 12)) is None


def test_pas_de_degradation():
    assert trouver_degradation(sauts_avec_latences(1, 5, 8, 10, 12)) is None
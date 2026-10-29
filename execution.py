from tests_reseau.interface import tester_interface
from tests_reseau.passerelle import tester_passerelle
from tests_reseau.latence import tester_acces_internet, tester_latence_et_perte
from tests_reseau.dns_test import tester_dns
from tests_reseau.traceroute import tester_traceroute
from tests_reseau.debit import tester_debit

NB_ETAPES = 7


def sans_suivi(numero, total, texte):
    pass


def executer_diagnostic(attendu=None, progression=sans_suivi):
    """Lance les tests du plus proche au plus lointain.
    progression(numero, total, texte) est appelée avant chaque étape,
    pour que la console ou l'interface graphique affichent l'avancement."""
    resultats = {}

    progression(0, NB_ETAPES, "Test de la connexion…")
    resultats["interface"] = tester_interface()

    progression(1, NB_ETAPES, "Test de la box…")
    resultats["passerelle"] = tester_passerelle()

    progression(2, NB_ETAPES, "Test de l'accès à Internet…")
    resultats["acces_internet"] = tester_acces_internet()

    progression(3, NB_ETAPES, "Test du DNS…")
    resultats["dns"] = tester_dns()

    progression(4, NB_ETAPES, "Mesure de la latence et des pertes (environ 20 s)…")
    resultats["latence"], resultats["perte"] = tester_latence_et_perte()

    progression(5, NB_ETAPES, "Traceroute (jusqu'à 1 min)…")
    resultats["traceroute"] = tester_traceroute()

    progression(6, NB_ETAPES, "Mesure du débit (environ 30 s)…")
    resultats["debit"] = tester_debit(attendu)

    progression(NB_ETAPES, NB_ETAPES, "Diagnostic terminé.")
    return resultats
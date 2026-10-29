from rich.console import Console
from rich.table import Table

from modele import Statut
from tests_reseau.interface import tester_interface
from tests_reseau.passerelle import tester_passerelle
from tests_reseau.latence import tester_acces_internet, tester_latence_et_perte
from tests_reseau.dns_test import tester_dns

COULEURS = {
    Statut.OK: "green",
    Statut.ATTENTION: "yellow",
    Statut.PROBLEME: "red",
    Statut.ECHEC: "magenta",
}


def afficher(resultats):
    table = Table(title="Diagnostic Internet")
    table.add_column("Test")
    table.add_column("Statut")
    table.add_column("Mesure")
    table.add_column("Détail")
    for r in resultats:
        mesure = f"{r.valeur:.0f} {r.unite}" if r.valeur is not None else "-"
        table.add_row(r.nom, f"[{COULEURS[r.statut]}]{r.statut.value}[/]", mesure, r.message)
    Console().print(table)


def main():
    console = Console()
    resultats = []
    with console.status("Test de la connexion…"):
        resultats.append(tester_interface())
    with console.status("Test de la box…"):
        resultats.append(tester_passerelle())
    with console.status("Test de l'accès à Internet…"):
        resultats.append(tester_acces_internet())
    with console.status("Test du DNS…"):
        resultats.append(tester_dns())
    with console.status("Mesure de la latence et des pertes (environ 20 s)…"):
        resultats.extend(tester_latence_et_perte())
    afficher(resultats)


if __name__ == "__main__":
    main()
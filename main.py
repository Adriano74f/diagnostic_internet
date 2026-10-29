from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from arbre_decision import diagnostiquer
from explications import EXPLICATIONS
from modele import Statut
from tests_reseau.interface import tester_interface
from tests_reseau.passerelle import tester_passerelle
from tests_reseau.latence import tester_acces_internet, tester_latence_et_perte
from tests_reseau.dns_test import tester_dns
from tests_reseau.traceroute import tester_traceroute
from tests_reseau.debit import tester_debit

COULEURS = {
    Statut.OK: "green",
    Statut.ATTENTION: "yellow",
    Statut.PROBLEME: "red",
    Statut.ECHEC: "magenta",
}

console = Console()


def afficher(resultats):
    table = Table(title="Diagnostic Internet")
    table.add_column("Test")
    table.add_column("Statut")
    table.add_column("Mesure")
    table.add_column("Détail")
    for r in resultats:
        mesure = f"{r.valeur:.0f} {r.unite}" if r.valeur is not None else "-"
        table.add_row(r.nom, f"[{COULEURS[r.statut]}]{r.statut.value}[/]", mesure, r.message)
    console.print(table)


def afficher_diagnostic(diag):
    texte = EXPLICATIONS[diag.cause]
    lignes = [f"[bold]Où ?[/] {diag.zone}   (certitude : {diag.confiance})",
              "", texte["explication"]]
    if diag.preuves:
        lignes += ["", "[bold]Ce qui le montre :[/]"] + [f"  • {p}" for p in diag.preuves]
    lignes += ["", "[bold]Que faire ?[/]"]
    lignes += [f"  {i}. {c}" for i, c in enumerate(texte["conseils"], 1)]
    if diag.secondaires:
        lignes += ["", "[bold]À surveiller aussi :[/]"] + [f"  • {s}" for s in diag.secondaires]
    if diag.non_realises:
        lignes += ["", f"[dim]Tests non réalisés : {', '.join(diag.non_realises)}[/]"]

    couleur = "green" if diag.cause == "connexion_saine" else "red"
    console.print(Panel("\n".join(lignes), title=texte["titre"], border_style=couleur))


def demander_debit_abonnement():
    texte = input("Débit de votre abonnement en Mbit/s (Entrée pour ignorer) : ")
    texte = texte.strip().replace(",", ".")
    try:
        return float(texte) if texte else None
    except ValueError:
        return None


def main():
    attendu = demander_debit_abonnement()
    resultats = {}

    with console.status("Test de la connexion…"):
        resultats["interface"] = tester_interface()
    with console.status("Test de la box…"):
        resultats["passerelle"] = tester_passerelle()
    with console.status("Test de l'accès à Internet…"):
        resultats["acces_internet"] = tester_acces_internet()
    with console.status("Test du DNS…"):
        resultats["dns"] = tester_dns()
    with console.status("Mesure de la latence et des pertes (environ 20 s)…"):
        resultats["latence"], resultats["perte"] = tester_latence_et_perte()
    with console.status("Traceroute en cours (jusqu'à 1 min)…"):
        resultats["traceroute"] = tester_traceroute()
    with console.status("Mesure du débit (environ 30 s)…"):
        resultats["debit"] = tester_debit(attendu)

    afficher(resultats.values())
    afficher_diagnostic(diagnostiquer(resultats))


if __name__ == "__main__":
    main()
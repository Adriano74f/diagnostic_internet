from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from arbre_decision import diagnostiquer
from execution import executer_diagnostic
from explications import EXPLICATIONS
from modele import Statut
from rapport import enregistrer_rapport, texte_mesure

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
        table.add_row(r.nom, f"[{COULEURS[r.statut]}]{r.statut.value}[/]",
                      texte_mesure(r), r.message)
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

    with console.status("Démarrage…") as statut:
        def progression(numero, total, texte):
            if numero < total:
                statut.update(f"Étape {numero + 1}/{total} — {texte}")

        resultats = executer_diagnostic(attendu, progression)

    afficher(resultats.values())
    diag = diagnostiquer(resultats)
    afficher_diagnostic(diag)

    chemin = enregistrer_rapport(resultats, diag, attendu)
    console.print(f"Rapport enregistré : [bold]{chemin}[/]")


if __name__ == "__main__":
    main()
from rich.console import Console
from rich.table import Table

from modele import ResultatTest, Statut
from seuils import classer, LATENCE_BOX_MS

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
    for r in resultats:
        mesure = f"{r.valeur} {r.unite}" if r.valeur is not None else "-"
        table.add_row(r.nom, f"[{COULEURS[r.statut]}]{r.statut.value}[/]", mesure)
    Console().print(table)


def main():
    # Résultat fictif, en attendant les vrais tests (J2)
    latence = 12.0
    resultats = [
        ResultatTest("Passerelle (simulé)", classer(latence, LATENCE_BOX_MS), latence, "ms")
    ]
    afficher(resultats)


if __name__ == "__main__":
    main()
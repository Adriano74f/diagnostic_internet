import html
from datetime import datetime
from pathlib import Path

from explications import EXPLICATIONS
from modele import Statut

COULEURS = {
    Statut.OK: "#1e8e3e",
    Statut.ATTENTION: "#e37400",
    Statut.PROBLEME: "#d93025",
    Statut.ECHEC: "#9334e6",
}
LIBELLES = {
    Statut.OK: "OK",
    Statut.ATTENTION: "À surveiller",
    Statut.PROBLEME: "Problème",
    Statut.ECHEC: "Non réalisé",
}

CSS = """
body { font-family: Segoe UI, Arial, sans-serif; max-width: 900px; margin: 30px auto;
       padding: 0 16px; color: #202124; background: #fff; }
h1 { margin-bottom: 4px; }
.date { color: #5f6368; margin-top: 0; }
.diagnostic { border-left: 6px solid; padding: 12px 20px; background: #f8f9fa;
              border-radius: 4px; margin: 20px 0; }
table { border-collapse: collapse; width: 100%; margin: 12px 0 24px; }
th, td { border-bottom: 1px solid #dadce0; padding: 8px; text-align: left;
         vertical-align: top; }
th { background: #f1f3f4; }
.statut { font-weight: bold; white-space: nowrap; }
footer { color: #5f6368; font-size: 0.9em; margin-top: 30px; }
"""


def e(texte):
    """Échappe le texte pour l'insérer sans risque dans du HTML."""
    return html.escape(str(texte))


def texte_mesure(r):
    return f"{r.valeur:.0f} {r.unite}" if r.valeur is not None else "-"


def liste_html(elements):
    return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in elements) + "</ul>"


def section_traceroute(resultats):
    trace = resultats.get("traceroute")
    sauts = trace.details.get("sauts") if trace else None
    if not sauts:
        return ""
    lignes = ""
    for s in sauts:
        latence = f"{s['latence']:.0f} ms" if s["latence"] is not None else "pas de réponse"
        lignes += f"<tr><td>{s['numero']}</td><td>{e(s['ip'] or '—')}</td><td>{latence}</td></tr>"
    return ("<h2>Chemin jusqu'à Internet (traceroute)</h2>"
            "<table><tr><th>Saut</th><th>Adresse</th><th>Latence</th></tr>"
            f"{lignes}</table>")


def generer_html(resultats, diag, attendu=None):
    texte = EXPLICATIONS[diag.cause]
    couleur = COULEURS[Statut.OK] if diag.cause == "connexion_saine" else COULEURS[Statut.PROBLEME]
    date = datetime.now().strftime("%d/%m/%Y à %H:%M")

    lignes = ""
    for r in resultats.values():
        lignes += (f"<tr><td>{e(r.nom)}</td>"
                   f"<td class='statut' style='color:{COULEURS[r.statut]}'>{LIBELLES[r.statut]}</td>"
                   f"<td>{e(texte_mesure(r))}</td><td>{e(r.message)}</td></tr>")

    preuves = f"<h3>Ce qui le montre</h3>{liste_html(diag.preuves)}" if diag.preuves else ""
    conseils = "<ol>" + "".join(f"<li>{e(c)}</li>" for c in texte["conseils"]) + "</ol>"
    secondaires = (f"<h3>À surveiller aussi</h3>{liste_html(diag.secondaires)}"
                   if diag.secondaires else "")
    non_realises = (f"<p><em>Tests non réalisés : {e(', '.join(diag.non_realises))}</em></p>"
                    if diag.non_realises else "")
    abonnement = f"{attendu:g} Mbit/s" if attendu else "non renseigné"

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Diagnostic Internet du {date}</title>
<style>{CSS}</style>
</head>
<body>
<h1>Pourquoi mon Internet est lent ?</h1>
<p class="date">Diagnostic réalisé le {date}, abonnement déclaré : {abonnement}</p>

<div class="diagnostic" style="border-color:{couleur}">
  <h2 style="color:{couleur}">{e(texte['titre'])}</h2>
  <p><strong>Où ?</strong> {e(diag.zone)} (certitude : {e(diag.confiance)})</p>
  <p>{e(texte['explication'])}</p>
  {preuves}
  <h3>Que faire ?</h3>
  {conseils}
  {secondaires}
  {non_realises}
</div>

<h2>Détail des mesures</h2>
<table>
<tr><th>Test</th><th>Statut</th><th>Mesure</th><th>Détail</th></tr>
{lignes}
</table>

{section_traceroute(resultats)}

<footer>Rapport généré automatiquement. Vous pouvez le transmettre à votre fournisseur
d'accès si le problème persiste.</footer>
</body>
</html>"""


def enregistrer_rapport(resultats, diag, attendu=None, dossier="rapports"):
    """Enregistre le rapport dans un fichier daté et renvoie son chemin."""
    Path(dossier).mkdir(exist_ok=True)
    chemin = Path(dossier) / f"diagnostic_{datetime.now():%Y-%m-%d_%H-%M-%S}.html"
    chemin.write_text(generer_html(resultats, diag, attendu), encoding="utf-8")
    return chemin
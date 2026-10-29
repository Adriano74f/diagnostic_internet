import re
from statistics import median

from modele import ResultatTest, Statut
from outils import executer

CIBLE = "1.1.1.1"
SAUT_MS = 50   # hausse de latence considérée comme significative

# Ligne de tracert : numéro, 3 colonnes de temps ("<1 ms", "12 ms" ou "*"), puis IP ou message
RE_LIGNE = re.compile(r"^\s*(\d+)\s+((?:(?:<?\d+\s*ms|\*)\s+){3})(.*)$")
RE_TEMPS = re.compile(r"<?(\d+)\s*ms")
RE_IP = re.compile(r"\d{1,3}(?:\.\d{1,3}){3}")


def analyser_tracert(sortie):
    """Transforme la sortie de tracert en liste de sauts."""
    sauts = []
    for ligne in sortie.splitlines():
        m = RE_LIGNE.match(ligne)
        if not m:
            continue
        temps = [int(t) for t in RE_TEMPS.findall(m.group(2))]
        ip = RE_IP.search(m.group(3))
        sauts.append({
            "numero": int(m.group(1)),
            "ip": ip.group(0) if ip else None,
            "temps": temps,
            "latence": median(temps) if temps else None,
        })
    return sauts


def zone(numero):
    """Localisation approximative d'un saut."""
    if numero == 1:
        return "votre box"
    if numero <= 4:
        return "le réseau de votre fournisseur"
    return "Internet, au-delà de votre fournisseur"


def trouver_degradation(sauts):
    """Premier saut où la latence augmente fortement ET reste élevée jusqu'au bout."""
    repondants = [s for s in sauts if s["latence"] is not None]
    if len(repondants) < 2:
        return None
    latence_finale = repondants[-1]["latence"]
    for precedent, courant in zip(repondants, repondants[1:]):
        hausse = courant["latence"] - precedent["latence"]
        if hausse >= SAUT_MS and latence_finale >= courant["latence"] - SAUT_MS / 2:
            return {"saut": courant["numero"], "ip": courant["ip"], "hausse": hausse}
    return None


def tester_traceroute(cible=CIBLE, max_sauts=15):
    nom = "Traceroute"
    sortie = executer(["tracert", "-d", "-h", str(max_sauts), "-w", "1000", cible], delai=120)
    sauts = analyser_tracert(sortie)
    if not sauts:
        return ResultatTest(nom, Statut.ECHEC, message="Impossible d'analyser le résultat de tracert.")

    atteinte = any(s["ip"] == cible for s in sauts)
    degradation = trouver_degradation(sauts)
    details = {"cible": cible, "sauts": sauts, "atteinte": atteinte, "degradation": degradation}

    if degradation:
        statut = Statut.PROBLEME if degradation["hausse"] >= 100 else Statut.ATTENTION
        message = (f"La latence augmente de {degradation['hausse']:.0f} ms au saut "
                   f"{degradation['saut']} ({degradation['ip']}), dans {zone(degradation['saut'])}.")
    elif not atteinte:
        statut = Statut.ATTENTION
        message = f"{cible} non atteint en {max_sauts} sauts (certains routeurs bloquent le traceroute)."
    else:
        statut = Statut.OK
        message = f"{cible} atteint en {len(sauts)} sauts, sans hausse anormale de latence."

    return ResultatTest(nom, statut, len(sauts), "sauts", details, message)
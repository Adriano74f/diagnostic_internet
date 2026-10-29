from statistics import mean

from modele import ResultatTest, Statut
from outils import ping, powershell
from seuils import classer, LATENCE_BOX_MS, PERTE_POURCENT

ORDRE = [Statut.OK, Statut.ATTENTION, Statut.PROBLEME]


def pire(*statuts):
    """Renvoie le statut le plus grave."""
    return max(statuts, key=ORDRE.index)


def ip_passerelle():
    """Adresse IP de la passerelle par défaut (la box), ou None."""
    script = (
        "Get-NetRoute -DestinationPrefix 0.0.0.0/0 | Where-Object NextHop -ne '0.0.0.0' | "
        "Sort-Object RouteMetric | Select-Object -First 1 -ExpandProperty NextHop"
    )
    ip = powershell(script).strip()
    return ip or None


def tester_passerelle(nb=4):
    nom = "Box (passerelle)"
    ip = ip_passerelle()
    if ip is None:
        return ResultatTest(nom, Statut.PROBLEME,
                            message="Aucune passerelle : le PC ne sait pas comment sortir vers Internet.")

    temps, _ = ping(ip, nb)
    perte = 100 * (nb - len(temps)) / nb
    if not temps:
        return ResultatTest(nom, Statut.PROBLEME, details={"ip": ip, "perte_pourcent": 100},
                            message=f"La box ({ip}) ne répond pas.")

    moyenne = round(mean(temps), 1)
    statut = pire(classer(moyenne, LATENCE_BOX_MS), classer(perte, PERTE_POURCENT))
    return ResultatTest(
        nom, statut, moyenne, "ms",
        {"ip": ip, "temps": temps, "perte_pourcent": perte},
        f"Box {ip} : {moyenne} ms en moyenne, {perte:.0f} % de perte.",
    )
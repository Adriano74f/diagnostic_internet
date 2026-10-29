from concurrent.futures import ThreadPoolExecutor
from statistics import mean

from modele import ResultatTest, Statut
from outils import ping
from seuils import classer, pire, LATENCE_INTERNET_MS, GIGUE_MS, PERTE_POURCENT
from tests_reseau.passerelle import ip_passerelle

CIBLES_INTERNET = ["1.1.1.1", "8.8.8.8"]


def statistiques(temps, nb):
    """Calcule les statistiques d'une série de pings."""
    perte = round(100 * (nb - len(temps)) / nb, 1)
    if not temps:
        return {"recus": 0, "envoyes": nb, "perte": perte}
    if len(temps) > 1:
        gigue = sum(abs(a - b) for a, b in zip(temps, temps[1:])) / (len(temps) - 1)
    else:
        gigue = 0.0
    return {
        "recus": len(temps),
        "envoyes": nb,
        "perte": perte,
        "moyenne": round(mean(temps), 1),
        "min": min(temps),
        "max": max(temps),
        "gigue": round(gigue, 1),
    }


def mesurer(cible, nb=20):
    temps, _ = ping(cible, nb)
    return statistiques(temps, nb)


def tester_acces_internet():
    """Vérifie qu'au moins un serveur public répond."""
    for cible in CIBLES_INTERNET:
        temps, _ = ping(cible, nb=2)
        if temps:
            return ResultatTest(
                "Accès Internet", Statut.OK, details={"cible": cible},
                message=f"{cible} répond : la connexion vers Internet fonctionne.",
            )
    return ResultatTest(
        "Accès Internet", Statut.PROBLEME,
        message="Aucun serveur Internet ne répond (1.1.1.1 et 8.8.8.8).",
    )


def tester_latence_et_perte(nb=20):
    """Mesure box et Internet en parallèle. Renvoie 2 résultats : latence et perte."""
    ip_box = ip_passerelle()
    cible = CIBLES_INTERNET[0]
    with ThreadPoolExecutor() as executeur:
        futur_box = executeur.submit(mesurer, ip_box, nb) if ip_box else None
        futur_net = executeur.submit(mesurer, cible, nb)
        box = futur_box.result() if futur_box else None
        net = futur_net.result()
    return resultat_latence(net, box, cible), resultat_perte(net, box)


def resultat_latence(net, box, cible):
    nom = "Latence Internet"
    if net["recus"] == 0:
        return ResultatTest(
            nom, Statut.PROBLEME, details={"internet": net, "box": box},
            message=f"{cible} ne répond pas : latence impossible à mesurer.",
        )
    statut = pire(classer(net["moyenne"], LATENCE_INTERNET_MS),
                  classer(net["gigue"], GIGUE_MS))
    message = (f"{net['moyenne']} ms en moyenne (min {net['min']} / max {net['max']}), "
               f"gigue {net['gigue']} ms.")
    if box and box["recus"]:
        message += f" Dont {box['moyenne']} ms jusqu'à la box."
    return ResultatTest(nom, statut, net["moyenne"], "ms",
                        {"internet": net, "box": box}, message)


def resultat_perte(net, box):
    nom = "Perte de paquets"
    perte_box = box["perte"] if box else None
    perte_net = net["perte"]

    if perte_box:
        ou = "dès le réseau local (entre le PC et la box)"
    elif perte_net:
        ou = "après la box (côté fournisseur ou Internet)"
    else:
        ou = None

    texte_box = f"{perte_box} %" if perte_box is not None else "?"
    message = f"Box : {texte_box}, Internet : {perte_net} %."
    message += f" Perte {ou}." if ou else " Aucune perte."

    statut = classer(max(perte_net, perte_box or 0), PERTE_POURCENT)
    return ResultatTest(nom, statut, perte_net, "%",
                        {"box": perte_box, "internet": perte_net}, message)